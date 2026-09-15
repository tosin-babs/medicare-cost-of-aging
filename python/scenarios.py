"""
RQ4: what the Hospital Insurance financing gap would do to households.

The 2026 Trustees Report projects HI trust fund depletion in the second
quarter of 2033, after which income covers 89% of scheduled Part A benefits,
85% by 2050 and about 93% by 2100 (report pp. 14, 37). The report's
convention is to project benefits as if paid in full. These scenarios ask
what happens to households if they are not.

The share of Medicare spending that Part A pays is taken from the Trustees'
per-beneficiary figures for 2024: HI $6,256 of $17,837, or 35.1% (Table
V.D1). A lower bound using only the inpatient and home-health spending the
MCBS Cost Supplement can see is reported alongside; it misses skilled
nursing and hospice, which are Part A and fall on exactly the people in the
long-term-care states.

A trust-fund shortfall reaches households only through a channel: reduced
supplemental or Medicare Advantage benefits, higher cost sharing enacted
alongside a payment reduction, or care that is not delivered and is bought
privately. The shift parameter is the share of the shortfall that becomes
household spending; s = 0 is a pure provider payment cut, whose effect works
through access and is not modelled.

  S0   benefits paid in full, the Trustees' convention
  S1   the payable path from 2033, with share s of the shortfall shifted to
       households, for s = 0, 25%, 50% and 100%
  S1b  as S1 at s = 50% and 100%, with the community Part A share the Cost
       Supplement measures instead of the Trustees' HI share (lower bound)
  S2   the whole cohort shortfall falls on person-years in long-term care,
       as a cut concentrated on post-acute and long-term-care benefits would
  S3   S1 at s = 50% with real cost growth at the Trustees' Part B per
       beneficiary rate

Dual eligibles are not charged: Medicaid covers Medicare cost sharing for
them, which is also why the spend-down rule matters for who bears the gap.

Writes Tables 6 (scenarios) and 6b (spend-down and scenario effects by
income tertile).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
import simulate as sim
from population import entry_mix, entry_sample, load_model


def scenario_list(model, mix, bundle):
    """(label, kwargs for run_population) pairs."""
    hi = config.HI_SHARE_OF_MEDICARE
    t3a = pd.read_csv(config.TABLES / "table3a_mcbs_costs.csv").set_index("cell")
    hi_low = float(t3a.loc["All", "part_a_share_of_medicare"])
    out = [("S0 baseline", {})]
    for s in (0.0, 0.25, 0.5, 1.0):
        out.append((f"S1 shortfall from 2033, shift {int(100 * s)}%",
                    {"scenario": {"shift": s, "hi_share": hi}}))
    for s in (0.5, 1.0):
        out.append((f"S1b community Part A share {100 * hi_low:.0f}%, shift {int(100 * s)}%",
                    {"scenario": {"shift": s, "hi_share": hi_low}}))
    out.append(("S2 shortfall on long-term-care years",
                {"scenario": {"ltc_charge": sim.ltc_charge_schedule(model, mix, bundle, hi, 1.0),
                              "hi_share": hi}}))
    g = config.TR_PER_BENEFICIARY_GROWTH_REAL["B"]
    out.append((f"S3 real growth {100 * g:.1f}% and shift 50%",
                {"scenario": {"shift": 0.5, "hi_share": hi}, "growth": g}))
    return out


def main():
    model = load_model()
    sample = entry_sample()
    mix = entry_mix(sample=sample)
    bundle = sim.decedent_adjustment(model, mix, sim.cost_bundle())
    disc = config.PRIMARY_DISCOUNT
    n = config.N_SIMULATIONS
    scenarios = scenario_list(model, mix, bundle)

    rows, base = [], {}
    for sex in ("male", "female"):
        cache = {}
        for label, kw in scenarios:
            rng = np.random.default_rng(config.SEED + 5)      # common random numbers
            r = sim.run_population(model, sex, n, rng, bundle, disc, sample=sample,
                                   cache=cache, **kw)
            pv = r["pv_oop"]
            q95, c95 = sim.cvar(pv, 0.95)
            q99, c99 = sim.cvar(pv, 0.99)
            if label.startswith("S0"):
                base[sex] = (pv.mean(), c95, float(r["ever_medicaid"].mean()))
            rows.append({"sex": sex, "scenario": label, "pv_oop_mean": pv.mean(),
                         "pv_oop_median": np.median(pv), "var95": q95, "cvar95": c95,
                         "var99": q99, "cvar99": c99,
                         "pv_shortfall_mean": float(r["pv_shortfall"].mean()),
                         "ever_medicaid_pct": 100 * float(r["ever_medicaid"].mean()),
                         "mean_change_vs_s0": pv.mean() - base[sex][0],
                         "cvar95_change_vs_s0": c95 - base[sex][1],
                         "medicaid_change_pts": 100 * (float(r["ever_medicaid"].mean()) - base[sex][2])})
    t6 = pd.DataFrame(rows)
    t6.to_csv(config.TABLES / "table6_scenarios.csv", index=False)

    # --- spend-down and scenario effects by income tertile
    keep = ["S0 baseline", "S1 shortfall from 2033, shift 50%",
            "S2 shortfall on long-term-care years"]
    rows = []
    for sex in ("male", "female"):
        cache = {}
        for t in (0, 1, 2):
            for label, kw in [s for s in scenarios if s[0] in keep]:
                rng = np.random.default_rng(config.SEED + 6)
                r = sim.run_population(model, sex, n // 2, rng, bundle, disc, sample=sample,
                                       tertile=t, cache=cache, **kw)
                pv = r["pv_oop"]
                q95, c95 = sim.cvar(pv, 0.95)
                spent = r["ever_medicaid"] & (r["age_medicaid"] > config.ENTRY_AGE)
                rows.append({"sex": sex, "income_tertile": ["low", "middle", "high"][t],
                             "scenario": label, "pv_oop_mean": pv.mean(), "cvar95": c95,
                             "median_assets_at_65": float(np.median(r["assets"])),
                             "no_assets_at_65_pct": 100 * float((r["assets"] <= 0).mean()),
                             "medicaid_at_65_pct": 100 * float(
                                 np.isclose(r["age_medicaid"], config.ENTRY_AGE).mean()),
                             "ever_medicaid_pct": 100 * float(r["ever_medicaid"].mean()),
                             "spend_down_pct": 100 * float(spent.mean()),
                             "median_age_spend_down": float(np.nanmedian(
                                 np.where(spent, r["age_medicaid"], np.nan))) if spent.any() else np.nan,
                             "mean_years_ltc": float(r["years_ltc"].mean())})
    t6b = pd.DataFrame(rows)
    t6b.to_csv(config.TABLES / "table6b_spend_down.csv", index=False)

    with pd.option_context("display.width", 240, "display.float_format", "{:,.0f}".format):
        print("=== Lifetime out-of-pocket cost under financing scenarios (population mix) ===")
        print(t6[["sex", "scenario", "pv_oop_mean", "cvar95", "cvar99", "mean_change_vs_s0",
                  "cvar95_change_vs_s0", "ever_medicaid_pct", "medicaid_change_pts"]].to_string(index=False))
        print("\n=== Spend-down by income tertile ===")
        print(t6b[["sex", "income_tertile", "scenario", "median_assets_at_65", "no_assets_at_65_pct",
                   "medicaid_at_65_pct", "ever_medicaid_pct", "spend_down_pct",
                   "median_age_spend_down", "pv_oop_mean", "cvar95"]].to_string(index=False))
    print("\nwrote tables 6 and 6b")


if __name__ == "__main__":
    main()
