# Auditing a wearable's AI against 2.4 million of my own sensor readings

**It never invented a number. It invented me.**

I have worn an Ultrahuman Ring AIR for nearly two years. In March 2026 Ultrahuman shipped **Jade**, billed as "the world's first real-time biointelligence AI," with a metered free tier and a paid upgrade.

This repository answers the only question that decides a purchase:

> **Does Jade know more about me than the general-purpose assistant I already pay for?**

To answer it I exported 18 months of raw sensor data — **2,422,726 readings** — built a tested pipeline over it, and used that pipeline as ground truth to grade Jade's answers.

**[→ Read the full report](REPORT.md)**

---

## The three findings

1. **Jade does not fabricate numbers.** Two traps designed to catch confabulation; it refused both, correctly, and explained why. That deserves to be said first.
2. **Jade fabricated *me*.** Unprompted, it concluded I work a shift-work schedule, retrieved genuine peer-reviewed literature about shift workers, and gave me health guidance based on it. I am a graduate student. The numbers were right, the citations were real, the patient was fictional.
3. **Its informational edge over my own screenshots is roughly zero, sometimes negative.** It cannot see about a year of the sleep data my ring recorded, and reports HRV "not available" for months in which the ring logged thousands of HRV readings.

**Business conclusion:** Ultrahuman is charging for the commodity layer and giving away the moat. Chat over summaries is fully substitutable by an assistant the customer already owns. The un-substitutable assets — continuous glucose, blood biomarkers, real-time intervention — are exactly what a general LLM can never touch.

---

## How the question decomposes

```
Is Jade worth paying for?
│
├── 1. Can it be trusted? ───────────► Does it fabricate figures?      → No. It refuses correctly.
│                                      Does it fabricate context?      → Yes. Invented an occupation.
│
├── 2. Does it know my data? ────────► Can it see what the ring wrote? → No. ~1 yr sleep, 337k HRV invisible.
│                                      Is it right where it can see?   → Yes. Exact to the step.
│
└── 3. Could ANY system advise me? ──► What does my own record support? → Nothing survives correction.
                                       What binds it?                   → Wear coverage (26%), not model quality.
```

Branch 3 is the one that reframes the study. Before grading Jade's advice, I asked what the same record could justify from *anyone*. Twelve coefficient tests across five models; after Holm–Bonferroni correction, **not one survived**. The binding constraint on personalised health AI is wear compliance, not model quality.

Where the data *does* have power — 2.4M intraday readings across 162 well-covered days — a clean signal appears: a real circadian rhythm in resting heart rate, amplitude ≈11 bpm. And it **refutes the feature these apps sell**: the afternoon dip is not there.

---

## The pipeline

Six stages, plain Python and SQLite, no framework.

| Stage | File | What it does |
|---|---|---|
| 1 | `01_ingest.py` | Land every CSV row untouched into `raw_readings` (long/EAV, with provenance). No cleaning during load. |
| 2 | `02_transform.py` | 10-minute epoch binning; sleep/wake derivation from motion + HR troughs — **the export contains no sleep events at all**. |
| 3 | `03_marts.py` | Analysis tables: `daily_summary`, `sleep_sessions`, `model_nights`. |
| 4 | `04_tests.py` | 17 data-quality assertions. |
| 5 | `05_models.py` | Recovery-driver regressions, HAC standard errors, Holm correction. |
| 6 | `06_charts.py` | Figures in `outputs/`. |

### Tests

```bash
python 04_tests.py
```

**17/17 pass.** They include full row reconciliation (2,422,726 readings binned with zero loss), a check that no derived sleep block overlaps a logged workout, and a timezone proof that all 57 logged workouts show elevated heart rate inside their recorded windows.

### Running it

```bash
pip install -r requirements.txt
RING_EXPORT_DIR="/path/to/your/data_export" python 01_ingest.py
python 02_transform.py && python 03_marts.py && python 04_tests.py && python 05_models.py && python 06_charts.py
```

`q.py` is an interactive query runner against the built database.

---

## Data

**The raw database is not in this repository, and will not be.** `ring.db` is 160MB of one person's continuous health telemetry — heart rate, HRV, temperature, SpO2, respiratory rate, motion, every ten minutes for eighteen months. Publishing it is irreversible in a way that publishing code is not.

What that costs you: you cannot re-run these exact numbers. What you can do is read every transformation that produced them, run the pipeline against your own export, and check the arithmetic in `REPORT.md` against the assertions in `04_tests.py`. See [DATA.md](DATA.md).

---

## Repository map

| Path | Contents |
|---|---|
| `REPORT.md` | **The published write-up.** Question → analysis → charts → recommendation. |
| `FINDINGS.md` | The case spine — answer-first skeleton the report is built from. |
| `SCOPE.md` | What was in and out of scope, and why. Includes the decision log. |
| `ECONOMICS.md` | Marginal-value analysis of the AI layer as a product line. |
| `RESEARCH-ultrahuman.md` | Sourced background on the company, pricing, and disclosures. |
| `probes/` | The probe battery: prompts, pre-computed answer keys, scoring rubric, transcripts. Reusable against any wearable AI. |
| `outputs/` | Figures and model coefficient tables. |

---

## On this repository's own corrections

Three errors were found in my own work and are documented rather than quietly fixed:

1. **Motion normalisation** — thresholding `motion_sum` per bin measured *sampling density*, not movement (readings per bin range 6–2037). Corrected to a per-reading mean.
2. **Circular time** — summary percentiles sorted clock strings lexically across midnight, ranking 03:00 before 20:00. This nearly hid a working sleep detector behind a meaningless summary.
3. **Stale and mislabelled figures** — pre-publication re-query found night counts carried over from a superseded build, and HRV counts labelled "non-zero" that included 15,601 sensor-dropout zeros. Corrected throughout; no conclusion changed.

The third one is the point. Its correction had already been made in the working notes on 2026-08-07 and never propagated to the published documents — which is the same failure this study documents in others: a claim travelling on the authority of whatever artifact carried it, unchecked against the raw record. An audit that catches the pattern only in the system under review has not understood the pattern.

---

## Limits

**N=1.** One user, one device, 18 months. This measures the *methodology and marginal value* of the AI layer on one deeply instrumented user — not population performance. Wear coverage is 26% of nights, which is the binding constraint on every result in Part 1 and the reason those are reported as failures to demonstrate rather than as absence of effect. HRV units are not comparable between the export and Jade's display, so all HRV findings rest on counts and direction, never absolute values.

No medical claims are made or intended.

---

## Licence

Code: [MIT](LICENSE). Prose (`REPORT.md`, `FINDINGS.md`, `ECONOMICS.md`, `probes/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

No affiliation with Ultrahuman. Ring and subscriptions purchased personally.
