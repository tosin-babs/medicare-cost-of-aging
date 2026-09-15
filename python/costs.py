"""
State-specific annual costs by payer, and the persistence of out-of-pocket
spending from year to year.

Out of pocket, from HRS. Each interview reports the respondent's out-of-pocket
medical spending since the last interview, or over the previous two years for
new respondents (RAND RwOOPMD). From wave 6 it is the sum of hospital,
nursing-home, doctor, dentist, outpatient-surgery, prescription-drug,
home-health and special-facility costs; insurance premiums are not included,
and neither is the "other" category RAND added at wave 10. Halved to an annual
figure and deflated to 2024 dollars, it is attached to the state observed at
that interview, by age band, sex, Medicaid enrolment and household income
tertile. Waves before 2006 are dropped: they precede Part D, and mean annual
spending in the chronic state at 65 to 74 was $3,465 in 2004 against $1,263 in
2022 in 2024 dollars.

Because the tail is what the paper is about, the whole weighted distribution
is kept rather than the mean, and two features of it are modelled that
independent annual draws would miss:

  persistence   normal-score correlation of spending two waves apart is about
                0.51 within the same state, and 0.35 at eight years, which is
                a permanent component plus a decaying one. Both are estimated
                here and used by the simulation's copula.
  Medicaid      Medicaid pays most long-term-care costs for those enrolled:
                in the nursing-home state its recipients' mean is a fraction
                of the private payer's. Draws are split accordingly, and the
                simulation moves a life onto Medicaid when it spends down.

End of life, from the HRS exit interview. Core interviews never see the months
before death. The exit interview with a proxy reports out-of-pocket spending
from the last core interview to death (REOOPMD, which includes hospice and is
imputed for about a third of decedents). Its last-year amount is taken as
REOOPMD x min(1, 12 / months since the last interview), by age band, sex and
whether the person was in long-term care at the last interview. Pro-rating a
longer window evenly understates the final year, so this is conservative.

Medicare, from the MCBS Cost Supplement (mcbs_costs.py). The PUF carries no
functional measure, so Medicare cost by state is built from its
age-by-chronic-condition cells and the condition mix within each HRS state,
with the level in each age band scaled to the MCBS mean. The gradient across
states therefore reflects condition counts only; the disability and
long-term-care states are also short of the facility, hospice and
institutional events the Cost Supplement excludes. Both limitations are
carried into the write-up and tested in robustness.

Writes Tables 3c (OOP by state), 3d (Medicare by state), 3e (end of life),
3f (Medicaid) and 3g (persistence), and data/derived/oop_draws.pkl.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.stats import norm, rankdata

import config
from population import person_weight, weighted_tertile

S = dict(enumerate(config.STATES))
LIVE = config.LIVE_STATES
# HRS interview year -> CPI factor to 2024 dollars. CPI-U (World Bank
# FP.CPI.TOTL), fetched from api.worldbank.org on 14 September 2026; the same
# series as config.CPI_TO_BASE. RAND amounts are nominal for the recall
# window, taken here at the interview year.
CPI = {1998: 1.9244, 2000: 1.8217, 2002: 1.7439, 2004: 1.6608, 2006: 1.5561,
       2008: 1.4570, 2010: 1.4386, 2012: 1.3663, 2014: 1.3251, 2016: 1.3070,
       2018: 1.2492, 2020: 1.2120, 2022: 1.0719}
BANDS = ("65-74", "75+")
MIN_CELL = 150          # smallest cell that gets its own draw distribution


def wquantile(v, w, q):
    o = np.argsort(v)
    cw = np.cumsum(w[o]) / np.sum(w)
    return float(np.interp(q, cw, v[o]))


def band_of(age):
    return np.where(np.asarray(age) < 75, BANDS[0], BANDS[1])


def oop_key(state, band, sex, medicaid=None, tertile=None):
    k = f"{state}|{band}|{sex}"
    if medicaid is None:
        return k
    k += "|mcd" if medicaid else "|nom"
    return k if tertile is None else f"{k}|t{tertile}"


def prepare(pw, min_wave=None):
    """Person-waves at 65 and over with annual out-of-pocket spending."""
    min_wave = config.OOP_MIN_WAVE if min_wave is None else min_wave
    pw = pw[pw["state"].notna() & pw["oopmd"].notna() & (pw["age"] >= 65)
            & (pw["wave"] >= min_wave)].copy()
    pw["w"] = person_weight(pw)
    pw = pw[pw["w"] > 0].copy()
    pw["year"] = 1992 + 2 * (pw["wave"] - 1)
    cpi = pw["year"].map(CPI)
    pw["oop_annual"] = pw["oopmd"] / 2.0 * cpi
    pw["income_real"] = pd.to_numeric(pw["hh_income"], errors="coerce") * cpi
    pw["age_band"] = band_of(pw["age"])
    pw["state_lab"] = pw["state"].astype(int).map(S)
    pw["sex"] = np.where(pw["female"] == 1, "F", "M")
    pw["medicaid"] = (pd.to_numeric(pw["govmd"], errors="coerce") == 1).astype(int)
    pw["tertile"] = -1
    for _, g in pw.groupby(["wave", "age_band"]):
        ok = g["income_real"].notna()
        if ok.any():
            pw.loc[g.index[ok], "tertile"] = weighted_tertile(g.loc[ok, "income_real"], g.loc[ok, "w"])
    return pw


def state_costs(pw, medicare_col="medicare_total_mean", scale=None, min_wave=None):
    """OOP draw distributions and Medicare cost by state."""
    pw = prepare(pw, min_wave)
    rows, draws = [], {}
    for (st, ab, sx), g in pw.groupby(["state_lab", "age_band", "sex"], observed=True):
        v, w = g["oop_annual"].to_numpy(float), g["w"].to_numpy(float)
        draws[oop_key(st, ab, sx)] = (v, w / w.sum())
        for mcd in (0, 1):
            h = g[g["medicaid"] == mcd]
            if len(h) >= MIN_CELL:
                vv, ww = h["oop_annual"].to_numpy(float), h["w"].to_numpy(float)
                draws[oop_key(st, ab, sx, mcd)] = (vv, ww / ww.sum())
            if mcd == 0:
                for t in (0, 1, 2):
                    q = h[h["tertile"] == t]
                    if len(q) >= MIN_CELL:
                        vv, ww = q["oop_annual"].to_numpy(float), q["w"].to_numpy(float)
                        draws[oop_key(st, ab, sx, 0, t)] = (vv, ww / ww.sum())
        rows.append({"state": st, "age_band": ab, "sex": "female" if sx == "F" else "male",
                     "n": len(g), "oop_mean": np.average(v, weights=w),
                     "oop_zero_share": np.average(v == 0, weights=w),
                     **{f"oop_p{int(q * 100)}": wquantile(v, w, q) for q in (0.5, 0.9, 0.95, 0.99)},
                     "medicaid_pct": 100 * np.average(g["medicaid"], weights=w)})
    t3c = pd.DataFrame(rows).sort_values(["state", "age_band", "sex"])

    # HRS counts eight "ever" conditions; MCBS bands are 0-1, 2-3 and 4+
    # ever-diagnosed conditions. The two condition lists differ, so the
    # mapping is by count only and is stated as an approximation.
    mc = pd.read_csv(config.TABLES / "table3a_mcbs_costs.csv").set_index("cell")
    cell = {}
    for ab, key in ((BANDS[0], "65-74"), (BANDS[1], "75 and over")):
        for band, lab in ((1, "0-1 chronic conditions"), (2, "2-3 chronic conditions"),
                          (3, "4+ chronic conditions")):
            r = mc.loc[f"{key}, {lab}"]
            cell[(ab, band)] = (r[medicare_col], r["pamttot_mean"])
    pw["band"] = np.select([pw["n_conditions_ever"] <= 1, pw["n_conditions_ever"] <= 3], [1, 2], 3)
    rows = []
    for (st, ab), g in pw.groupby(["state_lab", "age_band"], observed=True):
        mix = g.groupby("band")["w"].sum()
        mix = mix / mix.sum()
        rows.append({"state": st, "age_band": ab, "weight": g["w"].sum(),
                     "share_0_1_conditions": mix.get(1, 0), "share_2_3": mix.get(2, 0),
                     "share_4_plus": mix.get(3, 0),
                     "medicare_mix_only": sum(mix.get(b, 0) * cell[(ab, b)][0] for b in (1, 2, 3)),
                     "total_all_payers_annual": sum(mix.get(b, 0) * cell[(ab, b)][1] for b in (1, 2, 3)),
                     "hrs_oop_mean": np.average(g["oop_annual"], weights=g["w"])})
    t3d = pd.DataFrame(rows)
    # Level: HRS counts eight conditions and MCBS a longer list, so the count
    # mapping places HRS respondents in lighter MCBS cells than the Medicare
    # population they represent. State relativities are kept and the level in
    # each age band is scaled so the weighted HRS person-year average equals
    # the MCBS mean. The factors are computed once on the whole sample and
    # passed to subgroup calls, so that subgroups keep their level differences.
    t3d["mcbs_scale_factor"] = 1.0
    for ab, key in ((BANDS[0], "65-74"), (BANDS[1], "75 and over")):
        sel = t3d["age_band"] == ab
        if scale is None:
            hrs_mean = np.average(t3d.loc[sel, "medicare_mix_only"], weights=t3d.loc[sel, "weight"])
            f = mc.loc[key, medicare_col] / hrs_mean
        else:
            f = scale[ab]
        t3d.loc[sel, "mcbs_scale_factor"] = f
    t3d["medicare_annual"] = t3d["medicare_mix_only"] * t3d["mcbs_scale_factor"]
    # Medicare spending is higher for low-income beneficiaries in the MCBS
    # income cells; the factor is applied to the lowest income tertile.
    lo = np.average([mc.loc[f"65+, {n} chronic conditions, Income $25,000 or less", medicare_col]
                     for n in ("0-1", "2-3", "4+")],
                    weights=[mc.loc[f"65+, {n} chronic conditions, Income $25,000 or less", "n"]
                             for n in ("0-1", "2-3", "4+")])
    hi = np.average([mc.loc[f"65+, {n} chronic conditions, Income over $25,000", medicare_col]
                     for n in ("0-1", "2-3", "4+")],
                    weights=[mc.loc[f"65+, {n} chronic conditions, Income over $25,000", "n"]
                             for n in ("0-1", "2-3", "4+")])
    t3d["income_factor_low_tertile"] = lo / hi
    return t3c, draws, t3d


def end_of_life(pw, min_year=2006):
    """Out-of-pocket spending in the last year of life, from exit interviews."""
    d = pd.read_stata(config.HRS / "randhrs1992_2022v1.dta", convert_categoricals=False,
                      columns=["hhidpn", "ragender", "reoopmd", "reoopmdf", "rexityr",
                               "radtimtdth", "radage_y"])
    for c in d.columns[1:]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[d["reoopmd"].notna() & d["rexityr"].isin(list(CPI)) & (d["rexityr"] >= min_year)
          & (d["radage_y"] >= 65) & d["radtimtdth"].notna()].copy()
    # State at the last core interview: long-term care (L or N) or not.
    last = (pw[pw["state"].notna()].sort_values(["hhidpn", "t"])
            .groupby("hhidpn")["state"].last())
    ltc_codes = [config.STATES.index(s) for s in config.LTC_STATES]
    d["group"] = np.where(d["hhidpn"].map(last).isin(ltc_codes), "ltc", "other")
    months = d["radtimtdth"].clip(lower=1.0)
    d["eol"] = d["reoopmd"] * np.minimum(1.0, 12.0 / months) * d["rexityr"].map(CPI)
    d["whole_window"] = d["reoopmd"] * d["rexityr"].map(CPI)
    d["age_band"] = band_of(d["radage_y"])
    d["sex"] = np.where(d["ragender"] == 2, "F", "M")
    rows, draws = [], {}
    for (ab, sx), g in d.groupby(["age_band", "sex"]):
        v = g["eol"].to_numpy(float)
        draws[f"EOL|{ab}|{sx}"] = (v, np.full(len(v), 1.0 / len(v)))
    for (grp, ab, sx), g in d.groupby(["group", "age_band", "sex"]):
        v = g["eol"].to_numpy(float)
        if len(g) >= MIN_CELL:
            draws[f"EOL|{grp}|{ab}|{sx}"] = (v, np.full(len(v), 1.0 / len(v)))
        rows.append({"group": grp, "age_band": ab, "sex": "female" if sx == "F" else "male",
                     "n": len(g), "imputed_share": float(g["reoopmdf"].fillna(0).mean()),
                     "months_last_interview_to_death_median": float(g["radtimtdth"].median()),
                     "eol_mean": v.mean(), "eol_zero_share": float((v == 0).mean()),
                     **{f"eol_p{int(q * 100)}": float(np.quantile(v, q)) for q in (0.5, 0.9, 0.95, 0.99)},
                     "whole_window_mean": g["whole_window"].mean()})
    return pd.DataFrame(rows).sort_values(["group", "age_band", "sex"]), draws


def persistence(pw):
    """Permanent-plus-decaying correlation of out-of-pocket ranks over time.

    Normal scores are taken within state, age band and wave, so the estimate
    is of the correlation that survives the state path. corr(k years) is
    fitted as c + (1 - c) phi^k over lags of 2, 4, 6 and 8 years."""
    q = prepare(pw).sort_values(["hhidpn", "wave"]).copy()
    q["cell"] = q["state_lab"] + "|" + q["age_band"] + "|" + q["wave"].astype(str)
    q["ns"] = q.groupby("cell")["oop_annual"].transform(
        lambda v: pd.Series(norm.ppf((rankdata(v) - 0.5) / len(v)), index=v.index))
    lags, obs = [], []
    for lag in (1, 2, 3, 4):
        prev = q.groupby("hhidpn")["ns"].shift(lag)
        prev_w = q.groupby("hhidpn")["wave"].shift(lag)
        m = (q["wave"] - prev_w == lag) & prev.notna() & q["ns"].notna()
        if m.sum() > 500:
            lags.append(2 * lag)
            obs.append({"lag_years": 2 * lag, "n": int(m.sum()),
                        "correlation": float(np.corrcoef(q.loc[m, "ns"], prev[m])[0, 1])})
    y = np.array([o["correlation"] for o in obs])
    k = np.array(lags, float)
    fit = least_squares(lambda p: (p[0] + (1 - p[0]) * np.clip(p[1], 0, 0.999) ** k) - y,
                        x0=[0.3, 0.6], bounds=([0, 0], [0.95, 0.999]))
    c, phi = float(fit.x[0]), float(fit.x[1])
    out = pd.DataFrame(obs)
    out["fitted"] = c + (1 - c) * phi ** out["lag_years"]
    out["permanent_share"] = c
    out["annual_decay"] = phi
    return out, {"permanent": c, "phi": phi}


def medicaid_and_oop(pw):
    """Medicaid coverage by state and the out-of-pocket distribution with and
    without it, which is what the tail of the long-term-care states turns on."""
    pw = prepare(pw)
    rows = []
    for (st, ab), g in pw.groupby(["state_lab", "age_band"], observed=True):
        row = {"state": st, "age_band": ab, "n": len(g),
               "medicaid_pct": 100 * np.average(g["medicaid"], weights=g["w"])}
        for lab, sel in (("all", slice(None)), ("no_medicaid", g["medicaid"] == 0),
                         ("medicaid", g["medicaid"] == 1)):
            h = g if lab == "all" else g[sel]
            if len(h) >= 30:
                v, w = h["oop_annual"].to_numpy(float), h["w"].to_numpy(float)
                row[f"oop_mean_{lab}"] = np.average(v, weights=w)
                row[f"oop_p90_{lab}"] = wquantile(v, w, 0.9)
                row[f"oop_p99_{lab}"] = wquantile(v, w, 0.99)
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    pw = pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl")
    t3c, draws, t3d = state_costs(pw)
    t3e, eol = end_of_life(pw)
    t3f = medicaid_and_oop(pw)
    t3g, pers = persistence(pw)
    draws.update(eol)
    t3c.to_csv(config.TABLES / "table3c_oop_by_state.csv", index=False)
    t3d.to_csv(config.TABLES / "table3d_medicare_by_state.csv", index=False)
    t3e.to_csv(config.TABLES / "table3e_end_of_life_oop.csv", index=False)
    t3f.to_csv(config.TABLES / "table3f_medicaid_by_state.csv", index=False)
    t3g.to_csv(config.TABLES / "table3g_oop_persistence.csv", index=False)
    pd.to_pickle(draws, config.DERIVED / "oop_draws.pkl")
    (config.DERIVED / "oop_persistence.json").write_text(json.dumps(pers, indent=2))

    with pd.option_context("display.width", 220, "display.float_format", "{:,.0f}".format):
        print("=== Annual out-of-pocket spending by state, HRS 2006-2022, 2024 dollars ===")
        print(t3c[["state", "age_band", "sex", "n", "oop_mean", "oop_p50", "oop_p90",
                   "oop_p95", "oop_p99", "medicaid_pct"]].to_string(index=False))
        print("\n=== Out-of-pocket spending in the last year of life (exit interviews) ===")
        print(t3e.to_string(index=False))
        print("\n=== Medicaid and the out-of-pocket distribution ===")
        print(t3f.to_string(index=False))
    print("\n=== Persistence of out-of-pocket ranks ===")
    print(t3g.round(3).to_string(index=False))
    print(f"  permanent share {pers['permanent']:.3f}, annual decay {pers['phi']:.3f}")
    print("\n=== Medicare per beneficiary-year by state (MCBS cells x HRS condition mix) ===")
    with pd.option_context("display.width", 220, "display.float_format", "{:,.2f}".format):
        print(t3d.to_string(index=False))
    print("\n  Medicare for the disability and long-term-care states excludes facility, "
          "hospice and institutional events (MCBS Cost Supplement scope) and is a lower bound.")
    print("wrote tables 3c to 3g and oop_draws.pkl")


if __name__ == "__main__":
    main()
