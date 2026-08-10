"""
STEP 3 - MARTS
epochs_10min + sleep_sessions + events -> daily_summary, model_nights.

Two decisions worth stating, because both change the numbers:

1. LOCAL DATES ARE COMPUTED WITH A REAL TIMEZONE, NOT A FIXED OFFSET.
   Bucketing with (ts_epoch - 4*3600) assumes EDT year-round and shifts every
   winter date by an hour, which silently moves late-evening readings onto the
   wrong day. We convert per bin in Python via zoneinfo instead; epochs_10min is
   only ~37k rows, so correctness costs nothing here.

2. MODEL DIRECTION IS PRIOR-DAY -> THAT NIGHT'S RECOVERY.
   Overnight RHR/HRV are measured *during* the sleep block, so regressing them
   on that same block's own summary statistics would be partly circular. The
   modelling table therefore pairs each night's recovery outcome with the
   BEHAVIOUR OF THE DAY BEFORE (activity load, workout timing), alongside the
   night's own duration and timing.
"""

import sqlite3
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from statistics import mean, pstdev

DB = Path(__file__).parent / "ring.db"
LOCAL = ZoneInfo("America/New_York")
MOTION_ACTIVE = 75.0          # must match 02_transform (calibrated on labelled bins)
LATE_WORKOUT_HOUR = 20        # workouts starting at/after 20:00 local
CONSISTENCY_WINDOW = 7        # prior N detected nights for wake-time variability
NIGHT_ANCHOR_MIN = 20 * 60    # 20:00, matches the transform's night window

con = sqlite3.connect(DB)
cur = con.cursor()


def pct(sorted_vals, p):
    if not sorted_vals:
        return None
    return sorted_vals[min(len(sorted_vals) - 1, int(len(sorted_vals) * p))]


# --- daily_summary -----------------------------------------------------------
cur.executescript("""
DROP TABLE IF EXISTS daily_summary;
CREATE TABLE daily_summary (
    day            TEXT PRIMARY KEY,   -- local calendar date
    n_bins         INTEGER,            -- 10-min bins holding any reading (max 144)
    wear_frac      REAL,               -- n_bins / 144, a coverage proxy
    active_bins    INTEGER,
    steps_total    REAL,
    motion_mean    REAL,
    hr_mean        REAL,
    hr_p10         REAL,
    hrv_mean       REAL,
    temp_mean      REAL,
    spo2_mean      REAL,
    rr_mean        REAL,
    workouts       INTEGER,
    workout_min    REAL,
    last_workout_h REAL,               -- local hour of the last workout start
    late_workout   INTEGER
);
""")

rows = cur.execute("""
    SELECT bin_ts, hr_mean, hrv_mean, motion_mean, steps_sum, temp_mean,
           spo2_mean, rr_mean
    FROM epochs_10min ORDER BY bin_ts""").fetchall()

days = {}
for bin_ts, hr, hrv, mot, steps, temp, spo2, rr in rows:
    d = datetime.fromtimestamp(bin_ts, LOCAL).date().isoformat()
    e = days.setdefault(d, {"n": 0, "act": 0, "steps": 0.0,
                            "hr": [], "hrv": [], "mot": [], "temp": [], "spo2": [], "rr": []})
    e["n"] += 1
    e["steps"] += steps or 0
    if (steps or 0) > 0 or (mot is not None and mot >= MOTION_ACTIVE):
        e["act"] += 1
    for key, val in (("hr", hr), ("hrv", hrv), ("mot", mot),
                     ("temp", temp), ("spo2", spo2), ("rr", rr)):
        if val is not None:
            e[key].append(val)

# workouts carry LOCAL timestamps in the source export, so no conversion here
workouts = {}
for title, start, dur in cur.execute(
        "SELECT title, start_time, duration_s FROM events WHERE event_type IN ('NATIVE_WORKOUT','ACTIVITY')"):
    d = start[:10]
    w = workouts.setdefault(d, {"n": 0, "min": 0.0, "last_h": None})
    w["n"] += 1
    w["min"] += (dur or 0) / 60
    h = int(start[11:13]) + int(start[14:16]) / 60
    w["last_h"] = h if w["last_h"] is None else max(w["last_h"], h)

for d, e in sorted(days.items()):
    w = workouts.get(d, {"n": 0, "min": 0.0, "last_h": None})
    hr_sorted = sorted(e["hr"])
    cur.execute("INSERT OR REPLACE INTO daily_summary VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
        d, e["n"], round(e["n"] / 144, 3), e["act"], e["steps"],
        round(mean(e["mot"]), 2) if e["mot"] else None,
        round(mean(e["hr"]), 1) if e["hr"] else None,
        round(pct(hr_sorted, 0.10), 1) if hr_sorted else None,
        round(mean(e["hrv"]), 1) if e["hrv"] else None,
        round(mean(e["temp"]), 2) if e["temp"] else None,
        round(mean(e["spo2"]), 1) if e["spo2"] else None,
        round(mean(e["rr"]), 1) if e["rr"] else None,
        w["n"], round(w["min"], 1),
        round(w["last_h"], 2) if w["last_h"] is not None else None,
        1 if (w["last_h"] is not None and w["last_h"] >= LATE_WORKOUT_HOUR) else 0,
    ))

# --- model_nights ------------------------------------------------------------
# One row per derived night that also has a usable PRIOR day. Outcomes are the
# night's own recovery; predictors are the prior day's behaviour plus the
# night's duration/timing.
cur.executescript("""
DROP TABLE IF EXISTS model_nights;
CREATE TABLE model_nights (
    night_date        TEXT PRIMARY KEY,
    -- outcomes
    rhr               REAL,   -- sleep-block HR p10 (resting proxy)
    hrv               REAL,   -- sleep-block mean HRV
    -- night predictors
    sleep_h           REAL,
    wake_min          REAL,   -- minutes past 20:00 anchor
    sleep_start_min   REAL,
    awakenings        INTEGER,
    start_truncated   INTEGER,
    -- prior-day predictors
    prior_steps       REAL,
    prior_active_bins INTEGER,
    prior_workouts    INTEGER,
    prior_workout_min REAL,
    prior_late_workout INTEGER,
    prior_wear_frac   REAL,
    -- rolling context
    wake_sd_7         REAL,   -- SD of wake time over prior 7 detected nights
    wake_sd_span_d    INTEGER -- calendar span of that window; large = not a real routine
);
""")

sleep = cur.execute("""
    SELECT night_date, sleep_start, wake_time, duration_h, awakenings,
           hr_p10, hrv_mean, start_truncated
    FROM sleep_sessions ORDER BY night_date""").fetchall()
daily = {r[0]: r for r in cur.execute(
    "SELECT day, steps_total, active_bins, workouts, workout_min, late_workout, wear_frac FROM daily_summary")}


def night_minutes(hhmm):
    v = int(hhmm[:2]) * 60 + int(hhmm[3:5])
    return v - NIGHT_ANCHOR_MIN if v >= NIGHT_ANCHOR_MIN else v + 24 * 60 - NIGHT_ANCHOR_MIN


wake_hist = []   # (night_date, wake_min) for rolling consistency
built, skipped_no_prior = 0, 0
for night_date, s_start, w_time, dur, awak, rhr, hrv, trunc in sleep:
    nd = date.fromisoformat(night_date)
    prior = daily.get((nd - timedelta(days=1)).isoformat())
    wake_min = night_minutes(w_time[11:16])

    if len(wake_hist) >= 3:
        window = wake_hist[-CONSISTENCY_WINDOW:]
        sd = round(pstdev([w for _, w in window]), 1) if len(window) > 1 else None
        span = (date.fromisoformat(window[-1][0]) - date.fromisoformat(window[0][0])).days
    else:
        sd, span = None, None

    if prior is None:
        skipped_no_prior += 1
    else:
        cur.execute("INSERT OR REPLACE INTO model_nights VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            night_date, rhr, hrv, dur, wake_min, night_minutes(s_start[11:16]), awak, trunc,
            prior[1], prior[2], prior[3], prior[4], prior[5], prior[6], sd, span,
        ))
        built += 1
    wake_hist.append((night_date, wake_min))

con.commit()

# --- summary -----------------------------------------------------------------
n_days = cur.execute("SELECT COUNT(*) FROM daily_summary").fetchone()[0]
print(f"daily_summary: {n_days} days")
print(f"model_nights:  {built} rows  ({skipped_no_prior} nights dropped: no prior-day data)")
c = cur.execute("""SELECT COUNT(*) FROM model_nights
                   WHERE rhr IS NOT NULL AND hrv IS NOT NULL AND sleep_h IS NOT NULL""").fetchone()[0]
print(f"  complete cases (rhr+hrv+sleep_h): {c}")
for col in ("prior_late_workout", "start_truncated"):
    n = cur.execute(f"SELECT SUM({col}) FROM model_nights").fetchone()[0]
    print(f"  {col}=1: {n}")
r = cur.execute("SELECT MIN(wake_sd_span_d), AVG(wake_sd_span_d), MAX(wake_sd_span_d) FROM model_nights WHERE wake_sd_7 IS NOT NULL").fetchone()
if r[0] is not None:
    print(f"  wake_sd_7 window spans {r[0]}-{r[2]} calendar days (mean {r[1]:.0f}) "
          f"-> a '7-night routine' can straddle weeks; filter on wake_sd_span_d")
con.close()
