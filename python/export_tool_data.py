"""
Export the payload for the public cost-of-aging calculator.

The page answers: from my health at 65, how long should I expect to live and
how much of it in long-term care, what will Medicare and I pay over my
remaining life, how bad is the bad case, how likely am I to end up on
Medicaid, and what happens if the Hospital Insurance shortfall is passed on.
Everything comes from aggregate tables and binned simulation output; no HRS
record leaves the pipeline (HRS conditions of use).

Writes tool/model_data.json and prints the reference values the page must show.
"""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd

import config

OUT = config.ROOT / "tool" / "model_data.json"
T = config.TABLES
LAB = config.STATE_LABELS


def _f(x, d=0):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return None
    return round(float(x), d) if d else int(round(float(x)))


def main():
    t4 = pd.read_csv(T / "table4_lifetime_costs.csv")
    t4c = pd.read_csv(T / "table4c_lifetime_by_income.csv")
    t5 = pd.read_csv(T / "table5_tail_risk.csv")
    t6 = pd.read_csv(T / "table6_scenarios.csv")
    t6b = pd.read_csv(T / "table6b_spend_down.csv")
    t7 = pd.read_csv(T / "table7_mortality_validation.csv")
    t7e = pd.read_csv(T / "table7e_literature_comparison.csv")
    lives = pd.read_pickle(config.DERIVED / "sim_lives.pkl")
    t2c = pd.read_csv(T / "table2c_health_expectancies.csv")

    entries = [LAB[s] for s in config.LIVE_STATES] + ["Population mix"]
    payload = {
        "meta": {"generated": date.today().isoformat(),
                 "dollars": "2024 dollars, present value at 65 discounted at 3%",
                 "sources": "RAND HRS Longitudinal File 1992-2022 (V1); MCBS Cost Supplement PUF 2019, 2021-2023; "
                            "2026 Medicare Trustees Report; NCHS United States Life Tables, 2023",
                 "paper": "Health-State Transitions and the Lifetime Cost of Aging",
                 "author": "Oluwatosin Dorcas Babalola, Oluwakemi Elizabeth Iroko, Doris Ansah",
                 "repository": "https://github.com/tosin-babs/medicare-cost-of-aging",
                 "depletion": config.HI_DEPLETION,
                 "payable_path": {str(k): v for k, v in config.HI_PAYABLE_PATH.items()},
                 "hi_share": round(config.HI_SHARE_OF_MEDICARE, 3),
                 "asset_limit": config.MEDICAID_ASSET_LIMIT,
                 "n_lives": int(config.N_SIMULATIONS)},
        "entries": entries,
        "states": {s: LAB[s] for s in config.LIVE_STATES},
        "lifetime": [{"sex": r["sex"], "entry": r["entry_state"], "e65": _f(r["life_expectancy"], 1),
                      "ever_ltc": _f(r["ever_ltc_pct"], 1), "years_ltc": _f(r["years_ltc"], 1),
                      "ever_medicaid": _f(r["ever_medicaid_pct"], 1), "medicare": _f(r["pv_medicare_mean"]),
                      "oop_mean": _f(r["pv_oop_mean"]), "oop_median": _f(r["pv_oop_median"]),
                      "premium": _f(r["pv_premium_mean"])}
                     for _, r in t4.iterrows()],
        "income": [{"sex": r["sex"], "tertile": r["income_tertile"], "e65": _f(r["life_expectancy"], 1),
                    "ever_ltc": _f(r["ever_ltc_pct"], 1), "ever_medicaid": _f(r["ever_medicaid_pct"], 1),
                    "oop_mean": _f(r["pv_oop_mean"]), "cvar95": _f(r["cvar95"]),
                    "median_assets": _f(r["median_assets"])}
                   for _, r in t4c.iterrows()],
        "tail": [{"sex": r["sex"], "entry": r["entry_state"], "level": _f(r["level"], 2), "var": _f(r["var"]),
                  "cvar": _f(r["cvar"]), "ltc_in_tail": _f(r["share_of_tail_ever_ltc_pct"], 1),
                  "years_ltc_in_tail": _f(r["mean_years_ltc_in_tail"], 1)}
                 for _, r in t5.iterrows()],
        "scenarios": [{"sex": r["sex"], "scenario": r["scenario"], "mean": _f(r["pv_oop_mean"]),
                       "cvar95": _f(r["cvar95"]), "d_mean": _f(r["mean_change_vs_s0"]),
                       "d_cvar95": _f(r["cvar95_change_vs_s0"])}
                      for _, r in t6.iterrows()],
        "spend_down": [{"sex": r["sex"], "tertile": r["income_tertile"], "scenario": r["scenario"],
                        "assets": _f(r["median_assets_at_65"]), "medicaid65": _f(r["medicaid_at_65_pct"], 1),
                        "spend_down": _f(r["spend_down_pct"], 1), "ever": _f(r["ever_medicaid_pct"], 1),
                        "age": _f(r["median_age_spend_down"])}
                       for _, r in t6b.iterrows()],
        "mortality_check": [{"sex": r["sex"], "fitted": _f(r["model_e65_uncalibrated"], 1),
                             "model": _f(r["model_e65"], 1), "life_table": _f(r["life_table_e65_2023"], 1)}
                            for _, r in t7.iterrows()],
        "literature": [{"source": r["source"], "quantity": r["quantity"], "basis": r["basis"],
                        "published": _f(r["published_2024_dollars"]), "male": _f(r["model_male"]),
                        "female": _f(r["model_female"])}
                       for _, r in t7e.iterrows()],
    }
    # Years in each state by entry state, reference covariates, from the fitted
    # model (Table A6); the population-mix row weights them by the entry mix.
    ref = t2c[(t2c["college"] == 0) & (t2c["nonwhite"] == 0)]
    payload["years"] = [{"sex": r["sex"], "entry": LAB[r["entry_state"]],
                         "years": {s: _f(r[f"years_in_{s}"], 2) for s in config.LIVE_STATES}}
                        for _, r in ref.iterrows()]

    edges = np.arange(0, 405, 10)
    hist = {}
    for (sex, entry), r in lives.items():
        pv = np.clip(r["pv_oop"] / 1000, 0, edges[-1] - 1e-9)
        counts, _ = np.histogram(pv, bins=edges)
        hist[f"{sex}|{entry}"] = (counts / counts.sum()).round(5).tolist()
    payload["oop_histogram"] = {"edges_k": edges.tolist(), "top_bin_open": True, "share": hist}
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"wrote {OUT.relative_to(config.ROOT)} ({OUT.stat().st_size / 1024:,.0f} KB)")
    print("\nReference values the page must reproduce:")
    for _, r in t4[t4["entry_state"] == "Population mix"].iterrows():
        print(f"  {r['sex']}: e65 {r['life_expectancy']:.1f}, ever LTC {r['ever_ltc_pct']:.1f}%, "
              f"ever Medicaid {r['ever_medicaid_pct']:.1f}%, PV Medicare ${r['pv_medicare_mean']:,.0f}, "
              f"PV OOP ${r['pv_oop_mean']:,.0f}, premiums ${r['pv_premium_mean']:,.0f}")
    for _, r in t5[(t5["entry_state"] == "Population mix") & (t5["level"] == 0.95)].iterrows():
        print(f"  {r['sex']}: CVaR95 OOP ${r['cvar']:,.0f}")


if __name__ == "__main__":
    main()
