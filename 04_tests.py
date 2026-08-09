"""
STEP 4 — TESTS
Validation gates for the pipeline. Run after 01->02->03.

These are the checks that would actually have caught the two real bugs found
during the build (motion summed instead of averaged; clock times sorted
lexically across midnight), plus reconciliation between layers.

Exit code 1 if any test fails, so this can gate a CI run.
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

DB = Path(__file__).parent / "ring.db"
LOCAL = ZoneInfo("America/New_York")
con = sqlite3.connect(DB)
cur = con.cursor()

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def q1(sql, args=()):
    return cur.execute(sql, args).fetchone()[0]


# --- layer reconciliation ----------------------------------------------------
raw_n = q1("SELECT COUNT(*) FROM raw_readings")
epoch_readings = q1("SELECT SUM(n_readings) FROM epochs_10min")
check("every raw reading lands in exactly one epoch bin",
      raw_n == epoch_readings, f"raw={raw_n:,} binned={epoch_readings:,}")

raw_steps = q1("SELECT SUM(value) FROM raw_readings WHERE data_type='steps'")
mart_steps = q1("SELECT SUM(steps_total) FROM daily_summary")
check("steps reconcile raw -> daily_summary",
      abs((raw_steps or 0) - (mart_steps or 0)) < 1,
      f"raw={raw_steps:,.0f} mart={mart_steps:,.0f}")

# --- sleep session sanity ----------------------------------------------------
check("no sleep session shorter than the 3h floor",
      q1("SELECT COUNT(*) FROM sleep_sessions WHERE duration_h < 3") == 0)
check("no sleep session longer than 16h",
      q1("SELECT COUNT(*) FROM sleep_sessions WHERE duration_h > 16") == 0)
check("sleep block mean HR never exceeds the 75bpm sleep ceiling",
      q1("SELECT COUNT(*) FROM sleep_sessions WHERE hr_mean > 75") == 0)
check("resting HR proxy is physiologically plausible (30-90)",
      q1("SELECT COUNT(*) FROM sleep_sessions WHERE hr_p10 < 30 OR hr_p10 > 90") == 0)
check("wake_time is always after sleep_start",
      q1("SELECT COUNT(*) FROM sleep_sessions WHERE wake_time <= sleep_start") == 0)
check("one row per night_date",
      q1("SELECT COUNT(*) FROM (SELECT night_date FROM sleep_sessions GROUP BY night_date HAVING COUNT(*)>1)") == 0)

# duration must equal the wake-minus-start span (catches truncation/index bugs)
bad_span = 0
for s, w, d in cur.execute("SELECT sleep_start, wake_time, duration_h FROM sleep_sessions"):
    span = (datetime.fromisoformat(w) - datetime.fromisoformat(s)).total_seconds() / 3600
    if abs(span - d) > 0.02:
        bad_span += 1
check("duration_h equals wake_time - sleep_start", bad_span == 0, f"{bad_span} mismatches")

# --- the big external validity check: sleep must not overlap a workout -------
# Workout timestamps are LOCAL in the source export; sleep_sessions are LOCAL.
overlaps = []
sleep_rows = cur.execute("SELECT night_date, sleep_start, wake_time FROM sleep_sessions").fetchall()
workout_rows = cur.execute(
    "SELECT start_time, duration_s FROM events WHERE event_type='NATIVE_WORKOUT' AND duration_s > 600").fetchall()
w_iv = []
for st, dur in workout_rows:
    a = datetime.fromisoformat(st)
    w_iv.append((a, a + timedelta(seconds=dur or 0)))
for night, s, w in sleep_rows:
    a, b = datetime.fromisoformat(s), datetime.fromisoformat(w)
    for wa, wb in w_iv:
        if wa < b and a < wb:
            overlaps.append((night, wa.isoformat(sep=" ")))
check("no derived sleep overlaps a logged workout >10min",
      not overlaps, f"{len(overlaps)} overlaps e.g. {overlaps[:3]}")

# --- timezone regression -----------------------------------------------------
# Workout windows must show ELEVATED heart rate versus the daily mean. If the
# UTC/local offset were wrong, HR during logged workouts would look ordinary.
elevated, tested = 0, 0
for st, dur in workout_rows[:60]:
    start_local = datetime.fromisoformat(st).replace(tzinfo=LOCAL)
    t0 = int(start_local.timestamp())
    t1 = t0 + max(dur or 0, 600)
    hr = q1("SELECT AVG(value) FROM raw_readings WHERE data_type='raw_hr' AND ts_epoch BETWEEN ? AND ?", (t0, t1))
    day = start_local.date().isoformat()
    base = q1("SELECT hr_mean FROM daily_summary WHERE day=?", (day,))
    if hr and base:
        tested += 1
        if hr > base:
            elevated += 1
check("workout windows show elevated HR (timezone offset is correct)",
      tested >= 10 and elevated / max(tested, 1) >= 0.65,
      f"{elevated}/{tested} workouts above daily mean HR")

# --- motion normalisation regression ----------------------------------------
# The original bug: thresholding summed motion made dense-sampling bins look
# active. Guard: bins WITH steps must average higher per-reading motion than
# bins without. This fails loudly if motion ever reverts to a SUM.
mot_steps = q1("SELECT AVG(motion_mean) FROM epochs_10min WHERE steps_sum > 0")
mot_still = q1("SELECT AVG(motion_mean) FROM epochs_10min WHERE COALESCE(steps_sum,0) = 0")
check("per-reading motion separates moving from still bins",
      mot_steps and mot_still and mot_steps > mot_still * 1.5,
      f"steps>0: {mot_steps:.2f} vs steps=0: {mot_still:.2f}")

# --- circular-time regression ------------------------------------------------
# The second real bug: lexical sorting of clock strings across midnight. A
# night window running 20:00->13:00 must contain wake times on BOTH sides of
# midnight; assert the anchored transform orders them correctly.
anchor = 20 * 60


def night_minutes(hhmm):
    v = int(hhmm[:2]) * 60 + int(hhmm[3:5])
    return v - anchor if v >= anchor else v + 24 * 60 - anchor


wm = [night_minutes(r[0][11:16]) for r in cur.execute("SELECT wake_time FROM sleep_sessions")]
check("anchored night-minutes are all within the 20:00->13:00 window",
      all(0 <= m <= 17 * 60 for m in wm), f"range {min(wm)}-{max(wm)} min")
check("wake times occur on both sides of midnight (circular data present)",
      any(m < 4 * 60 for m in wm) and any(m > 4 * 60 for m in wm))

# --- model table -------------------------------------------------------------
check("model_nights rows all reference a real sleep session",
      q1("""SELECT COUNT(*) FROM model_nights m
            LEFT JOIN sleep_sessions s ON s.night_date=m.night_date
            WHERE s.night_date IS NULL""") == 0)
check("model_nights has no null outcomes",
      q1("SELECT COUNT(*) FROM model_nights WHERE rhr IS NULL OR hrv IS NULL") == 0)
check("daily wear_frac is a fraction",
      q1("SELECT COUNT(*) FROM daily_summary WHERE wear_frac < 0 OR wear_frac > 1") == 0)

# --- report ------------------------------------------------------------------
width = max(len(n) for n, _, _ in results)
failed = 0
for name, ok, detail in results:
    print(f"[{'PASS' if ok else 'FAIL'}] {name:<{width}}  {detail}")
    failed += not ok
print(f"\n{len(results)-failed}/{len(results)} passed")
con.close()
sys.exit(1 if failed else 0)
