"""
STEP 5 - MODELS
M2: what actually moves overnight recovery (resting HR, HRV)?

Deliberately small. n=142 nights supports a handful of coefficients with honest
intervals; it does not support a tree ensemble whose feature importances would
be noise dressed as insight. Every claim here ships with a CI and an n.

Design notes:
- Predictors are PRIOR-DAY behaviour plus the night's own duration/timing.
  Regressing a night's HR on statistics of that same block would be circular.
- Nights flagged start_truncated have a censored (lower-bound) sleep_h, so the
  sleep-duration model is fitted on uncensored nights and the full set is
  reported alongside as a sensitivity check.
- HAC (Newey-West) standard errors: consecutive nights are autocorrelated, and
  plain OLS errors would be too narrow.
"""

import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

DB = Path(__file__).parent / "ring.db"
OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

con = sqlite3.connect(DB)
df = pd.read_sql("SELECT * FROM model_nights ORDER BY night_date", con)
con.close()

df["night_date"] = pd.to_datetime(df["night_date"])
df["prior_steps_k"] = df["prior_steps"] / 1000.0
df["wake_h"] = df["wake_min"] / 60.0            # hours past the 20:00 anchor
df["sleep_h_c"] = df["sleep_h"] - df["sleep_h"].mean()

print(f"n = {len(df)} nights   ({df.night_date.min():%Y-%m-%d} .. {df.night_date.max():%Y-%m-%d})")
print(f"uncensored (start_truncated=0): {(df.start_truncated == 0).sum()}")
print()
print("outcome distributions")
for c in ("rhr", "hrv", "sleep_h", "prior_steps_k"):
    s = df[c].describe()
    print(f"  {c:14s} mean {s['mean']:7.2f}  sd {s['std']:6.2f}  "
          f"min {s['min']:6.1f}  med {s['50%']:6.1f}  max {s['max']:7.1f}")


def fit(data, y, xs, label):
    """OLS with HAC errors. Returns tidy coefficient rows."""
    d = data[[y] + xs].dropna()
    if len(d) < 20:
        print(f"\n[{label}] SKIPPED - only {len(d)} complete rows")
        return None
    X = sm.add_constant(d[xs])
    m = sm.OLS(d[y], X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    ci = m.conf_int()
    print(f"\n[{label}]  n={int(m.nobs)}  R²={m.rsquared:.3f}  adj={m.rsquared_adj:.3f}")
    print(f"  {'term':22s} {'coef':>9s} {'95% CI':>20s} {'p':>8s}")
    rows = []
    for term in X.columns:
        lo, hi = ci.loc[term]
        star = "  *" if m.pvalues[term] < 0.05 else ""
        print(f"  {term:22s} {m.params[term]:9.3f}  [{lo:8.3f},{hi:8.3f}] {m.pvalues[term]:8.3f}{star}")
        rows.append({"model": label, "term": term, "coef": m.params[term],
                     "ci_lo": lo, "ci_hi": hi, "p": m.pvalues[term], "n": int(m.nobs),
                     "r2": m.rsquared})
    return pd.DataFrame(rows)


results = []
unc = df[df.start_truncated == 0]

# --- M2a: does sleep duration move next-morning resting HR? ------------------
results.append(fit(unc, "rhr", ["sleep_h", "prior_steps_k"], "RHR ~ sleep + prior activity (uncensored)"))
results.append(fit(df, "rhr", ["sleep_h", "prior_steps_k"], "RHR ~ sleep + prior activity (ALL, sensitivity)"))

# --- M2b: same for HRV -------------------------------------------------------
results.append(fit(unc, "hrv", ["sleep_h", "prior_steps_k"], "HRV ~ sleep + prior activity (uncensored)"))

# --- M2c: does WHEN you sleep matter beyond how long? ------------------------
results.append(fit(unc, "rhr", ["sleep_h", "wake_h"], "RHR ~ sleep + wake timing (uncensored)"))

# --- M2d: wake-time consistency ---------------------------------------------
# Only meaningful where the 7-night window is a real routine, not a window
# straddling months of non-wear.
routine = df[(df.wake_sd_7.notna()) & (df.wake_sd_span_d <= 14)]
print(f"\n[routine subset] nights whose prior-7 window spans <=14 days: {len(routine)}")
results.append(fit(routine, "rhr", ["wake_sd_7", "sleep_h"], "RHR ~ wake-time variability (routine only)"))

# --- workout load ------------------------------------------------------------
print(f"\n[workout exposure] nights after a workout day: {(df.prior_workouts > 0).sum()} "
      f"| after a LATE workout: {int(df.prior_late_workout.sum())}")
if df.prior_late_workout.sum() >= 15:
    results.append(fit(df, "rhr", ["prior_late_workout", "sleep_h"], "RHR ~ late workout"))
else:
    print("  -> too few late-workout nights to model. Reported as an unanswerable "
          "question, not a null result.")
results.append(fit(df[df.prior_workouts > 0], "rhr", ["prior_workout_min", "sleep_h"],
                   "RHR ~ workout minutes (workout days only)"))

tidy = pd.concat([r for r in results if r is not None], ignore_index=True)

# --- multiple-comparison correction -----------------------------------------
# Several models were fitted on one dataset. Reporting the surviving p-values
# without correction is the classic way to publish noise, so apply Holm-
# Bonferroni across the family of non-intercept tests and label what survives.
fam = tidy[tidy.term != "const"].copy().sort_values("p").reset_index(drop=True)
m = len(fam)
fam["holm_threshold"] = [0.05 / (m - i) for i in range(m)]
fam["survives_holm"] = False
for i in range(m):
    if fam.loc[i, "p"] <= fam.loc[i, "holm_threshold"]:
        fam.loc[i, "survives_holm"] = True
    else:
        break   # Holm stops at the first failure
print(f"\n=== Holm-Bonferroni across {m} coefficient tests ===")
print(f"  {'term':22s} {'model':44s} {'p':>7s} {'thresh':>8s}  survives")
for _, r in fam.iterrows():
    print(f"  {r.term:22s} {r.model[:44]:44s} {r.p:7.3f} {r.holm_threshold:8.4f}  "
          f"{'YES' if r.survives_holm else 'no'}")
tidy = tidy.merge(fam[["model", "term", "holm_threshold", "survives_holm"]],
                  on=["model", "term"], how="left")
tidy.to_csv(OUT / "m2_coefficients.csv", index=False)
df.to_csv(OUT / "model_nights.csv", index=False)
print(f"\nwrote {OUT/'m2_coefficients.csv'} and {OUT/'model_nights.csv'}")
