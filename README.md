# Auditing a wearable's AI against 2.4 million of my own sensor readings

**It never invented a number. It invented me.**

I have worn an Ultrahuman Ring AIR for nearly two years. In March 2026 Ultrahuman shipped **Jade**, billed as "the world's first real-time biointelligence AI," with a metered free tier and a paid upgrade.

This repository answers the only question that decides a purchase:

> **Does Jade know more about me than the general-purpose assistant I already pay for?**

To answer it I exported 18 months of raw sensor data - **2,422,726 readings** - built a tested pipeline over it, and used that pipeline as ground truth to grade Jade's answers.

**[→ Read the full report](REPORT.md)**

---

## The three findings

1. **Jade does not fabricate numbers.** Two traps designed to catch confabulation; it refused both, correctly, and explained why. That deserves to be said first.
2. **Jade fabricated *me*.** Unprompted, it concluded I work a shift-work schedule, retrieved genuine peer-reviewed literature about shift workers, and gave me health guidance based on it. I am a graduate student. The numbers were right, the citations were real, the patient was fictional.
3. **Its informational edge over my own screenshots is roughly zero, sometimes negative.** It cannot see about a year of the sleep data my ring recorded, and reports HRV "not available" for months in which the ring logged thousands of HRV readings.

**Business conclusion:** Ultrahuman is charging for the commodity layer and giving away the moat. Chat over summaries is fully substitutable by an assistant the customer already owns. The un-substitutable assets - continuous glucose, blood biomarkers, real-time intervention - are exactly what a general LLM can never touch.

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

Branch 3 is the one that reframes the study. Before grading Jade's advice, I asked what the same record could justify from *anyone*. Twelve coefficient tests across five models; after Holm-Bonferroni correction, **not one survived**. The binding constraint on personalised health AI is wear compliance, not model quality.

Where the data *does* have power - 2.4M intraday readings across 162 well-covered days - a clean signal appears: a real circadian rhythm in resting heart rate, amplitude ≈11 bpm. And it **refutes the feature these apps sell**: the afternoon dip is not there.

### Is "unlimited" viable? (stages 7 and 8)

Flat-rate pricing is decided by the tail, not the average. Simulating a full population with usage-driven conversion: break-even is **11.4 questions/month** on-demand versus **164.9** under precompute, a 14x wider envelope, and **55-80% of subscribers are gross-margin negative** on-demand across every distribution family tested. **No credit cap fixes it** - even a 15-question cap, refusing 82% of demand, still misses breakeven.

Two honesty notes, because they matter more than the numbers. Stage 7 is a **simulation under declared priors, not a forecast**: no Jade query logs exist publicly, so a "predictive model" of credit usage would be fit to invented data and presented as prediction - the exact failure this study documents in Jade. Stage 8 *is* fit to real data, and its result is negative: wear is ~87% predictable but a logistic model **does not beat "tomorrow = today."** Gating advice on coverage needs a counter, not machine learning. Both results are reported as found.

The better instrument is built and empty. `09_credit_model.py` implements the full trained model - usage regression, measured conversion elasticity, fitted tail quantiles - and **refuses to run until someone supplies real usage data.** It prints the schema it needs and exits. If that data ever arrives, the simulation's robustness argument gets retired in favour of measurement, with no new code. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## The pipeline

Six stages, plain Python and SQLite, no framework.

| Stage | File | What it does |
|---|---|---|
| 1 | `01_ingest.py` | Land every CSV row untouched into `raw_readings` (long/EAV, with provenance). No cleaning during load. |
| 2 | `02_transform.py` | 10-minute epoch binning; sleep/wake derivation from motion + HR troughs - **the export contains no sleep events at all**. |
| 3 | `03_marts.py` | Analysis tables: `daily_summary`, `sleep_sessions`, `model_nights`. |
| 4 | `04_tests.py` | 17 data-quality assertions. |
| 5 | `05_models.py` | Recovery-driver regressions, HAC standard errors, Holm correction. |
| 6 | `06_charts.py` | Figures in `outputs/`. |
| 7 | `07_usage_sim.py` | Monte Carlo over per-user query volume: is flat-rate "unlimited" viable? **Simulation under stated priors, not a fitted model** - no Jade usage data is public. Tested across three distribution families. |
| 8 | `08_wear_forecast.py` | Wear-compliance forecasting on the real 562-day record, strict temporal split, against honest baselines. |
| 9 | `09_credit_model.py` | **Placeholder, armed but unfed.** The trained credit-usage model that would retire stage 7's assumptions. Refuses to run without real data; prints the exact schema it needs. `--selftest` verifies the code path on synthetic input and states plainly that the output means nothing. |

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

**The raw database is not in this repository, and will not be.** `ring.db` is 160MB of one person's continuous health telemetry - heart rate, HRV, temperature, SpO2, respiratory rate, motion, every ten minutes for eighteen months. Publishing it is irreversible in a way that publishing code is not.

What that costs you: you cannot re-run these exact numbers. What you can do is read every transformation that produced them, run the pipeline against your own export, and check the arithmetic in `REPORT.md` against the assertions in `04_tests.py`. See [DATA.md](DATA.md).

---

## Repository map

| Path | Contents |
|---|---|
| `REPORT.md` | **The published write-up.** Question → analysis → charts → recommendation. |
| `FINDINGS.md` | The case spine - answer-first skeleton the report is built from. |
| `SCOPE.md` | What was in and out of scope, and why. Includes the decision log. |
| `ECONOMICS.md` | Marginal-value analysis of the AI layer as a product line. |
| `RESEARCH-ultrahuman.md` | Sourced background on the company, pricing, and disclosures. |
| `probes/` | The probe battery: prompts, pre-computed answer keys, scoring rubric, transcripts. Reusable against any wearable AI. |
| `outputs/` | Figures and model coefficient tables. |

---

## On this repository's own corrections

Three errors were found in my own work and are documented rather than quietly fixed:

1. **Motion normalisation** - thresholding `motion_sum` per bin measured *sampling density*, not movement (readings per bin range 6-2037). Corrected to a per-reading mean.
2. **Circular time** - summary percentiles sorted clock strings lexically across midnight, ranking 03:00 before 20:00. This nearly hid a working sleep detector behind a meaningless summary.
3. **Stale and mislabelled figures** - pre-publication re-query found night counts carried over from a superseded build, and HRV counts labelled "non-zero" that included 15,601 sensor-dropout zeros. Corrected throughout; no conclusion changed.

The third one is the point. Its correction had already been made in the working notes on 2026-08-07 and never propagated to the published documents - which is the same failure this study documents in others: a claim travelling on the authority of whatever artifact carried it, unchecked against the raw record. An audit that catches the pattern only in the system under review has not understood the pattern.

---

## Limits

**N=1.** One user, one device, 18 months. This measures the *methodology and marginal value* of the AI layer on one deeply instrumented user - not population performance. Wear coverage is 26% of nights, which is the binding constraint on every result in Part 1 and the reason those are reported as failures to demonstrate rather than as absence of effect. HRV units are not comparable between the export and Jade's display, so all HRV findings rest on counts and direction, never absolute values.

No medical claims are made or intended.

---

## Licence

Code: [MIT](LICENSE). Prose (`REPORT.md`, `FINDINGS.md`, `ECONOMICS.md`, `probes/`): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

No affiliation with Ultrahuman. Ring and subscriptions purchased personally.
