"""
State-specific annual costs by payer.

Out of pocket, from HRS. Each interview reports the respondent's out-of-pocket
medical spending over the previous two years (r*oopmd, RAND-imputed; it
excludes insurance premiums). Halved to an annual figure and deflated to 2024
dollars, it is attached to the state observed at that interview, by age band
and sex. Because the tail is what the paper is about, the whole weighted
distribution by state is kept, not only the mean: the microsimulation draws
from it.

End of life, from the HRS exit interview. Core interviews never see the months
before death, which are the most expensive. The exit interview with a proxy
reports out-of-pocket spending from the last core interview to death
(reoopmd). Its last-year amount is taken as reoopmd x min(1, 12 / months from
the last core interview to death), deflated to 2024 dollars, by age band at
death and sex. Exit interviews carry no analysis weight, so these draws are
unweighted. In the simulation the draw replaces the ordinary annual draw in
the year of death. Pro-rating a longer window evenly understates how much of
it falls in the final year, so the end-of-life cost is conservative.

Medicare, from the MCBS Cost Supplement (mcbs_costs.py). The PUF carries no
functional measure, so Medicare cost cannot be read off by state directly. It
is built from the PUF's age-by-chronic-condition cells and the observed mix of
chronic-condition bands within each HRS state. For the D and L states this is
a lower bound: the Cost Supplement excludes facility, hospice and
institutional events, which fall mostly in those states. That limitation is
carried into the write-up and tested in robustness with an uplift lever.

Writes Tables 3c (OOP distribution by state), 3d (Medicare by state) and 3e
(end-of-life OOP), and data/derived/oop_draws.pkl.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from population import person_weight

S = {0: "H", 1: "C", 2: "D", 3: "L"}
# HRS interview year -> CPI factor to 2024 dollars. CPI-U (World Bank
# FP.CPI.TOTL), fetched from api.worldbank.org on 14 September 2026; the same
# series as config.CPI_TO_BASE. RAND amounts are nominal for the recall
# window, taken here at the interview year.
CPI = {1998: 1.9244, 2000: 1.8217, 2002: 1.7439, 2004: 1.6608, 2006: 1.5561,
       2008: 1.4570, 2010: 1.4386, 2012: 1.3663, 2014: 1.3251, 2016: 1.3070,
       2018: 1.2492, 2020: 1.2120, 2022: 1.0719}


def wquantile(v, w, q):
    o = np.argsort(v)
    cw = np.cumsum(w[o]) / np.sum(w)
    return float(np.interp(q, cw, v[o]))


def state_costs(pw):
    """OOP distribution and Medicare cost by state from a person-wave file."""
    pw = pw[pw["state"].notna() & pw["oopmd"].notna() & (pw["age"] >= 65)].copy()
    pw["w"] = person_weight(pw)
    pw = pw[pw["w"] > 0]
    pw["year"] = 1992 + 2 * (pw["wave"] - 1)
    pw["oop_annual"] = pw["oopmd"] / 2.0 * pw["year"].map(CPI)
    pw["age_band"] = pd.cut(pw["age"], [65, 75, 200], right=False, labels=["65-74", "75+"])
    pw["state_lab"] = pw["state"].astype(int).map(S)

    rows, draws = [], {}
    for (st, ab, fem), g in pw.groupby(["state_lab", "age_band", "female"], observed=True):
        v, w = g["oop_annual"].to_numpy(float), g["w"].to_numpy(float)
        draws[f"{st}|{ab}|{'F' if fem else 'M'}"] = (v, w / w.sum())
        rows.append({"state": st, "age_band": ab, "sex": "female" if fem else "male",
                     "n": len(g), "oop_mean": np.average(v, weights=w),
                     "oop_zero_share": np.average(v == 0, weights=w),
                     **{f"oop_p{int(q * 100)}": wquantile(v, w, q) for q in (0.5, 0.9, 0.95, 0.99)}})
    t3c = pd.DataFrame(rows).sort_values(["state", "age_band", "sex"])

    # HRS counts eight "ever" conditions; MCBS bands are 0-1, 2-3 and 4+
    # ever-diagnosed conditions. The two condition lists differ, so the
    # mapping is by count only and is stated as an approximation.
    mc = pd.read_csv(config.TABLES / "table3a_mcbs_costs.csv").set_index("cell")
    cell = {}
    for ab, key in (("65-74", "65-74"), ("75+", "75 and over")):
        for band, lab in ((1, "0-1 chronic conditions"), (2, "2-3 chronic conditions"), (3, "4+ chronic conditions")):
            r = mc.loc[f"{key}, {lab}"]
            cell[(ab, band)] = (r["medicare_total_mean"], r["pamttot_mean"])
    pw["band"] = np.select([pw["n_conditions_ever"] <= 1, pw["n_conditions_ever"] <= 3], [1, 2], 3)
    rows = []
    for (st, ab), g in pw.groupby(["state_lab", "age_band"], observed=True):
        mix = g.groupby("band")["w"].sum()
        mix = mix / mix.sum()
        rows.append({"state": st, "age_band": str(ab), "weight": g["w"].sum(),
                     "share_0_1_conditions": mix.get(1, 0), "share_2_3": mix.get(2, 0), "share_4_plus": mix.get(3, 0),
                     "medicare_mix_only": sum(mix.get(b, 0) * cell[(str(ab), b)][0] for b in (1, 2, 3)),
                     "total_all_payers_annual": sum(mix.get(b, 0) * cell[(str(ab), b)][1] for b in (1, 2, 3)),
                     "hrs_oop_mean": np.average(g["oop_annual"], weights=g["w"])})
    t3d = pd.DataFrame(rows)
    # Level: HRS counts eight conditions and MCBS a longer list, so the count
    # mapping places HRS respondents in lighter MCBS bands than the Medicare
    # population they represent. The state relativities are kept and the
    # level in each age band is scaled so that the weighted HRS person-year
    # average equals the MCBS mean for that band.
    t3d["mcbs_scale_factor"] = 1.0
    for ab, key in (("65-74", "65-74"), ("75+", "75 and over")):
        sel = t3d["age_band"] == ab
        hrs_mean = np.average(t3d.loc[sel, "medicare_mix_only"], weights=t3d.loc[sel, "weight"])
        t3d.loc[sel, "mcbs_scale_factor"] = mc.loc[key, "medicare_total_mean"] / hrs_mean
    t3d["medicare_annual"] = t3d["medicare_mix_only"] * t3d["mcbs_scale_factor"]
    return t3c, draws, t3d


def end_of_life():
    d = pd.read_stata(config.HRS / "randhrs1992_2022v1.dta", convert_categoricals=False,
                      columns=["hhidpn", "ragender", "reoopmd", "rexityr", "radtimtdth", "radage_y"])
    for c in d.columns[1:]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[d["reoopmd"].notna() & d["rexityr"].isin(list(CPI)) & (d["radage_y"] >= 65)
          & d["radtimtdth"].notna()].copy()
    months = d["radtimtdth"].clip(lower=1.0)
    d["eol"] = d["reoopmd"] * np.minimum(1.0, 12.0 / months) * d["rexityr"].map(CPI)
    d["whole_window"] = d["reoopmd"] * d["rexityr"].map(CPI)
    d["age_band"] = np.where(d["radage_y"] < 75, "65-74", "75+")
    rows, draws = [], {}
    for (ab, sex), g in d.groupby(["age_band", "ragender"]):
        sk = "F" if sex == 2 else "M"
        v = g["eol"].to_numpy(float)
        draws[f"EOL|{ab}|{sk}"] = (v, np.full(len(v), 1.0 / len(v)))
        rows.append({"age_band": ab, "sex": "female" if sex == 2 else "male", "n": len(g),
                     "months_last_interview_to_death_median": float(g["radtimtdth"].median()),
                     "eol_mean": v.mean(), "eol_zero_share": float((v == 0).mean()),
                     **{f"eol_p{int(q * 100)}": float(np.quantile(v, q)) for q in (0.5, 0.9, 0.95, 0.99)},
                     "whole_window_mean": g["whole_window"].mean()})
    return pd.DataFrame(rows), draws


def main():
    pw = pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl")
    t3c, draws, t3d = state_costs(pw)
    t3e, eol = end_of_life()
    draws.update(eol)
    t3c.to_csv(config.TABLES / "table3c_oop_by_state.csv", index=False)
    t3d.to_csv(config.TABLES / "table3d_medicare_by_state.csv", index=False)
    t3e.to_csv(config.TABLES / "table3e_end_of_life_oop.csv", index=False)
    pd.to_pickle(draws, config.DERIVED / "oop_draws.pkl")

    with pd.option_context("display.width", 200, "display.float_format", "{:,.0f}".format):
        print("=== Annual out-of-pocket spending by state, HRS, 2024 dollars ===")
        print(t3c[["state", "age_band", "sex", "n", "oop_mean", "oop_p50", "oop_p90",
                   "oop_p95", "oop_p99"]].to_string(index=False))
        print("\n=== Out-of-pocket spending in the last year of life, HRS exit interviews ===")
        print(t3e.to_string(index=False))
    print("\n=== Medicare per beneficiary-year by state (MCBS cells x HRS chronic mix) ===")
    with pd.option_context("display.width", 200, "display.float_format", "{:,.2f}".format):
        print(t3d.to_string(index=False))
    print("\n  Medicare for D and L excludes facility, hospice and institutional events "
          "(MCBS Cost Supplement scope) and is a lower bound.")
    print("wrote tables 3c, 3d, 3e and oop_draws.pkl")


if __name__ == "__main__":
    main()
