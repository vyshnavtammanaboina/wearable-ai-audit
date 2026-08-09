# DATA.md — what is here, what is not, and why

## The raw data is not in this repository

`ring.db` (~160MB) holds 2,422,726 continuous physiological readings from one person: heart rate, heart-rate variability, skin temperature, SpO2, respiratory rate, motion, and step counts, sampled roughly every five minutes for eighteen months. Alongside it, `events` holds 337 logged activities with timestamps.

That record is enough to reconstruct when I slept, when I woke, when I exercised, when I travelled, and when I was ill. It is excluded deliberately and permanently, not for size reasons.

Publishing code is reversible. Publishing eighteen months of your own body is not.

## What this costs the reader, stated plainly

You cannot re-run my exact figures. A reader who wants to verify this work has three routes, in descending strength:

1. **Run the pipeline against your own Ultrahuman export.** Every transformation is in the six numbered scripts. Point `RING_EXPORT_DIR` at your export folder and the whole chain rebuilds from raw.
2. **Read the assertions.** `04_tests.py` encodes 17 data-quality checks — row reconciliation, physiological bounds, sleep/workout non-overlap, a timezone proof. They are the same checks that constrain my numbers.
3. **Check the internal arithmetic.** Counts in `REPORT.md` are stated with their definitions, and `probes/` carries pre-computed answer keys for every question put to Jade.

This is weaker than shipping the database, and I would rather say so than pretend otherwise.

## Schema

**`raw_readings`** — the landing table. Nothing is cleaned on the way in.

| Column | Type | Notes |
|---|---|---|
| `ts_epoch` | INTEGER | Seconds since 1970-01-01 UTC |
| `data_type` | TEXT | `raw_hr`, `raw_hrv_2`, `steps`, `raw_motion`, `temp`, `spo2`, `respiratory_rate` |
| `value` | REAL | As recorded, sentinels and all |
| `src_file` | TEXT | Provenance — which CSV this row came from |

**`events`** — logged activities: `event_id`, `event_type`, `title`, `start_time`, `end_time`, `duration_s`.

**`epochs_10min`** — 10-minute bins with per-channel aggregates. **`daily_summary`** — one row per day, wear fraction and daily aggregates. **`sleep_sessions`** — one row per derived night, with a `start_truncated` flag. **`model_nights`** — modelling frame joining each night's outcome to prior-day exposures.

## Two definitional traps in this data

Both cost me real errors; both are documented in `REPORT.md`.

**Zeros are not measurements.** `raw_hrv_2` contains 15,601 rows whose value is literally `0` — sensor dropouts, not physiological readings. The pipeline filters `value > 0` for HRV (`02_transform.py`). Any count you quote must state whether zeros are in or out: the record holds 352,441 HRV rows but only **336,840 non-zero** readings. An earlier draft of the report quoted the first number under the second's label.

**Sampling density is not movement.** Readings per 10-minute bin range from 6 to 2037. Summing `motion` per bin therefore measures how often the device sampled, not how much the wearer moved. It must be normalised to a per-reading mean.

## Coverage — the binding constraint

| | |
|---|---|
| Calendar span | 2025-01-08 → 2026-07-23 (562 days) |
| Raw readings | 2,422,726 |
| Days with any data | 300 |
| Nights sleep could be derived | 144 (26% of span) |
| Consecutive night-pairs | 79 |
| Uncensored nights in final models | 95 |

The export runs stale after 2026-07-23; the ring was off-body from roughly that date. Every probe in `probes/` therefore targets historical periods.

Sleep is **derived, not reported** — the export contains no sleep events whatsoever. `02_transform.py` infers sleep and wake from overnight motion and heart-rate troughs, and `04_tests.py` constrains the result (3h floor, 16h ceiling, 75bpm sleep HR ceiling, no overlap with logged workouts).
