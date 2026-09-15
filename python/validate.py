"""
Validation of the fitted model against external benchmarks.

  mortality    life expectancy at 65 and one-year death probabilities for the
               HRS entry mix, before and after calibration, against the 2023
               US period life table (NCHS NVSR 74-6). The uncalibrated gap is
               the test of the fitted model; the calibrated one shows the
               calibration did its job.
  prevalence   the calibrated model's state distribution by age against the
               weighted HRS cross-section at ages 65 and over, nursing-home
               residents included through their own weight. The model follows
               a cohort from 65 while the cross-section pools 2006 to 2022, so
               close but not exact agreement is expected.
  Medicaid     the model's share of long-term-care person-years on Medicaid
               against the HRS share, which tests the spend-down rule.
  spending     the cohort's Medicare per person-year against the MCBS mean
               (a consistency check, since the level is scaled to it) and
               against the Trustees' per-beneficiary figure, which is not.
  literature   lifetime and end-of-life out-of-pocket spending against
               published estimates, on the same basis where possible.

Writes Tables 7 (mortality), 7q (qx), 7b (prevalence), 7d (spending),
7e (literature) and 7h (Medicaid).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
import costs as costmod
import population as pop
import simulate as sim

S = dict(enumerate(config.STATES))
LIVE = len(config.STATES) - 1
LTC = [config.STATES.index(s) for s in config.LTC_STATES]

# Published estimates, on the basis each is stated on. The conversion to 2024
# dollars uses the CPI-U factors in costs.CPI.
PUBLISHED = [
    {"source": "Jones et al. (2018)", "quantity": "Lifetime medical spending from 70, mean",
     "published": 122000, "dollar_year": 2014,
     "basis": "per household, includes Medicaid payments, PV at 3%"},
    {"source": "Jones et al. (2018)", "quantity": "Lifetime medical spending from 70, 95th percentile",
     "published": 300000, "dollar_year": 2014,
     "basis": "per household, includes Medicaid payments, PV at 3%"},
    {"source": "Kelley et al. (2013)", "quantity": "Out-of-pocket spending in the last five years of life, mean",
     "published": 38688, "dollar_year": 2008, "basis": "per individual, includes insurance premiums"},
    {"source": "Kelley et al. (2013)", "quantity": "Out-of-pocket spending in the last five years of life, median",
     "published": 22885, "dollar_year": 2008, "basis": "per individual, includes insurance premiums"},
    {"source": "Marshall et al. (2011)", "quantity": "Out-of-pocket spending in the last year of life, mean",
     "published": 11618, "dollar_year": 2008,
     "basis": "per individual, HRS 1998-2006; the source's dollar year is not stated"},
    {"source": "Marshall et al. (2011)", "quantity": "Out-of-pocket spending in the last year of life, 95th percentile",
     "published": 49907, "dollar_year": 2008,
     "basis": "per individual, HRS 1998-2006; the source's dollar year is not stated"},
    {"source": "Hurd et al. (2017)", "quantity": "Ever a nursing-home stay",
     "published": 56.0, "dollar_year": None, "basis": "percent, from ages 57-61; the model starts at 65"},
    {"source": "Hurd et al. (2017)", "quantity": "Lifetime nursing-home out-of-pocket spending, mean",
     "published": 7300, "dollar_year": 2014, "basis": "per person from 57, PV at 3%; zero for most"},
]


def model_counterparts(store):
    """The same quantities from the simulated lives, in 2024 dollars."""
    out = {}
    for sex in ("male", "female"):
        r = store[(sex, "Population mix")]
        oop, da = r["oop_by_year"].astype(float), r["death_age"]
        st = r["state_by_year"]
        idx = np.clip((da - config.ENTRY_AGE - 0.5).round().astype(int), 0, oop.shape[0] - 1)
        cols = np.arange(oop.shape[1])
        v70 = np.array([1 / 1.03 ** i for i in range(oop.shape[0] - 5)])
        alive70 = da > 70
        pv70 = (oop[5:, alive70] * v70[:, None]).sum(axis=0)
        last5 = np.array([oop[max(0, i - 4):i + 1, j].sum() for j, i in enumerate(idx)])
        last1 = oop[idx, cols]
        in_n = st == config.STATES.index("N")
        v = np.array([1 / 1.03 ** i for i in range(oop.shape[0])])
        pv_nh = (np.where(in_n, oop, 0.0) * v[:, None]).sum(axis=0)
        prem5 = 5 * sim.PREMIUM
        out[sex] = {
            "Lifetime medical spending from 70, mean": pv70.mean(),
            "Lifetime medical spending from 70, 95th percentile": np.percentile(pv70, 95),
            "Out-of-pocket spending in the last five years of life, mean": last5.mean() + prem5,
            "Out-of-pocket spending in the last five years of life, median": np.median(last5) + prem5,
            "Out-of-pocket spending in the last year of life, mean": last1.mean(),
            "Out-of-pocket spending in the last year of life, 95th percentile": np.percentile(last1, 95),
            "Ever a nursing-home stay": 100 * float(in_n.any(axis=0).mean()),
            "Lifetime nursing-home out-of-pocket spending, mean": pv_nh.mean(),
        }
    return out


def main():
    raw, cal = pop.load_model(calibrated=False), pop.load_model()
    sample = pop.entry_sample()
    mix = pop.entry_mix(sample=sample)
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
            rows_q.append({"sex": sex, "age": a, "model_qx_uncalibrated": q_raw[a],
                           "model_qx": q_cal[a], "life_table_qx": float(t.loc[a, "qx"]),
                           "ratio_to_life_table": q_cal[a] / float(t.loc[a, "qx"])})
    t7 = pd.DataFrame(rows_m)
    t7.to_csv(config.TABLES / "table7_mortality_validation.csv", index=False)
    t7q = pd.DataFrame(rows_q)
    t7q.to_csv(config.TABLES / "table7_qx_validation.csv", index=False)

    # --- prevalence
    pw = pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl")
    obs = pw[pw["state"].notna() & (pw["age"] >= 65) & (pw["wave"] >= config.OOP_MIN_WAVE)].copy()
    obs["w"] = pop.person_weight(obs)
    obs = obs[obs["w"] > 0]
    bands = [(65, 70), (70, 75), (75, 80), (80, 85), (85, 90), (90, 100)]
    rows, prev_all = [], {}
    for sex in ("male", "female"):
        fem = int(sex == "female")
        prev = np.zeros((len(sim.AGES), LIVE))
        prev_all[sex] = prev
        starts = {}
        for s, z, w in mix[sex]:
            starts.setdefault(tuple(z), np.zeros(len(config.STATES)))[s] += w
        for z, p in starts.items():
            P = sim.annual_matrices(cal, list(z))
            for i, a in enumerate(sim.AGES):
                prev[i] += p[:LIVE]
                p = p @ P[a]
        for lo, hi in bands:
            g = obs[(obs["female"] == fem) & obs["age"].between(lo, hi - 0.001)]
            w = g.groupby(g["state"].astype(int))["w"].sum()
            o = (w / w.sum()).reindex(range(LIVE), fill_value=0).to_numpy()
            mod = prev[lo - config.ENTRY_AGE:hi - config.ENTRY_AGE].sum(axis=0)
            mod = mod / mod.sum()
            for k in range(LIVE):
                rows.append({"sex": sex, "age_band": f"{lo}-{hi - 1}", "state": S[k],
                             "observed_pct": 100 * o[k], "model_pct": 100 * mod[k],
                             "difference_pts": 100 * (mod[k] - o[k]), "n": len(g)})
    t7b = pd.DataFrame(rows)
    t7b.to_csv(config.TABLES / "table7b_prevalence_validation.csv", index=False)

    # --- spending
    t3d = pd.read_csv(config.TABLES / "table3d_medicare_by_state.csv")
    med = {(r["state"], r["age_band"]): r["medicare_annual"] for _, r in t3d.iterrows()}
    rawm = {(r["state"], r["age_band"]): r["medicare_mix_only"] for _, r in t3d.iterrows()}
    t3a = pd.read_csv(config.TABLES / "table3a_mcbs_costs.csv").set_index("cell")
    rows = []
    for band, lo, hi, cell in (("65-74", 65, 75, "65-74"), ("75+", 75, config.MAX_AGE, "75 and over")):
        occ = sum(prev_all[s][lo - config.ENTRY_AGE:hi - config.ENTRY_AGE].sum(axis=0) for s in prev_all)
        model = float(sum(occ[k] * med[(S[k], band)] for k in range(LIVE)) / occ.sum())
        before = float(sum(occ[k] * rawm[(S[k], band)] for k in range(LIVE)) / occ.sum())
        rows.append({"age_band": band, "model_before_scaling": before,
                     "model_medicare_per_person_year": model,
                     "mcbs_medicare_mean": float(t3a.loc[cell, "medicare_total_mean"]),
                     "mcbs_se": float(t3a.loc[cell, "medicare_total_se"]),
                     "ratio_to_mcbs": model / float(t3a.loc[cell, "medicare_total_mean"]),
                     "trustees_per_beneficiary_2024": config.TR_PER_BENEFICIARY_2024["total"],
                     "ratio_to_trustees": model / config.TR_PER_BENEFICIARY_2024["total"]})
    t7d = pd.DataFrame(rows)
    t7d.to_csv(config.TABLES / "table7d_spending_validation.csv", index=False)

    # --- Medicaid: model against HRS
    store = pd.read_pickle(config.DERIVED / "sim_lives.pkl")
    obs_ltc = obs[obs["state"].isin(LTC)]
    obs_share = 100 * float(np.average(
        pd.to_numeric(obs_ltc["govmd"], errors="coerce").fillna(0) == 1, weights=obs_ltc["w"]))
    rows = []
    for sex in ("male", "female"):
        r = store[(sex, "Population mix")]
        in_ltc = np.isin(r["state_by_year"], LTC)
        rows.append({"sex": sex,
                     "model_ltc_person_years_on_medicaid_pct": 100 * float(r["medicaid_by_year"][in_ltc].mean()),
                     "hrs_ltc_person_years_on_medicaid_pct": obs_share,
                     "model_ever_medicaid_pct": 100 * float(r["ever_medicaid"].mean()),
                     "model_medicaid_at_65_pct": 100 * float(
                         np.isclose(r["age_medicaid"], config.ENTRY_AGE).mean())})
    t7h = pd.DataFrame(rows)
    t7h.to_csv(config.TABLES / "table7h_medicaid_validation.csv", index=False)

    # --- published comparisons
    counter = model_counterparts(store)
    rows = []
    for p in PUBLISHED:
        f = 1.0 if p["dollar_year"] is None else costmod.CPI[p["dollar_year"]]
        rows.append({**p, "published_2024_dollars": p["published"] * f,
                     "model_male": counter["male"][p["quantity"]],
                     "model_female": counter["female"][p["quantity"]]})
    t7e = pd.DataFrame(rows)
    t7e.to_csv(config.TABLES / "table7e_literature_comparison.csv", index=False)

    print("=== Life expectancy at 65: model against the 2023 US life table ===")
    print(t7.round(2).to_string(index=False))
    print("\n=== One-year death probability ===")
    print(t7q.round(4).to_string(index=False))
    print("\n=== State prevalence by age band (percent of survivors) ===")
    print(t7b.pivot_table(index=["sex", "age_band"], columns="state",
                          values=["observed_pct", "model_pct"]).round(1).to_string())
    with pd.option_context("display.width", 240, "display.float_format", "{:,.2f}".format):
        print("\n=== Medicare per person-year: model, MCBS and Trustees ===")
        print(t7d.to_string(index=False))
        print("\n=== Medicaid in the long-term-care states ===")
        print(t7h.to_string(index=False))
    with pd.option_context("display.width", 260, "display.float_format", "{:,.0f}".format):
        print("\n=== Against published estimates ===")
        print(t7e[["source", "quantity", "published", "dollar_year", "published_2024_dollars",
                   "model_male", "model_female"]].to_string(index=False))
    print("\nwrote tables 7, 7q, 7b, 7d, 7e, 7h")


if __name__ == "__main__":
    main()
