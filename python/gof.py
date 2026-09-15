"""
Goodness of fit of the transition model: observed against expected
destination counts.

For every interval between interviews the fitted model gives the probability
of each destination state, P(x, x + d) from the starting state. Summed over
intervals in a cell, those probabilities are the expected counts; the cell's
observed counts are compared with them. Cells are starting state by age
group at the start of the interval by interval length. This is the grouped
comparison behind the Pearson-type test of Aguirre-Hernandez and Farewell
(2002) used for panel Markov models; deaths are counted as a destination
whether or not the death date is exact, and the chi-square reference
distribution is approximate because the cells are formed after estimation.

Writes Table 7f (by cell) and 7g (summary by starting state).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from population import load_fitted

S = dict(enumerate(config.STATES))
K = len(config.STATES)
AGE_GROUPS = [(50, 65), (65, 75), (75, 85), (85, 120)]
LEN_GROUPS = [(0, 2.25), (2.25, 20)]


def main():
    m = load_fitted()
    iv = pd.read_pickle(config.DERIVED / "hrs_intervals.pkl")
    # censored observations have no observed destination and are excluded
    iv = iv[iv["obstype"] != 2].reset_index(drop=True)
    P = m.interval_probabilities(iv)
    iv = iv.assign(**{f"p{k}": P[:, k] for k in range(K)})
    iv["age_mid"] = iv["age_start"] + iv["duration"] / 2
    iv["age_group"] = pd.cut(iv["age_mid"], [a for a, _ in AGE_GROUPS] + [AGE_GROUPS[-1][1]], right=False,
                             labels=[f"{a}-{b - 1}" if b < 120 else f"{a}+" for a, b in AGE_GROUPS])
    iv["len_group"] = np.where(iv["duration"] < LEN_GROUPS[0][1], "up to 2.25 years", "over 2.25 years")
    rows = []
    for (fr, ag, lg), g in iv.groupby(["from_state", "age_group", "len_group"], observed=True):
        obs = np.bincount(g["to_state"].astype(int), minlength=K)
        exp = g[[f"p{k}" for k in range(K)]].sum().to_numpy()
        allowed = exp > 0.5
        x2 = float(((obs[allowed] - exp[allowed]) ** 2 / exp[allowed]).sum())
        rows.append({"from": S[int(fr)], "age_group": str(ag), "interval": lg, "n": len(g),
                     **{f"obs_{S[k]}": int(obs[k]) for k in range(K)},
                     **{f"exp_{S[k]}": float(exp[k]) for k in range(K)},
                     "pearson_x2": x2, "cells": int(allowed.sum())})
    t = pd.DataFrame(rows)
    t.to_csv(config.TABLES / "table7f_goodness_of_fit.csv", index=False)
    summ = []
    for fr, g in t.groupby("from", sort=False):
        obs = g[[f"obs_{S[k]}" for k in range(K)]].sum().to_numpy()
        exp = g[[f"exp_{S[k]}" for k in range(K)]].sum().to_numpy()
        summ.append({"from": fr, "n": int(g["n"].sum()),
                     **{f"obs_{S[k]}_pct": 100 * obs[k] / obs.sum() for k in range(K)},
                     **{f"exp_{S[k]}_pct": 100 * exp[k] / exp.sum() for k in range(K)},
                     "max_abs_gap_pts": float(np.max(np.abs(obs - exp)) / obs.sum() * 100),
                     "pearson_x2_sum": float(g["pearson_x2"].sum()), "cells": int(g["cells"].sum())})
    t7g = pd.DataFrame(summ)
    t7g.to_csv(config.TABLES / "table7g_goodness_of_fit_summary.csv", index=False)
    with pd.option_context("display.width", 250, "display.float_format", "{:,.1f}".format):
        print("=== Observed against expected destinations, by starting state (percent) ===")
        print(t7g.to_string(index=False))
        print("\n=== Largest cell contributions ===")
        print(t.sort_values("pearson_x2", ascending=False).head(10)[
            ["from", "age_group", "interval", "n", "pearson_x2"] + [f"obs_{S[k]}" for k in range(K)]
            + [f"exp_{S[k]}" for k in range(K)]].to_string(index=False))
    print("\nwrote tables 7f and 7g")


if __name__ == "__main__":
    main()
