"""
STEP 2 - TRANSFORM
raw_readings (EAV, burst-sampled, UTC) -> epochs_10min -> sleep_sessions.

Facts this transform is built on (verified against the data, 2026-08-04):

1. ts_epoch is UTC; local time is America/New_York. Proof: user_events carries
   LOCAL timestamps, and the HR spike for the 2026-07-22 badminton session lands
   at event_time + 4h (EDT offset), not at event_time.

2. Sampling is bursty and wildly uneven: readings per 10-min bin run 6 (p5) to
   2037 (p99). So any SUM over a bin measures sampling density as much as the
   underlying signal. Motion is therefore normalised per reading. (An earlier
   cut of this file thresholded motion_sum and mislabelled dense-sampling bins
   as movement, fragmenting real sleep blocks.)
   Validation of the normalised signal: bins with steps>0 average motion 19.3
   and HR 81.4; bins with steps==0 average motion 7.8 and HR 66.6.

3. The export contains NO sleep events - sleep must be derived. Quiet = no steps
   and low per-reading motion; a real night is additionally confirmed by low HR
   and by having been worn (charger time produces no readings at all, so bin
   coverage inside the block is a hard gate).
"""

import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

DB = Path(__file__).parent / "ring.db"
LOCAL = ZoneInfo("America/New_York")

BIN_S = 600                 # 10-minute bins
# Calibrated on labelled bins, not on a guess:
#   known-sleep bins (02:00-05:00 local, no steps, HR<60): median 4, p95 72
#   known-active bins (steps>10):                          p25 86, median 145
# 75 sits in the gap. (An earlier value of 15 came from a ratio that divided by
# ALL data types rather than motion readings alone - roughly a 10x scale error,
# which put the threshold below the median of genuinely still bins and
# fragmented real sleep.)
MOTION_ACTIVE = 75.0
BRIDGE_BINS = 2             # tolerate <=20 min of movement inside a night (bathroom, turning over)
MIN_SLEEP_H = 3.0           # shorter blocks are naps or noise, not the night
MIN_HR_SAMPLES = 20         # worn-proof: a real night carries HR bursts throughout
MIN_COVERAGE = 0.20         # frac of bins holding any reading; charger time scores ~0
MAX_SLEEP_HR = 75.0         # block mean above this is not sleep (quiet overnight HR sits ~57-62)
NIGHT_START_H = 20          # night window: 20:00 local ...
NIGHT_END_H = 13            # ... to 13:00 local next day

con = sqlite3.connect(DB)
cur = con.cursor()

# --- epochs_10min ------------------------------------------------------------
# motion_mean is per-reading (see note 2); steps stay a SUM because they are
# already an event count rather than a sampled level.
# Sensor dropouts encode as literal zeros: 529 HR readings and 15,601 HRV
# readings are 0, which is not a heart rate. They are excluded HERE rather than
# at ingest so raw_readings stays a faithful copy of the source (see 01_ingest).
cur.executescript(f"""
DROP TABLE IF EXISTS epochs_10min;
CREATE TABLE epochs_10min AS
SELECT
    (ts_epoch / {BIN_S}) * {BIN_S}                        AS bin_ts,
    AVG(CASE WHEN data_type='raw_hr'    AND value > 0 THEN value END) AS hr_mean,
    MIN(CASE WHEN data_type='raw_hr'    AND value > 0 THEN value END) AS hr_min,
    SUM(CASE WHEN data_type='raw_hr'    AND value > 0 THEN 1 END)     AS hr_n,
    AVG(CASE WHEN data_type='raw_hrv_2' AND value > 0 THEN value END) AS hrv_mean,
    AVG(CASE WHEN data_type='raw_motion' THEN value END)  AS motion_mean,
    SUM(CASE WHEN data_type='steps'     THEN value END)   AS steps_sum,
    AVG(CASE WHEN data_type='temp'      THEN value END)   AS temp_mean,
    AVG(CASE WHEN data_type='spo2'      THEN value END)   AS spo2_mean,
    AVG(CASE WHEN data_type='respiratory_rate' THEN value END) AS rr_mean,
    COUNT(*)                                              AS n_readings
FROM raw_readings
GROUP BY bin_ts;
CREATE UNIQUE INDEX idx_epochs_bin ON epochs_10min(bin_ts);
""")
n_epochs = cur.execute("SELECT COUNT(*) FROM epochs_10min").fetchone()[0]

# --- sleep_sessions ----------------------------------------------------------
cur.executescript("""
DROP TABLE IF EXISTS sleep_sessions;
CREATE TABLE sleep_sessions (
    night_date    TEXT PRIMARY KEY,  -- local date of the wake-up morning
    sleep_start   TEXT,              -- local 'YYYY-MM-DD HH:MM'
    wake_time     TEXT,
    duration_h    REAL,
    coverage      REAL,              -- frac of bins in the block holding any reading
    awakenings    INTEGER,           -- bridged active bins inside the block
    hr_mean       REAL,
    hr_p10        REAL,              -- resting-HR proxy for the night
    hrv_mean      REAL,
    temp_mean     REAL,
    rr_mean       REAL,
    start_truncated INTEGER            -- block began at the 20:00 window edge, so
                                       -- sleep_start/duration are lower bounds only.
                                       -- Exclude from any bedtime analysis; wake_time
                                       -- is still trustworthy on these nights.
);
""")

rows = cur.execute(
    "SELECT bin_ts, hr_mean, hrv_mean, motion_mean, steps_sum, temp_mean, rr_mean, hr_n "
    "FROM epochs_10min ORDER BY bin_ts").fetchall()
by_ts = {r[0]: r for r in rows}
TS, HR, HRV, MOT, STEP, TEMP, RR, HRN = range(8)

first_local = datetime.fromtimestamp(rows[0][TS], LOCAL).date()
last_local = datetime.fromtimestamp(rows[-1][TS], LOCAL).date()

# Logged workouts are ground truth for being awake. A candidate block that
# overlaps one is a false positive no matter how quiet it looks - a still ring
# on a nightstand reads exactly like a sleeping wrist. Source timestamps are
# LOCAL, so they are localised before comparison.
workout_iv = []
for st, dur in cur.execute(
        "SELECT start_time, duration_s FROM events WHERE event_type='NATIVE_WORKOUT' AND duration_s > 600"):
    a = datetime.fromisoformat(st).replace(tzinfo=LOCAL)
    workout_iv.append((int(a.timestamp()), int(a.timestamp()) + (dur or 0)))


def overlaps_workout(t_start, t_end):
    return any(wa < t_end and t_start < wb for wa, wb in workout_iv)


def bin_state(b):
    """ACTIVE = moving; QUIET = worn and still; EMPTY = no data (charger or sparse gap)."""
    if b is None:
        return "EMPTY"
    if (b[STEP] or 0) > 0:
        return "ACTIVE"
    if b[MOT] is not None and b[MOT] >= MOTION_ACTIVE:
        return "ACTIVE"
    return "QUIET"


def candidate_blocks(states):
    """Maximal runs of QUIET bins, bridging <=BRIDGE_BINS consecutive ACTIVE bins.
    Yields (start_idx, end_idx, awakenings); both indices land on QUIET bins."""
    i = 0
    while i < len(states):
        if states[i] != "QUIET":
            i += 1
            continue
        j, active_run, awakenings, k = i, 0, 0, i
        while k < len(states):
            if states[k] == "ACTIVE":
                active_run += 1
                if active_run > BRIDGE_BINS:
                    break
            elif states[k] == "QUIET":
                awakenings += active_run
                active_run = 0
                j = k
            k += 1
        yield i, j, awakenings
        i = max(k, i + 1)


sessions, rejected = 0, {"too_short": 0, "few_hr": 0, "low_coverage": 0,
                         "hr_too_high": 0, "workout_overlap": 0, "no_quiet": 0}
day = first_local
while day <= last_local:
    start = datetime.combine(day, datetime.min.time(), LOCAL).replace(hour=NIGHT_START_H)
    end = datetime.combine(day + timedelta(days=1), datetime.min.time(), LOCAL).replace(hour=NIGHT_END_H)
    t0, t1 = int(start.timestamp()) // BIN_S * BIN_S, int(end.timestamp())

    window = [by_ts.get(ts) for ts in range(t0, t1, BIN_S)]
    win_ts = list(range(t0, t1, BIN_S))
    states = [bin_state(b) for b in window]

    best, saw_candidate = None, False
    for i, j, awakenings in candidate_blocks(states):
        saw_candidate = True
        block = window[i:j + 1]
        n_bins = j - i + 1
        dur_h = n_bins * BIN_S / 3600
        if dur_h < MIN_SLEEP_H:
            rejected["too_short"] += 1
            continue
        hr_samples = sum(b[HRN] or 0 for b in block if b)
        if hr_samples < MIN_HR_SAMPLES:
            rejected["few_hr"] += 1
            continue
        cov = sum(1 for b in block if b) / n_bins
        if cov < MIN_COVERAGE:
            rejected["low_coverage"] += 1
            continue
        hrs = [b[HR] for b in block if b and b[HR] is not None]
        hr_mean = sum(hrs) / len(hrs) if hrs else None
        if hr_mean is None or hr_mean > MAX_SLEEP_HR:
            rejected["hr_too_high"] += 1
            continue
        if overlaps_workout(win_ts[i], win_ts[j] + BIN_S):
            rejected["workout_overlap"] += 1
            continue
        if best is None or dur_h > best[0]:
            best = (dur_h, i, j, awakenings, block, hrs, cov)
    if not saw_candidate:
        rejected["no_quiet"] += 1

    if best:
        dur_h, i, j, awakenings, block, hrs, cov = best
        hrs_sorted = sorted(hrs)
        hrvs = [b[HRV] for b in block if b and b[HRV] is not None]
        temps = [b[TEMP] for b in block if b and b[TEMP] is not None]
        rrs = [b[RR] for b in block if b and b[RR] is not None]
        s_local = datetime.fromtimestamp(win_ts[i], LOCAL)
        w_local = datetime.fromtimestamp(win_ts[j] + BIN_S, LOCAL)
        cur.execute("INSERT OR REPLACE INTO sleep_sessions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
            w_local.date().isoformat(),
            s_local.strftime("%Y-%m-%d %H:%M"),
            w_local.strftime("%Y-%m-%d %H:%M"),
            round(dur_h, 2),
            round(cov, 3),
            awakenings,
            round(sum(hrs) / len(hrs), 1),
            round(hrs_sorted[int(len(hrs_sorted) * 0.10)], 1),
            round(sum(hrvs) / len(hrvs), 1) if hrvs else None,
            round(sum(temps) / len(temps), 2) if temps else None,
            round(sum(rrs) / len(rrs), 1) if rrs else None,
            1 if i == 0 else 0,
        ))
        sessions += 1
    day += timedelta(days=1)

con.commit()

# --- validation summary (read this before trusting anything downstream) ------
total_days = (last_local - first_local).days + 1
# Count rows, not inserts: two adjacent night windows can resolve to the same
# wake date, and INSERT OR REPLACE silently collapses those.
n_nights = cur.execute("SELECT COUNT(*) FROM sleep_sessions").fetchone()[0]
print(f"epochs_10min:   {n_epochs:,} bins")
print(f"sleep_sessions: {n_nights} nights over {total_days} calendar days "
      f"({100*n_nights/total_days:.0f}% coverage; {sessions - n_nights} same-wake-date collisions)")
print(f"blocks rejected: {rejected}")
for label, q in [("duration_h", "SELECT duration_h FROM sleep_sessions ORDER BY duration_h"),
                 ("hr_p10    ", "SELECT hr_p10 FROM sleep_sessions ORDER BY hr_p10"),
                 ("coverage  ", "SELECT coverage FROM sleep_sessions ORDER BY coverage")]:
    v = [r[0] for r in cur.execute(q)]
    if v:
        print(f"{label} p25/med/p75: {v[len(v)//4]} / {v[len(v)//2]} / {v[3*len(v)//4]}")
# Clock times must be ordered chronologically within the night window, NOT
# lexically: the window spans midnight, so plain string sort ranks "03:00"
# before "20:00" and makes the medians meaningless.
def night_minutes(hhmm, anchor=NIGHT_START_H * 60):
    v = int(hhmm[:2]) * 60 + int(hhmm[3:5])
    return v - anchor if v >= anchor else v + 24 * 60 - anchor


def clock(m, anchor=NIGHT_START_H * 60):
    m = (m + anchor) % (24 * 60)
    return f"{m//60:02d}:{m%60:02d}"


for label, q in [("sleep_start", "SELECT sleep_start FROM sleep_sessions WHERE start_truncated=0"),
                 ("wake_time  ", "SELECT wake_time FROM sleep_sessions")]:
    v = sorted(night_minutes(r[0][11:16]) for r in cur.execute(q))
    if v:
        print(f"{label} p25/med/p75: " + " / ".join(clock(v[int(len(v)*p)]) for p in (.25, .50, .75)))
trunc = cur.execute("SELECT COUNT(*) FROM sleep_sessions WHERE start_truncated=1").fetchone()[0]
print(f"  ({trunc} nights start at the {NIGHT_START_H}:00 window edge -> bedtime is a lower "
      f"bound there; excluded from sleep_start above)")
print("nights by duration:")
for lo, hi in [(3, 5), (5, 7), (7, 9), (9, 12), (12, 24)]:
    n = cur.execute("SELECT COUNT(*) FROM sleep_sessions WHERE duration_h>=? AND duration_h<?", (lo, hi)).fetchone()[0]
    print(f"  {lo:>2}-{hi:<2}h: {n}")
con.close()
