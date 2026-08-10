"""
STEP 6 - CHARTS
Three figures for the case study. Palette: validated slots 1-2 of the reference
categorical palette (all-pairs PASS, worst CVD dE 24.7) plus neutral ink.

Form choices (job -> form):
  fig1  presence/absence of data over 18 months -> daily bars; the gaps ARE the message
  fig2  effect estimates with uncertainty       -> dot + CI, zero reference line
  fig3  one bivariate relationship              -> scatter + fit, honestly labelled
"""

from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DB = Path(__file__).parent / "ring.db"
OUT = Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASE = "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
    "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": BASE,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "figure.dpi": 150,
})


def finish(ax, title, subtitle=None):
    ax.set_title(title, fontsize=13, fontweight="bold", loc="left", pad=18 if subtitle else 8)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9.5,
                color=INK2, va="bottom")


con = sqlite3.connect(DB)
daily = pd.read_sql("SELECT day, wear_frac FROM daily_summary", con, parse_dates=["day"])
nights = pd.read_sql("SELECT * FROM model_nights", con, parse_dates=["night_date"])
coef = pd.read_csv(OUT / "m2_coefficients.csv")
con.close()

# ---------------------------------------------------------------- fig 1
# Reindex to EVERY calendar day so non-wear days are zero-height, not absent.
full = pd.date_range(daily.day.min(), daily.day.max(), freq="D")
s = daily.set_index("day").wear_frac.reindex(full, fill_value=0.0)

fig, ax = plt.subplots(figsize=(11, 3.4))
ax.bar(s.index, s.values * 100, width=1.0, color=BLUE, linewidth=0)
worn = (s > 0).sum()
ax.set_ylabel("share of day with readings (%)")
ax.set_ylim(0, 100)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.grid(axis="x", visible=False)
finish(ax, "The ring recorded on 300 of 562 days - and the gaps run for weeks",
       f"Daily sensor coverage, Jan 2025 - Jul 2026. {worn} days with any data; "
       f"longest gap 61 days (Nov 2025 - Jan 2026).")
# annotate the two longest gaps directly rather than relying on the reader to spot them
for a, b, txt in [("2025-11-07", "2026-01-06", "61-day gap"),
                  ("2026-04-03", "2026-05-12", "40-day gap")]:
    mid = pd.Timestamp(a) + (pd.Timestamp(b) - pd.Timestamp(a)) / 2
    ax.annotate(txt, xy=(mid, 4), xytext=(mid, 62), ha="center", fontsize=9, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1.2, shrinkA=0, shrinkB=2))
fig.tight_layout()
fig.savefig(OUT / "fig1_coverage.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- fig 2
keep = coef[(coef.term != "const") & (~coef.model.str.contains("sensitivity"))].copy()
label_map = {
    ("sleep_h", "RHR ~ sleep + prior activity (uncensored)"): "Sleep duration (+1 h)",
    ("prior_steps_k", "RHR ~ sleep + prior activity (uncensored)"): "Prior-day steps (+1,000)",
    ("wake_h", "RHR ~ sleep + wake timing (uncensored)"): "Waking 1 h later",
    ("wake_sd_7", "RHR ~ wake-time variability (routine only)"): "Wake-time variability (+1 min SD)",
    ("prior_workout_min", "RHR ~ workout minutes (workout days only)"): "Workout minutes (+1 min)",
}
rhr = keep[keep.model.str.startswith("RHR")].copy()
rhr["label"] = [label_map.get((t, m)) for t, m in zip(rhr.term, rhr.model)]
rhr = rhr.dropna(subset=["label"]).drop_duplicates("label").sort_values("coef")

fig, ax = plt.subplots(figsize=(8.4, 3.6))
y = np.arange(len(rhr))
ax.axvline(0, color=BASE, lw=1.4, zorder=1)
ax.hlines(y, rhr.ci_lo, rhr.ci_hi, color=BLUE, lw=2, zorder=2)
ax.plot(rhr.coef, y, "o", ms=9, color=BLUE, mec=SURFACE, mew=2, zorder=3)
ax.set_yticks(y, rhr.label, fontsize=10)
ax.set_xlabel("change in resting heart rate (bpm)   ·   95% CI")
ax.grid(axis="y", visible=False)
finish(ax, "Only wake timing separates from zero - and it does not survive correction",
       "Effect on overnight resting HR, n=95-142 nights. Four of five intervals cross zero; "
       "after Holm-Bonferroni across 12 tests, none survives.")
fig.tight_layout()
fig.savefig(OUT / "fig2_effects.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- fig 3
d = nights.dropna(subset=["hrv", "prior_steps"])
x, yv = d.prior_steps / 1000, d.hrv
b, a = np.polyfit(x, yv, 1)
fig, ax = plt.subplots(figsize=(7.4, 4.2))
ax.plot(x, yv, "o", ms=7, color=BLUE, alpha=0.55, mec=SURFACE, mew=1.2)
xs = np.linspace(x.min(), x.max(), 50)
ax.plot(xs, a + b * xs, color=ORANGE, lw=2)
ax.set_xlabel("prior-day steps (thousands)")
ax.set_ylabel("overnight HRV (ms)")
finish(ax, f"The strongest relationship found: +{b:.1f} ms HRV per 1,000 prior-day steps",
       f"Bivariate fit, all n={len(d)} nights. The adjusted model (n=95, controlling for sleep "
       f"duration) gives +1.4 ms, p=0.009  - \nwhich does NOT survive Holm correction across 12 "
       f"tests (threshold 0.004). Suggestive, not established.")
fig.tight_layout()
fig.savefig(OUT / "fig3_hrv_steps.png", bbox_inches="tight")
plt.close(fig)

print("wrote:", *[p.name for p in sorted(OUT.glob("fig*.png"))])
