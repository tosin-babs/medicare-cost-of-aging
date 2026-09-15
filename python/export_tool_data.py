"""
Export the payload for the public cost-of-aging calculator.

The page answers: from my health at 65, how many years should I expect in
each health state, what will Medicare and I pay over my remaining life, how
bad is the bad case, and what happens if the Hospital Insurance shortfall is
passed on. Everything comes from aggregate tables and binned simulation
output; no HRS record leaves the pipeline (HRS conditions of use).

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


def _f(x, d=0):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return None
    return round(float(x), d) if d else int(round(float(x)))


def main():
    t4 = pd.read_csv(T / "table4_lifetime_costs.csv")
    t5 = pd.read_csv(T / "table5_tail_risk.csv")
    t6 = pd.read_csv(T / "table6_scenarios.csv")
    t6b = pd.read_csv(T / "table6b_spend_down.csv")
    t7 = pd.read_csv(T / "table7_mortality_validation.csv")
    lives = pd.read_pickle(config.DERIVED / "sim_lives.pkl")

    payload = {
        "meta": {"generated": date.today().isoformat(),
                 "dollars": "2024 dollars, present value at 65 discounted at 3%",
                 "sources": "RAND HRS Longitudinal File 1992-2022 (V1); MCBS Cost Supplement PUF 2019, 2021-2023; "
                            "2026 Medicare Trustees Report; NCHS United States Life Tables, 2023",
                 "paper": "Health-State Transitions and the Lifetime Cost of Aging in Medicare",
                 "author": "Oluwatosin Dorcas Babalola",
                 "repository": "https://github.com/tosin-babs/medicare-cost-of-aging",
                 "depletion": config.HI_DEPLETION, "payable": config.HI_PAYABLE_SHARE_AT_DEPLETION,
                 "n_lives": int(config.N_SIMULATIONS)},
        "states": {k: config.STATE_LABELS[k] for k in ("H", "C", "D", "L")},
        "expectancy": [{"sex": r["sex"], "entry": r["entry_state"], "e65": _f(r["life_expectancy"], 1),
                        "years": {s: _f(r[f"years_in_{s}"], 2) for s in ("H", "C", "D", "L")}}
                       for _, r in t4.iterrows()],
        "lifetime": [{"sex": r["sex"], "entry": r["entry_state"], "e65": _f(r["life_expectancy"], 1),
                      "ever_ltc": _f(r["ever_ltc_pct"], 1), "medicare": _f(r["pv_medicare_mean"]),
                      "oop_mean": _f(r["pv_oop_mean"]), "oop_median": _f(r["pv_oop_median"]),
                      "premium": _f(r["pv_premium_mean"]), "eol": _f(r["pv_eol_increment_mean"])}
                     for _, r in t4.iterrows()],
        "tail": [{"sex": r["sex"], "entry": r["entry_state"], "level": _f(r["level"], 2), "var": _f(r["var"]),
                  "cvar": _f(r["cvar"]), "ltc_in_tail": _f(r["share_of_tail_ever_ltc_pct"], 1)}
                 for _, r in t5.iterrows()],
        "scenarios": [{"sex": r["sex"], "entry": r["entry_state"], "scenario": r["scenario"],
                       "mean": _f(r["pv_oop_mean"]), "cvar95": _f(r["cvar95"]),
                       "d_mean": _f(r["mean_change_vs_s0"]), "d_cvar95": _f(r["cvar95_change_vs_s0"])}
                      for _, r in t6.iterrows()],
        "spend_down": [{"sex": r["sex"], "tertile": r["income_tertile"], "scenario": r["scenario"],
                        "assets": _f(r["median_assets_at_65"]), "nopos": _f(r["pct_no_positive_assets"], 1),
                        "pct": _f(r["pct_exhausting_assets"], 1), "age": _f(r["median_age_at_exhaustion"])}
                       for _, r in t6b.iterrows()],
        "mortality_check": [{"sex": r["sex"], "fitted": _f(r["model_e65_uncalibrated"], 1),
                             "model": _f(r["model_e65"], 1), "life_table": _f(r["life_table_e65_2023"], 1)}
                            for _, r in t7.iterrows()],
    }
    # Binned distribution of lifetime OOP by sex and entry state, so the page
    # can draw it without any per-life data.
    edges = np.arange(0, 305, 10)
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
        print(f"  {r['sex']}: e65 {r['life_expectancy']:.1f}, PV Medicare ${r['pv_medicare_mean']:,.0f}, "
              f"PV OOP ${r['pv_oop_mean']:,.0f}, Part B premium ${r['pv_premium_mean']:,.0f}")
    for _, r in t5[(t5["entry_state"] == "Population mix") & (t5["level"] == 0.95)].iterrows():
        print(f"  {r['sex']}: CVaR95 OOP ${r['cvar']:,.0f}")


if __name__ == "__main__":
    main()
