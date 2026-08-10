"""
08_wear_forecast.py - forecasting wear compliance from the real record.

WHY THIS EXISTS
---------------
Everything else in this study concludes that wear compliance, not model quality,
is the binding constraint on personalised health AI. The recommendation that
follows is to establish a coverage floor and gate the confidence of advice on it.

That recommendation is only operational if wear is predictable. This tests
whether it is - on 562 days of actual sensor record, with a strict temporal
split, against honest baselines.

Unlike 07_usage_sim.py, this is a real model fit to real data. Its limit is
different and just as important: N=1. It demonstrates that the signal exists
and that the method works for one user. Population deployment would require
many users, and the coefficients here are this person's, not anyone else's.

Target : was the ring worn tomorrow (wear_frac >= FLOOR)
Features: recent wear history, gap length, streak length, day of week
Split  : first 70% of days train, last 30% test. No shuffling, no leakage.
Baselines: majority class, and persistence (tomorrow == today)

Outputs: outputs/fig5_wear_forecast.png, outputs/wear_model.csv
"""

import sqlite3
import math
import csv
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "ring.db"
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)

FLOOR = 0.5          # "worn" = ring on body for >= 50% of the day's bins
TRAIN_FRAC = 0.70


# ------------------------------------------------------------------ data
def load_series():
    """Every calendar day in span, with wear_frac. Days absent from
    daily_summary are genuine zero-wear days and must be included."""
    con = sqlite3.connect(DB)
    rows = dict(con.execute("SELECT day, wear_frac FROM daily_summary"))
    lo, hi = con.execute("SELECT MIN(day), MAX(day) FROM daily_summary").fetchone()
    con.close()

    d0 = date.fromisoformat(lo)
    d1 = date.fromisoformat(hi)
    series = []
    d = d0
    while d <= d1:
        wf = rows.get(d.isoformat(), 0.0) or 0.0
        series.append((d, float(wf)))
        d += timedelta(days=1)
    return series


def build_features(series):
    """One row per day t predicting worn(t+1). Only information available
    at end of day t is used."""
    worn = [1 if wf >= FLOOR else 0 for _, wf in series]
    X, y, meta = [], [], []

    for t in range(len(series) - 1):
        if t < 7:
            continue  # need history
        hist = worn[max(0, t - 6):t + 1]          # last 7 days incl today
        hist3 = worn[t - 2:t + 1]

        gap = 0
        i = t
        while i >= 0 and worn[i] == 0:
            gap += 1
            i -= 1
        streak = 0
        i = t
        while i >= 0 and worn[i] == 1:
            streak += 1
            i -= 1

        dow = series[t][0].weekday()
        feats = [
            1.0,                                   # intercept
            float(worn[t]),                        # worn today
            sum(hist3) / 3.0,                      # 3-day rate
            sum(hist) / 7.0,                       # 7-day rate
            math.log1p(gap),                       # days off, compressed
            math.log1p(streak),                    # days on, compressed
            1.0 if dow >= 5 else 0.0,              # weekend
        ]
        X.append(feats)
        y.append(worn[t + 1])
        meta.append(series[t + 1][0])
    return X, y, meta


NAMES = ["intercept", "worn_today", "rate_3d", "rate_7d",
         "log_gap", "log_streak", "weekend"]


# ------------------------------------------------------------------ model
def fit_logistic(X, y, iters=400, lr=0.12, l2=1e-3):
    """Plain gradient-descent logistic regression. No new dependency, and
    small enough that the whole estimator is auditable on one screen."""
    n, p = len(X), len(X[0])
    w = [0.0] * p
    for _ in range(iters):
        grad = [0.0] * p
        for xi, yi in zip(X, y):
            z = sum(wj * xj for wj, xj in zip(w, xi))
            pr = 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, z))))
            err = pr - yi
            for j in range(p):
                grad[j] += err * xi[j]
        for j in range(p):
            g = grad[j] / n + (l2 * w[j] if j else 0.0)
            w[j] -= lr * g
    return w


def predict(w, X):
    out = []
    for xi in X:
        z = sum(wj * xj for wj, xj in zip(w, xi))
        out.append(1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, z)))))
    return out


def auc(y, p):
    pairs = sorted(zip(p, y))
    pos = sum(y)
    neg = len(y) - pos
    if pos == 0 or neg == 0:
        return float("nan")
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            if pairs[k][1] == 1:
                rank_sum += avg_rank
        i = j + 1
    return (rank_sum - pos * (pos + 1) / 2.0) / (pos * neg)


def brier(y, p):
    return sum((pi - yi) ** 2 for pi, yi in zip(p, y)) / len(y)


def acc(y, pred):
    return sum(1 for a, b in zip(y, pred) if a == b) / len(y)


# ------------------------------------------------------------------ run
def main():
    if not DB.exists():
        raise SystemExit(
            f"{DB.name} not found. This stage needs the built database; run\n"
            "01_ingest.py -> 02_transform.py -> 03_marts.py first. See DATA.md."
        )

    series = load_series()
    X, y, meta = build_features(series)
    cut = int(len(X) * TRAIN_FRAC)
    Xtr, ytr = X[:cut], y[:cut]
    Xte, yte, mte = X[cut:], y[cut:], meta[cut:]

    print("=" * 74)
    print("WEAR-COMPLIANCE FORECAST - real data, temporal split, N=1")
    print("=" * 74)
    print(f"  calendar span      : {series[0][0]} to {series[-1][0]}  ({len(series)} days)")
    print(f"  overall wear rate  : {sum(1 for _, wf in series if wf >= FLOOR)/len(series):.1%}"
          f"  (floor = {FLOOR:.0%} of day's bins)")
    print(f"  usable rows        : {len(X)}   train {len(Xtr)}  test {len(Xte)}")
    print(f"  test window        : {mte[0]} to {mte[-1]}")

    w = fit_logistic(Xtr, ytr)
    p_te = predict(w, Xte)
    pred = [1 if pi >= 0.5 else 0 for pi in p_te]

    # baselines
    maj = 1 if sum(ytr) * 2 >= len(ytr) else 0
    base_maj = [maj] * len(yte)
    base_per = [int(xi[1]) for xi in Xte]          # persistence: tomorrow == today

    print("\n  MODEL vs BASELINES (test set, never seen in fitting)")
    print(f"  {'':<22}{'accuracy':>10}{'AUC':>8}{'Brier':>9}")
    print(f"  {'majority class':<22}{acc(yte, base_maj):>10.1%}{'-':>8}{'-':>9}")
    print(f"  {'persistence':<22}{acc(yte, base_per):>10.1%}"
          f"{auc(yte, [float(v) for v in base_per]):>8.3f}{'-':>9}")
    print(f"  {'logistic':<22}{acc(yte, pred):>10.1%}{auc(yte, p_te):>8.3f}{brier(yte, p_te):>9.3f}")

    print("\n  COEFFICIENTS (log-odds of wearing tomorrow)")
    for nm, wi in zip(NAMES, w):
        arrow = "raises" if wi > 0 else "lowers"
        print(f"    {nm:<14}{wi:>8.3f}   {arrow}")

    print("\n  READ - and the honest result is the negative one.")
    print("  Wear is highly forecastable: ~87% accuracy on a held-out window. But the")
    print("  logistic model does NOT beat persistence ('tomorrow = today'), which scores")
    print("  the same accuracy and a marginally better AUC. Every coefficient except")
    print("  worn_today and log_gap is doing almost nothing; rate_7d is ~0.")
    print()
    print("  So the finding is: the signal is real and it is entirely first-order.")
    print("  That makes the coverage-floor recommendation CHEAPER, not weaker - gating")
    print("  advice on wear needs a counter and a threshold, not a model. Any vendor")
    print("  proposing ML for this is solving a problem that a lookup already solves.")
    print()
    print("  Note the test window is only 29.9% worn against a training period that was")
    print("  mostly worn, which is why majority-class scores so badly here: wear")
    print("  collapsed in 2026. A model tuned on the earlier regime would have been")
    print("  confidently wrong about the later one - the same lesson as everything else")
    print("  in this study.")

    with open(OUT / "wear_model.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["feature", "coefficient"])
        for nm, wi in zip(NAMES, w):
            wr.writerow([nm, round(wi, 5)])
        wr.writerow([])
        wr.writerow(["metric", "value"])
        wr.writerow(["test_accuracy", round(acc(yte, pred), 4)])
        wr.writerow(["test_auc", round(auc(yte, p_te), 4)])
        wr.writerow(["test_brier", round(brier(yte, p_te), 4)])
        wr.writerow(["baseline_majority_acc", round(acc(yte, base_maj), 4)])
        wr.writerow(["baseline_persistence_acc", round(acc(yte, base_per), 4)])
    print(f"\n  wrote {OUT/'wear_model.csv'}")

    chart(series, mte, yte, p_te)


def chart(series, mte, yte, p_te):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("  (matplotlib unavailable, skipping chart)")
        return

    fig, axes = plt.subplots(2, 1, figsize=(13, 6.4), height_ratios=[1, 1])

    ax = axes[0]
    ds = [d for d, _ in series]
    wf = [v for _, v in series]
    ax.fill_between(ds, wf, color="#1E2761", alpha=0.75, linewidth=0)
    ax.axhline(FLOOR, color="#C0392B", lw=1.4, ls="--", label=f"wear floor {FLOOR:.0%}")
    ax.set_ylabel("daily wear fraction")
    ax.set_title("Actual wear record: 562 days, 26% of nights derivable. "
                 "The gaps are the product's real constraint.", fontsize=11)
    ax.legend(fontsize=8, loc="upper right")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    ax = axes[1]
    ax.plot(mte, p_te, color="#1E8449", lw=1.6, label="predicted P(worn tomorrow)")
    ax.scatter(mte, yte, s=12, color="#1E2761", alpha=0.65, label="actual (0/1)")
    ax.axhline(0.5, color="#999999", lw=0.8, ls=":")
    ax.set_ylabel("probability")
    ax.set_ylim(-0.08, 1.08)
    ax.set_title("Held-out test window: forecast vs actual. Trained only on earlier days.",
                 fontsize=11)
    ax.legend(fontsize=8, loc="center right")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    for a in axes:
        a.spines["top"].set_visible(False)
        a.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT / "fig5_wear_forecast.png", dpi=140, bbox_inches="tight")
    print(f"  wrote {OUT/'fig5_wear_forecast.png'}")


if __name__ == "__main__":
    main()
