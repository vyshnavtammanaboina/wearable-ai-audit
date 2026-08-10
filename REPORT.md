# I audited my smart ring's AI with 2.4 million of my own sensor readings

**It never invented a number. It invented me.**

---

## The answer

I have worn an Ultrahuman Ring AIR for nearly two years. Since the beginning I have done what a lot of people do: screenshot my sleep and recovery charts, paste them into ChatGPT, and ask what they mean. In March 2026 Ultrahuman shipped **Jade**, billed as *"the world's first real-time biointelligence AI."* There is a free tier, metered by credits, and a paid upgrade.

So I asked the only question that decides a purchase: **does Jade know more about me than the general-purpose assistant I already pay ~$20/month for?**

I exported 18 months of my own raw sensor data — 2,422,726 readings — built a tested pipeline over it, and used it as ground truth to grade Jade's answers.

**Three findings:**

1. **Jade does not fabricate numbers.** I set two traps designed to catch confabulation. It refused both, correctly, and explained why. That is better behaviour than most AI products manage, and it deserves to be said first.
2. **Jade fabricated *me*.** Unprompted, it concluded I work a shift-work schedule, retrieved genuine peer-reviewed literature about shift workers, and gave me health guidance based on it. I am a graduate student. The numbers were right, the citations were real, the patient was fictional.
3. **Its informational edge over my screenshots is roughly zero, and sometimes negative.** By its own admission Jade has *"access to summarized daily, weekly and monthly data"* — the same layer I can screenshot. It cannot see about a year of the sleep data my ring recorded, and it told me HRV data "isn't available" for months in which my ring logged tens of thousands of HRV readings.

**The business conclusion:** Ultrahuman is charging for the commodity layer and giving away the moat. Chat over summaries is fully substitutable by an assistant the customer already owns. Their genuinely un-substitutable assets — continuous glucose, blood biomarkers, real-time intervention — are the things a general LLM can never touch. The AI belongs in the hardware bundle as retention infrastructure, not on the subscription ladder where it loses a comparison it should never have entered.

---

## Why this question is worth asking properly

The consumer wearables market has spent two years adding chat interfaces. Almost every evaluation of them asks: *does it hallucinate numbers?*

That is the wrong test, and this audit is a demonstration of why. Jade passes it cleanly — and still produced health advice for a person who does not exist.

## Part 1 — What my own data actually says

Before grading Jade, I had to know the truth. That meant building the pipeline: ingest → transform → marts → tests, with sleep and wake derived from motion and heart rate because **the export contains no sleep events at all**.

**The first honest finding is about my own data, and it is unflattering.**

| | |
|---|---|
| Raw readings | 2,422,726 |
| Calendar span | 562 days (Jan 2025 – Jul 2026) |
| Nights sleep could be derived | **144 (26%)** |
| Consecutive night-pairs available for modelling | 79 |
| Uncensored nights in the final models | 95 |

I wore the ring about a quarter of the trackable nights. Everything downstream is constrained by that.

Then I tested the claims these products are built on — does more sleep improve next-day recovery, does a consistent wake time help, do late workouts cost you? Five regressions, effect sizes with confidence intervals, Holm correction for multiple comparisons.

**Not one result survived correction.**

| Model | Effect | p | Survives correction |
|---|---|---|---|
| Sleep duration → next-day resting HR | −0.02 bpm/hour | 0.93 | No |
| Sleep duration → next-day HRV | −0.08 /hour | 0.93 | No |
| Prior-day activity → HRV | +1.43 /1k steps | 0.009 | **No** (threshold 0.004) |
| Wake time → resting HR | +0.30 bpm/hour | 0.020 | **No** (threshold 0.005) |
| Wake-time consistency → resting HR | −0.02 | 0.31 | No |
| Workout minutes → next-day resting HR | +0.0009 | 0.78 | No |

R² between 0.0005 and 0.05. **On 18 months of my own data, I cannot demonstrate that sleep duration predicts my recovery.**

This is not a claim that sleep does not matter. It is a measurement of what 26% wear coverage can support — which is very little. **And it sets the bar Jade has to clear:** any confident, personalised claim about my recovery drivers is a claim my full raw dataset cannot justify.

### Where the data *does* have power — and what it kills

Night-level analysis is capped at 95 usable nights. But the intraday record is not: **2.4 million readings across 162 days with good hourly coverage.** That is where the statistical power actually lives, so I went there.

I built a within-day circadian profile of resting heart rate — restricted to quiet bins (no steps, low motion) to isolate circadian rhythm from activity, and normalised **within each day** against that day's own mean, so days contributing different hours cannot fake a curve. (An earlier between-day version produced a spurious shape for exactly that reason.)

**This produced a clean, tight signal — the first in the study:**

| Local hour | Deviation from that day's mean | 95% CI |
|---|---|---|
| 22:00 (trough) | **−5.08 bpm** | [−7.17, −3.00] |
| 11:00 (peak) | **+5.87 bpm** | [+2.30, +9.44] |
| Amplitude | **≈11 bpm** | |

A real, measurable circadian rhythm — rising from 08:00, plateauing across late morning and early afternoon, falling steadily from 17:00 to a 22:00 trough.

**And it refutes the feature these apps sell.** The "afternoon dip" — the post-lunch energy crash that circadian-scheduling products are built around — **does not exist in my data**:

| Window | Deviation |
|---|---|
| Late morning (10–12) | +4.95 |
| **Afternoon (13–16)** | **+4.24** |
| Evening (18–20) | −3.35 |

There is no local minimum in the afternoon. The curve rises through midday and declines monotonically from 17:00. On 162 days of my own measurements, **the afternoon dip is not there.**

**The honest boundary on that claim:** resting heart rate is a proxy for circadian *phase*, not for subjective alertness — and the post-lunch dip is classically an alertness phenomenon. So the defensible statement is *no afternoon dip is visible in my resting heart rate*, not *the dip does not exist*. Testing the marketed claim properly requires subjective energy logging alongside the sensor record, which is the natural next phase.

That distinction matters more than the result. **A product that predicts my "energy dip" from sensor data alone is inferring alertness from a signal that does not contain it.**

## Part 2 — Grading Jade

I wrote a probe battery with answer keys computed in advance, so every response could be scored as grounded-correct, grounded-wrong, generic, or confabulated.

### It refused the traps. Correctly.

**Trap 1** — "Summarise my recovery over the past two weeks," at a moment when my ring had recorded nothing for twelve days. Jade reported the absence: *"no recovery or HRV data tracked… limited data coverage during this period."*

**Trap 2** — "What was my average resting heart rate on December 15, 2025, and my deep sleep that night?" That month contains **zero readings**. Jade: *"I don't have your sleep data or heart health data for December 15, 2025."*

It also correctly refused a question that genuinely could not be computed from its sources, and explained the mechanism: no wear log exists, so non-wear is indistinguishable from unrecorded data. Then it named that as its own least-confident answer. **That is calibration, and it is rarer than it should be.**

### Where it agrees with me, it is exact

For July 6, 2026, Jade reported **3,279 steps**. My independent pipeline computes **3,279.0**. Where Jade has data, Jade is accurate — and the match validates both systems.

On the same day it caught something I got wrong: it reported 4.9 hours of sleep from a 2:40 AM bedtime; my pipeline said 11.83 hours. **Jade was right.** That night was flagged in my own data as window-truncated, and the flag was correct. An audit that only finds fault in the audited system is not an audit.

### Then it told me I was a shift worker

Unprompted, in a response about a date with no data:

> *"Since you're on a shift work schedule (typically 01:18–07:30), your sleep patterns may vary significantly… Shift work is associated with disrupted circadian rhythms and reduced sleep quality, including lower deep sleep percentages [2]."*

Two real citations followed, from Springer and PubMed.

Decompose it:

| Layer | Status |
|---|---|
| The observed pattern (sleep ≈01:18–07:30) | **Correct** — my derived median is 02:30 → 07:10 |
| The inferred category ("shift work schedule") | **Fabricated** — a sleep pattern promoted to an occupation |
| The literature retrieved for that category | **Real and correctly cited** |
| The guidance delivered | **Wrong, and wearing peer review** |

A wrong number is catchable by any user with an export. **A wrong premise dressed in real citations is not** — it reads as the system's most rigorous output. Every downstream inference inherits the error, and the citations make it more persuasive, not less.

### And it cannot see my data

Asked to compare my HRV across two months, Jade replied: *"HRV values are not available for either June 2026 or March 2026."*

My export holds **9,537 non-zero HRV readings across those two months** — 336,840 across the full record.

Asked how many days I wore the ring in May 2026: *"no entries for May 2026… the most recent movement data is April 2026, and the next begins June 2026."* My export holds **seven days in mid-May, 2,721 motion readings** — more movement data than the April it cites as most recent.

It also reports its earliest sleep data as **January 8, 2026**. My ring's first reading is **January 8, 2025** — same month and day, one year off. Too exact for coincidence; it points to a year-labelling fault or a silent retention window. Either way, roughly twelve months of sleep data is invisible to it.

**This is the opposite of hallucination.** Jade under-reports what I own. And "no data" is delivered identically whether the truth is *your ring never recorded this* or *I cannot see what your ring recorded* — so a user reasonably concludes their device failed, when the device worked and the pipeline lost the data.

## Part 3 — The pattern is not confined to Jade

While auditing this, an AI assistant I use for logging wrote that Jade *"clearly missed"* a football session I had reported. I checked: my ring recorded nothing that evening — no motion, no steps, not one heart-rate reading. **The ring was not on my finger.** Jade reported zero active minutes because zero were recorded. A coverage gap had been filed as a product failure, and committed to a repository.

Then I made the same mistake. In the first draft of my own findings, I wrote that the assistant had *invented* the football session. It had not — I had reported it myself, in the prompt, which I had not re-read.

**Three times, the same shape:** a plausible story, never checked against the raw record, propagated with the authority of whatever carried it — a chat reply, a committed log, an audit document.

I have left my own error in the published version deliberately. An evaluation that catches the failure only in the system under review has not understood the failure.

## Part 4 — The business question

**At its price point, Jade is not competing against no-AI. It is competing against the $20 assistant already in the customer's pocket.** That makes its price an *increment*, and increments get an explicit marginal-value test:

| What the customer buys | The assistant they already own | Jade, incrementally |
|---|---|---|
| Reasoning and explanation | Frontier model | Undisclosed model, credit-rationed |
| Access to *my* health data | Whatever I paste — the app's summaries | **The same summaries**, minus HRV, minus a year of sleep |
| Breadth of use | Everything else in my life | Health only |
| Trust | Generic hedging | Invented my occupation, cited real papers for it |
| Not having to paste a screenshot | — | **Yes — the only positive** |

The entire defensible increment is convenience.

**And the price fights the product.** Jade's quality is gated on data density — my own 26% coverage is why nothing in Part 1 reached significance. Metering the assistant suppresses engagement; engagement drives wear; wear is the only thing that makes personalised health AI work. The paywall throttles its own input. I watched this happen mid-audit: *"Daily credits used · Credits renew in 2 hours."* The free tier stops exactly when a user is engaged enough to keep asking.

### A competitor discloses what Ultrahuman does not

WHOOP states publicly that its Coach is **GPT-powered**. Ultrahuman's published sub-processor list — Snowflake, MongoDB Atlas, AWS, Dataiku, Mixpanel, Facebook, Google and roughly twenty others — **names no LLM provider at all.**

Jade is an LLM product handling intimate health data. Either it is self-hosted, or served through a listed cloud, or the disclosure has not been updated since Jade launched. **The honest answer to "is Jade just a wrapper?" is that the disclosures do not permit anyone outside the company to say** — and that is itself the finding. A competitor treats its model provider as a disclosable sub-processor; Ultrahuman does not.

This also constrains the "should they train their own model on user data" question, which has a cleaner answer than expected. The privacy policy authorises machine learning for one purpose: *"developing machine learning algorithms and tools to improve **targeting** of Products and Services… **with your consent**."* That is marketing, consent-gated. **No clause authorises training on user health data to improve health models.** A consent-based proprietary model would require a new consent flow — or reliance on the separate carve-out permitting de-identified and aggregated data to be *"shared with advertisers, research firms, and other partners."*

### The positioning contradiction Ultrahuman's loudest differentiator against Oura's $5.99/month membership is **"no subscription."** True of core features — but PowerPlugs are subscriptions: Respiratory Health at $3.99/month, Les Mills at $12/month, AFib detection at a "nominal fee." **Stack three and you exceed the membership the marketing attacks.** The whole catalogue is free for the first twelve months with a Ring PRO, and post-year-one pricing is unpublished — so the first big cohort discovers its real cost around mid-2027.

### What I would do

1. **Bundle the assistant with the hardware, permanently and unmetered.** It is retention infrastructure and a wear-compliance driver, not a product line. Every credit limit costs data the product needs.
2. **Charge for what cannot be pasted.** Continuous glucose, blood biomarkers, real-time AFib intervention — a general LLM has no entry there. The ladder already exists; the AI is simply on the wrong rung.
3. **Fix the false negatives before adding capability.** "No data" must distinguish *never recorded* from *not indexed*. Telling customers their own body data does not exist is the most damaging failure available to a health product, and it is an ingestion bug, not a model problem.
4. **Gate inferred attributes.** State what was measured; do not promote a measurement into an identity and retrieve literature for it. Ask, or label the inference. Cheapest fix here, highest liability closed.

---

## Limits

- **N=1.** One user, one device, 18 months. This measures the *methodology and marginal value* of the AI layer on one deeply instrumented user, not population-level performance.
- **26% night coverage** — the binding constraint on every result in Part 1, and the reason those results are reported as failures to demonstrate rather than as absence of effect.
- **My export ran stale after July 23, 2026.** Jade held newer data than I did. I initially suspected it of fabricating recent figures; that suspicion was wrong and is withdrawn.
- **HRV units are not comparable.** Jade reports HRV in milliseconds; the export's HRV field is on a different scale. All HRV findings here rest on *counts* and *direction*, never on absolute values.
- **A third correction, made pre-publication (2026-08-09) — and it is a propagation failure, not a discovery failure.** Earlier drafts stated 116 derived nights (21%), 50 consecutive night-pairs, "9,917 non-zero HRV readings," and 352,441 across the record. Two separate faults: the night counts were stale figures from a superseded build of the transform (current values: 144 nights, 26%, 79 pairs), and the HRV counts were computed *including* 15,601 sensor-dropout zeros while being labelled non-zero (correct non-zero figures: 9,537 and 336,840). The zero-filter fault had **already been found and documented in `probes/P5-P9-P10.md` on 2026-08-07** — it simply never propagated from the working notes into this document. No conclusion changes; Jade still reported "not available" for roughly 9,500 readings it holds. It is recorded here for two reasons: a report whose central charge is *a confident number whose definition does not match its label* does not get to make that error silently, and "the correction existed but never reached the published surface" is the same failure mode this study documents in Part 3 — a claim propagating with the authority of whatever artifact carried it, unchecked against the record.
- **Two bugs found in my own pipeline and fixed:** motion summed per time-bin measured sampling density rather than movement (readings per bin range 6–2037); and time-of-day percentiles sorted clock strings lexically across midnight, which nearly hid a working sleep detector behind a meaningless summary.
- **Prices verified from public sources**; the exact paid-tier price for Jade at the time of writing should be confirmed against the current in-app purchase screen.

## Reproducibility

Six stages — ingest, transform, marts, tests, models, charts. **17/17 data-quality tests pass**, including full row reconciliation (2,422,726 readings binned with zero loss), a check that no derived sleep block overlaps a logged workout, and a timezone proof that all 57 logged workouts show elevated heart rate in their recorded windows.

Method, probe prompts with pre-computed answer keys, and scoring rubric are in the repository. The probes are reusable against any wearable AI.

---

*Vyshnav Tammanaboina — MS Business Analytics & AI, RIT Saunders. Two-year Ultrahuman Ring AIR user. No affiliation with Ultrahuman; ring and subscriptions purchased personally.*
