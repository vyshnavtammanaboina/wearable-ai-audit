# FINDINGS — the case spine
*Answer-first. This is the skeleton the published write-up and the exec deck are both built from.*
*Status 2026-08-07: framing locked; P1 and P5 run; P9/P10/P11 and a fresh export pending.*

---

## The framing (set by the author, 2026-08-07)

**Who is asking:** a two-year Ultrahuman Ring AIR user who has been pasting his own scores and charts into general-purpose LLMs for interpretation since day one. Not a reviewer — an existing power user who **already built, by hand and for free, the thing Jade now sells.**

**The question:** at **$3.99/month**, is Jade AI a step in the right direction for Ultrahuman and its customers — or another wrapper on an existing model with health packaging?

**Why this narrator makes the study work:** he *is* the counterfactual. The benchmark is not "is Jade good in the abstract," it is the only comparison that decides a purchase:

> **Does Jade know more about me than a general LLM I hand my screenshots to?**

That reframes the whole evaluation. A dedicated health AI's *only* defensible edge over a commodity model is **privileged access to the user's actual data** — the reasoning layer is a commodity, available free in a dozen chat apps. So the study measures exactly one thing: **the size of Jade's information advantage over a screenshot.** Everything already found feeds straight into that number.

---

## The answer (slide 1, sentence 1)

**Jade is not competing against no-AI. It is competing against the $20 LLM already in the customer's pocket — and at $3.99 it is asking to be compared on the one dimension where it loses.**

### The pricing error, stated plainly

The target customer already pays ~$20/month for a general assistant that answers health questions, explains charts, cites literature, and does a hundred other things. Jade's $3.99 is therefore **not a price — it is an increment**, and it triggers an explicit marginal-value test the moment it appears:

| What the customer is buying | The $20 LLM they already own | Jade at +$3.99 | Marginal value |
|---|---|---|---|
| Reasoning and explanation | Frontier model | Undisclosed, cost-rationed by credits | **≤ 0** |
| Access to *my* health data | Whatever I paste — i.e. the app's summaries | **The same summaries**, minus HRV, minus ~a year of sleep | **negative** |
| Breadth of use | Everything in my life | Health only | negative |
| Trust | Generic hedging | Invented my occupation, then cited real papers for it | negative |
| Not having to paste screenshots | — | Yes | **the only positive** |

**Jade's entire defensible increment is convenience.** Everything else the customer already has, and on data access — the one axis where a first-party health app should be unbeatable — Jade is *behind* the screenshots, because it denies HRV that exists and cannot see a year of sleep.

**$3.99/month is $48/year for not taking a screenshot.** That is a feature priced as a product.

### Why the price actively damages the product

Jade's output quality is gated on **data density** — this user wore the ring 26% of nights, and at that coverage nothing personal is statistically supportable (see §4). So:

> **Metering Jade suppresses engagement → engagement is what drives wear → wear is what makes Jade good.**

The paywall throttles the exact input the product needs to stop being generic. It is a negative feedback loop pointed at their own moat. (Observed directly: the session hit *"Daily credits used · Credits renew in 2 hours"* mid-evaluation — the free tier stops working precisely when a user is engaged enough to keep asking.)

Note also the positioning gap: the marketing page says Jade is **"available now as a platform upgrade to all Ultrahuman users globally"** while the app meters usage and upsells Jade Pro. Free in the announcement, rationed in the hand.

### Where the money actually is

A general LLM can replicate anything a customer can paste. It cannot replicate **what it cannot be given**:

| Ultrahuman asset | Can a $20 LLM substitute? |
|---|---|
| Chat over daily/weekly/monthly summaries | **Yes** — paste a screenshot. This is what Jade currently sells |
| Raw 5-minute timeseries (2.4M readings/18 months) | No — but Jade cannot see it either |
| Blood Vision biomarkers, M2 CGM, Home environment | **No** — genuinely proprietary, un-pasteable |
| Real-time action (trigger breathwork, flag Afib) | **No** — an LLM can advise, it cannot act on a live signal |

**Recommendation: make Jade free and permanent, and move the price onto what cannot be pasted.** Bundle the chat layer with the hardware as retention infrastructure and a wear-compliance driver; charge for the multi-source clinical products (Blood Vision, CGM, Afib) and real-time intervention, where the general LLM has no entry.

**Verdict on the question as asked:** for the company, Jade is the right *capability* attached to the wrong *business model* — the $3.99 invites a comparison it cannot win and starves the data supply it depends on. For this consumer, already paying ~$20 for a broader assistant: **not worth it today**, and the reason is not model quality — it is that Ultrahuman is charging for the commodity layer and giving away the moat.

### And the failure that no price justifies

**Jade's numbers are real. Its patient isn't.** Asked about a date with no data, Jade correctly refuses — it does not fabricate figures. But unprompted, it decided this user "is on a shift work schedule," retrieved genuine peer-reviewed literature on shift-work sleep disruption, and delivered health guidance built on an occupational identity it invented. Meanwhile it cannot see roughly a year of the sleep data the ring recorded, and reports "no data" for 336,840 non-zero HRV readings it holds.

**The industry checks whether a health AI's numbers are real. Nobody checks whether the person it is reasoning about is real.**

## The three supporting points (the deck's spine)

**1. Jade is honest and well-calibrated — the hallucination thesis is wrong.**
Given a deliberate trap (summarise recovery over two weeks with zero data) it reported the absence instead of inventing a narrative. Asked an uncomputable question it refused and explained the mechanism correctly. It named its own least-confident answer accurately. Rules out "ungrounded chatbot" and "templated rule engine."

**2. It answers from pre-built documents, not from your data.**
Self-declared access: heart-health trends (monthly), heart-health data (weekly), recovery trends (monthly), recovery metrics (weekly) — plus "no sleep or activity data is available for you." Its own vocabulary is documents and inventories, never queries. The capability boundary is therefore **pre-computed vs. not** — not recent vs. old.

**3. That boundary produces false negatives, which is worse than it sounds.**
Verified against 18 months of the same user's export:

| Jade said | The record holds |
|---|---|
| "No HRV data for June 2026 or March 2026" | 9,537 non-zero HRV readings across those two months (March 6,473 / mean 147.0; June 3,046 / mean 135.3) |
| "No movement entries for May 2026; most recent is April, next is June" | May 13–19: 7 days, 2,721 motion + 2,721 step readings — **more than the April it cites** |

A user hears "no data" and concludes their ring failed. The ring worked perfectly. **The pipeline lost it.**

**4. And the deeper problem: this data cannot support confident personal advice from anyone.**
*(added 2026-08-05, after building the models — this reframes the case)*

Before judging Jade's advice, I asked what the same record could justify. Twelve coefficient tests across five models of overnight recovery (n=95–142 nights, HAC errors for night-to-night autocorrelation):

| Candidate driver | Effect on resting HR | 95% CI | Verdict |
|---|---|---|---|
| Sleep duration (+1 h) | −0.02 bpm | [−0.48, +0.44] | **Precise null** — not underpowered; bounded within ±0.5 bpm/h |
| Prior-day steps (+1,000) | −0.03 bpm | [−0.36, +0.30] | null |
| Waking 1 h later | **+0.30 bpm** | [+0.05, +0.56] | separates from zero, **fails correction** |
| Wake-time variability | −0.02 bpm | [−0.06, +0.02] | null |
| Workout minutes | +0.001 bpm | [−0.005, +0.007] | null |
| Late workouts | — | — | **unanswerable**: only 7 such nights |
| Prior-day steps → HRV | +1.4 ms | [+0.35, +2.50] | strongest found, p=0.009, **fails correction** |

**After Holm–Bonferroni across all 12 tests, nothing survives.** The strongest result (activity → HRV) needed p ≤ 0.004 and reached 0.009.

So the sharpest question in the study is not "is Jade's advice right?" but: **if 18 months and 2.4 million readings from a committed user cannot establish one statistically defensible personal recommendation, what is any AI layer's confident advice actually based on?**

The binding constraint is **wear compliance, not model quality.** At 26% night coverage, with real effects this small, no model — LLM, rule engine, or regression — can produce defensible personalisation. The AI is being asked to do something the sensor record does not support.

*Note the precise null on sleep duration is itself a finding: this is not "no signal, need more data." The interval is tight. For this user, an hour more sleep moves resting HR by at most half a beat per minute.*

**5. The failure that matters most: a fabricated premise wearing real citations.**
*(added 2026-08-05 from P5 — this is now the headline)*

Unprompted, Jade told this user: *"Since you're on a shift work schedule (typically 01:18–07:30)…"* and cited two real papers (Springer, PubMed) on shift-work sleep disruption.

He is a graduate student. Decompose what failed:

| Layer | Status |
|---|---|
| Observed pattern (sleep ≈01:18–07:30) | **Correct** — my derived median is 02:30 → 07:10 |
| Inferred category ("shift work schedule") | **Fabricated** — a sleep pattern promoted to an occupational identity |
| Literature retrieved for that category | **Real and correctly cited** |
| Guidance delivered | **Wrong, and wearing peer review** |

Right numbers, coherent reasoning, genuine citations — advice for a different person. A wrong *number* is catchable by any user with an export. A wrong *premise* dressed in real references is not: it reads as the system's most rigorous output.

**And it generalises further than Ultrahuman — it recurred twice more inside this very study** (full record: `probes/XVAL-2026-07-06.md`):

| # | Who | Premise asserted without checking the raw record | Consequence |
|---|---|---|---|
| 1 | JADE | "you're on a shift work schedule" | Real citations, wrong person |
| 2 | A logging assistant | "JADE clearly missed your workout" | The ring was simply not worn; a coverage gap was misfiled as a product failure and committed to a repo |
| 3 | **This analysis, first draft** | "the assistant invented the football session" | False — the user had reported it himself. A wrong accusation written into a findings file, then retracted |

Same shape three times: a plausible story, never tested against the raw record, propagated with the authority of whatever artifact carried it — a chat reply, a committed log, an audit document.

**The instrument is not exempt from the failure it measures.** That is the finding, and the reason the third row stays in the published version: an audit that catches the pattern only in the system under review has not understood the pattern.

## Why it matters (the "so what")

**Correction (2026-08-05):** an earlier draft asserted Jade was free with no subscription attached, and built the cost-centre argument on that. **It was wrong.** The UI meters usage — *"Credits renew in 2 hours · Upgrade to Jade Pro for unlimited credits"* — so Jade is a **rationed free tier with a paid upgrade.** Three consequences:

1. **Inference cost is material enough to ration**, which is direct evidence for the build-vs-buy question (a fine-tuned small model runs 20–100× cheaper per conversation than frontier API calls for narrow, repeatable tasks).
2. Cost-vs-price is a live question, not a moot one.
3. Every failure above occurs inside **a product users are asked to pay to use more of** — which raises the stakes on the false negatives and the fabricated premise considerably.

Marketed as "the world's first real-time biointelligence AI," Jade cannot see roughly a year of the sleep data its own ring captured, says "no data" to 337k non-zero HRV readings, and — by its own admission — has **"access to summarized daily, weekly and monthly data"** only.

**None of these are model-quality failures.** One is an ingestion gap, one is a wear-compliance gap, one is an unguarded inference step. Better models fix none of them, which is the good commercial news: **the AI isn't the gimmick; the data supply and the guardrails are the product.** Scaling model spend against a 26%-coverage sensor record buys nothing a user would notice.

## Recommendation (quantified where the data allows)

0. **Gate inferred user attributes.** Jade may state what it *measured*; it must not promote a measurement into an identity ("shift worker") and then retrieve literature for it. Either ask ("does your schedule involve shift work?") or label the inference as one. This is the cheapest fix on the list and it closes the failure with the highest liability — clinical-sounding advice aimed at the wrong person.
1. **Close the false-negative class.** Any "no data" response should distinguish *never recorded* from *not in my index* — a one-line provenance change that removes the most damaging data failure a health product can have: telling users their own body data doesn't exist. Start with the ~12-month sleep blind spot (Jade reports earliest sleep data Jan 2026; the ring recorded from Jan 2025).
2. **Give the model query access to the raw store**, or expand document coverage to the streams already captured. HRV is the glaring omission: 337k non-zero readings, invisible.
3. **Move spend from model to compliance.** Personalisation is gated on wear-nights, not parameters. On this record the ring was worn ~26% of nights; below some coverage floor, confident advice is unsupportable by construction. **Establish that floor, measure each user against it, and gate the confidence of advice on it** — a user under the floor should be told their data is too thin, not handed a recommendation.
4. **Instrument both boundaries.** Track (a) the share of "no data" answers that are false negatives, and (b) per-user wear coverage against the floor. Neither is measured today; on this sample both are bad.

## Evidence base and its limits (state these before anyone asks)

- **N=1**, one user, 18 months, ~2.4M readings; one probe run (P1, Deep Research mode).
- The user's export is **stale after 2026-07-23**; Jade holds newer data. No confabulation claim is made about post-Jul-23 figures — the earlier suspicion was withdrawn once the export cutoff was identified.
- Derived sleep covers 144 of 562 nights (26%); 79 consecutive-night pairs exist, so recovery-driver modelling stays a simple regression with confidence intervals. (Corrected 2026-08-09: earlier drafts cited 116/21%/50 from a superseded build of the transform.)
- Two bugs found and fixed in the author's own pipeline (motion normalised per reading after summing conflated sampling density with movement; circular-time percentiles sorted lexically across midnight) — documented because a study auditing someone else's data handling must show its own.

## Open items before publication

- [ ] Fresh export → verify Jade's July/August absolutes
- [ ] P5 (2025-12-15, zero readings) → clean confabulation test
- [ ] P9 boundary mapping → confirm bucket-2 behaviour
- [ ] P10 → does Jade acknowledge or defend the boundary when challenged with the HRV counts?
- [ ] Standard-mode re-run for the mode comparison
- [ ] M2/M3 models → what the data itself says about recovery and energy timing
