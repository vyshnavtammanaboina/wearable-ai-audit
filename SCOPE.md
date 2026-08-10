# SCOPE.md — Ring Pipeline: Data vs. Jade
*Rescoped 2026-08-04 (evening). A previous, broader scope (small-model build-vs-buy, value-vs-usage quadrant, full competitive teardown) was cut deliberately — parked in git history, with one implications page surviving. Focus: model the data, compare to Jade.*

---

## The question

**"What does 18 months of my ring data actually say about my sleep, recovery, and energy — and does Jade know it?"**

One user, fully instrumented, ground truth in hand. Jade's answers get scored against models built from the same data it claims to read. The gimmick-or-real verdict falls out as a one-page implication at the end — it is not a workstream.

## Constraints

- Ring off-body since ~Jul 23 (complaint pending) → all probes target **historical** data; ring.db is ground truth
- Report + repo ship by **Aug 9–10** — a fixed external deadline, which is why the scope above was cut rather than extended
- Report opens with the business question, not the stack

---

## Workstreams

### 1. Pipeline (public repo, merged by Aug 6)

`01_ingest.py` done (raw_readings 2M+ rows, events). Remaining:
- `02_transform.py` — sleep/wake derivation, daily rollups (below)
- `03_marts.py` — analysis tables: `daily_summary`, `sleep_sessions`, `recovery_daily`
- `04_tests.py` — row counts tie ingest→marts; derived sleep never overlaps workouts; no impossible values (HR bounds, temp bounds); date coverage report
- Public GitHub repo, feature-branch → PR → merge, README with the driver tree

### 2. Models — three, interpretable, each answering one question the data can settle

| # | Model | Method | Validated how |
|---|---|---|---|
| M1 | **Sleep/wake detection** (export has no sleep events) | Rule-based/HMM on overnight motion + HR troughs | Sanity: no overlap with logged workouts; visual spot-check against known schedule |
| M2 | **Recovery drivers** — what actually moves next-day RHR/HRV | ⚠️ **n=79 consecutive night pairs** (re-measured 2026-08-09; the 50 quoted on Aug 4 predates the transform fixes). Simple regression, 2–3 features max, effect sizes with CIs. Tree ensemble is OFF — it would overfit and the importances would be noise | Time-series CV; report CIs and state the n everywhere |
| M3 | **Energy curve** — when are peaks/dips, do they move | Two-process circadian model (sleep midpoint + temp rhythm) → predicted dip windows | Predicted dips vs. observed midday activity lulls in steps/motion |

M2 is the centerpiece: it answers "which advice claims are true *for me*" (consistency, late workouts, load) with effect sizes.

### 3. Jade comparison (the probe battery — unchanged, it IS the comparison)

Ask Jade the exact questions M1–M3 answer. Score each response: **grounded-correct / grounded-wrong / generic-ungrounded / confabulated**, fact-checked against ring.db.

| Probe | Prompt pattern | Compares against |
|---|---|---|
| A | "What was my average HRV in June 2026?" (+ 4 more factual recalls) | ring.db direct query |
| B | "When do my energy dips usually happen?" | M3 predicted windows |
| C | "What should I change to improve recovery?" — generic vs. "based on my data" | M2 effect sizes; identical answers ⇒ rulebook |
| D | Deep Research mode: same as C — does it cite MY numbers? | M2 |
| E | Repeat A + C after 3 days | Response stability |
| G | "How is my recovery this week?" (ring off 1.5 weeks) | **Gap awareness — most diagnostic probe.** Real system flags missing data; wrapper confabulates |

Transcripts + screenshots → `probes/`, scored same day, scoring rubric in the report appendix.

### 4. Report (published by Aug 9–10)

- Answer-first: one-line verdict up top
- Side-by-side per question: *data says X (effect size) — Jade says Y (score)*
- One chart per model; one summary scorecard chart for Jade
- Final page: implications for Ultrahuman's AI layer (the parked strategy questions live here as implications only, incl. the sourced fact that Jade is free / no subscription revenue)
- Formats: written post (public) + 6–8 slide exec deck

---

## Build order

| Date | Ship |
|---|---|
| Aug 4 (tonight) | Probes A + G run (screenshots in `probes/`); caffeine/energy self-log starts |
| Aug 5–6 | 02_transform + 03_marts + 04_tests; repo public, PR merged |
| Aug 6–8 | M1 → M2 → M3; charts |
| Aug 8 | Probe battery complete (C/D/E), scored |
| Aug 9–10 | Report written + exec deck; published |

## Data-quality findings (2026-08-04, from the built transform — these belong IN the report)

The headline "2M+ readings / 18 months" does not survive contact with the analysis grain:

| Finding | Number | Consequence |
|---|---|---|
| Usable derived nights | **144 of 562 days (26%)** | Ring worn ~half the nights; sleep derivable on ~half of those. *(Superseded 2026-08-09: the 116/21% measured on Aug 4 predates the transform fixes below.)* |
| Consecutive night pairs | **50** | Hard ceiling on M2. Simple model + CIs only |
| Nights with no overnight data at all | 267 | Not a detector failure — the ring was off |
| Coverage collapse in 2026 | Feb 2, Apr 2, May 1 | Nov–Dec 2025 missing entirely; recent months thinnest |
| Median derived sleep | 4.5 h (p25 3.7 / p75 6.0) | Short. Real signal, but partly truncated blocks |
| Bedtime unusable on 23 nights | window-edge truncation | Flagged in `start_truncated`; wake time still valid |

**Two bugs found and fixed during the build — both are report material, not embarrassments:**
1. *Normalisation:* thresholding `motion_sum` per 10-min bin measured **sampling density**, not movement (readings/bin range 6–2037). Corrected to per-reading mean; validated by separation (steps>0 bins: motion 19.3 / HR 81.4 vs steps==0: 7.8 / 66.6).
2. *Circular time:* summary percentiles sorted clock strings lexically across a midnight-spanning window, ranking 03:00 before 20:00 and making the medians meaningless. This one nearly hid a working detector behind a nonsense summary.

These make the "does Jade know your data?" question sharper: **if the sensor record is this sparse, any confident Jade claim about a period with no data is confabulation by construction.** Probe G now has a target list — the specific date ranges where the ring recorded nothing.

## Out of scope

- SLM build-vs-buy model, unit economics, value-vs-usage quadrant (parked — implications page only)
- Rise/Oura competitive teardown beyond one contextual paragraph
- Building a better recommendation engine
- Any population-level or medical claim
