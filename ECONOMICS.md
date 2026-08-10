# Is Jade a profitable venture?
*Consulting note, 2026-08-07. Built on public financials, observed product behaviour, and published inference pricing. **Every number below marked (est.) is my estimate under stated assumptions - Ultrahuman publishes no segment data for Jade.** Structure and sensitivity matter more than point estimates; the verdict is tested against the ranges, not the midpoints.*

---

## Answer

**Not as currently built. But the fault is the compute architecture, not the model and not the price - and it is fixable.**

Four findings:

1. **The paid tier probably has negative gross margin**, and structurally so: flat $3.99 for *unlimited* usage of a multi-agent architecture, sold to the heaviest users.
2. **The cause is compute shape, not model quality.** Jade re-synthesises the same weekly picture on every question, so cost is variable and unbounded, scaling with the engagement the product needs. That is what forces metering.
3. **Precomputing a weekly per-user digest converts that variable cost into a fixed one** and drops the marginal cost of a follow-up question roughly 8×. It takes the paid tier from negative margin to an estimated ~55% gross margin, removes the need to meter, closes the false-negative defect, and creates the only genuine informational edge this product has over a general LLM. See §8.
4. **The free tier is affordable either way** - an estimated 1-2% of revenue, ~10-20% of FY25 net profit.

**So the answer is conditional: unprofitable as an on-demand synthesis engine, viable as a precomputed digest with cheap retrieval on top.** The question "should we charge for Jade?" is the wrong first question. "Why does answering one question cost ten model calls?" is the right one.

---

## 1. The base

| Input | Value | Source |
|---|---|---|
| FY25 revenue | ~$68M (₹565 Cr), 5.4× YoY | Entrackr |
| FY25 net profit | ~$8.8M (₹73 Cr) | Entrackr |
| Revenue from rings | 91% | Entrackr |
| Annualised run rate | ~$150M | trade press |
| Capital raised | $103M ($48M Mar 2026) | Tracxn |
| Ring price | $349 AIR / $479 PRO, **one-time** | Ultrahuman |
| Jade | free tier, credit-metered; "Jade Pro" for unlimited | in-app |
| Competitor benchmark | Oura $5.99/mo membership | Oura |

**Derived user base (est.):** $62M ring revenue ÷ ~$300 net ASP ≈ **207k units in FY25**; cumulative active base **~400k (est.)**.

## 2. Cost per query - and why the architecture matters

The probe transcripts show what one Deep Research query actually does: a planner selecting data-source agents (`sleep_daily`, `cardio_weekly`, tiering logic), retrieval across them, a literature RAG issuing **8 research queries**, then synthesis. That is roughly **10-15 model calls per user question**, with ~30 seconds of latency.

That is not a thin wrapper on one cheap call. It is an expensive request shape.

| Scenario | Model class | Cost/query (est.) | Cost per heavy user/mo (60 q) |
|---|---|---|---|
| **A** Frontier | GPT-5.5-class ($5/$30 per M) | ~$0.30-0.40 | **$18-24** |
| **B** Mid-tier | mini/flash-class | ~$0.02-0.05 | $1.20-3.00 |
| **C** Self-hosted SLM | fine-tuned 7-8B | ~$0.002-0.01 | $0.12-0.60 |

## 3. The decisive evidence: they meter the free tier

This is the part that does not require guessing.

The app enforces hard credit limits - *"Daily credits used · Credits renew in 2 hours"* - and the limit was reached during a single evaluation session of ordinary length.

**Companies do not aggressively ration what costs them nothing.** Metering this tight is revealed preference about unit economics: it places Jade in **Scenario A or B, not C**. If inference were near-free, the rational move would be unlimited usage to drive engagement and wear-compliance - the exact input the product needs.

## 4. The paid tier loses money on the users who buy it

"Jade Pro for **unlimited** credits" at a flat ~$3.99/month is the structural problem.

Flat-rate pricing on an unbounded variable cost inverts the usual SaaS logic: **the customers who subscribe are self-selected heavy users**, i.e. the most expensive ones. There is no light-user base to cross-subsidise them, because light users stay on the free tier.

| Scenario | Revenue/user/mo | Est. COGS at 60 queries | Gross margin |
|---|---|---|---|
| **A** Frontier | $3.99 | $18-24 | **−$14 to −$20** |
| **B** Mid-tier | $3.99 | $1.20-3.00 | +$1.00 to +$2.80 |
| **C** SLM | $3.99 | $0.12-0.60 | +$3.39 to +$3.87 |

Given the metering evidence points at A or B, and the observed architecture points at the expensive end: **the paid tier is at best thin-margin and quite possibly loss-making per subscriber.** Every incremental Pro subscriber may destroy value.

**Illustrative scale (est.):** at 5% conversion on 400k users = 20k subscribers → **~$958k/year revenue**. Under Scenario A the same cohort costs ~$4.3M-5.8M/year to serve. Under B it nets roughly +$240k-670k. Neither outcome is material against a $150M run rate - **the paid tier cannot move the company either way.** It can only lose money or annoy customers.

## 5. The free tier is affordable

60k regular users (est.) × 15 queries/month × ~$0.125 blended ≈ **$112k/month → ~$1.35M/year (est.)**

That is **~2% of FY25 revenue** but **~15% of FY25 net profit** - real, containable, and the right order of magnitude for a strategic capability. Under Scenario B or C it drops to a rounding error.

## 6. Where the value actually is

Ultrahuman sells a **one-time $350-479 device with no recurring revenue**. Its economics are therefore driven by unit volume, repurchase/upgrade, returns, and ecosystem attach (CGM, Blood Vision, Home) - not by software ARPU.

Against that, a $3.99 subscription is rounding-error revenue. But retention is not:

| Lever | Value of a 1-point improvement (est.) |
|---|---|
| Jade Pro subscription revenue (5% conversion) | ~$1.0M/yr |
| +1pt ecosystem attach on 400k users | **~$1.4M+/yr** |
| +1pt reduction in returns/churn on $62M hardware | **~$620k/yr, recurring in cohort value** |
| Wear-compliance improvement | **Compounding** - see below |

**The compounding term is the real prize.** This audit measured 26% night coverage on a two-year user, and at that density *nothing* personal reached statistical significance - not sleep→recovery, not wake-consistency, not workout load. **Wear compliance is the binding constraint on whether personalised health AI works at all.** An assistant that increases wear makes every downstream feature better, including the paid clinical products. Metering that assistant does the opposite.

**So the current pricing trades a compounding retention asset for ~$1M of thin-margin subscription revenue.** That is the strategic error, and it is quantifiable.

## 7. The 2027 cliff

All PowerPlugs are free for 12 months with a Ring PRO, and post-year-one pricing is unpublished. The launch cohort (shipping ~June 2026) reprices around **mid-2027**. Whatever Jade's monetisation becomes, it lands inside that event - a simultaneous ask across the whole add-on catalogue, against a brand whose loudest promise is *"no subscription."* Stacking three PowerPlugs already exceeds the Oura membership the marketing attacks.

## 8. The architectural fix: precompute the digest, price the follow-ups

Everything above diagnoses a pricing problem. It is actually a **compute-shape** problem, and that reframing changes the recommendation.

**The fault:** Jade synthesises on demand. Every question fires a planner, retrieval across data-source agents, a literature RAG, and a synthesis pass. The company is paying to re-derive the same weekly picture on every question a user asks. Cost is therefore **variable and unbounded**, scaling with engagement - which is precisely why a flat $3.99 for "unlimited" cannot work, and why the free tier must be metered.

**The fix:** generate one **weekly health digest per user** as a batch job, the same cadence as the weekly snapshot the app already ships. It compiles the full record the company holds into a single readable document, and is **stored as user data**. Follow-up questions then run as retrieval over that document plus one small-model call, not a fresh multi-agent synthesis.

### What that does to the unit economics (est.)

| | Today: synthesise per question | Proposed: precompute weekly |
|---|---|---|
| Dominant cost driver | queries asked | **users served** |
| Cost shape | variable, unbounded | **fixed per user, 52/year** |
| Cost of the *next* question | ~$0.125 blended | **~$0.015** (retrieval + one small call) |
| Est. cost per regular user/year | ~$22.50 (180 questions) | **~$20.90** (52 digests + 180 cheap follow-ups) |
| Heavy user at 5x volume | ~$112/year | **~$29/year** |
| Flat-rate pricing | breaks | **works** |

The average barely moves. **The margin behaviour is what changes.** Today a 5× heavy user costs 5× more, which is exactly who self-selects into a $3.99 unlimited plan, and why §4 shows the paid tier destroying value. Under precompute the same user costs ~40% more, not 400% more. At $47.88/year revenue against ~$21 of cost, the paid tier moves from **negative margin to roughly 55% gross margin** - and metering becomes unnecessary rather than merely undesirable.

### The file boundary is the cost control, not a limitation

The decisive property is that each user's digest is **a single bounded file**. The model can only answer from what that file contains, which means:

- **Context size is capped by construction.** No retrieval fan-out, no planner selecting among data-source agents, no literature RAG issuing eight queries. There is nothing to search.
- **Cost per question has a ceiling, not an average.** The current architecture's danger is the tail: an engaged user asking hard questions is the expensive one. Bound the input and the tail disappears.
- **Latency collapses** from ~30 seconds to roughly one small-model call.

The scope limit is the feature. "You can only answer from this user's file" is simultaneously the privacy boundary, the cost boundary, and the grounding boundary.

### This inverts the obvious fix, and that matters

The natural reading of the false negatives is: *the document boundary is the problem, so give the model query access to the raw store.* That is exactly the unbounded, expensive architecture diagnosed above. It would raise cost per query, reintroduce metering, and reinstate the loop that starves the product of the engagement it needs.

**The boundary was never the fault. The contents were.** Jade already answers from pre-built documents; it says so itself. Its defect is that those documents omit HRV and roughly a year of sleep the company holds. So the recommendation is not to rearchitect the product but to **widen a batch job that already runs** - the cheapest intervention on this list, and the one a client is most likely to actually adopt.

*(This supersedes recommendation 2 in `FINDINGS.md`, "give the model query access to the raw store." That recommendation is withdrawn: it treats a symptom by adopting the cost structure that causes the underlying problem.)*

### It closes the quality defect with the same change

The false negatives in §Findings are not model failures - Jade answers from pre-built documents with incomplete coverage. If the digest is generated deliberately, its coverage is a **design decision**: include HRV, include the full sleep history, and "no data for June 2026" stops being emittable for data the company holds.

**Be precise about what is and isn't new here.** Answering from a pre-built document is what Jade already does - by its own description it has "access to summarized daily, weekly and monthly data," and that accidental document layer is where the false negatives live. The proposal does not change the architecture class; it changes who owns the document. Today it is an unaudited index with holes. Under precompute it is a deliberately generated artifact with a coverage contract: complete streams, known cadence, auditable. The bounded file is also the cost ceiling - a follow-up can only ever cost what reading one document costs, which is what makes flat-rate pricing safe. **The same property that caps the cost caps the failure: the digest can only say what it holds, so what it holds must be a design decision, not an accident.**

**One guardrail is mandatory.** The digest must record *measurements*, not inferred identities. The shift-worker failure occurred because a sleep pattern was promoted to an occupation; write that inference into a stored document and every future answer inherits it, with the document's authority behind it. State observations, label inferences as inferences, or ask.

### And it builds the moat the current product lacks

The marginal-value test in §6 turns on substitutability: a customer can paste a screenshot into an assistant they already own. **A screenshot is one screen. A compiled digest across 18 months is not pasteable.** Precompute is therefore not only the cheaper architecture, it is the only version of this product that has an informational edge over a general LLM at all.

## 9. Recommendation

1. **Precompute a weekly per-user digest and stop synthesising on demand.** This is the highest-ROI change available and everything else follows from it: fixed cost per user, an ~8× cheaper marginal question, metering becomes unnecessary, digest coverage becomes a design decision that closes the false negatives, and the compiled artifact becomes something the customer cannot reproduce by pasting a screenshot. Ship it at the cadence of the weekly snapshot that already exists, and store it as user data. See §8.
2. **Then the paid tier is worth keeping, and the free tier should stop being metered.** With cost fixed per user, $3.99 clears ~55% gross margin (est.) instead of running negative, so the earlier "stop selling it" conclusion is withdrawn. Give the free tier a lighter digest on a slower cadence: it protects wear compliance, which is the binding constraint on the whole product, at bounded cost. Route routine follow-ups to a small self-hosted model (Scenario C) and reserve the multi-agent path for genuine Deep Research.
3. **Charge for what a general LLM cannot substitute** - CGM, Blood Vision, real-time AFib intervention. The ladder exists; Jade is on the wrong rung. Chat over summaries is fully substitutable by an assistant the customer already pays ~$20/month for.
4. **Fix the false negatives before adding capability.** Jade denies HRV data the ring recorded 336,840 times (non-zero) and cannot see ~12 months of sleep. That is an ingestion defect suppressing the perceived value of the whole ecosystem - and it is cheaper to fix than any model upgrade.

## 10. What would change this verdict

| If true | Effect |
|---|---|
| Jade already runs a self-hosted small model | Paid tier becomes viable; metering becomes an unforced error |
| Conversion is >15%, not 5% | Subscription revenue becomes material; the margin question gets urgent |
| Jade measurably lifts ecosystem attach | Reclassifies as customer-acquisition spend; strengthens the case for a free-tier digest |
| **Precompute cannot cover the question distribution** | If a large share of questions genuinely need fresh multi-agent synthesis rather than retrieval over a digest, §8 collapses and the original bundle-it-free conclusion returns. **This is the load-bearing assumption and it is testable from their own query logs.** |
| Post-2027 PowerPlug pricing is aggressive | Whole analysis shifts from AI economics to bundle-repricing risk |

**Highest-value disclosure to seek:** Jade's inference stack and per-query cost. Everything here turns on it - and it is exactly what the sub-processor list omits while a competitor (WHOOP, GPT-powered Coach) discloses.
