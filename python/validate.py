"""
Validation of the fitted model against external benchmarks.

  mortality    life expectancy at 65 and one-year death probabilities for the
               HRS entry mix, uncalibrated and calibrated, against the 2023 US
               period life table (NCHS NVSR 74-6). The uncalibrated gap is
               the honest test of the fitted model; the calibrated one shows
               the calibration did its job.
  prevalence   the calibrated model's state distribution by age against the
               weighted cross-sectional HRS distribution at ages 65 and over,
               nursing-home residents included through their weight, the
               standard prevalence check for panel multi-state models. The
               model follows a cohort from 65 while the cross-section pools
               1998 to 2022, so close but not exact agreement is expected.

Writes Tables 7 (mortality), 7q (one-year qx) and 7b (prevalence).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
import population as pop
from simulate import AGES, annual_matrices

S = {0: "H", 1: "C", 2: "D", 3: "L"}


def main():
    raw, cal = pop.load_model(calibrated=False), pop.load_model()
    mix = pop.entry_mix()
    lt = pd.read_csv(config.DERIVED / "lifetable_us_2023.csv")
    rows_m, rows_q = [], []
    for sex in ("male", "female"):
        t = lt[lt["sex"] == sex].set_index("age")
        e_raw, q_raw = pop.life_table(raw, mix, sex)
        e_cal, q_cal = pop.life_table(cal, mix, sex)
        e_lt = float(t.loc[65, "ex"])
        rows_m.append({"sex": sex, "model_e65_uncalibrated": e_raw, "model_e65": e_cal,
                       "life_table_e65_2023": e_lt, "difference_uncalibrated": e_raw - e_lt,
                       "difference_years": e_cal - e_lt})
        for a in (65, 70, 75, 80, 85, 90, 95):
            rows_q.append({"sex": sex, "age": a, "model_qx_uncalibrated": q_raw[a], "model_qx": q_cal[a],
                           "life_table_qx": float(t.loc[a, "qx"])})
    t7 = pd.DataFrame(rows_m)
    t7.to_csv(config.TABLES / "table7_mortality_validation.csv", index=False)
    t7q = pd.DataFrame(rows_q)
    t7q.to_csv(config.TABLES / "table7_qx_validation.csv", index=False)

    pw = pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl")
    pw = pw[pw["state"].notna() & (pw["age"] >= 65)].copy()
    pw["w"] = pop.person_weight(pw)
    pw = pw[pw["w"] > 0]
    bands = [(65, 70), (70, 75), (75, 80), (80, 85), (85, 90), (90, 100)]
    rows, prev_all = [], {}
    for sex in ("male", "female"):
        fem = int(sex == "female")
        prev = np.zeros((len(AGES), 4))
        prev_all[sex] = prev
        starts = {}
        for s, z, w in mix[sex]:
            starts.setdefault(tuple(z), np.zeros(5))[s] += w
        for z, p in starts.items():
            P = annual_matrices(cal, list(z))
            for i, a in enumerate(AGES):
                prev[i] += p[:4]
                p = p @ P[a]
        for lo, hi in bands:
            g = pw[(pw["female"] == fem) & pw["age"].between(lo, hi - 0.001)]
            w = g.groupby(g["state"].astype(int))["w"].sum()
            obs = (w / w.sum()).reindex(range(4), fill_value=0).to_numpy()
            mod = prev[lo - config.ENTRY_AGE:hi - config.ENTRY_AGE].sum(axis=0)
            mod = mod / mod.sum()
            for k in range(4):
                rows.append({"sex": sex, "age_band": f"{lo}-{hi - 1}", "state": S[k],
                             "observed_pct": 100 * obs[k], "model_pct": 100 * mod[k], "n": len(g)})
    t7b = pd.DataFrame(rows)
    t7b.to_csv(config.TABLES / "table7b_prevalence_validation.csv", index=False)

    # Spending: the model cohort's Medicare per surviving person-year by age
    # band, both sexes starting in equal numbers, against the MCBS mean.
    t3d = pd.read_csv(config.TABLES / "table3d_medicare_by_state.csv")
    med = {(r["state"], r["age_band"]): r["medicare_annual"] for _, r in t3d.iterrows()}
    raw = {(r["state"], r["age_band"]): r["medicare_mix_only"] for _, r in t3d.iterrows()}
    t3a = pd.read_csv(config.TABLES / "table3a_mcbs_costs.csv").set_index("cell")
    rows = []
    for band, lo, hi, cell in (("65-74", 65, 75, "65-74"), ("75+", 75, config.MAX_AGE, "75 and over")):
        occ = sum(prev_all[s][lo - config.ENTRY_AGE:hi - config.ENTRY_AGE].sum(axis=0) for s in prev_all)
        model = float(sum(occ[k] * med[(S[k], band)] for k in range(4)) / occ.sum())
        before = float(sum(occ[k] * raw[(S[k], band)] for k in range(4)) / occ.sum())
        rows.append({"age_band": band, "model_before_scaling": before,
                     "ratio_before_scaling": before / float(t3a.loc[cell, "medicare_total_mean"]),
                     "model_medicare_per_person_year": model,
                     "mcbs_medicare_mean": float(t3a.loc[cell, "medicare_total_mean"]),
                     "mcbs_se": float(t3a.loc[cell, "medicare_total_se"]),
                     "ratio": model / float(t3a.loc[cell, "medicare_total_mean"])})
    t7d = pd.DataFrame(rows)
    t7d.to_csv(config.TABLES / "table7d_spending_validation.csv", index=False)

    print("=== Life expectancy at 65: model against the 2023 US life table ===")
    print(t7.round(2).to_string(index=False))
    print("\n=== One-year death probability ===")
    print(t7q.round(4).to_string(index=False))
    print("\n=== State prevalence by age band, observed HRS against calibrated model (percent) ===")
    piv = t7b.pivot_table(index=["sex", "age_band"], columns="state", values=["observed_pct", "model_pct"])
    print(piv.round(1).to_string())
    print("\n=== Medicare per person-year: model cohort against MCBS ===")
    print(t7d.round(3).to_string(index=False))
    print("\nwrote tables 7, 7q, 7b, 7d")


if __name__ == "__main__":
    main()
