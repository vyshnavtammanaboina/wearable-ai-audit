"""
STEP 1 — INGEST (Extract + Load raw)
Read every ring CSV into ONE SQLite table, exactly as-is. No cleaning yet.

Rule of ETL: land the raw data first, untouched. If you clean during load,
you can never prove what the source actually said.
"""

import sqlite3
import csv
import os
from pathlib import Path

# Point RING_EXPORT_DIR at your own Ultrahuman export folder (the one holding
# ring_data_*.csv). Defaults to ./data_export next to this script.
SRC = Path(os.environ.get("RING_EXPORT_DIR", Path(__file__).parent / "data_export"))
DB = Path(os.environ.get("RING_DB", Path(__file__).parent / "ring.db"))

if not SRC.is_dir():
    raise SystemExit(
        f"Export directory not found: {SRC}\n"
        "Set RING_EXPORT_DIR to your Ultrahuman CSV export folder, e.g.\n"
        '  RING_EXPORT_DIR="/path/to/data_export" python 01_ingest.py'
    )

con = sqlite3.connect(DB)
cur = con.cursor()

# --- schema -----------------------------------------------------------------
cur.executescript("""
DROP TABLE IF EXISTS raw_readings;
CREATE TABLE raw_readings (
    ts_epoch    INTEGER NOT NULL,   -- seconds since 1970-01-01 UTC
    data_type   TEXT    NOT NULL,   -- steps / raw_hr / spo2 / temp / ...
    value       REAL,
    src_file    TEXT    NOT NULL    -- provenance: which CSV this row came from
);

DROP TABLE IF EXISTS events;
CREATE TABLE events (
    event_id    TEXT PRIMARY KEY,
    event_type  TEXT,
    title       TEXT,
    start_time  TEXT,               -- 'YYYY-MM-DD HH:MM:SS' local
    end_time    TEXT,
    duration_s  INTEGER
);
""")

# --- load the long/EAV readings ---------------------------------------------
rows = 0
for f in sorted(SRC.glob("ring_data_*.csv")):
    with open(f, newline="", encoding="utf-8") as fh:
        r = csv.reader(fh)
        header = next(r, None)
        if header != ["timestamp_epoch", "data_type", "value"]:
            continue                       # skips the 32-byte empty weeks
        batch = [(int(a), b, float(c), f.name) for a, b, c in r if c != ""]
        cur.executemany("INSERT INTO raw_readings VALUES (?,?,?,?)", batch)
        rows += len(batch)

# --- load the workout / sleep events ----------------------------------------
with open(SRC / "user_events.csv", newline="", encoding="utf-8") as fh:
    r = csv.DictReader(fh)
    cur.executemany(
        "INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?)",
        [(x["Event ID"], x["Event Type"], x["Title"], x["Event Time"],
          x["End Time"], int(x["Duration (seconds)"] or 0)) for x in r],
    )

# --- indexes: build AFTER the insert, never before --------------------------
cur.executescript("""
CREATE INDEX idx_readings_type_ts ON raw_readings(data_type, ts_epoch);
CREATE INDEX idx_events_start     ON events(start_time);
""")

con.commit()
print(f"raw_readings: {rows:,} rows")
print("events:", cur.execute("SELECT COUNT(*) FROM events").fetchone()[0])
con.close()
