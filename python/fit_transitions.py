"""
RQ1: transition intensities among Healthy, Chronic illness, Disability,
Severe disability at home, Nursing home and Dead.

Two models are fitted to the HRS interval file with the estimator in
multistate.py:

  base   log q_jk = b0 + b1 (age-65)/10 + spline terms + g_female female
  full   base + g_college college + g_nonwhite nonwhite

Allowed transitions are those the crude counts support and that a two-year
panel can identify: H -> C, D, X; C -> D, L, N, X; D -> H, C, L, N, X;
L -> D, N, X; N -> D, L, X. C -> H is impossible by construction (conditions
are "ever had"). Transitions not given their own intensity (H -> N, L -> C and
the rest) are reached through the intervening states within an interval, which
is what a continuous-time model does with interval-censored data.

Standard errors are clustered on the household by a sandwich estimator:
spouses are both in the sample and their health and survival are correlated.

Outputs: coefficient tables with hazard ratios, one-year transition
probabilities at ages 65, 75 and 85 by sex, and the model's implied life
expectancy at 65 by entry state.

Writes Tables 2, 2b, 2c and data/derived/msm_full.pkl.
"""

from __future__ import annotations

import os
import pickle
import time

import numpy as np
import pandas as pd

import config
from multistate import MultiStateMarkov

H, C, D, L, N, X = range(6)
ALLOWED = [(H, C), (H, D), (H, X),
           (C, D), (C, L), (C, N), (C, X),
           (D, H), (D, C), (D, L), (D, N), (D, X),
           (L, D), (L, N), (L, X),
           (N, D), (N, L), (N, X)]
S = {i: s for i, s in enumerate(config.STATES)}
COV_BASE = ["female"]
COV_FULL = ["female", "college", "nonwhite"]
ROBUST = os.environ.get("P5_ROBUST_SE", "1") == "1"


def life_expectancy(model, z, entry_state=0, entry_age=config.ENTRY_AGE,
                    max_age=config.MAX_AGE):
    """Expected years alive from entry, and years in each live state."""
    K = len(config.STATES)
    live = K - 1
    p = np.zeros(K)
    p[entry_state] = 1.0
    years, in_state = 0.0, np.zeros(live)
    for a in range(entry_age, max_age):
        P = model.transition_matrix(a, 1.0, z)
        p_next = p @ P
        years += 0.5 * (p[:live].sum() + p_next[:live].sum())
        in_state += 0.5 * (p[:live] + p_next[:live])
        p = p_next
    return years, in_state


def fit_one(name, iv):
    cov = COV_FULL if name == "full" else COV_BASE
    t0 = time.time()
    m = MultiStateMarkov(len(config.STATES), ALLOWED, covariates=cov,
                         age_knots=config.AGE_KNOTS, max_piece=config.MAX_PIECE_YEARS)
    m.fit(iv, robust_se=ROBUST and name == "full")
    print(f"  {name}: {m.method_}, converged {m.converged_}, loglik {m.loglik_:,.1f}, "
          f"AIC {m.aic_:,.1f}, {len(m.theta_)} params, {time.time() - t0:.0f}s"
          + (f", at bound: {m.at_bound_}" if m.at_bound_ else ""), flush=True)
    state = {k: getattr(m, k, None) for k in ("theta_", "cov_", "se_", "cov_robust_", "se_robust_",
                                              "loglik_", "method_", "converged_", "at_bound_", "aic_",
                                              "n_obs_", "n_clusters_")}
    with open(config.DERIVED / f"msm_fit_{name}.pkl", "wb") as fh:
        pickle.dump({"covariates": cov, "state": state}, fh)
    return m


def load_one(name):
    with open(config.DERIVED / f"msm_fit_{name}.pkl", "rb") as fh:
        d = pickle.load(fh)
    m = MultiStateMarkov(len(config.STATES), ALLOWED, covariates=d["covariates"],
                         age_knots=config.AGE_KNOTS, max_piece=config.MAX_PIECE_YEARS)
    for k, v in d["state"].items():
        setattr(m, k, v)
    return m


def main():
    """P5_FIT_WHICH=base or full fits one model and saves it, so the two can
    run in parallel; otherwise the saved fits are used where they exist, the
    rest are fitted, and the tables are written."""
    which = os.environ.get("P5_FIT_WHICH")
    iv = pd.read_pickle(config.DERIVED / "hrs_intervals.pkl")
    print(f"{len(iv):,} observations, {iv['hhidpn'].nunique():,} persons, "
          f"{iv['household'].nunique():,} households "
          f"({int((iv['obstype'] == 1).sum()):,} transitions, "
          f"{int((iv['obstype'] == 3).sum()):,} deaths, "
          f"{int((iv['obstype'] == 2).sum()):,} censored)", flush=True)
    if which in ("base", "full"):
        fit_one(which, iv)
        return
    fits = {name: (load_one(name) if (config.DERIVED / f"msm_fit_{name}.pkl").exists() else fit_one(name, iv))
            for name in ("base", "full")}

    m = fits["full"]
    with open(config.DERIVED / "msm_full.pkl", "wb") as fh:
        pickle.dump({"allowed": ALLOWED, "covariates": COV_FULL, "age_knots": config.AGE_KNOTS,
                     "max_piece": config.MAX_PIECE_YEARS, "theta": m.theta_, "cov": m.cov_,
                     "se": m.se_, "cov_robust": m.cov_robust_, "se_robust": m.se_robust_,
                     "loglik": m.loglik_, "base_theta": fits["base"].theta_,
                     "base_loglik": fits["base"].loglik_, "n_obs": m.n_obs_,
                     "n_clusters": getattr(m, "n_clusters_", None),
                     "method": m.method_, "converged": m.converged_}, fh)

    tab = m.coef_table()
    tab["transition"] = tab["parameter"].str.extract(r"q(\d)(\d)").apply(
        lambda r: f"{S[int(r[0])]} to {S[int(r[1])]}", axis=1)
    tab["term"] = tab["parameter"].str.split(":").str[1]
    tab["lr_test_vs_base"] = np.nan
    tab.loc[0, "lr_test_vs_base"] = 2 * (m.loglik_ - fits["base"].loglik_)
    tab.loc[0, "lr_df"] = len(m.theta_) - len(fits["base"].theta_)
    tab.to_csv(config.TABLES / "table2_intensities.csv", index=False)

    print("\n=== Full model: hazard ratios ===")
    piv = tab.pivot_table(index="transition", columns="term", values="hazard_ratio")
    piv = piv.reindex([f"{S[j]} to {S[k]}" for j, k in ALLOWED])
    age_cols = [c for c in piv.columns if c.startswith("age")]
    print(piv[age_cols + ["female", "college", "nonwhite"]].round(3).to_string())
    print(f"\n  likelihood-ratio test, full against base: {tab.loc[0, 'lr_test_vs_base']:,.1f} "
          f"on {int(tab.loc[0, 'lr_df'])} df")
    if m.se_robust_ is not None:
        ratio = m.se_robust_ / m.se_
        print(f"  cluster-robust SEs on {m.n_clusters_:,} households: ratio to model SEs "
              f"median {np.median(ratio):.2f}, range {ratio.min():.2f} to {ratio.max():.2f}")

    rows = []
    for female in (0, 1):
        z = [female, 0, 0]
        for age in (65, 75, 85):
            P = m.transition_matrix(age, 1.0, z)
            for j in range(len(config.LIVE_STATES)):
                rows.append({"sex": "female" if female else "male", "age": age,
                             "from": S[j], **{f"to_{S[k]}": P[j, k] for k in range(len(config.STATES))}})
    pd.DataFrame(rows).to_csv(config.TABLES / "table2b_annual_transition_probabilities.csv", index=False)

    rows = []
    for female in (0, 1):
        for college in (0, 1):
            for nonwhite in (0, 1):
                z = [female, college, nonwhite]
                for entry in range(len(config.LIVE_STATES)):
                    e, ins = life_expectancy(m, z, entry_state=entry)
                    rows.append({"sex": "female" if female else "male",
                                 "college": college, "nonwhite": nonwhite,
                                 "entry_state": S[entry], "life_expectancy_65": e,
                                 **{f"years_in_{S[k]}": ins[k] for k in range(len(config.LIVE_STATES))}})
    t2c = pd.DataFrame(rows)
    t2c.to_csv(config.TABLES / "table2c_health_expectancies.csv", index=False)
    print("\n=== Life expectancy at 65 by entry state (reference: no college, white) ===")
    ref = t2c[(t2c["college"] == 0) & (t2c["nonwhite"] == 0)]
    print(ref[["sex", "entry_state", "life_expectancy_65"]
              + [f"years_in_{s}" for s in config.LIVE_STATES]].round(2).to_string(index=False))
    print("\nwrote tables 2, 2b, 2c and msm_full.pkl")


if __name__ == "__main__":
    main()
