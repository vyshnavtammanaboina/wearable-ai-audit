# Is Jade a profitable venture?
*Consulting note, 2026-08-07. Built on public financials, observed product behaviour, and published inference pricing. **Every number below marked (est.) is my estimate under stated assumptions — Ultrahuman publishes no segment data for Jade.** Structure and sensitivity matter more than point estimates; the verdict is tested against the ranges, not the midpoints.*

---

## Answer

**No — and more importantly, it cannot be, at its current price. But that is the wrong objective for it.**

Three findings:

1. **The paid tier probably has negative gross margin**, and structurally so: flat $3.99 for *unlimited* usage of a multi-agent architecture, sold to the heaviest users.
2. **The free tier is affordable but not free** — an estimated 1–2% of revenue, ~10–20% of FY25 net profit.
3. **The retention lever is worth several times the subscription lever**, and the current pricing trades the larger for the smaller.

**Jade should be run as cost of goods on the hardware, not as a P&L line.** The question "is Jade profitable?" invites a build that destroys more value than it captures.

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

## 2. Cost per query — and why the architecture matters

The probe transcripts show what one Deep Research query actually does: a planner selecting data-source agents (`sleep_daily`, `cardio_weekly`, tiering logic), retrieval across them, a literature RAG issuing **8 research queries**, then synthesis. That is roughly **10–15 model calls per user question**, with ~30 seconds of latency.

That is not a thin wrapper on one cheap call. It is an expensive request shape.

| Scenario | Model class | Cost/query (est.) | Cost per heavy user/mo (60 q) |
|---|---|---|---|
| **A** Frontier | GPT-5.5-class ($5/$30 per M) | ~$0.30–0.40 | **$18–24** |
| **B** Mid-tier | mini/flash-class | ~$0.02–0.05 | $1.20–3.00 |
| **C** Self-hosted SLM | fine-tuned 7–8B | ~$0.002–0.01 | $0.12–0.60 |

## 3. The decisive evidence: they meter the free tier

This is the part that does not require guessing.

The app enforces hard credit limits — *"Daily credits used · Credits renew in 2 hours"* — and the limit was reached during a single evaluation session of ordinary length.

**Companies do not aggressively ration what costs them nothing.** Metering this tight is revealed preference about unit economics: it places Jade in **Scenario A or B, not C**. If inference were near-free, the rational move would be unlimited usage to drive engagement and wear-compliance — the exact input the product needs.

## 4. The paid tier loses money on the users who buy it

"Jade Pro for **unlimited** credits" at a flat ~$3.99/month is the structural problem.

Flat-rate pricing on an unbounded variable cost inverts the usual SaaS logic: **the customers who subscribe are self-selected heavy users**, i.e. the most expensive ones. There is no light-user base to cross-subsidise them, because light users stay on the free tier.

| Scenario | Revenue/user/mo | Est. COGS at 60 queries | Gross margin |
|---|---|---|---|
| **A** Frontier | $3.99 | $18–24 | **−$14 to −$20** |
| **B** Mid-tier | $3.99 | $1.20–3.00 | +$1.00 to +$2.80 |
| **C** SLM | $3.99 | $0.12–0.60 | +$3.39 to +$3.87 |

Given the metering evidence points at A or B, and the observed architecture points at the expensive end: **the paid tier is at best thin-margin and quite possibly loss-making per subscriber.** Every incremental Pro subscriber may destroy value.

**Illustrative scale (est.):** at 5% conversion on 400k users = 20k subscribers → **~$958k/year revenue**. Under Scenario A the same cohort costs ~$4.3M–5.8M/year to serve. Under B it nets roughly +$240k–670k. Neither outcome is material against a $150M run rate — **the paid tier cannot move the company either way.** It can only lose money or annoy customers.

## 5. The free tier is affordable

60k regular users (est.) × 15 queries/month × ~$0.125 blended ≈ **$112k/month → ~$1.35M/year (est.)**

That is **~2% of FY25 revenue** but **~15% of FY25 net profit** — real, containable, and the right order of magnitude for a strategic capability. Under Scenario B or C it drops to a rounding error.

## 6. Where the value actually is

Ultrahuman sells a **one-time $350–479 device with no recurring revenue**. Its economics are therefore driven by unit volume, repurchase/upgrade, returns, and ecosystem attach (CGM, Blood Vision, Home) — not by software ARPU.

Against that, a $3.99 subscription is rounding-error revenue. But retention is not:

| Lever | Value of a 1-point improvement (est.) |
|---|---|
| Jade Pro subscription revenue (5% conversion) | ~$1.0M/yr |
| +1pt ecosystem attach on 400k users | **~$1.4M+/yr** |
| +1pt reduction in returns/churn on $62M hardware | **~$620k/yr, recurring in cohort value** |
| Wear-compliance improvement | **Compounding** — see below |

**The compounding term is the real prize.** This audit measured 21% night coverage on a two-year user, and at that density *nothing* personal reached statistical significance — not sleep→recovery, not wake-consistency, not workout load. **Wear compliance is the binding constraint on whether personalised health AI works at all.** An assistant that increases wear makes every downstream feature better, including the paid clinical products. Metering that assistant does the opposite.

**So the current pricing trades a compounding retention asset for ~$1M of thin-margin subscription revenue.** That is the strategic error, and it is quantifiable.

## 7. The 2027 cliff

All PowerPlugs are free for 12 months with a Ring PRO, and post-year-one pricing is unpublished. The launch cohort (shipping ~June 2026) reprices around **mid-2027**. Whatever Jade's monetisation becomes, it lands inside that event — a simultaneous ask across the whole add-on catalogue, against a brand whose loudest promise is *"no subscription."* Stacking three PowerPlugs already exceeds the Oura membership the marketing attacks.

## 8. Recommendation

1. **Stop selling Jade. Bundle it, unmetered, with the hardware.** It is COGS on a $350 device, not a product line. Forgone revenue ~$1M/yr (est.); the retention and wear-compliance upside plausibly exceeds it, and the downside risk of negative-margin power users disappears.
2. **Move inference to Scenario C for the routine 80%.** Most traffic is bounded retrieval-and-summarise over the user's own summaries — a narrow, repeatable task, exactly where a fine-tuned small model runs 20–100× cheaper. Reserve the expensive multi-agent path for genuine Deep Research. This is the single highest-ROI engineering change available, and it converts the metering decision from necessity to choice.
3. **Charge for what a general LLM cannot substitute** — CGM, Blood Vision, real-time AFib intervention. The ladder exists; Jade is on the wrong rung. Chat over summaries is fully substitutable by an assistant the customer already pays ~$20/month for.
4. **Fix the false negatives before adding capability.** Jade denies HRV data the ring recorded 352,441 times and cannot see ~12 months of sleep. That is an ingestion defect suppressing the perceived value of the whole ecosystem — and it is cheaper to fix than any model upgrade.

## 9. What would change this verdict

| If true | Effect |
|---|---|
| Jade already runs a self-hosted small model | Paid tier becomes viable; metering becomes an unforced error |
| Conversion is >15%, not 5% | Subscription revenue becomes material; the margin question gets urgent |
| Jade measurably lifts ecosystem attach | Reclassifies as customer-acquisition spend, and the bundle case gets stronger |
| Post-2027 PowerPlug pricing is aggressive | Whole analysis shifts from AI economics to bundle-repricing risk |

**Highest-value disclosure to seek:** Jade's inference stack and per-query cost. Everything here turns on it — and it is exactly what the sub-processor list omits while a competitor (WHOOP, GPT-powered Coach) discloses.
