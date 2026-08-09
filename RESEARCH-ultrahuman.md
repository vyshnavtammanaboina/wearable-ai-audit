# Ultrahuman — terms, policies, pricing: research file
*Compiled 2026-08-07 from ultrahuman.com, the US privacy policy, Mozilla Foundation's independent review, and trade press. Every claim carries its source. Items marked ⚠️ are unverified and must be confirmed before publication.*

---

## 1. The pricing architecture — and the contradiction at its centre

**The brand's single loudest claim is "no subscription."** It is the entire positioning against Oura's $5.99/month membership, repeated across the trade press: *"subscription-free,"* *"lifetime access to all core health features,"* *"The Only Smart Ring With Zero Subscription Fees."*

**But a subscription stack exists underneath it:**

| Item | Price | Source |
|---|---|---|
| Ring PRO hardware | $299 (early bird) → $479 → $699 couples pack | Ultrahuman / trade press |
| **Respiratory Health PowerPlug** | **$3.99/mo or $39.99/yr** | Ultrahuman blog |
| **Les Mills PowerPlug** | **$12/mo or $100/yr** | Android Central |
| AFib Detection PowerPlug | "nominal fee" (~$4.99 reported) | trade press |
| Cardio Adaptability | free 1 yr with Ring PRO, then unpriced | trade press |
| Cycle & Ovulation Pro | free 1 yr with Ring PRO, then unpriced | trade press |
| **Jade Pro** | ⚠️ **$3.99/mo per the author's own app — NOT independently confirmed** | in-app screenshot |
| Jade (free tier) | metered: *"Credits renew in 2 hours"* | in-app screenshot |

**The finding:** *"no subscription"* is true only of **core** features. PowerPlugs are subscriptions, priced $3.99–$12/month, and — critically — **the entire catalogue is free for the first 12 months with a Ring PRO, with post-year-one pricing unpublished.**

Two consequences that matter for the case:

1. **A user stacking three PowerPlugs beats Oura's $5.99/month.** Respiratory ($3.99) + AFib (~$4.99) + Jade Pro (~$3.99) ≈ **$12.97/month** — more than double the competitor the "no subscription" message attacks. The differentiator inverts under normal use.
2. **The 12-month free window is a deferred-revenue cliff, not generosity.** Cohorts that bought a Ring PRO at launch (shipping ~June 2026) hit repricing around **mid-2027** — with prices still unpublished. That is the single most important unknown in Ultrahuman's consumer economics, and it lands right where this study's recommendation sits.

## 2. Privacy and data rights — the ownership claim and its carve-out

**The headline commitment** (privacy policy, verbatim): *"You own your data and control our usage of your data. We will never sell your data to third-parties."*

**The carve-out that follows:** the company may *"create de-identified and/or aggregated information,"* which it states is **"not personal information"** and therefore outside those protections. Such data may be used for *"research, internal analysis, analytics, and any other legally permissible purposes"* and — verbatim — **"shared with advertisers, research firms, and other partners."**

So: your identified data is not sold; your de-identified data may be shared with advertisers. Both statements are true simultaneously. This is standard industry construction, but it is the clause that decides the SLM question below.

**Machine-learning clause** (verbatim): *"Developing machine learning algorithms and tools to improve **targeting** of Products and Services… **with your consent**."*

Note precisely what this says and does not say:
- The stated ML purpose is **targeting** — marketing — not health inference.
- It is **consent-gated**.
- **There is no clause authorising training on user health data to improve health models.**

**⚠️ Direct answer to the parked SLM question:** a consented-data small language model is **not covered by the current policy.** Ultrahuman would need either a new consent flow or reliance on the de-identified/aggregated carve-out. This is a real, citable constraint on the "should they build an SLM" recommendation — not a hypothetical.

**Retention:** *"only for as long as necessary,"* with de-identified data kept *"for a longer period."* **No specific period is published.** This neither confirms nor rules out a retention window as the cause of Jade's ~12-month sleep blindness — worth stating as an open hypothesis, not a conclusion.

## 3. Where Jade's model actually runs — an unanswered question

The privacy policy publishes a sub-processor list: **Snowflake, MongoDB Atlas, MySQL, AWS** (storage); **InfluxDB, Dataiku, Mixpanel, Clevertap, Metabase** (analytics); Mailchimp, Gupshup, WhatsApp, Kustomer, Intercom, Razorpay, Stripe, PayU, Facebook, Google, Shopify, Typeform, Zapier.

**No LLM provider appears on it** — no OpenAI, Anthropic, Google Gemini, Mistral, or comparable.

Jade is an LLM product. Three possibilities: it runs self-hosted (plausibly on AWS, which is listed); it is served through a listed cloud provider's model service; or **the sub-processor list has not been updated since Jade launched (~March 2026).**

For a product handling intimate health data and marketed as *"the world's first real-time biointelligence AI,"* **the model provider is undisclosed.** That is a legitimate, evidence-backed transparency finding — and it is also the honest answer to "is it a wrapper?": *the disclosures do not permit anyone outside the company to say.*

## 4. Independent assessment — Mozilla Foundation, "Nothing Personal"

**Rating: 5/10.** Their specific findings:

- Some user data is sent to **Facebook** under an *"Ads and Social media"* justification. Mozilla notes health data is not necessarily included, but *"it's unclear exactly which parts of your profile are sent to Facebook, which is slightly worrying."*
- **Not a HIPAA-covered entity.** Ultrahuman says it *"strives"* to comply; it carries no legal obligation under that framework. For a company selling CGM and blood biomarker products, this gap is material.
- **2024 patent litigation:** allegedly submitted *"doctored"* manufacturing-facility footage with fake branding. Mozilla: *"not a good look for a company that is asking you to trust it with intimate details about your personal health."*
- **Security:** researchers found the ring can sync to another app instance over Bluetooth **without docking-station authentication**, a potential unauthorised-access path.
- International transfer is **mandatory** — consent or you cannot use the platform.

## 5. What this adds to the case study

| Existing finding | What the research does to it |
|---|---|
| "$3.99 is a feature priced as a product" | **Strengthened and generalised.** $3.99 is Ultrahuman's standard PowerPlug price point; Jade is being slotted into an existing subscription ladder, not priced on its own merit |
| "The price starves the data supply" | **Now systemic.** The whole PowerPlug catalogue meters engagement, and post-year-one pricing is unpublished |
| "Charge for what can't be pasted" | **Sharpened.** Their genuinely un-pasteable assets (CGM, Blood Vision, real-time AFib) are *already* PowerPlugs — the ladder exists, Jade is simply on the wrong rung |
| SLM build-vs-buy (parked) | **Unparked as a constraint:** current policy authorises ML for *targeting*, with consent. Health-model training on user data is not covered |
| Jade's ~1-year sleep blindness | Retention policy is **unspecified** — remains a hypothesis, not an explanation |

**The strategic headline this unlocks:** Ultrahuman's differentiator is *"no subscription."* It is building a subscription business behind that promise, has not published what it will cost after month twelve, and has placed its AI on that ladder at the exact price point where a $20 general assistant already outperforms it. **The positioning and the monetisation are pointed in opposite directions**, and the first big cohort finds out in mid-2027.

---

## Verification queue before publication

- [ ] ⚠️ **Confirm Jade Pro is $3.99/mo** — screenshot the in-app purchase screen. $3.99 is also the Respiratory Health price; the two must not be conflated
- [ ] ⚠️ Confirm whether Jade Pro is a PowerPlug or a separate tier
- [ ] Check the Ring **AIR** (the author's device) PowerPlug entitlements — the free-12-month offer is documented for Ring **PRO**
- [ ] Re-read the sub-processor list at publication time in case an LLM provider is added
- [ ] Terms of Service proper (distinct from privacy policy) — not yet retrieved

## Sources

[Ultrahuman US](https://www.ultrahuman.com/us/) · [Privacy Policy](https://www.ultrahuman.com/us/privacyPolicy/) · [Mozilla — Nothing Personal review](https://www.mozillafoundation.org/en/nothing-personal/ultrahuman-ring-privacy-review/) · [Respiratory Health PowerPlug pricing](https://blog.ultrahuman.com/blog/introducing-respiratory-health-powerplug/) · [Les Mills PowerPlug — Android Central](https://www.androidcentral.com/wearables/ultrahuman/ultrahuman-les-mills-partner-for-a-powerplug-that-pushes-you-if-you-can-take-it) · [Ring Pro pricing/subscription-free — Tech Times](https://www.techtimes.com/articles/318765/20260620/ultrahuman-ring-pro-ships-today-subscription-free-ring-targets-oura-15-day-battery.htm) · [PowerPlugs free-year caveat — the5krunner](https://the5krunner.com/2026/05/06/ultrahuman-ring-pro/) · [Ring price overview — TrackerVS](https://trackervs.com/pricing/ultrahuman-ring-price/)
