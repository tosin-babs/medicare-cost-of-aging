"""
Figures, in a plain journal style. Every figure is drawn from CSVs the
analysis wrote or from the fitted model, so a figure cannot disagree with its
table. Figures carry no number of their own; the manuscript numbers them in
reading order.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.22, "grid.linewidth": 0.5,
    "axes.axisbelow": True, "figure.dpi": 110,
    "legend.frameon": False, "axes.titlesize": 10, "axes.titleweight": "bold",
})
P = config.PALETTE
T = config.TABLES
LAB = config.STATE_LABELS
LIVE = list(config.LIVE_STATES)
SHORT = {"H": "Healthy", "C": "Chronic", "D": "Disability", "L": "Severe, at home",
         "N": "Nursing home", "X": "Dead"}


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(config.FIGURES / f"{name}.{ext}", dpi=config.FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


def figure_state_diagram():
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.grid(False)
    pos = {"H": (0.09, 0.68), "C": (0.30, 0.68), "D": (0.51, 0.68), "L": (0.72, 0.68),
           "N": (0.92, 0.68), "X": (0.51, 0.14)}
    for s, (x, y) in pos.items():
        ax.add_patch(FancyBboxPatch((x - 0.07, y - 0.085), 0.14, 0.17, boxstyle="round,pad=0.008",
                                    fc=P[s], ec="none", alpha=0.92, zorder=2))
        ax.text(x, y, SHORT[s].replace(", ", ",\n"), ha="center", va="center", color="white",
                fontsize=8.4, fontweight="bold", zorder=3)

    def arrow(a, b, rad=0.0):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=1,
                    arrowprops=dict(arrowstyle="-|>", color=P["ink"], lw=0.9, shrinkA=28, shrinkB=28,
                                    connectionstyle=f"arc3,rad={rad}", mutation_scale=9))
    for a, b, rad in (("H", "C", 0.2), ("C", "D", 0.2), ("D", "C", 0.2), ("D", "L", 0.2), ("L", "D", 0.2),
                      ("L", "N", 0.2), ("N", "L", 0.2), ("H", "D", -0.45), ("D", "H", -0.3),
                      ("C", "L", -0.45), ("C", "N", -0.55), ("D", "N", -0.4), ("N", "D", -0.25),
                      ("H", "X", 0.15), ("C", "X", 0.05), ("D", "X", 0.0), ("L", "X", -0.05), ("N", "X", -0.15)):
        arrow(a, b, rad)
    ax.text(0.5, 0.0, "Conditions are ever diagnosed, so Chronic does not return to Healthy. "
            "Eighteen intensities are estimated; other moves pass through intervening states.",
            ha="center", fontsize=7.4, color=P["muted"])
    _save(fig, "fig_state_diagram")


def figure_transitions():
    t = pd.read_csv(T / "table2b_annual_transition_probabilities.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=True)
    for ax, sex in zip(axes, ("male", "female")):
        s = t[t["sex"] == sex]
        for frm in LIVE:
            g = s[s["from"] == frm]
            ax.plot(g["age"], 100 * g["to_X"], marker="o", color=P[frm], linewidth=1.8, label=f"from {SHORT[frm]}")
        ax.set_title(f"{sex.capitalize()}: one-year probability of death by state")
        ax.set_xlabel("Age")
        ax.set_xticks([65, 75, 85])
    axes[0].set_ylabel("Percent")
    axes[0].legend(loc="upper left", fontsize=8)
    _save(fig, "fig_transitions")


def figure_prevalence():
    t = pd.read_csv(T / "table7b_prevalence_validation.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=True)
    for ax, sex in zip(axes, ("male", "female")):
        s = t[t["sex"] == sex]
        bands = list(dict.fromkeys(s["age_band"]))
        x = np.arange(len(bands))
        for st in LIVE:
            g = s[s["state"] == st].set_index("age_band").reindex(bands)
            ax.plot(x, g["observed_pct"], marker="o", color=P[st], linewidth=1.8, label=f"{SHORT[st]}, HRS")
            ax.plot(x, g["model_pct"], linestyle="--", color=P[st], linewidth=1.4, label=f"{SHORT[st]}, model")
        ax.set_xticks(x, bands)
        ax.set_title(f"{sex.capitalize()}: state prevalence by age")
        ax.set_xlabel("Age band")
    axes[0].set_ylabel("Percent of survivors")
    axes[0].legend(fontsize=6.5, ncol=2, loc="upper center")
    _save(fig, "fig_prevalence")


def figure_health_expectancy():
    """Expected years in each state from 65 by health state at 65 and for the
    population mix, from the calibrated model by forward recursion."""
    import simulate as sim
    from population import entry_mix, load_model
    model = load_model()
    mix = entry_mix()
    order = LIVE + [None]
    names = [SHORT[s] for s in LIVE] + ["Population mix"]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6), sharey=True)
    for ax, sex in zip(axes, ("male", "female")):
        cache = {}
        rows = []
        for entry in order:
            e = None if entry is None else config.STATES.index(entry)
            cells = [c for c in mix[sex] if e is None or c[0] == e]
            tot = sum(c[2] for c in cells)
            yrs = np.zeros(len(LIVE))
            for s0, z, w0 in cells:
                key = tuple(z)
                if key not in cache:
                    cache[key] = sim.annual_matrices(model, z)
                mats = cache[key]          # not P: P is the palette
                p = np.zeros(len(config.STATES)); p[s0] = w0 / tot
                for a in sim.AGES:
                    pn = p @ mats[a]
                    yrs += 0.5 * (p[:len(LIVE)] + pn[:len(LIVE)])
                    p = pn
            rows.append(yrs)
        rows = np.array(rows)
        left = np.zeros(len(order))
        for j, st in enumerate(LIVE):
            ax.barh(np.arange(len(order)), rows[:, j], left=left, color=P[st], label=SHORT[st], height=0.62)
            left += rows[:, j]
        for i, e in enumerate(left):
            ax.text(e + 0.2, i, f"{e:.1f}", va="center", fontsize=8)
        ax.set_yticks(np.arange(len(order)), names)
        ax.invert_yaxis()
        ax.set_title(f"{sex.capitalize()}: expected years in each state from 65")
        ax.set_xlabel("Years")
    axes[0].set_ylabel("Health state at 65")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, fontsize=8, bbox_to_anchor=(0.5, -0.13))
    _save(fig, "fig_health_expectancy")


def figure_lifetime_oop():
    lives = pd.read_pickle(config.DERIVED / "sim_lives.pkl")
    t5 = pd.read_csv(T / "table5_tail_risk.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=False)
    for ax, sex in zip(axes, ("male", "female")):
        pv = lives[(sex, "Population mix")]["pv_oop"] / 1000
        ax.hist(pv, bins=np.arange(0, np.percentile(pv, 99.5), 5), color=P["C"], alpha=0.8, density=True)
        r = t5[(t5["sex"] == sex) & (t5["entry_state"] == "Population mix")].set_index("level")
        for lvl, colour in ((0.90, P["D"]), (0.95, P["L"]), (0.99, P["X"])):
            ax.axvline(r.loc[lvl, "var"] / 1000, color=colour, linewidth=1.2, linestyle="--")
            ax.text(r.loc[lvl, "var"] / 1000, ax.get_ylim()[1] * 0.92, f"VaR{int(100 * lvl)}\n${r.loc[lvl, 'var'] / 1000:,.0f}k",
                    fontsize=7, color=colour, ha="left")
        ax.set_title(sex.capitalize())
        ax.set_xlabel("Thousands of 2024 dollars, discounted at 3%")
    axes[0].set_ylabel("Density")
    fig.suptitle("Present value of lifetime out-of-pocket cost from 65, population mix", fontsize=10, fontweight="bold")
    _save(fig, "fig_lifetime_oop")


def figure_entry_states():
    t = pd.read_csv(T / "table4_lifetime_costs.csv")
    t5 = pd.read_csv(T / "table5_tail_risk.csv")
    t5 = t5[t5["level"] == 0.95]
    labels = [LAB[s] for s in LIVE]
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    x = np.arange(len(labels))
    for off, sex, hatch in ((-0.2, "male", None), (0.2, "female", "//")):
        s = t[t["sex"] == sex].set_index("entry_state").reindex(labels)
        c = t5[t5["sex"] == sex].set_index("entry_state").reindex(labels)
        ax.bar(x + off, s["pv_oop_mean"] / 1000, width=0.38, color=P["C"], alpha=0.85 if sex == "male" else 0.55,
               hatch=hatch, label=f"{sex}, mean")
        ax.scatter(x + off, c["cvar"] / 1000, color=P["L"], marker="_", s=300, linewidths=2.5,
                   label=f"{sex}, CVaR95" if sex == "male" else None)
    ax.set_xticks(x, [SHORT[s] for s in LIVE])
    ax.set_ylabel("Lifetime out-of-pocket, thousands of 2024 dollars")
    ax.set_title("Expected and tail lifetime out-of-pocket cost by health state at 65")
    ax.legend(fontsize=8)
    _save(fig, "fig_entry_states")


def figure_cost_by_age():
    """Expected annual cost by age and entry state, from the analytic
    recursion: the timing of costs that entry health changes."""
    import simulate as sim
    from population import entry_mix, load_model
    model = load_model()
    mix = entry_mix()
    bundle = sim.decedent_adjustment(model, mix, sim.cost_bundle(persistence=False))
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8), sharey=True)
    for ax, sex in zip(axes, ("male", "female")):
        om, em = sim.cost_means(bundle, sex)
        for entry in LIVE:
            e = config.STATES.index(entry)
            cells = [c for c in mix[sex] if c[0] == e]
            tot = sum(c[2] for c in cells)
            prof = np.zeros(len(sim.AGES))
            for s0, z, w0 in cells:
                mats = sim.annual_matrices(model, z)          # not P: P is the palette
                p = np.zeros(len(config.STATES)); p[s0] = w0 / tot
                for i, a in enumerate(sim.AGES):
                    band = "65-74" if a < 75 else "75+"
                    live = p[:len(LIVE)]
                    med = np.array([bundle["medicare"][(st, band)] for st in LIVE]) * bundle["level"]
                    d_prob = mats[a][:len(LIVE), config.DEAD]
                    prof[i] += (live * med * (1 + d_prob * (bundle["decedent_multiplier"] - 1))).sum()
                    p = p @ mats[a]
            ax.plot(sim.AGES, prof / 1000, color=P[entry], linewidth=1.8, label=SHORT[entry])
        ax.set_title(f"{sex.capitalize()}: expected Medicare cost per original life, by age")
        ax.set_xlabel("Age")
        ax.set_xlim(65, 100)
    axes[0].set_ylabel("Thousands of 2024 dollars a year (undiscounted, survival included)")
    axes[0].legend(fontsize=7.5)
    _save(fig, "fig_cost_by_age")


def figure_scenarios():
    t = pd.read_csv(T / "table6_scenarios.csv")
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    scen = list(dict.fromkeys(t["scenario"]))
    y = np.arange(len(scen))
    for off, sex, alpha in ((-0.18, "male", 0.9), (0.18, "female", 0.55)):
        s = t[t["sex"] == sex].set_index("scenario").reindex(scen)
        ax.barh(y + off, s["cvar95_change_vs_s0"] / 1000, height=0.34, color=P["L"], alpha=alpha,
                label=f"{sex}, change in CVaR95")
        ax.scatter(s["mean_change_vs_s0"] / 1000, y + off, color=P["ink"], s=18, zorder=3,
                   label=f"{sex}, change in mean" if sex == "male" else None)
    ax.set_yticks(y, scen)
    ax.invert_yaxis()
    ax.set_xlabel("Change in lifetime out-of-pocket cost against baseline, thousands of 2024 dollars")
    ax.set_title("Financing scenarios: change in the mean and in CVaR95")
    ax.legend(fontsize=8, loc="lower right")
    _save(fig, "fig_scenarios")


def figure_spend_down():
    t = pd.read_csv(T / "table6b_spend_down.csv")
    t = t[t["scenario"].str.startswith("S0")]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
    order = ["low", "middle", "high"]
    x = np.arange(3)
    for off, sex, alpha in ((-0.18, "male", 0.9), (0.18, "female", 0.55)):
        s = t[t["sex"] == sex].set_index("income_tertile").reindex(order)
        axes[0].bar(x + off, s["medicaid_at_65_pct"], width=0.36, color=P["X"], alpha=alpha,
                    label=f"{sex}, on Medicaid at 65")
        axes[0].bar(x + off, s["spend_down_pct"], bottom=s["medicaid_at_65_pct"], width=0.36, color=P["N"],
                    alpha=alpha, label=f"{sex}, spend down later")
        axes[1].bar(x + off, s["cvar95"] / 1000, width=0.36, color=P["L"], alpha=alpha, label=f"{sex}, CVaR95")
        axes[1].scatter(x + off, s["pv_oop_mean"] / 1000, color=P["ink"], s=18, zorder=3,
                        label=f"{sex}, mean" if sex == "male" else None)
    for ax in axes:
        ax.set_xticks(x, ["Low income", "Middle", "High"])
    axes[0].set_ylabel("Percent of lives")
    axes[0].set_title("Medicaid at 65 and spend-down after 65")
    axes[1].set_ylabel("Thousands of 2024 dollars")
    axes[1].set_title("Lifetime out-of-pocket cost: mean and CVaR95")
    axes[0].legend(fontsize=7)
    axes[1].legend(fontsize=7)
    _save(fig, "fig_spend_down")


def main():
    print("=== figures ===")
    for f in (figure_state_diagram, figure_transitions, figure_prevalence, figure_health_expectancy,
              figure_cost_by_age, figure_lifetime_oop, figure_entry_states, figure_scenarios,
              figure_spend_down):
        try:
            f()
        except FileNotFoundError as e:
            print(f"  skipped {f.__name__}: {e.filename} not built yet")


if __name__ == "__main__":
    main()
