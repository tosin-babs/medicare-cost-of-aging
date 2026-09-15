"""
RQ1: transition intensities among Healthy, Chronic, Disabled, LTC-need and Dead.

Two models are fitted to the HRS interval file with the estimator in
multistate.py:

  base   log q_jk = b0 + b1 (age - 65)/10 + g_female * female
  full   base + g_college * college + g_nonwhite * nonwhite

Allowed transitions are those the crude counts support: H -> C, D, X;
C -> D, L, X; D -> H, C, L, X; L -> D, X. C -> H is impossible by construction
(conditions are "ever had"). L -> H and L -> C are not given direct
intensities; the model reaches them through D within an interval, which is
what a continuous-time Markov model does with interval-censored data.

Outputs: coefficient tables with hazard ratios, one-year transition
probabilities at ages 65, 75 and 85 by sex, and the model's implied life
expectancy at 65 by sex for the validation step.

Writes Tables 2, 2b, 2c and data/derived/msm_full.pkl.
"""

from __future__ import annotations

import pickle
import time

import numpy as np
import pandas as pd

import config
from multistate import MultiStateMarkov

ALLOWED = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 4),
           (2, 0), (2, 1), (2, 3), (2, 4), (3, 2), (3, 4)]
S = {0: "H", 1: "C", 2: "D", 3: "L", 4: "X"}
COV_BASE = ["female"]
COV_FULL = ["female", "college", "nonwhite"]


def life_expectancy(model, z, entry_state=0, entry_age=65, max_age=config.MAX_AGE):
    """Expected years alive from entry, by annual steps of P(age, age+1)."""
    p = np.zeros(5); p[entry_state] = 1.0
    years, in_state = 0.0, np.zeros(5)
    for a in range(entry_age, max_age):
        P = model.transition_matrix(a, 1.0, z)
        alive_start = p[:4].sum()
        p_next = p @ P
        # trapezoid on survival within the year
        years += 0.5 * (alive_start + p_next[:4].sum())
        in_state += 0.5 * (p[:4].sum(keepdims=False) * 0 + np.append(p[:4], 0)
                           + np.append(p_next[:4], 0))
        p = p_next
    return years, in_state[:4]


def main():
    iv = pd.read_pickle(config.DERIVED / "hrs_intervals.pkl")
    print(f"{len(iv):,} intervals, {iv['hhidpn'].nunique():,} persons")
    fits = {}
    for name, cov in (("base", COV_BASE), ("full", COV_FULL)):
        t0 = time.time()
        m = MultiStateMarkov(5, ALLOWED, covariates=cov).fit(iv)
        print(f"  {name}: {m.method_}, converged {m.converged_}, loglik {m.loglik_:,.1f}, "
              f"AIC {m.aic_:,.1f}, {len(m.theta_)} params, {time.time() - t0:.0f}s"
              + (f", at bound: {m.at_bound_}" if m.at_bound_ else ""))
        fits[name] = m
    with open(config.DERIVED / "msm_full.pkl", "wb") as fh:
        pickle.dump({"allowed": ALLOWED, "covariates": COV_FULL,
                     "theta": fits["full"].theta_, "cov": fits["full"].cov_,
                     "se": fits["full"].se_, "loglik": fits["full"].loglik_,
                     "base_theta": fits["base"].theta_, "base_loglik": fits["base"].loglik_},
                    fh)

    m = fits["full"]
    tab = m.coef_table()
    tab["transition"] = tab["parameter"].str.extract(r"q(\d)(\d)").apply(
        lambda r: f"{S[int(r[0])]} to {S[int(r[1])]}", axis=1)
    tab["term"] = tab["parameter"].str.split(":").str[1]
    tab["lr_test_vs_base"] = np.nan
    tab.loc[0, "lr_test_vs_base"] = 2 * (fits["full"].loglik_ - fits["base"].loglik_)
    tab.to_csv(config.TABLES / "table2_intensities.csv", index=False)

    print("\n=== Full model: hazard ratios ===")
    piv = tab.pivot_table(index="transition", columns="term", values="hazard_ratio")
    piv = piv.reindex([f"{S[j]} to {S[k]}" for j, k in ALLOWED])
    print(piv[["age_per_10y", "female", "college", "nonwhite"]].round(3).to_string())
    print(f"\n  likelihood-ratio test, full against base: {tab.loc[0, 'lr_test_vs_base']:,.1f} "
          f"on {len(fits['full'].theta_) - len(fits['base'].theta_)} df")

    rows = []
    for female in (0, 1):
        z = [female, 0, 0]
        for age in (65, 75, 85):
            P = m.transition_matrix(age, 1.0, z)
            for j in range(4):
                rows.append({"sex": "female" if female else "male", "age": age,
                             "from": S[j], **{f"to_{S[k]}": P[j, k] for k in range(5)}})
    t2b = pd.DataFrame(rows)
    t2b.to_csv(config.TABLES / "table2b_annual_transition_probabilities.csv", index=False)

    rows = []
    for female in (0, 1):
        for college in (0, 1):
            for nonwhite in (0, 1):
                z = [female, college, nonwhite]
                for entry in range(4):
                    e, ins = life_expectancy(m, z, entry_state=entry)
                    rows.append({"sex": "female" if female else "male",
                                 "college": college, "nonwhite": nonwhite,
                                 "entry_state": S[entry], "life_expectancy_65": e,
                                 **{f"years_in_{S[k]}": ins[k] for k in range(4)}})
    t2c = pd.DataFrame(rows)
    t2c.to_csv(config.TABLES / "table2c_health_expectancies.csv", index=False)
    print("\n=== Life expectancy at 65 by entry state (reference: no college, white) ===")
    ref = t2c[(t2c["college"] == 0) & (t2c["nonwhite"] == 0)]
    print(ref[["sex", "entry_state", "life_expectancy_65", "years_in_H", "years_in_C",
               "years_in_D", "years_in_L"]].round(2).to_string(index=False))
    print("\nwrote tables 2, 2b, 2c and msm_full.pkl")


if __name__ == "__main__":
    main()
