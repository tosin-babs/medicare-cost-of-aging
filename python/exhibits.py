"""
Figures, in a plain journal style. Every figure is drawn from CSVs the
analysis wrote, so a figure cannot disagree with its table. Figures carry no
number of their own; the manuscript numbers them in reading order.
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


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(config.FIGURES / f"{name}.{ext}", dpi=config.FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


def figure_state_diagram():
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(7.6, 3.7))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.grid(False)
    pos = {"H": (0.10, 0.66), "C": (0.37, 0.66), "D": (0.63, 0.66), "L": (0.90, 0.66), "X": (0.50, 0.14)}
    for s, (x, y) in pos.items():
        ax.add_patch(FancyBboxPatch((x - 0.08, y - 0.085), 0.16, 0.17, boxstyle="round,pad=0.008",
                                    fc=P[s], ec="none", alpha=0.92, zorder=2))
        ax.text(x, y, LAB[s].replace("-term-care", "-term\ncare").replace(" illness", "\nillness"),
                ha="center", va="center", color="white", fontsize=8.6, fontweight="bold", zorder=3)
    def arrow(a, b, rad=0.0):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=1,
                    arrowprops=dict(arrowstyle="-|>", color=P["ink"], lw=1.0, shrinkA=30, shrinkB=30,
                                    connectionstyle=f"arc3,rad={rad}", mutation_scale=10))
    for a, b, rad in (("H", "C", 0.18), ("C", "D", 0.18), ("D", "C", 0.18), ("D", "L", 0.18), ("L", "D", 0.18),
                      ("H", "D", -0.42), ("D", "H", -0.30), ("C", "L", -0.42),
                      ("H", "X", 0.12), ("C", "X", 0.05), ("D", "X", -0.05), ("L", "X", -0.12)):
        arrow(a, b, rad)
    ax.text(0.5, 0.005, "Conditions are ever diagnosed, so Chronic illness does not return to Healthy. "
            "Twelve intensities are estimated.", ha="center", fontsize=7.6, color=P["muted"])
    _save(fig, "fig_state_diagram")


def figure_health_expectancy():
    t = pd.read_csv(T / "table4_lifetime_costs.csv")
    order = ["H", "C", "D", "L", "Population mix"]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4), sharey=True)
    for ax, sex in zip(axes, ("male", "female")):
        s = t[t["sex"] == sex].set_index("entry_state").reindex(order)
        left = np.zeros(len(order))
        for st in ("H", "C", "D", "L"):
            v = s[f"years_in_{st}"].to_numpy()
            ax.barh(np.arange(len(order)), v, left=left, color=P[st], label=LAB[st], height=0.62)
            left += v
        for i, e in enumerate(s["life_expectancy"]):
            ax.text(e + 0.2, i, f"{e:.1f}", va="center", fontsize=8)
        ax.set_yticks(np.arange(len(order)), [LAB.get(o, o) for o in order])
        ax.invert_yaxis()
        ax.set_title(f"{sex.capitalize()}: expected years in each state from 65")
        ax.set_xlabel("Years")
    axes[0].set_ylabel("Health state at 65")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, -0.13))
    _save(fig, "fig_health_expectancy")


def figure_transitions():
    t = pd.read_csv(T / "table2b_annual_transition_probabilities.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=True)
    for ax, sex in zip(axes, ("male", "female")):
        s = t[t["sex"] == sex]
        for frm, colour in (("H", P["H"]), ("C", P["C"]), ("D", P["D"]), ("L", P["L"])):
            g = s[s["from"] == frm]
            ax.plot(g["age"], 100 * g["to_X"], marker="o", color=colour, linewidth=1.8, label=f"from {LAB[frm]}")
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
        for st in ("H", "C", "D", "L"):
            g = s[s["state"] == st].set_index("age_band").reindex(bands)
            ax.plot(x, g["observed_pct"], marker="o", color=P[st], linewidth=1.8, label=f"{LAB[st]}, observed")
            ax.plot(x, g["model_pct"], linestyle="--", color=P[st], linewidth=1.4, label=f"{LAB[st]}, model")
        ax.set_xticks(x, bands)
        ax.set_title(f"{sex.capitalize()}: state prevalence by age")
        ax.set_xlabel("Age band")
    axes[0].set_ylabel("Percent of survivors")
    axes[0].legend(fontsize=7, ncol=2, loc="upper center")
    _save(fig, "fig_prevalence")


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
    t = t[t["entry_state"] != "Population mix"]
    t5 = pd.read_csv(T / "table5_tail_risk.csv")
    t5 = t5[(t5["level"] == 0.95) & (t5["entry_state"] != "Population mix")]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    states = ["H", "C", "D", "L"]
    x = np.arange(len(states))
    for off, sex, hatch in ((-0.2, "male", None), (0.2, "female", "//")):
        s = t[t["sex"] == sex].set_index("entry_state").reindex(states)
        c = t5[t5["sex"] == sex].set_index("entry_state").reindex(states)
        ax.bar(x + off, s["pv_oop_mean"] / 1000, width=0.38, color=P["C"], alpha=0.85 if sex == "male" else 0.55,
               hatch=hatch, label=f"{sex}, mean")
        ax.scatter(x + off, c["cvar"] / 1000, color=P["L"], marker="_", s=300, linewidths=2.5,
                   label=f"{sex}, CVaR95" if sex == "male" else None)
    ax.set_xticks(x, [LAB[s] for s in states])
    ax.set_ylabel("Lifetime out-of-pocket, thousands of 2024 dollars")
    ax.set_title("Expected and tail lifetime out-of-pocket cost by health state at 65")
    ax.legend(fontsize=8)
    _save(fig, "fig_entry_states")


def figure_scenarios():
    t = pd.read_csv(T / "table6_scenarios.csv")
    t = t[t["entry_state"] == "Population mix"]
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    scen = list(dict.fromkeys(t["scenario"]))
    y = np.arange(len(scen))
    for off, sex, alpha in ((-0.18, "male", 0.9), (0.18, "female", 0.55)):
        s = t[t["sex"] == sex].set_index("scenario").reindex(scen)
        ax.barh(y + off, s["cvar95_change_vs_s0"] / 1000, height=0.34, color=P["L"], alpha=alpha, label=f"{sex}, change in CVaR95")
        ax.scatter(s["mean_change_vs_s0"] / 1000, y + off, color=P["ink"], s=18, zorder=3,
                   label=f"{sex}, change in mean" if sex == "male" else None)
    ax.set_yticks(y, [s.replace("S1 Part A payable 89% from 2033, ", "S1 ") for s in scen])
    ax.invert_yaxis()
    ax.set_xlabel("Change in lifetime out-of-pocket cost against baseline, thousands of 2024 dollars")
    ax.set_title("Financing scenarios: change in the mean and in CVaR95")
    ax.legend(fontsize=8, loc="lower right")
    _save(fig, "fig_scenarios")


def main():
    print("=== figures ===")
    for f in (figure_state_diagram, figure_transitions, figure_prevalence, figure_health_expectancy,
              figure_lifetime_oop, figure_entry_states, figure_scenarios):
        try:
            f()
        except FileNotFoundError as e:
            print(f"  skipped {f.__name__}: {e.filename} not built yet")


if __name__ == "__main__":
    main()
