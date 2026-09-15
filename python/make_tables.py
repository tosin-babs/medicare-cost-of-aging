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
ORDER = {s: i for i, s in enumerate(config.LIVE_STATES)}
ORDER.update({LAB[s]: i for i, s in enumerate(config.LIVE_STATES)})
ORDER["Population mix"] = 99


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


def label(s):
    return LAB.get(s, s)


def by(df, col, extra=()):
    return df.assign(_o=df[col].map(ORDER)).sort_values(["_o", *extra], kind="stable").drop(columns="_o")


def sexfirst(df):
    return df.sort_values("sex", kind="stable", key=lambda s: s.map({"male": 0, "female": 1}))


def main():
    parts = ["# Tables\n",
             "*Generated from `output/tables/*.csv` by `python/make_tables.py`. Dollar amounts are 2024 "
             "dollars; present values are discounted at 3% a year to age 65. HRS estimates use the "
             "respondent analysis weight, or the nursing-home resident weight for residents; MCBS "
             "estimates use the Cost Supplement weight with Fay-adjusted balanced repeated replication.*\n"]

    # --- 1: sample
    t = pd.read_csv(T / "table1_sample.csv")
    t["value"] = t["value"].map(value)
    parts += [caption(1, "The HRS panel, waves 4 to 16 (1998 to 2022), respondents aged 50 and over."),
              render(t, ["quantity", "value"], [None, None], ["Quantity", "Value"])]

    # --- 2: intensities
    t = pd.read_csv(T / "table2_intensities.csv")
    lr = t["lr_test_vs_base"].dropna()
    t["term"] = t["term"].replace({"intercept": "log rate at 65", "age_per_10y": "age, per 10 years",
                                   "age_over_70_per_10y": "age over 70, change in slope",
                                   "age_over_85_per_10y": "age over 85, change in slope",
                                   "college": "any college", "nonwhite": "nonwhite or Hispanic"})
    note = ("Log-linear intensities with a linear spline in age (knots at 70 and 85), fitted by maximum "
            "likelihood to interval-censored transitions, exact deaths and known-alive censoring. Reference: "
            "male, no college, non-Hispanic white, age 65. Standard errors clustered on households (sandwich); "
            "hazard ratios with 95% intervals.")
    if len(lr):
        note += (f" Likelihood-ratio test of the education and race-ethnicity terms: {lr.iloc[0]:,.1f} on "
                 f"{int(t['lr_df'].dropna().iloc[0])} degrees of freedom.")
    parts += [caption(2, "Transition intensities among health states.", note),
              render(t, ["transition", "term", "estimate", "se", "hazard_ratio", "hr_lo", "hr_hi"],
                     [None, None, num(3), num(3), num(2), num(2), num(2)],
                     ["Transition", "Term", "Estimate", "SE", "Hazard ratio", "95% low", "95% high"])]

    # --- 3: goodness of fit and mortality
    g = pd.read_csv(T / "table7g_goodness_of_fit_summary.csv")
    g["from_label"] = g["from"].map(label)
    cols = ["from_label", "n"] + [f"{k}_{s}_pct" for s in config.STATES for k in ("obs", "exp")] + ["max_abs_gap_pts"]
    parts += [caption(3, "Goodness of fit: observed and expected destination at the next observation, by starting state (percent).",
                      "Expected shares sum the fitted transition probabilities over each observed interval; "
                      "censored observations are excluded. Cell-level comparisons by age group and interval "
                      "length are in the replication files (table7f)."),
              render(g, cols, [None, num(0)] + [pct(1)] * (2 * len(config.STATES)) + [num(1)],
                     ["From", "n"] + [f"{config.STATES[i // 2]} {'obs' if i % 2 == 0 else 'exp'}"
                                      for i in range(2 * len(config.STATES))] + ["Largest gap, pts"])]
    t7 = pd.read_csv(T / "table7_mortality_validation.csv").merge(
        pd.read_csv(T / "table7c_mortality_calibration.csv")[["sex", "death_multiplier_at_65", "death_multiplier_at_75",
                                                             "death_multiplier_at_85", "death_multiplier_at_95"]], on="sex")
    q = pd.read_csv(T / "table7_qx_validation.csv")
    parts += [caption("3b", "Mortality: the fitted model, the calibrated model and the 2023 US period life table.",
                      "Entry mix of HRS respondents aged 64 to 66. The multiplier scales death intensities from "
                      "every live state and equals exp(c0 + c1 (age - 65)/10) at the calibrated values."),
              render(t7, ["sex", "model_e65_uncalibrated", "model_e65", "life_table_e65_2023",
                          "death_multiplier_at_65", "death_multiplier_at_75", "death_multiplier_at_85",
                          "death_multiplier_at_95"],
                     [None, num(2), num(2), num(2), num(2), num(2), num(2), num(2)],
                     ["Sex", "e65, fitted", "e65, calibrated", "e65, life table", "Multiplier at 65", "75", "85", "95"]),
              "",
              render(q, ["sex", "age", "model_qx_uncalibrated", "model_qx", "life_table_qx", "ratio_to_life_table"],
                     [None, num(0), num(4), num(4), num(4), num(2)],
                     ["Sex", "Age", "qx, fitted", "qx, calibrated", "qx, life table", "Calibrated / table"])]

    # --- 4: annual costs
    t3d = by(pd.read_csv(T / "table3d_medicare_by_state.csv"), "state", ["age_band"])
    t3d["state_label"] = t3d["state"].map(label)
    parts += [caption(4, "Annual Medicare cost by health state and age band.",
                      "MCBS Cost Supplement cells (age by chronic-condition count) weighted by each HRS state's "
                      "condition-count mix, with the level in each age band scaled to the MCBS mean. The gradient "
                      "across states reflects condition counts only; facility, hospice and institutional events are "
                      "outside the Cost Supplement. The simulation further concentrates this spending in the last "
                      "year of life (Section 4.3)."),
              render(t3d, ["state_label", "age_band", "share_0_1_conditions", "share_2_3", "share_4_plus",
                           "medicare_mix_only", "mcbs_scale_factor", "medicare_annual"],
                     [None, None, num(2), num(2), num(2), dollars(), num(2), dollars()],
                     ["State", "Age", "Share 0-1 conditions", "2-3", "4+", "Cell mix", "Scale", "Medicare"])]
    t3c = by(pd.read_csv(T / "table3c_oop_by_state.csv"), "state", ["age_band"])
    t3c = t3c.sort_values(["state", "age_band", "sex"], key=lambda s: s.map(ORDER) if s.name == "state" else s)
    t3c["state_label"] = t3c["state"].map(label)
    parts += [caption("4b", "Annual out-of-pocket spending by state, age band and sex (HRS core interviews, 2006 to 2022).",
                      "Annualized from the recall since the last interview; premiums excluded. The share on Medicaid "
                      "is the weighted share of person-waves reporting Medicaid coverage."),
              render(t3c, ["state_label", "age_band", "sex", "n", "oop_mean", "oop_p50", "oop_p90", "oop_p99", "medicaid_pct"],
                     [None, None, None, num(0), dollars(), dollars(), dollars(), dollars(), pct(0)],
                     ["State", "Age", "Sex", "n", "Mean", "p50", "p90", "p99", "On Medicaid"])]
    t3f = by(pd.read_csv(T / "table3f_medicaid_by_state.csv"), "state", ["age_band"])
    t3f["state_label"] = t3f["state"].map(label)
    parts += [caption("4c", "Out-of-pocket spending with and without Medicaid, by state and age band.",
                      "Weighted, sexes pooled. Medicaid pays most long-term-care costs for those enrolled, which is why "
                      "the simulation draws from the two distributions separately and moves a life onto Medicaid "
                      "when it spends down."),
              render(t3f, ["state_label", "age_band", "medicaid_pct", "oop_mean_no_medicaid", "oop_p99_no_medicaid",
                           "oop_mean_medicaid", "oop_p99_medicaid"],
                     [None, None, pct(1), dollars(), dollars(), dollars(), dollars()],
                     ["State", "Age", "On Medicaid", "Mean, not on Medicaid", "p99", "Mean, on Medicaid", "p99"])]
    t3e = pd.read_csv(T / "table3e_end_of_life_oop.csv")
    t3e["group"] = t3e["group"].map({"ltc": "Long-term care at last interview", "other": "Other"})
    parts += [caption("4d", "Out-of-pocket spending in the last year of life (HRS exit interviews, 2006 to 2022).",
                      "Spending from the last core interview to death, pro-rated to twelve months where that window is "
                      "longer; includes hospice. Unweighted; age band at death."),
              render(t3e, ["group", "age_band", "sex", "n", "imputed_share", "eol_mean", "eol_p50", "eol_p90", "eol_p99"],
                     [None, None, None, num(0), lambda x: f"{100 * x:.0f}%", dollars(), dollars(), dollars(), dollars()],
                     ["Group", "Age at death", "Sex", "n", "Imputed", "Mean", "p50", "p90", "p99"])]
    t3g = pd.read_csv(T / "table3g_oop_persistence.csv")
    parts += [caption("4e", "Persistence of out-of-pocket spending.",
                      "Correlation of normal scores of annual out-of-pocket spending (within state, age band and wave) "
                      f"between interviews k years apart, and the fitted permanent-plus-decaying form "
                      f"c + (1 - c) phi^k with c = {t3g['permanent_share'].iloc[0]:.3f} and phi = "
                      f"{t3g['annual_decay'].iloc[0]:.3f}."),
              render(t3g, ["lag_years", "n", "correlation", "fitted"], [num(0), num(0), num(3), num(3)],
                     ["Years apart", "Pairs", "Correlation", "Fitted"])]

    # --- 5: lifetime cost
    t4 = pd.read_csv(T / "table4_lifetime_costs.csv").merge(
        pd.read_csv(T / "table4b_parameter_uncertainty.csv"), on=["sex", "entry_state"], how="left")
    t4 = sexfirst(by(t4, "entry_state"))
    parts += [caption(5, "Expected lifetime cost from age 65 by sex and health state at 65, present value at 3%.",
                      f"{config.N_SIMULATIONS:,} simulated lives per row, calibrated mortality, persistent out-of-pocket "
                      "draws and Medicaid spend-down. Parameter intervals are the 2.5th and 97.5th percentiles of the "
                      "exact expected value over 200 draws of the transition parameters from their cluster-robust "
                      "covariance, with spend-down and persistence off. Premiums are the standard Part B and base Part D "
                      "premiums in years not on Medicaid."),
              render(t4, ["sex", "entry_state", "life_expectancy", "ever_ltc_pct", "years_ltc", "ever_medicaid_pct",
                          "pv_medicare_mean", "pv_medicare_lo", "pv_medicare_hi", "pv_oop_mean", "pv_oop_lo",
                          "pv_oop_hi", "pv_oop_median", "pv_premium_mean"],
                     [None, None, num(1), pct(1), num(2), pct(1), dollars(), dollars(), dollars(), dollars(),
                      dollars(), dollars(), dollars(), dollars()],
                     ["Sex", "State at 65", "e65", "Ever LTC", "Years LTC", "Ever Medicaid", "Medicare", "low", "high",
                      "Out of pocket", "low", "high", "OOP median", "Premiums"])]
    t4c = sexfirst(pd.read_csv(T / "table4c_lifetime_by_income.csv"))
    parts += [caption("5b", "Lifetime cost, Medicaid and tail risk by household income tertile at 65.",
                      "Tertiles of household income within interview wave at ages 64 to 66. Each simulated life keeps "
                      "its income, non-housing assets and Medicaid status at 65. The transition model has no income term "
                      "(Section 6.1 reports the extension that adds one)."),
              render(t4c, ["sex", "income_tertile", "median_income", "median_assets", "medicaid_at_65_pct",
                           "entry_share_ltc_pct", "life_expectancy", "ever_ltc_pct", "ever_medicaid_pct",
                           "pv_medicare_mean", "pv_oop_mean", "cvar95", "pv_premium_mean"],
                     [None, None, dollars(), dollars(), pct(1), pct(1), num(1), pct(1), pct(1), dollars(), dollars(),
                      dollars(), dollars()],
                     ["Sex", "Income", "Median income", "Median assets", "Medicaid at 65", "LTC at 65", "e65",
                      "Ever LTC", "Ever Medicaid", "Medicare", "Out of pocket", "CVaR95", "Premiums"])]
    t4d = pd.read_csv(T / "table4d_analytic_check.csv")
    parts += [caption("5c", "The simulation against the exact recursion, with spend-down and persistence off.",
                      "Population mix. The difference is within about two Monte Carlo standard errors."),
              render(t4d, ["sex", "pv_medicare_sim", "pv_medicare_exact", "pv_oop_sim", "pv_oop_exact", "mc_se_oop"],
                     [None, dollars(), dollars(), dollars(), dollars(), dollars()],
                     ["Sex", "Medicare, simulated", "Medicare, exact", "OOP, simulated", "OOP, exact", "MC SE"])]

    # --- 6: tail
    t5 = sexfirst(by(pd.read_csv(T / "table5_tail_risk.csv"), "entry_state"))
    t5 = t5[t5["level"].isin([0.95, 0.99])]
    parts += [caption(6, "The tail of lifetime out-of-pocket cost.",
                      "VaR is the quantile of the present value of lifetime out-of-pocket cost; CVaR the mean beyond it, "
                      "with its Monte Carlo standard error from 200 bootstrap resamples of the simulated lives. The last "
                      "columns describe the lives in the tail."),
              render(t5, ["sex", "entry_state", "level", "var", "cvar", "cvar_mc_se", "cvar_over_mean",
                          "share_of_tail_ever_ltc_pct", "share_of_all_ever_ltc_pct", "mean_years_ltc_in_tail",
                          "share_of_tail_medicaid_pct", "eol_share_of_tail_pv_pct"],
                     [None, None, lambda x: f"{round(100 * x)}%", dollars(), dollars(), dollars(), num(1), pct(1),
                      pct(1), num(1), pct(1), pct(1)],
                     ["Sex", "State at 65", "Level", "VaR", "CVaR", "MC SE", "CVaR / mean", "LTC in tail",
                      "LTC overall", "Years LTC in tail", "Medicaid in tail", "End-of-life share"])]

    # --- 7: scenarios and spend-down
    t6 = sexfirst(pd.read_csv(T / "table6_scenarios.csv"))
    parts += [caption(7, "Financing scenarios: lifetime out-of-pocket cost for a cohort turning 65 in 2026, population mix.",
                      "Hospital Insurance pays 35.1% of Medicare spending per beneficiary (Trustees Table V.D1, 2024). "
                      "S1: from 2033 the payable share follows the Trustees' path (89% in 2033, 85% in 2050, 93% in "
                      "2100) and the stated share of the shortfall falls on beneficiaries not on Medicaid. S1b: the "
                      "same with the community inpatient and home-health share the Cost Supplement measures. S2: the "
                      "whole cohort shortfall falls on person-years in long-term care. S3: S1 at 50% with real cost "
                      "growth. Common random numbers across scenarios."),
              render(t6, ["sex", "scenario", "pv_oop_mean", "cvar95", "cvar99", "mean_change_vs_s0",
                          "cvar95_change_vs_s0", "ever_medicaid_pct", "medicaid_change_pts"],
                     [None, None, dollars(), dollars(), dollars(), dollars(), dollars(), pct(1), num(1)],
                     ["Sex", "Scenario", "Mean", "CVaR95", "CVaR99", "Change in mean", "Change in CVaR95",
                      "Ever Medicaid", "Change, pts"])]
    t6b = sexfirst(pd.read_csv(T / "table6b_spend_down.csv"))
    parts += [caption("7b", "Medicaid spend-down and scenario effects by household income tertile at 65.",
                      "Households meet out-of-pocket costs from income up to 10% of income and from non-housing assets "
                      "beyond that; a life needing long-term care whose assets fall below $2,000 goes onto Medicaid. "
                      "Spend-down counts lives that reach Medicaid after 65."),
              render(t6b, ["sex", "income_tertile", "scenario", "median_assets_at_65", "medicaid_at_65_pct",
                           "spend_down_pct", "ever_medicaid_pct", "median_age_spend_down", "pv_oop_mean", "cvar95"],
                     [None, None, None, dollars(), pct(1), pct(1), pct(1), num(0), dollars(), dollars()],
                     ["Sex", "Income", "Scenario", "Median assets", "Medicaid at 65", "Spend down", "Ever Medicaid",
                      "Median age at spend-down", "Mean OOP", "CVaR95"])]

    # --- 8: validation against the literature
    t7e = pd.read_csv(T / "table7e_literature_comparison.csv")
    parts += [caption(8, "The model's out-of-pocket spending against published estimates.",
                      "Published values converted to 2024 dollars with the CPI-U. Bases differ, as the basis column "
                      "states; model values are per person, include Part B and Part D premiums only where the source's "
                      "measure does, and exclude Medicaid payments throughout."),
              render(t7e, ["source", "quantity", "basis", "published", "published_2024_dollars", "model_male", "model_female"],
                     [None, None, None, num(0), num(0), num(0), num(0)],
                     ["Source", "Quantity", "Basis", "Published", "2024 dollars", "Model, men", "Model, women"])]

    # --- 9: robustness
    t8 = pd.read_csv(T / "table8_robustness.csv")
    parts += [caption(9, "Robustness: each row changes one decision.",
                      "Population mix at 65; 40,000 lives per sex with common random numbers. Refits use the sex-only "
                      "covariate set and rebuild the entry sample, state costs and calibration from the variant panel; "
                      "compare them with the sex-only row. The CVaR95 Monte Carlo standard error is about the last "
                      "column's size."),
              render(t8, ["variant", "male_e65", "female_e65", "male_ever_ltc_pct", "female_ever_ltc_pct",
                          "male_ever_medicaid_pct", "female_ever_medicaid_pct", "male_pv_medicare", "female_pv_medicare",
                          "male_pv_oop", "female_pv_oop", "male_cvar95_oop", "female_cvar95_oop", "male_cvar95_mc_se"],
                     [None, num(1), num(1), pct(0), pct(0), pct(0), pct(0), dollars(), dollars(), dollars(), dollars(),
                      dollars(), dollars(), dollars()],
                     ["Variant", "e65 M", "e65 F", "LTC M", "LTC F", "Medicaid M", "Medicaid F", "Medicare M",
                      "Medicare F", "OOP M", "OOP F", "CVaR95 M", "CVaR95 F", "MC SE"])]

    # --- appendix
    parts += ["\n\n# Appendix tables\n"]
    ext = T / "table2d_model_extensions.csv"
    if ext.exists():
        t = pd.read_csv(ext)
        lr = t.groupby("extension").agg(lr=("lr_test_vs_full", "first"), df=("df", "first")).reset_index()
        parts += [caption("A1", "Extensions to the transition model: likelihood-ratio tests against the main model.",
                          "income: low and high household income tertile against middle. duration: in the same state "
                          "at the previous interview, a first-order check on the Markov assumption. age2: a quadratic "
                          "age term on top of the spline. period: calendar year, per decade from 2010."),
                  render(lr, ["extension", "lr", "df"], [None, num(1), num(0)], ["Extension", "LR statistic", "df"]),
                  "",
                  render(t, ["extension", "transition", "term", "hazard_ratio", "hr_lo", "hr_hi"],
                         [None, None, None, num(2), num(2), num(2)],
                         ["Extension", "Transition", "Term", "Hazard ratio", "95% low", "95% high"])]
    c = pd.read_csv(T / "table1b_crude_transitions.csv", index_col=0)
    names = {**{i: LAB[s] for i, s in enumerate(config.STATES)}, -1: "Alive, state unknown"}
    c.index = [names[int(float(i))] for i in c.index]
    c.columns = [names[int(float(j))] for j in c.columns]
    c = c.reset_index().rename(columns={"index": "From"})
    parts += [caption("A2", "Observations by state at the start (rows) and at the end (columns)."),
              render(c, list(c.columns), [None] + [num(0)] * (len(c.columns) - 1))]
    t = pd.read_csv(T / "table2b_annual_transition_probabilities.csv")
    parts += [caption("A3", "One-year transition probabilities from the fitted model, reference covariates, before calibration."),
              render(t, ["sex", "age", "from"] + [f"to_{s}" for s in config.STATES],
                     [None, num(0), label] + [num(3)] * len(config.STATES),
                     ["Sex", "Age", "From"] + [LAB[s] for s in config.STATES])]
    t = pd.read_csv(T / "table7b_prevalence_validation.csv")
    w = t.pivot_table(index=["sex", "age_band"], columns="state", values=["observed_pct", "model_pct"]).reset_index()
    w.columns = [f"{a}_{b}" if b else a for a, b in w.columns]
    parts += [caption("A4", "State prevalence by age band: the weighted HRS cross-section (2006 to 2022) against the calibrated model (percent of survivors)."),
              render(w, ["sex", "age_band"] + [f"{k}_{s}" for s in config.LIVE_STATES for k in ("observed_pct", "model_pct")],
                     [None, None] + [pct(1)] * (2 * len(config.LIVE_STATES)),
                     ["Sex", "Age"] + [f"{s} {k}" for s in config.LIVE_STATES for k in ("HRS", "model")])]
    t = pd.read_csv(T / "table7d_spending_validation.csv")
    t7h = pd.read_csv(T / "table7h_medicaid_validation.csv")
    parts += [caption("A5", "Medicare per person-year and Medicaid in long-term care: model against MCBS, the Trustees and HRS.",
                      "The MCBS ratio is a consistency check (the level is scaled to it); the Trustees' figure covers all "
                      "beneficiaries including the disabled under 65 and all services."),
              render(t, ["age_band", "model_before_scaling", "model_medicare_per_person_year", "mcbs_medicare_mean",
                         "ratio_to_mcbs", "trustees_per_beneficiary_2024", "ratio_to_trustees"],
                     [None, dollars(), dollars(), dollars(), num(3), dollars(), num(3)],
                     ["Age", "Before scaling", "Model", "MCBS", "Model / MCBS", "Trustees 2024", "Model / Trustees"]),
              "",
              render(t7h, ["sex", "model_ltc_person_years_on_medicaid_pct", "hrs_ltc_person_years_on_medicaid_pct",
                           "model_ever_medicaid_pct", "model_medicaid_at_65_pct"],
                     [None, pct(1), pct(1), pct(1), pct(1)],
                     ["Sex", "LTC person-years on Medicaid, model", "HRS", "Ever Medicaid, model", "Medicaid at 65"])]
    t = pd.read_csv(T / "table2c_health_expectancies.csv")
    w = t.pivot_table(index=["sex", "college", "nonwhite"], columns="entry_state", values="life_expectancy_65").reset_index()
    parts += [caption("A6", "Life expectancy at 65 by covariate profile and health state at 65, fitted model before calibration."),
              render(w, ["sex", "college", "nonwhite"] + list(config.LIVE_STATES),
                     [None, lambda x: "yes" if x else "no", lambda x: "yes" if x else "no"] + [num(1)] * len(config.LIVE_STATES),
                     ["Sex", "Any college", "Nonwhite or Hispanic"] + [LAB[s] for s in config.LIVE_STATES])]
    t = pd.read_csv(T / "table3a_mcbs_costs.csv")
    parts += [caption("A7", "MCBS Cost Supplement: annual spending per beneficiary by payer, 2019 and 2021 to 2023 pooled.",
                      "Medicare includes fee-for-service and Medicare Advantage payments. The All row includes "
                      "beneficiaries under 65. Standard errors from Fay-adjusted BRR with 100 replicates."),
              render(t, ["cell", "n", "share_in_ma", "medicare_total_mean", "medicare_total_se", "medicare_ffs_only_mean",
                         "pamtoop_mean", "pamttot_mean", "part_a_share_of_medicare"],
                     [None, num(0), lambda x: f"{100 * x:.1f}%", dollars(), dollars(), dollars(), dollars(), dollars(),
                      lambda x: f"{100 * x:.1f}%"],
                     ["Cell", "n", "In MA", "Medicare", "SE", "Medicare, FFS only", "Out of pocket", "All payers",
                      "IP + HH / Medicare"])]
    t = pd.read_csv(T / "tableA1_us_life_table_2023.csv")
    parts += [caption("A8", "2023 US period life table, selected ages (NCHS)."),
              render(t, ["age", "qx_male", "ex_male", "qx_female", "ex_female"],
                     [num(0), num(5), num(2), num(5), num(2)], ["Age", "qx, male", "ex, male", "qx, female", "ex, female"])]

    OUT.write_text("\n".join(parts) + "\n")
    n = sum(1 for line in OUT.read_text().splitlines() if line.startswith("**Table"))
    print(f"wrote {OUT.relative_to(config.ROOT)} with {n} tables")


if __name__ == "__main__":
    main()
