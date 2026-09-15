"""
RQ4: what the Hospital Insurance financing gap would do to households.

The 2026 Trustees Report projects HI trust fund depletion in the second
quarter of 2033, after which incoming revenue covers 89% of scheduled Part A
benefits. The report's convention is to project benefits as if paid in full.
This module asks what happens to lifetime out-of-pocket cost if they are not.

Scenarios, applied to the simulated lives from simulate.py for a cohort
turning 65 in 2026 (so calendar year = 2026 + years since 65):

  S0  baseline: benefits paid in full
  S1  from 2033, Part A payments fall to the payable share; a fraction x of
      the shortfall becomes household out-of-pocket cost (x = 0 is a pure
      provider payment cut; x = 0.25, 0.5 and 1.0 are cost-shift cases)
  S2  from 2033, the shortfall is concentrated on the long-term-care state
      (skilled nursing and home health after hospital stays), where the full
      shortfall becomes out-of-pocket for people in L
  S3  higher real cost growth throughout, at the Trustees' Part B real per
      beneficiary rate, with S1 at x = 0.5

Part A's share of Medicare spending by state is the MCBS inpatient-plus-home-
health share of total spending, applied to the state's Medicare cost.

Spend-down: a household with positive assets at 65 whose cumulative
undiscounted out-of-pocket cost reaches those assets is counted as exhausting
them, a simple exposure measure with no asset returns, income or spouse.
Households with no positive assets at 65 are reported separately, since they
start at the point the others spend down to. Asset distributions at 65 come
from HRS household assets (h*atotb) by income tertile.

Writes Tables 6 (scenario mean and tail of lifetime OOP) and 6b (spend-down).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config

S = {0: "H", 1: "C", 2: "D", 3: "L"}
DEPLETION_OFFSET = config.HI_DEPLETION_YEAR - 2026        # years after 65 for the 2026 cohort
SHIFTS = (0.0, 0.25, 0.5, 1.0)


def cvar(x, level):
    q = np.quantile(x, level)
    return float(q), float(x[x >= q].mean())


def parta_share_by_state():
    t3d = pd.read_csv(config.TABLES / "table3d_medicare_by_state.csv")
    t3a = pd.read_csv(config.TABLES / "table3a_mcbs_costs.csv").set_index("cell")
    # weight the MCBS Part A shares by the chronic mix in each state and age band
    out = {}
    for _, r in t3d.iterrows():
        key = "65-74" if r["age_band"] == "65-74" else "75 and over"
        sh = (r["share_0_1_conditions"] * t3a.loc[f"{key}, 0-1 chronic conditions", "part_a_share_of_total"]
              + r["share_2_3"] * t3a.loc[f"{key}, 2-3 chronic conditions", "part_a_share_of_total"]
              + r["share_4_plus"] * t3a.loc[f"{key}, 4+ chronic conditions", "part_a_share_of_total"])
        out[(r["state"], r["age_band"])] = float(sh)
    return out


def assets_at_65():
    pw = pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl")
    e = pw[pw["age"].between(64, 66.99) & pw["hh_assets"].notna() & pw["hh_income"].notna()
           & (pw["wtresp"] > 0)].copy()
    from costs import CPI
    e["year"] = 1992 + 2 * (e["wave"] - 1)
    e["assets"] = e["hh_assets"] * e["year"].map(CPI)
    e["income"] = e["hh_income"] * e["year"].map(CPI)
    e["tertile"] = pd.qcut(e["income"].rank(method="first"), 3, labels=["low", "middle", "high"])
    return e[["tertile", "assets", "wtresp"]]


def main():
    store = pd.read_pickle(config.DERIVED / "sim_lives.pkl")
    pa = parta_share_by_state()
    rng = np.random.default_rng(config.SEED + 1)
    disc = config.PRIMARY_DISCOUNT
    growth_hi = config.TR_PER_BENEFICIARY_GROWTH_REAL["B"]
    n_years = config.MAX_AGE - config.ENTRY_AGE
    v = np.array([1 / (1 + disc) ** i for i in range(n_years)])

    rows = []
    for (sex, entry), r in store.items():
        oop, med, st = r["oop_by_year"], r["med_by_year"], r["state_by_year"]
        ages = np.arange(config.ENTRY_AGE, config.MAX_AGE)
        share = np.zeros_like(med)
        for i, a in enumerate(ages):
            band = "65-74" if a < 75 else "75+"
            for k in range(4):
                share[i, st[i] == k] = pa[(S[k], band)]
        parta = med * share
        shortfall = parta * (1 - config.HI_PAYABLE_SHARE_AT_DEPLETION)
        shortfall[:DEPLETION_OFFSET] = 0.0
        in_l = st == 3
        base_pv = (oop * v[:, None]).sum(axis=0)

        def record(label, pv):
            q95, c95 = cvar(pv, 0.95)
            q99, c99 = cvar(pv, 0.99)
            rows.append({"sex": sex, "entry_state": entry, "scenario": label,
                         "pv_oop_mean": pv.mean(), "pv_oop_median": np.median(pv),
                         "var95": q95, "cvar95": c95, "var99": q99, "cvar99": c99,
                         "mean_change_vs_s0": pv.mean() - base_pv.mean(),
                         "cvar95_change_vs_s0": c95 - cvar(base_pv, 0.95)[1]})

        record("S0 baseline", base_pv)
        for x in SHIFTS:
            pv = ((oop + x * shortfall) * v[:, None]).sum(axis=0)
            record(f"S1 Part A payable 89% from 2033, shift {int(100 * x)}%", pv)
        # S2: the whole cohort shortfall is borne by person-years in L (skilled
        # nursing and home health after hospital stays), as extra OOP.
        total_sf = shortfall.sum(axis=1, keepdims=True)              # by year
        n_l = np.maximum(in_l.sum(axis=1, keepdims=True), 1)
        extra_l = np.where(in_l, total_sf / n_l, 0.0)
        pv = ((oop + extra_l) * v[:, None]).sum(axis=0)
        record("S2 shortfall on long-term-care state", pv)
        g = np.array([(1 + growth_hi) ** i for i in range(n_years)])
        pv = ((oop + 0.5 * shortfall) * g[:, None] * v[:, None]).sum(axis=0)
        record(f"S3 real growth {100 * growth_hi:.1f}% and shift 50%", pv)
    t6 = pd.DataFrame(rows)
    t6.to_csv(config.TABLES / "table6_scenarios.csv", index=False)

    # Spend-down by income tertile, population-mix lives.
    assets = assets_at_65()
    rows = []
    for sex in ("male", "female"):
        r = store[(sex, "Population mix")]
        oop = r["oop_by_year"]
        for tert, g in assets.groupby("tertile", observed=True):
            a = rng.choice(g["assets"].to_numpy(float), size=oop.shape[1], p=(g["wtresp"] / g["wtresp"].sum()).to_numpy())
            st = r["state_by_year"]
            share = np.zeros_like(r["med_by_year"])
            for i, age in enumerate(range(config.ENTRY_AGE, config.MAX_AGE)):
                band = "65-74" if age < 75 else "75+"
                for k in range(4):
                    share[i, st[i] == k] = pa[(S[k], band)]
            sf = r["med_by_year"] * share * (1 - config.HI_PAYABLE_SHARE_AT_DEPLETION)
            sf[:DEPLETION_OFFSET] = 0
            pos = a > 0
            for label, extra in (("S0 baseline", 0.0), ("S1 shift 50%", 0.5)):
                cum = np.cumsum(oop + extra * sf, axis=0)
                hit = cum >= a[None, :]
                exhausted = hit.any(axis=0) & pos
                first = np.argmax(hit, axis=0)
                rows.append({"sex": sex, "income_tertile": str(tert), "scenario": label,
                             "median_assets_at_65": float(np.median(a)),
                             "pct_no_positive_assets": 100 * float((~pos).mean()),
                             "pct_exhausting_assets": 100 * float(exhausted[pos].mean()),
                             "median_age_at_exhaustion": (config.ENTRY_AGE + float(np.median(first[exhausted]))
                                                          if exhausted.any() else np.nan)})
    t6b = pd.DataFrame(rows)
    t6b.to_csv(config.TABLES / "table6b_spend_down.csv", index=False)

    print("=== Lifetime OOP under financing scenarios (population mix) ===")
    with pd.option_context("display.width", 220, "display.float_format", "{:,.0f}".format):
        print(t6[t6["entry_state"] == "Population mix"][["sex", "scenario", "pv_oop_mean", "cvar95",
              "mean_change_vs_s0", "cvar95_change_vs_s0"]].to_string(index=False))
    print("\n=== Share exhausting assets at 65 through out-of-pocket cost ===")
    with pd.option_context("display.width", 220, "display.float_format", "{:,.1f}".format):
        print(t6b.to_string(index=False))
    print("\nwrote tables 6 and 6b")


if __name__ == "__main__":
    main()
