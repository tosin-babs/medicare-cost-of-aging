"""
Extensions to the transition model, each a refit of the full model with one
more term, reported as a likelihood-ratio test, hazard ratios and the change
in life expectancy at 65:

  income     household income tertile at the start of the interval (low and
             high against middle), ranked within interview wave and ten-year
             age group with the analysis weight
  duration   an indicator that the person was already in the starting state
             at the previous interview (at least one interval, about two
             years, in the state), a first-order check on the Markov
             assumption; zero at a person's first interview
  age2       a quadratic age term, ((age - 65)/10)^2, on top of the
             spline in age
  period     calendar time, (interview year - 2010)/10, for trend in the
             intensities over 1998 to 2022

    ../.venv/bin/python python/fit_extensions.py income     # one extension
    ../.venv/bin/python python/fit_extensions.py            # all, in sequence

Writes table2d_extension_<name>.csv per extension and, when all four exist,
table2d_model_extensions.csv.
"""

from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

import config
from fit_transitions import ALLOWED, COV_FULL, S, life_expectancy
from multistate import MultiStateMarkov
from population import person_weight

EXT = {"income": ["low_income", "high_income"], "duration": ["same_state_prev"],
       "age2": ["age2"], "period": ["period"]}


def weighted_tertile(g):
    o = np.argsort(g["hh_income"].to_numpy(float), kind="stable")
    w = g["w"].to_numpy(float)[o]
    cum = (np.cumsum(w) - 0.5 * w) / w.sum()
    out = np.empty(len(g), dtype=int)
    out[o] = np.minimum((cum * 3).astype(int), 2)
    return pd.Series(out, index=g.index)


def extended_intervals():
    iv = pd.read_pickle(config.DERIVED / "hrs_intervals.pkl")
    pw = pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl")
    pw = pw[pw["state"].notna()].sort_values(["hhidpn", "t"]).copy()
    pw["w"] = person_weight(pw)
    pw["prev_state"] = pw.groupby("hhidpn")["state"].shift(1)
    pw["same_state_prev"] = (pw["prev_state"] == pw["state"]).astype(int)
    pw["ageband10"] = (pw["age"] // 10).astype(int)
    ok = pw["hh_income"].notna() & (pw["w"] > 0)
    pw["tert"] = np.nan
    pw.loc[ok, "tert"] = pw[ok].groupby(["wave", "ageband10"], group_keys=False).apply(weighted_tertile)
    pw["tert"] = pw["tert"].fillna(1)          # missing income or weight: middle
    pw["low_income"] = (pw["tert"] == 0).astype(int)
    pw["high_income"] = (pw["tert"] == 2).astype(int)
    pw["period"] = (pw["iwendy"] - 2010) / 10.0
    pw["t_start"] = pw["t"].round(6)
    iv["t_start"] = iv["t_start"].round(6)
    keep = ["hhidpn", "t_start", "same_state_prev", "low_income", "high_income", "period"]
    iv = iv.merge(pw[keep], on=["hhidpn", "t_start"], how="left")
    assert iv["period"].notna().all(), "interval start not matched to an interview"
    iv["same_state_prev"] = iv["same_state_prev"].fillna(0)
    iv["age2"] = ((iv["age_start"] + iv["duration"] / 2 - 65) / 10) ** 2
    return iv


def fit_one(name, iv, full_loglik):
    cov = COV_FULL + EXT[name]
    t0 = time.time()
    m = MultiStateMarkov(len(config.STATES), ALLOWED, covariates=cov, age_knots=config.AGE_KNOTS,
                         max_piece=config.MAX_PIECE_YEARS).fit(iv, robust_se=False)
    print(f"  {name}: {m.method_}, converged {m.converged_}, loglik {m.loglik_:,.1f}, "
          f"{len(m.theta_)} params, {time.time() - t0:.0f}s", flush=True)
    tab = m.coef_table()
    tab["transition"] = tab["parameter"].str.extract(r"q(\d)(\d)").apply(
        lambda r: f"{S[int(r[0])]} to {S[int(r[1])]}", axis=1)
    tab["term"] = tab["parameter"].str.split(":").str[1]
    tab = tab[tab["term"].isin(EXT[name])].copy()
    tab["extension"] = name
    tab["loglik"] = m.loglik_
    tab["lr_test_vs_full"] = 2 * (m.loglik_ - full_loglik)
    tab["df"] = 12 * len(EXT[name])
    # life expectancy at 65 for reference men and women at each level of the
    # new term (age2 and duration enter through the intensities directly)
    levels = {"income": {"low": [1, 0], "middle": [0, 0], "high": [0, 1]},
              "duration": {"new to state": [0], "in state at previous interview": [1]},
              "age2": {"quadratic age": None},
              "period": {"1998": [-1.2], "2010": [0.0], "2022": [1.2]}}[name]
    rows = []
    for fem in (0, 1):
        for lab, zx in levels.items():
            z = [fem, 0, 0] + (zx if zx is not None else [])
            if name == "age2":
                e = _e65_quadratic(m, z)
            else:
                e, _ = life_expectancy(m, z, entry_state=1)
            rows.append({"extension": name, "sex": "female" if fem else "male", "level": lab,
                         "e65_from_C": e})
    return tab, pd.DataFrame(rows)


def _e65_quadratic(m, z):
    """Life expectancy when a covariate is a function of age (age2)."""
    K = len(config.STATES)
    p = np.zeros(K); p[1] = 1.0
    years = 0.0
    for a in range(65, config.MAX_AGE):
        zz = z + [((a + 0.5 - 65) / 10) ** 2]
        P = m.transition_matrix(a, 1.0, zz)
        pn = p @ P
        years += 0.5 * (p[:K - 1].sum() + pn[:K - 1].sum())
        p = pn
    return years


def combine():
    parts, e65 = [], []
    for name in EXT:
        f = config.TABLES / f"table2d_extension_{name}.csv"
        if f.exists():
            parts.append(pd.read_csv(f))
            e65.append(pd.read_csv(config.TABLES / f"table2d_extension_{name}_e65.csv"))
    if len(parts) == len(EXT):
        pd.concat(parts).to_csv(config.TABLES / "table2d_model_extensions.csv", index=False)
        pd.concat(e65).to_csv(config.TABLES / "table2d_model_extensions_e65.csv", index=False)
        print("wrote table2d_model_extensions.csv")


def main():
    names = sys.argv[1:] or list(EXT)
    iv = extended_intervals()
    print(f"{len(iv):,} intervals; low/high income {iv['low_income'].mean():.3f}/{iv['high_income'].mean():.3f}; "
          f"same state at previous interview {iv['same_state_prev'].mean():.3f}", flush=True)
    full_loglik = pd.read_pickle(config.DERIVED / "msm_full.pkl")["loglik"]
    for name in names:
        tab, e65 = fit_one(name, iv, full_loglik)
        tab.to_csv(config.TABLES / f"table2d_extension_{name}.csv", index=False)
        e65.to_csv(config.TABLES / f"table2d_extension_{name}_e65.csv", index=False)
        with pd.option_context("display.width", 200):
            print(tab[["transition", "term", "hazard_ratio", "hr_lo", "hr_hi"]].round(3).to_string(index=False))
            print(f"  LR test against the full model: {tab['lr_test_vs_full'].iloc[0]:,.1f} on {tab['df'].iloc[0]} df")
            print(e65.round(2).to_string(index=False), flush=True)
    combine()


if __name__ == "__main__":
    main()
