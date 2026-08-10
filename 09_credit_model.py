"""
09_credit_model.py - trained credit-usage model. PLACEHOLDER, ARMED BUT UNFED.

STATUS: no input data exists yet. This stage will not produce a number until
real usage data is supplied. That is deliberate and it is the whole point of
the file.

WHY IT IS EMPTY
---------------
Stage 07 answers "is unlimited viable?" by simulation, because no wearable
vendor publishes per-user query logs. A *trained* model of credit consumption
is the strictly better instrument - it would replace assumed priors with
fitted ones - and it is impossible today for exactly one reason: there is
nothing to fit.

So rather than fake it, this file specifies precisely what would be needed,
implements the full modelling and validation path against that specification,
and refuses to run without it. If usage data ever arrives - a contributor with
their own export, a vendor publishing aggregates, a research partnership, a
leak of nothing more sensitive than distributions - this stage becomes live
with no new code.

Run `python 09_credit_model.py --selftest` to verify the code path on
synthetic data. That mode prints results marked as a PIPELINE CHECK and
refuses to state any business conclusion, because synthetic inputs can only
tell you the code runs, never what is true.

WHAT WOULD UNLOCK IT
--------------------
Place a CSV at data/usage.csv with one row per user-month:

    user_id            str    stable pseudonymous id, no PII
    month              str    YYYY-MM
    tier               str    "free" or "paid"
    questions          int    questions asked that month
    credits_consumed   float  provider-side credit or token units, if known
    tenure_months      int    months since device activation
    wear_frac_month    float  0-1, share of days the device was worn
    converted_next     int    0/1, did a free user convert the following month
                              (blank for paid rows)

Aggregated or differentially-private versions work: the three heads below need
distributions and conditional means, not individuals. A per-decile summary
would answer most of it.

WHAT IT WOULD ANSWER, IN ORDER OF VALUE
---------------------------------------
  HEAD 1  Usage regression   - questions ~ tenure + wear + tier
                               replaces the assumed lognormal in stage 07 with
                               a fitted conditional distribution
  HEAD 2  Conversion model   - P(convert) ~ usage
                               the adverse-selection elasticity is ASSUMED at
                               0.85 in stage 07; this measures it
  HEAD 3  Tail / cap policy  - fitted quantiles drive the credit-cap curve and
                               the break-even envelope

Until then, stage 07's conclusion stands on its robustness across three
distribution families, not on any single prior.
"""

import csv
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "usage.csv"

REQUIRED = ["user_id", "month", "tier", "questions",
            "tenure_months", "wear_frac_month"]
OPTIONAL = ["credits_consumed", "converted_next"]


# --------------------------------------------------------------- guard
def explain_and_exit():
    print("=" * 76)
    print("09_credit_model.py - NO DATA, NOTHING COMPUTED")
    print("=" * 76)
    print(f"\nExpected input: {DATA.relative_to(HERE)}  (not found)")
    print("\nThis stage is a placeholder held open on purpose. A trained model of")
    print("per-user credit consumption would be strictly better than the simulation")
    print("in 07_usage_sim.py - it would replace assumed priors with fitted ones.")
    print("No wearable vendor publishes the per-user query logs it needs, so the")
    print("honest state of this file is armed and empty rather than confidently wrong.")
    print("\nRequired columns, one row per user-month:")
    for c in REQUIRED:
        print(f"    {c}")
    print("  optional:")
    for c in OPTIONAL:
        print(f"    {c}")
    print("\nAggregated or differentially-private data is fine. The three model heads")
    print("need distributions and conditional means, not individuals; a per-decile")
    print("summary would answer most of it.")
    print("\n  python 09_credit_model.py --selftest   verify the code path on synthetic")
    print("                                         input (prints no business result)")
    print("\nIf you have data of this shape and are willing to share it, open an issue.")
    print("Contribution notes: CONTRIBUTING.md")
    sys.exit(0)


# --------------------------------------------------------------- io
def load(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (rd.fieldnames or [])]
        if missing:
            sys.exit(f"ERROR: {path} is missing required columns: {', '.join(missing)}")
        for r in rd:
            try:
                rows.append({
                    "user_id": r["user_id"],
                    "month": r["month"],
                    "tier": r["tier"].strip().lower(),
                    "questions": float(r["questions"]),
                    "tenure_months": float(r["tenure_months"]),
                    "wear": float(r["wear_frac_month"]),
                    "converted_next": (int(r["converted_next"])
                                       if r.get("converted_next") not in (None, "") else None),
                })
            except (ValueError, KeyError) as e:
                sys.exit(f"ERROR: bad row in {path}: {e}")
    if not rows:
        sys.exit(f"ERROR: {path} has no rows.")
    return rows


def synth(n_users=4000, months=12, seed=7):
    """Synthetic input for a PIPELINE CHECK ONLY. Deliberately generated from
    a different process than stage 07 assumes, so that a passing self-test
    cannot be mistaken for corroboration of stage 07's priors."""
    random.seed(seed)
    rows = []
    for u in range(n_users):
        base = math.exp(random.gauss(math.log(6), 1.1))
        wear = min(1.0, max(0.05, random.betavariate(2, 3)))
        paid = random.random() < min(0.9, 0.02 + 0.06 * math.log1p(base))
        for m in range(months):
            ten = m + random.randint(0, 18)
            q = max(0.0, base * (0.6 + 0.8 * wear) * math.exp(-0.02 * ten)
                    * random.lognormvariate(0, 0.4))
            rows.append({
                "user_id": f"u{u}", "month": f"2026-{m+1:02d}",
                "tier": "paid" if paid else "free",
                "questions": q, "tenure_months": ten, "wear": wear,
                "converted_next": (0 if paid else int(random.random() < 0.01 * (1 + base / 6))),
            })
    return rows


# --------------------------------------------------------------- model heads
def ols(X, y, l2=1e-6):
    """Ridge via Gaussian elimination on the normal equations."""
    p = len(X[0])
    A = [[sum(X[i][a] * X[i][b] for i in range(len(X))) + (l2 if a == b else 0.0)
          for b in range(p)] for a in range(p)]
    b = [sum(X[i][a] * y[i] for i in range(len(X))) for a in range(p)]
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(A[r][c]))
        if abs(A[piv][c]) < 1e-12:
            continue
        A[c], A[piv] = A[piv], A[c]
        b[c], b[piv] = b[piv], b[c]
        for r in range(p):
            if r == c:
                continue
            f = A[r][c] / A[c][c]
            for k in range(c, p):
                A[r][k] -= f * A[c][k]
            b[r] -= f * b[c]
    return [b[i] / A[i][i] if abs(A[i][i]) > 1e-12 else 0.0 for i in range(p)]


def logistic(X, y, iters=300, lr=0.1, l2=1e-3):
    n, p = len(X), len(X[0])
    w = [0.0] * p
    for _ in range(iters):
        g = [0.0] * p
        for xi, yi in zip(X, y):
            z = sum(a * b for a, b in zip(w, xi))
            pr = 1 / (1 + math.exp(-max(-35, min(35, z))))
            for j in range(p):
                g[j] += (pr - yi) * xi[j]
        for j in range(p):
            w[j] -= lr * (g[j] / n + (l2 * w[j] if j else 0))
    return w


def quantile(v, q):
    s = sorted(v)
    if not s:
        return 0.0
    return s[min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))]


def run(rows, selftest):
    months = sorted({r["month"] for r in rows})
    cut = months[int(len(months) * 0.7)]
    tr = [r for r in rows if r["month"] < cut]
    te = [r for r in rows if r["month"] >= cut]
    print(f"  rows {len(rows):,}   users {len({r['user_id'] for r in rows}):,}   "
          f"months {len(months)}   train<{cut} ({len(tr):,})  test>={cut} ({len(te):,})")

    # HEAD 1 - usage regression on log questions
    def feats(r):
        return [1.0, math.log1p(r["tenure_months"]), r["wear"], 1.0 if r["tier"] == "paid" else 0.0]
    Xtr = [feats(r) for r in tr]
    ytr = [math.log1p(r["questions"]) for r in tr]
    w1 = ols(Xtr, ytr)
    pred = [sum(a * b for a, b in zip(w1, feats(r))) for r in te]
    act = [math.log1p(r["questions"]) for r in te]
    mu = sum(act) / len(act)
    ss_res = sum((a - p) ** 2 for a, p in zip(act, pred))
    ss_tot = sum((a - mu) ** 2 for a in act)
    mae = sum(abs(a - p) for a, p in zip(act, pred)) / len(act)
    print("\n  HEAD 1  usage regression   log1p(questions) ~ log1p(tenure) + wear + paid")
    for nm, wi in zip(["intercept", "log_tenure", "wear", "paid"], w1):
        print(f"            {nm:<12}{wi:>9.4f}")
    print(f"            out-of-sample R2 {1 - ss_res/ss_tot if ss_tot else float('nan'):.3f}   MAE(log) {mae:.3f}")

    # HEAD 2 - conversion elasticity
    freetr = [r for r in tr if r["tier"] == "free" and r["converted_next"] is not None]
    freete = [r for r in te if r["tier"] == "free" and r["converted_next"] is not None]
    if len(freetr) > 50 and len({r["converted_next"] for r in freetr}) > 1:
        med = quantile([r["questions"] for r in freetr], 0.5) or 1.0
        f2 = lambda r: [1.0, math.log1p(r["questions"] / med), r["wear"]]
        w2 = logistic([f2(r) for r in freetr], [r["converted_next"] for r in freetr])
        print("\n  HEAD 2  conversion         P(convert next month) ~ relative usage + wear")
        for nm, wi in zip(["intercept", "log_rel_usage", "wear"], w2):
            print(f"            {nm:<14}{wi:>9.4f}")
        print(f"            adverse-selection elasticity (measured): {w2[1]:.3f}")
        print("            stage 07 ASSUMES 0.85 - this replaces the assumption")
        if freete:
            base_rate = sum(r["converted_next"] for r in freete) / len(freete)
            print(f"            test-set conversion base rate {base_rate:.2%}")
    else:
        print("\n  HEAD 2  conversion         skipped: needs free-tier rows with converted_next")

    # HEAD 3 - tail and cap policy
    paid = [r["questions"] for r in rows if r["tier"] == "paid"]
    if paid:
        print("\n  HEAD 3  tail / cap policy  fitted quantiles for the cap curve")
        for q in (0.5, 0.9, 0.99):
            print(f"            p{int(q*100):<3} {quantile(paid, q):>10.1f} questions/month")
        print(f"            top 1% share of all paid questions: "
              f"{sum(x for x in paid if x >= quantile(paid, 0.99))/sum(paid):.1%}")
        print("            feed these into 07_usage_sim.py in place of the assumed prior")

    print("\n" + "=" * 76)
    if selftest:
        print("PIPELINE CHECK PASSED - AND THESE NUMBERS MEAN NOTHING.")
        print("Input was synthetic, generated here, from a process chosen to differ from")
        print("stage 07's assumptions. This run proves the code executes end to end. It")
        print("is not evidence about Jade, Ultrahuman, or any real user. Do not quote it,")
        print("do not put it in a deck, do not treat agreement with stage 07 as support.")
    else:
        print("Fitted on real data. Now re-run 07_usage_sim.py with these parameters in")
        print("place of its assumed priors, and update ECONOMICS.md s8b - the simulation's")
        print("robustness argument can be retired in favour of measurement.")
    print("=" * 76)


def main():
    selftest = "--selftest" in sys.argv
    if selftest:
        print("=" * 76)
        print("09_credit_model.py - SELF-TEST ON SYNTHETIC DATA (not a result)")
        print("=" * 76)
        run(synth(), selftest=True)
        return
    if not DATA.exists():
        explain_and_exit()
    print("=" * 76)
    print(f"09_credit_model.py - fitting on {DATA}")
    print("=" * 76)
    run(load(DATA), selftest=False)


if __name__ == "__main__":
    main()
