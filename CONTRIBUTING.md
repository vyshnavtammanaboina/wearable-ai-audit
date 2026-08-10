# Contributing

Two kinds of contribution are useful here, and one of them would materially change the conclusions.

---

## 1. Data (the one that matters)

This study's weakest link is stated plainly in `ECONOMICS.md` §8b: the economics rest on a **simulation under declared priors**, not measurement, because no wearable vendor publishes per-user query logs. `09_credit_model.py` is built and waiting for that data. It refuses to run without it.

### What would retire the assumption

| Contribution | What it unlocks | Effort for you |
|---|---|---|
| **Usage data** (schema below) | Replaces the assumed lognormal and the assumed 0.85 adverse-selection elasticity with fitted values. Retires the robustness argument in favour of measurement. | Highest value |
| **Your own ring export** run through stages 1-6 | A second N. Every result here is one user; two is not a population but it is the difference between a case study and a case study with a control. | One afternoon |
| **Jade probe transcripts** run against `probes/PROBE-PACK.md` | Answer keys are pre-computed. Independent runs test whether the false negatives and the fabricated-premise failure reproduce, or were specific to this account. | One evening |
| **Corrections** | See §3. | Minutes |

### Usage data schema

One row per user-month at `data/usage.csv`:

| Column | Type | Notes |
|---|---|---|
| `user_id` | str | Stable pseudonymous id. **No PII, no email, no device serial.** |
| `month` | str | `YYYY-MM` |
| `tier` | str | `free` or `paid` |
| `questions` | int | Questions asked that month |
| `credits_consumed` | float | Provider-side credit or token units, if known. Optional. |
| `tenure_months` | int | Months since device activation |
| `wear_frac_month` | float | 0-1, share of days the device was worn |
| `converted_next` | 0/1 | Did a free user convert the following month. Blank for paid rows. |

**Aggregated data is fine and is preferred.** The three model heads need distributions and conditional means, not individuals. A per-decile summary table answers most of the question and carries far less risk. Differentially-private aggregates are welcome.

**Do not send anything you are not entitled to share.** Nothing here is worth a broken NDA or a violated terms of service. If you work at a wearable company, publishing per-decile usage aggregates is a decision for your employer, not for you personally, and this project would rather have no data than get someone fired.

Verify the path first:

```bash
python 09_credit_model.py --selftest
```

That runs on synthetic data and prints results explicitly marked as meaningless. Then drop your CSV at `data/usage.csv` and run without the flag.

---

## 2. The raw sensor data will never be published

`ring.db` is 160MB of one person's continuous physiological record, and it is excluded permanently. See `DATA.md` for what that costs a reader and the three verification routes that remain open. Please do not open issues asking for it, and please do not publish your own raw export either. Aggregates and derived tables are the right unit of sharing for this kind of data.

---

## 3. Corrections

This repository has a standing bias toward documenting its own errors rather than quietly fixing them. Three are recorded in `README.md`, and the third one - a correction that was made in working notes on 2026-08-07 and never propagated to the published documents - is the one the study cares about most, because it is the same failure mode it documents in others.

So: **if you find an error, the correction gets written down, not erased.** Open an issue with the file, the claim, and what the record actually says. A pull request that fixes a number silently will be asked to add the note.

Numbers are checkable. `04_tests.py` encodes 17 data-quality assertions, and every count in `REPORT.md` is stated with its definition. The most useful thing you can do in ten minutes is pick one figure and try to break it.

---

## 4. Reproducing the pipeline

```bash
pip install -r requirements.txt
RING_EXPORT_DIR="/path/to/your/data_export" python 01_ingest.py
python 02_transform.py && python 03_marts.py && python 04_tests.py
python 05_models.py && python 06_charts.py
python 07_usage_sim.py          # simulation, no data needed
python 08_wear_forecast.py      # needs a built ring.db
python 09_credit_model.py       # explains what it needs and exits
```

Stages 1-6 and 8 need a built database. Stage 7 is self-contained. Stage 9 is the placeholder above.

If a stage fails against your export, that is a finding: this pipeline has only ever been run against one device's output, and the export format is undocumented. Open an issue with the error and the failing stage.
