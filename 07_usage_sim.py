"""
07_usage_sim.py - Monte Carlo over per-user query volume.

WHAT THIS IS, STATED FIRST
--------------------------
This is a SIMULATION, not a trained model. No Jade query logs, credit-consumption
records, or user-level telemetry are public, so there is nothing to fit. Anything
calling itself a "forecast" of Jade's per-user credit usage would be fit to
invented data and then presented as prediction: the exact failure this study
documents in Jade, committed by the instrument that measures it.

What is defensible without their data:
  1. Per-user engagement in freemium products is heavy-tailed. That is a
     structural regularity across consumer software, not a claim about
     Ultrahuman. We therefore assume a heavy-tailed distribution and test the
     conclusion across three different families rather than trusting one.
  2. Conversion to a paid tier RISES with usage. Heavy users are the ones who
     hit the paywall, so subscribers are a right-shifted sample of the base.
     This adverse selection is the entire mechanism behind the margin problem,
     and it is modelled explicitly here.
  3. Flat-rate pricing over an unbounded variable cost is decided by the TAIL,
     not the mean. Monte Carlo is the right instrument for a tail question.

Every parameter is declared in ASSUMPTIONS below and is meant to be varied.
The output is a distribution of outcomes and a break-even threshold, not a
point forecast. Read the sensitivity block before quoting any single number.

Outputs: outputs/fig4_usage_tail.png, outputs/sim_summary.csv
"""

import csv
import math
import random
from pathlib import Path

OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

# ----------------------------------------------------------------- ASSUMPTIONS
SEED = 20260809
N_USERS = 400_000          # cumulative active ring base (est., see ECONOMICS.md s1)
MEDIAN_Q = 8               # median questions/user/month among engaged users
SIGMA = 1.30               # lognormal shape. Higher = heavier tail
BASE_CONV = 0.05           # overall paid conversion (est.)
CONV_ELASTICITY = 0.85     # how strongly usage drives conversion. 0 = no adverse
                           # selection, 1 = strongly usage-driven
PRICE = 3.99               # $/month

COST_ON_DEMAND = 0.35      # $/query, frontier-class multi-agent (10-15 calls)
DIGEST_COST = 0.35         # $/digest, one synthesis pass over the week
DIGESTS_PER_MONTH = 52 / 12
COST_FOLLOWUP = 0.015      # $/question, retrieval over the stored digest

random.seed(SEED)


# ----------------------------------------------------------------- generators
def draw_lognormal(n, median, sigma):
    mu = math.log(median)
    return [math.exp(random.gauss(mu, sigma)) for _ in range(n)]


def draw_pareto(n, median, alpha=1.6):
    xm = median / (2 ** (1 / alpha))
    return [xm / (random.random() ** (1 / alpha)) for _ in range(n)]


def draw_negbinom_like(n, median, disp=2.2):
    """Gamma-Poisson mixture: Poisson rate itself gamma-distributed."""
    shape = 1.0 / disp
    scale = median / shape
    out = []
    for _ in range(n):
        lam = random.gammavariate(shape, scale)
        out.append(lam)
    return out


FAMILIES = {
    "lognormal": lambda n: draw_lognormal(n, MEDIAN_Q, SIGMA),
    "pareto": lambda n: draw_pareto(n, MEDIAN_Q),
    "gamma-poisson": lambda n: draw_negbinom_like(n, MEDIAN_Q),
}


def pct(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    k = min(len(sorted_vals) - 1, max(0, int(round(p / 100 * (len(sorted_vals) - 1)))))
    return sorted_vals[k]


def simulate(family_name, n_users=N_USERS):
    """Draw a population, apply usage-driven conversion, cost both architectures."""
    q = FAMILIES[family_name](n_users)
    med = sorted(q)[len(q) // 2]

    # Adverse selection: P(convert) scales with usage relative to the median,
    # then is renormalised so the population conversion equals BASE_CONV.
    weights = [(x / med) ** CONV_ELASTICITY for x in q]
    mean_w = sum(weights) / len(weights)
    scale = BASE_CONV / mean_w

    subs = []
    frees = []
    for x, w in zip(q, weights):
        if random.random() < min(1.0, w * scale):
            subs.append(x)
        else:
            frees.append(x)

    def cost_od(x):
        return x * COST_ON_DEMAND

    def cost_pc(x):
        return DIGESTS_PER_MONTH * DIGEST_COST + x * COST_FOLLOWUP

    od = sorted(cost_od(x) for x in subs)
    pc = sorted(cost_pc(x) for x in subs)
    subs_sorted = sorted(subs)

    n_sub = len(subs) or 1
    total_od = sum(od)
    top1_cut = pct(od, 99)
    top1_cost = sum(c for c in od if c >= top1_cut)

    return {
        "family": family_name,
        "subs": len(subs),
        "free": len(frees),
        "conv_pct": len(subs) / n_users,
        "q_median_sub": pct(subs_sorted, 50),
        "q_p90_sub": pct(subs_sorted, 90),
        "q_p99_sub": pct(subs_sorted, 99),
        "q_median_all": med,
        "od_mean": total_od / n_sub,
        "od_p50": pct(od, 50),
        "od_p99": pct(od, 99),
        "od_loss_share": sum(1 for c in od if c > PRICE) / n_sub,
        "od_top1_costshare": top1_cost / total_od if total_od else 0,
        "od_margin_pct": (PRICE - total_od / n_sub) / PRICE,
        "pc_mean": sum(pc) / n_sub,
        "pc_p99": pct(pc, 99),
        "pc_loss_share": sum(1 for c in pc if c > PRICE) / n_sub,
        "pc_margin_pct": (PRICE - sum(pc) / n_sub) / PRICE,
        "_sub_q": subs_sorted,
    }


def breakeven_queries():
    """Questions/month at which a $3.99 subscriber stops being profitable."""
    od = PRICE / COST_ON_DEMAND
    pc = (PRICE - DIGESTS_PER_MONTH * DIGEST_COST) / COST_FOLLOWUP
    return od, pc


def credit_cap_curve(sub_q, caps):
    """For each monthly cap: share of users unaffected, share of questions
    refused, and resulting mean COGS under the on-demand architecture."""
    rows = []
    n = len(sub_q) or 1
    total_q = sum(sub_q) or 1
    for cap in caps:
        served = [min(x, cap) for x in sub_q]
        rows.append({
            "cap": cap,
            "users_unaffected": sum(1 for x in sub_q if x <= cap) / n,
            "questions_refused": 1 - sum(served) / total_q,
            "mean_cogs_od": sum(served) * COST_ON_DEMAND / n,
            "margin_od": (PRICE - sum(served) * COST_ON_DEMAND / n) / PRICE,
        })
    return rows


# ----------------------------------------------------------------- run
def main():
    print("=" * 74)
    print("MONTE CARLO: per-user query volume and flat-rate viability")
    print("SIMULATION under stated priors - not a trained model, no Jade data exists")
    print("=" * 74)

    be_od, be_pc = breakeven_queries()
    print(f"\nBreak-even questions/month at ${PRICE:.2f}:")
    print(f"  On-demand  : {be_od:6.1f} q/mo  (at ${COST_ON_DEMAND:.3f}/query)")
    print(f"  Precompute : {be_pc:6.1f} q/mo  (digest ${DIGESTS_PER_MONTH*DIGEST_COST:.2f} fixed"
          f" + ${COST_FOLLOWUP:.3f}/query)")

    results = []
    for fam in FAMILIES:
        r = simulate(fam)
        results.append(r)
        print(f"\n--- {fam} " + "-" * (66 - len(fam)))
        print(f"  subscribers {r['subs']:,} ({r['conv_pct']:.1%} of base)   "
              f"median q/mo: all users {r['q_median_all']:.1f} -> subscribers {r['q_median_sub']:.1f}"
              f"  (adverse selection)")
        print(f"  subscriber usage    p50 {r['q_median_sub']:6.1f}   p90 {r['q_p90_sub']:7.1f}"
              f"   p99 {r['q_p99_sub']:8.1f}  questions/mo")
        print(f"  ON-DEMAND   mean COGS ${r['od_mean']:7.2f}   p99 ${r['od_p99']:8.2f}"
              f"   margin {r['od_margin_pct']:8.1%}")
        print(f"              {r['od_loss_share']:.1%} of subscribers are gross-margin NEGATIVE;"
              f" top 1% burn {r['od_top1_costshare']:.1%} of all inference cost")
        print(f"  PRECOMPUTE  mean COGS ${r['pc_mean']:7.2f}   p99 ${r['pc_p99']:8.2f}"
              f"   margin {r['pc_margin_pct']:8.1%}")
        print(f"              {r['pc_loss_share']:.1%} of subscribers are gross-margin negative")

    # credit cap analysis on the lognormal base case
    base = results[0]
    print("\n" + "=" * 74)
    print("CREDIT CAP (on-demand architecture): what a cap buys and what it costs")
    print("=" * 74)
    print(f"  {'cap q/mo':>9} {'users unaffected':>18} {'questions refused':>19} {'margin':>9}")
    caps = [15, 30, 60, 120, 240]
    cap_rows = credit_cap_curve(base["_sub_q"], caps)
    for row in cap_rows:
        print(f"  {row['cap']:>9} {row['users_unaffected']:>17.1%} "
              f"{row['questions_refused']:>18.1%} {row['margin_od']:>9.1%}")
    print("\n  No cap makes on-demand comfortable: the cap that protects margin refuses")
    print("  questions from the most engaged users, which is the wear-compliance input")
    print("  the product depends on. Precompute removes the trade-off entirely.")

    # write csv
    keys = [k for k in results[0] if not k.startswith("_")]
    with open(OUT / "sim_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in results:
            w.writerow({k: r[k] for k in keys})

    print(f"\n  wrote {OUT/'sim_summary.csv'}")
    chart(results, cap_rows)


def chart(results, cap_rows):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib unavailable, skipping chart)")
        return

    base = results[0]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))

    # 1. usage tail
    ax = axes[0]
    q = [x for x in base["_sub_q"] if x <= 200]
    ax.hist(q, bins=60, color="#1E2761", alpha=0.85)
    ax.axvline(base["q_median_sub"], color="#1E8449", lw=2,
               label=f"median {base['q_median_sub']:.0f} q/mo")
    ax.axvline(PRICE / COST_ON_DEMAND, color="#C0392B", lw=2, ls="--",
               label=f"break-even {PRICE/COST_ON_DEMAND:.0f} q/mo")
    ax.set_title("Subscriber query volume (lognormal)\ntruncated at 200 for display", fontsize=10)
    ax.set_xlabel("questions per month")
    ax.set_ylabel("subscribers")
    ax.legend(fontsize=8)

    # 2. cost per user, both architectures
    ax = axes[1]
    od = [min(x * COST_ON_DEMAND, 80) for x in base["_sub_q"]]
    pc = [DIGESTS_PER_MONTH * DIGEST_COST + x * COST_FOLLOWUP for x in base["_sub_q"]]
    pc = [min(x, 80) for x in pc]
    ax.hist(od, bins=60, color="#C0392B", alpha=0.7, label="on-demand")
    ax.hist(pc, bins=60, color="#1E8449", alpha=0.8, label="precompute")
    ax.axvline(PRICE, color="#333333", lw=2, ls="--", label=f"price ${PRICE}")
    ax.set_yscale("log")
    ax.set_title("Monthly COGS per subscriber\n(log count, clipped at $80)", fontsize=10)
    ax.set_xlabel("$ per subscriber per month")
    ax.legend(fontsize=8)

    # 3. cap trade-off
    ax = axes[2]
    caps = [r["cap"] for r in cap_rows]
    ax.plot(caps, [r["users_unaffected"] * 100 for r in cap_rows], "o-",
            color="#1E2761", label="users unaffected %")
    ax.plot(caps, [r["questions_refused"] * 100 for r in cap_rows], "s-",
            color="#C0392B", label="questions refused %")
    ax.plot(caps, [max(r["margin_od"], -1) * 100 for r in cap_rows], "^-",
            color="#5A5A6E", label="on-demand margin %")
    ax.axhline(0, color="#999999", lw=0.8)
    ax.set_title("The credit-cap trade-off\n(on-demand only)", fontsize=10)
    ax.set_xlabel("monthly credit cap (questions)")
    ax.set_ylabel("%")
    ax.legend(fontsize=8)

    for a in axes:
        a.spines["top"].set_visible(False)
        a.spines["right"].set_visible(False)

    fig.suptitle("Simulated per-user usage and flat-rate viability - priors stated in 07_usage_sim.py, not fitted to Jade data",
                 fontsize=9, color="#5A5A6E", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_usage_tail.png", dpi=140, bbox_inches="tight")
    print(f"  wrote {OUT/'fig4_usage_tail.png'}")


if __name__ == "__main__":
    main()
