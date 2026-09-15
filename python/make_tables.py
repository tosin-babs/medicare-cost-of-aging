"""
Render the manuscript's tables from the analysis CSVs. Manuscript numbering
follows reading order; the CSV each table comes from is named in its block.
Writes manuscript/tables.md.
"""

from __future__ import annotations

import pandas as pd

import config

OUT = config.ROOT / "manuscript" / "tables.md"
T = config.TABLES
LAB = config.STATE_LABELS
ORDER = {"H": 0, "C": 1, "D": 2, "L": 3, "Population mix": 4}


def num(d=2):
    return lambda x: "" if pd.isna(x) else f"{x:,.{d}f}"


def dollars(d=0):
    return lambda x: "" if pd.isna(x) else (f"-${abs(x):,.{d}f}" if round(x, d) < 0 else f"${x:,.{d}f}")


def pct(d=1):
    return lambda x: "" if pd.isna(x) else f"{x:,.{d}f}%"


def value(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return v
    return f"{x:,.0f}" if x.is_integer() else f"{x:,.1f}"


def render(df, cols, fmts, headers=None):
    out = pd.DataFrame({c: (df[c].map(f) if f else df[c].astype(str)) for c, f in zip(cols, fmts)})
    out.columns = headers or cols
    align = ["---" if i == 0 else "---:" for i in range(len(out.columns))]
    lines = ["| " + " | ".join(out.columns) + " |", "|" + "|".join(align) + "|"]
    lines += ["| " + " | ".join(str(v) for v in r) + " |" for _, r in out.iterrows()]
    return "\n".join(lines)


def caption(n, title, note=None):
    return f"\n**Table {n}.** {title}\n" + (f"\n*{note}*\n" if note else "")


def state_label(s):
    return LAB.get(s, s)


def by_state(df, col="state", extra=()):
    return df.assign(_o=df[col].map(ORDER)).sort_values(["_o", *extra]).drop(columns="_o")


def main():
    parts = ["# Tables\n",
             "*Generated from `output/tables/*.csv` by `python/make_tables.py`. Dollar amounts are 2024 "
             "dollars; present values are discounted at 3% a year to age 65. HRS estimates use the "
             "respondent analysis weight, or the nursing-home resident weight for residents; MCBS "
             "estimates use the Cost Supplement weight with Fay-adjusted balanced repeated replication.*\n"]

    # --- Table 1: sample
    t = pd.read_csv(T / "table1_sample.csv")
    t["value"] = t["value"].map(value)
    parts += [caption(1, "The HRS panel, waves 4 to 16 (1998 to 2022), respondents aged 50 and over."),
              render(t, ["quantity", "value"], [None, None], ["Quantity", "Value"])]

    # --- Table 2: intensities
    t = pd.read_csv(T / "table2_intensities.csv")
    lr = t["lr_test_vs_base"].dropna()
    t["term"] = t["term"].replace({"intercept": "log rate at 65", "age_per_10y": "age, per 10 years",
                                   "college": "any college", "nonwhite": "nonwhite or Hispanic"})
    note = ("Log-linear intensities fitted by maximum likelihood to interval-censored transitions. "
            "Reference: male, no college, non-Hispanic white, age 65. Hazard ratios with 95% intervals from "
            "the inverse observed information.")
    if len(lr):
        note += f" Likelihood-ratio test of the education and race-ethnicity terms: {lr.iloc[0]:,.1f} on 24 degrees of freedom."
    parts += [caption(2, "Transition intensities among health states.", note),
              render(t, ["transition", "term", "estimate", "se", "hazard_ratio", "hr_lo", "hr_hi"],
                     [None, None, num(3), num(3), num(2), num(2), num(2)],
                     ["Transition", "Term", "Estimate", "SE", "Hazard ratio", "95% low", "95% high"])]

    # --- Table 3: mortality validation and calibration
    t7 = pd.read_csv(T / "table7_mortality_validation.csv")
    t7c = pd.read_csv(T / "table7c_mortality_calibration.csv")
    t7 = t7.merge(t7c[["sex", "death_multiplier_at_65", "death_multiplier_at_75", "death_multiplier_at_85",
                       "death_multiplier_at_95"]], on="sex")
    q = pd.read_csv(T / "table7_qx_validation.csv")
    parts += [caption(3, "Mortality: the fitted model, the calibrated model and the 2023 US period life table.",
                      "Entry mix of HRS respondents aged 64 to 66. The multiplier scales death intensities from "
                      "every live state and equals exp(c0 + c1 (age - 65)/10) at the calibrated values."),
              render(t7, ["sex", "model_e65_uncalibrated", "model_e65", "life_table_e65_2023",
                          "death_multiplier_at_65", "death_multiplier_at_75", "death_multiplier_at_85", "death_multiplier_at_95"],
                     [None, num(2), num(2), num(2), num(2), num(2), num(2), num(2)],
                     ["Sex", "e65, fitted", "e65, calibrated", "e65, life table", "Multiplier at 65", "75", "85", "95"]),
              "",
              render(q, ["sex", "age", "model_qx_uncalibrated", "model_qx", "life_table_qx"],
                     [None, num(0), num(4), num(4), num(4)],
                     ["Sex", "Age", "qx, fitted", "qx, calibrated", "qx, life table"])]

    # --- Table 4: annual costs by state
    t3d = by_state(pd.read_csv(T / "table3d_medicare_by_state.csv"), extra=["age_band"])
    t3d["state_label"] = t3d["state"].map(state_label)
    parts += [caption(4, "Annual cost by health state and age band: Medicare and out of pocket.",
                      "Medicare: MCBS Cost Supplement cells (age by chronic-condition count) weighted by each HRS "
                      "state's condition-count mix; it excludes facility, hospice and institutional events and is a "
                      "lower bound for the disability and long-term-care states. Out of pocket: HRS, annualized "
                      "from the two-year recall, premiums excluded."),
              render(t3d, ["state_label", "age_band", "share_0_1_conditions", "share_2_3", "share_4_plus",
                           "medicare_annual", "hrs_oop_mean"],
                     [None, None, num(2), num(2), num(2), dollars(), dollars()],
                     ["State", "Age", "Share 0-1 conditions", "2-3", "4+", "Medicare", "Out of pocket, mean"])]
    t3c = by_state(pd.read_csv(T / "table3c_oop_by_state.csv"), extra=["age_band", "sex"])
    t3c["state_label"] = t3c["state"].map(state_label)
    parts += [caption("4b", "The annual out-of-pocket distribution by state, age band and sex (HRS core interviews)."),
              render(t3c, ["state_label", "age_band", "sex", "n", "oop_mean", "oop_p50", "oop_p90", "oop_p95", "oop_p99"],
                     [None, None, None, num(0), dollars(), dollars(), dollars(), dollars(), dollars()],
                     ["State", "Age", "Sex", "n", "Mean", "p50", "p90", "p95", "p99"])]
    t3e = pd.read_csv(T / "table3e_end_of_life_oop.csv")
    parts += [caption("4c", "Out-of-pocket spending in the last year of life (HRS exit interviews).",
                      "Spending from the last core interview to death, pro-rated to twelve months where that window "
                      "is longer. Unweighted; age band at death."),
              render(t3e, ["age_band", "sex", "n", "months_last_interview_to_death_median", "eol_mean", "eol_p50",
                           "eol_p90", "eol_p95", "eol_p99", "whole_window_mean"],
                     [None, None, num(0), num(0), dollars(), dollars(), dollars(), dollars(), dollars(), dollars()],
                     ["Age at death", "Sex", "n", "Months, median", "Mean", "p50", "p90", "p95", "p99", "Whole window, mean"])]

    # --- Table 5: lifetime cost
    t4 = pd.read_csv(T / "table4_lifetime_costs.csv")
    u = pd.read_csv(T / "table4b_parameter_uncertainty.csv")
    t4 = by_state(t4.merge(u, on=["sex", "entry_state"], how="left"), col="entry_state", extra=[])
    t4 = t4.sort_values("sex", kind="stable", key=lambda s: s.map({"male": 0, "female": 1}))
    t4["entry_label"] = t4["entry_state"].map(state_label)
    parts += [caption(5, "Expected lifetime cost from age 65 by sex and health state at 65, present value at 3%.",
                      f"{config.N_SIMULATIONS:,} simulated lives per row, calibrated mortality. Intervals are the 2.5th "
                      "and 97.5th percentiles of the analytic expected value over 200 draws of the transition "
                      "parameters. The analytic column is the forward recursion the simulation mean must match."),
              render(t4, ["sex", "entry_label", "life_expectancy", "ever_ltc_pct", "pv_medicare_mean", "pv_medicare_lo",
                          "pv_medicare_hi", "pv_oop_mean", "pv_oop_analytic", "pv_oop_lo", "pv_oop_hi", "pv_oop_median",
                          "pv_premium_mean"],
                     [None, None, num(1), pct(1), dollars(), dollars(), dollars(), dollars(), dollars(), dollars(),
                      dollars(), dollars(), dollars()],
                     ["Sex", "State at 65", "e65", "Ever LTC need", "Medicare", "low", "high", "Out of pocket",
                      "analytic", "low", "high", "OOP median", "Part B premium"])]
    parts += [caption("5b", "Expected years in each health state from 65, and the end-of-life component of out-of-pocket cost."),
              render(t4, ["sex", "entry_label", "life_expectancy", "years_in_H", "years_in_C", "years_in_D", "years_in_L",
                          "pv_eol_increment_mean"],
                     [None, None, num(1), num(1), num(1), num(1), num(1), dollars()],
                     ["Sex", "State at 65", "e65", "Healthy", "Chronic illness", "Disability", "LTC need",
                      "End-of-life increment, PV"])]
    inc = T / "table4c_lifetime_by_income.csv"
    if inc.exists():
        t = pd.read_csv(inc)
        parts += [caption("5c", "Lifetime cost and tail risk by household income tertile at 65, population mix.",
                          "Income tertiles within interview wave and age group. Out-of-pocket draws come from the same "
                          "tertile at every age. The transition model has no income term, so life-expectancy "
                          "differences by income are understated."),
                  render(t, ["sex", "income_tertile", "entry_share_H_pct", "entry_share_L_pct", "any_college_pct",
                             "life_expectancy", "ever_ltc_pct", "pv_medicare_mean", "pv_oop_mean", "pv_oop_median",
                             "cvar95", "cvar99"],
                         [None, None, pct(1), pct(1), pct(0), num(1), pct(1), dollars(), dollars(), dollars(), dollars(), dollars()],
                         ["Sex", "Income", "Healthy at 65", "LTC need at 65", "Any college", "e65", "Ever LTC need",
                          "Medicare", "Out of pocket", "OOP median", "CVaR95", "CVaR99"])]

    # --- Table 6: tail
    t5 = pd.read_csv(T / "table5_tail_risk.csv")
    t5 = t5[t5["level"].isin([0.95, 0.99])].copy()
    t5["entry_label"] = t5["entry_state"].map(state_label)
    parts += [caption(6, "The tail of lifetime out-of-pocket cost.",
                      "VaR is the quantile of the present value of lifetime out-of-pocket cost; CVaR is the mean "
                      "beyond it. LTC columns are the percentages of lives that ever entered the long-term-care-need "
                      "state, in the tail and overall. The end-of-life share is the part of the tail's present value "
                      "that comes from the final year's excess over an ordinary year."),
              render(t5, ["sex", "entry_label", "level", "var", "cvar", "cvar_over_mean", "share_of_tail_ever_ltc_pct",
                          "share_of_all_ever_ltc_pct", "eol_share_of_tail_pv_pct"],
                     [None, None, lambda x: f"{round(100 * x)}%", dollars(), dollars(), num(1), pct(1), pct(1), pct(1)],
                     ["Sex", "State at 65", "Level", "VaR", "CVaR", "CVaR / mean", "LTC in tail", "LTC overall",
                      "End-of-life share of tail"])]

    # --- Table 7: scenarios
    t6 = pd.read_csv(T / "table6_scenarios.csv")
    t6 = t6[t6["entry_state"] == "Population mix"]
    parts += [caption(7, "Financing scenarios: lifetime out-of-pocket cost for a cohort turning 65 in 2026, population mix.",
                      "S1: from 2033, Part A pays 89% of scheduled benefits and the stated share of the shortfall "
                      "falls on beneficiaries. S2: the whole cohort shortfall falls on person-years in long-term-care "
                      "need. S3: S1 at 50% with real cost growth at the Trustees' Part B per-beneficiary rate."),
              render(t6, ["sex", "scenario", "pv_oop_mean", "var95", "cvar95", "cvar99", "mean_change_vs_s0",
                          "cvar95_change_vs_s0"],
                     [None, None, dollars(), dollars(), dollars(), dollars(), dollars(), dollars()],
                     ["Sex", "Scenario", "Mean", "VaR95", "CVaR95", "CVaR99", "Change in mean", "Change in CVaR95"])]
    t6b = pd.read_csv(T / "table6b_spend_down.csv")
    parts += [caption("7b", "Exhausting household assets at 65 through out-of-pocket cost, by household income tertile at 65.",
                      "Undiscounted cumulative out-of-pocket cost against household net assets at 65 in 2024 dollars, "
                      "with no asset returns or income. The exhaustion share is among households with positive assets."),
              render(t6b, ["sex", "income_tertile", "scenario", "median_assets_at_65", "pct_no_positive_assets",
                           "pct_exhausting_assets", "median_age_at_exhaustion"],
                     [None, None, None, dollars(), pct(1), pct(1), num(0)],
                     ["Sex", "Income", "Scenario", "Median assets", "No positive assets", "Exhaust assets",
                      "Median age at exhaustion"])]

    # --- Table 8: robustness
    t8 = pd.read_csv(T / "table8_robustness.csv")
    parts += [caption(8, "Robustness: each row changes one decision.",
                      "Population mix at 65, calibrated mortality unless stated; 40,000 lives per sex. Refits use the "
                      "sex-only covariate set and rebuild the entry mix, state costs and calibration from the variant "
                      "panel; compare them with the sex-only row."),
              render(t8, ["variant", "male_e65", "female_e65", "male_ever_ltc_pct", "female_ever_ltc_pct",
                          "male_pv_medicare", "female_pv_medicare", "male_pv_oop", "female_pv_oop",
                          "male_cvar95_oop", "female_cvar95_oop"],
                     [None, num(1), num(1), pct(0), pct(0), dollars(), dollars(), dollars(), dollars(), dollars(), dollars()],
                     ["Variant", "e65 M", "e65 F", "Ever LTC M", "Ever LTC F", "Medicare M", "Medicare F",
                      "OOP M", "OOP F", "CVaR95 M", "CVaR95 F"])]

    # --- Appendix
    parts += ["\n\n# Appendix tables\n"]
    c = pd.read_csv(T / "table1b_crude_transitions.csv", index_col=0)
    c.index = [LAB[config.STATES[int(float(i))]] for i in c.index]
    c.columns = [LAB[config.STATES[int(float(j))]] for j in c.columns]
    c = c.reset_index().rename(columns={"index": "From"})
    parts += [caption("A1", "Observed transitions between consecutive interviews, and deaths.",
                      "Counts of intervals by state at the start (rows) and at the end (columns). Deaths are dated to the month."),
              render(c, list(c.columns), [None] + [num(0)] * (len(c.columns) - 1))]
    t = pd.read_csv(T / "table2b_annual_transition_probabilities.csv")
    t["from"] = t["from"].map(state_label)
    parts += [caption("A2", "One-year transition probabilities from the fitted model, reference covariates, before calibration."),
              render(t, ["sex", "age", "from", "to_H", "to_C", "to_D", "to_L", "to_X"],
                     [None, num(0), None, num(3), num(3), num(3), num(3), num(3)],
                     ["Sex", "Age", "From", "Healthy", "Chronic", "Disability", "LTC need", "Dead"])]
    t = pd.read_csv(T / "table7b_prevalence_validation.csv")
    w = t.pivot_table(index=["sex", "age_band"], columns="state", values=["observed_pct", "model_pct"]).reset_index()
    w.columns = [f"{a}_{b}" if b else a for a, b in w.columns]
    parts += [caption("A3", "State prevalence by age band: the weighted HRS cross-section against the calibrated model (percent of survivors)."),
              render(w, ["sex", "age_band"] + [f"{k}_{s}" for s in ("H", "C", "D", "L") for k in ("observed_pct", "model_pct")],
                     [None, None] + [pct(1)] * 8,
                     ["Sex", "Age"] + [f"{LAB[s]}, {k}" for s in ("H", "C", "D", "L") for k in ("HRS", "model")])]
    sp = T / "table7d_spending_validation.csv"
    if sp.exists():
        t = pd.read_csv(sp)
        parts += [caption("A4", "Medicare spending per person-year by age band: the model cohort against the MCBS Cost Supplement.",
                          "The model applies the MCBS cells to the simulated cohort's state and condition mix; a gap "
                          "reflects the difference between that mix and the MCBS population's."),
                  render(t, ["age_band", "model_medicare_per_person_year", "mcbs_medicare_mean", "mcbs_se", "ratio"],
                         [None, dollars(), dollars(), dollars(), num(3)],
                         ["Age", "Model", "MCBS", "MCBS SE", "Model / MCBS"])]
    t = pd.read_csv(T / "table2c_health_expectancies.csv")
    w = t.pivot_table(index=["sex", "college", "nonwhite"], columns="entry_state", values="life_expectancy_65").reset_index()
    parts += [caption("A5", "Life expectancy at 65 by covariate profile and health state at 65, fitted model before calibration."),
              render(w, ["sex", "college", "nonwhite", "H", "C", "D", "L"],
                     [None, lambda x: "yes" if x else "no", lambda x: "yes" if x else "no", num(1), num(1), num(1), num(1)],
                     ["Sex", "Any college", "Nonwhite or Hispanic", "Healthy", "Chronic illness", "Disability", "LTC need"])]
    t = pd.read_csv(T / "table3a_mcbs_costs.csv")
    parts += [caption("A6", "MCBS Cost Supplement: annual spending per beneficiary by payer, 2019 and 2021 to 2023 pooled.",
                      "Medicare includes fee-for-service and Medicare Advantage payments. Standard errors from "
                      "Fay-adjusted BRR with 100 replicates."),
              render(t, ["cell", "n", "share_in_ma", "medicare_total_mean", "medicare_total_se", "pamtcaid_mean",
                         "pamtoop_mean", "pamtoop_se", "pamttot_mean", "part_a_share_of_total"],
                     [None, num(0), lambda x: f"{100 * x:.1f}%", dollars(), dollars(), dollars(), dollars(), dollars(),
                      dollars(), lambda x: f"{100 * x:.1f}%"],
                     ["Cell", "n", "In MA", "Medicare", "SE", "Medicaid", "Out of pocket", "SE", "All payers", "Part A share"])]
    t = pd.read_csv(T / "tableA1_us_life_table_2023.csv")
    parts += [caption("A7", "2023 US period life table, selected ages (NCHS)."),
              render(t, ["age", "qx_male", "ex_male", "qx_female", "ex_female"],
                     [num(0), num(5), num(2), num(5), num(2)], ["Age", "qx, male", "ex, male", "qx, female", "ex, female"])]

    OUT.write_text("\n".join(parts) + "\n")
    n = sum(1 for line in OUT.read_text().splitlines() if line.startswith("**Table"))
    print(f"wrote {OUT.relative_to(config.ROOT)} with {n} tables")


if __name__ == "__main__":
    main()
