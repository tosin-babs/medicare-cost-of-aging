"""
Check that the manuscript's numbers still match the analysis output.

The prose is written by hand, so a rerun that moves an estimate leaves the text
stale unless someone notices. This reads the current tables, formats each
quoted figure the way the manuscript writes it, and fails if the string is
absent. It also checks that every table cited is rendered and vice versa, that
every embedded figure exists, that no placeholder is left, and that the prose
carries no em dashes. It then writes the exact body word count into the
manuscript.

Run after run_all.py and make_tables.py, before make_manuscript.py.
"""

from __future__ import annotations

import re
import sys

import pandas as pd

import config

MS = config.ROOT / "manuscript" / "Paper5_manuscript.md"
T = config.TABLES
M, F, P = "male", "female", "Population mix"
LTC_LABEL = {"H": "Healthy", "C": "Chronic illness", "D": "Disability",
             "L": "Severe disability at home", "N": "Nursing home"}


def d(x):
    return f"${x:,.0f}"


def pc(x, n=1):
    return f"{x:.{n}f}%"


def sample_checks(t1):
    v = lambda k: float(t1[k])
    return {
        "respondents": f"{int(v('Respondents with at least one classified interview')):,} respondents",
        "person-interviews": f"{int(v('Person-interviews with a classified state')):,} classified person-interviews",
        "transitions": f"{int(v('Intervals between interviews')):,} transitions",
        "interval length": f"mean interval of {v('Mean interval length, years'):.2f} years",
        "deaths": f"{int(v('Deaths')):,} deaths are dated",
        "year-only deaths": f"{int(v('Deaths dated to the year only, placed at mid-year'))} of them to the year only",
        "censored": f"{int(v('Known-alive censored observations')):,} observations are censored",
        "censored years": f"{v('Person-years in censored observations'):,.0f} person-years",
        "dropped": f"{int(v('Observations dropped for missing race'))} observations are dropped",
        "share H": pc(v('Weighted share of person-interviews in Healthy, %')),
        "share C": pc(v('Weighted share of person-interviews in Chronic illness, %')),
        "share D": pc(v('Weighted share of person-interviews in Disability, %')),
        "share L": pc(v('Weighted share of person-interviews in Severe disability at home, %')),
        "share N": pc(v('Weighted share of person-interviews in Nursing home, %')),
    }


def cost_checks():
    t3d = pd.read_csv(T / "table3d_medicare_by_state.csv").set_index(["state", "age_band"])
    t3c = pd.read_csv(T / "table3c_oop_by_state.csv").set_index(["state", "age_band", "sex"])
    t3e = pd.read_csv(T / "table3e_end_of_life_oop.csv").set_index(["group", "age_band", "sex"])
    t3a = pd.read_csv(T / "table3a_mcbs_costs.csv").set_index("cell")
    med = lambda s, b: d(t3d.loc[(s, b), "medicare_annual"])
    oop = lambda s, x: d(t3c.loc[(s, "75+", x), "oop_mean"])
    c = {
        "mcbs n": f"{int(t3a.loc['All', 'n']):,} beneficiary-years",
        "mcbs mean": f"{d(t3a.loc['All', 'medicare_total_mean'])} (standard error {d(t3a.loc['All', 'medicare_total_se'])})",
        "mcbs ma": f"{100 * t3a.loc['All', 'share_in_ma']:.0f}% of beneficiary-years",
        "scale factors": (f"factors of {t3d.loc[('C', '65-74'), 'mcbs_scale_factor']:.2f} and "
                          f"{t3d.loc[('C', '75+'), 'mcbs_scale_factor']:.2f}"),
        "income factor": f"{100 * (t3d.loc[('C', '65-74'), 'income_factor_low_tertile'] - 1):.0f}% higher in the lowest income tertile",
        "eol n": f"{int(pd.read_csv(T / 'table3e_end_of_life_oop.csv')['n'].sum()):,} decedents",
        "medicare 65-74": (f"from {med('H', '65-74')} in H through {med('C', '65-74')} in C, "
                           f"{med('D', '65-74')} in D and {med('L', '65-74')} in L to {med('N', '65-74')} in N"),
        "medicare 75+": f"from {med('H', '75+')} to {med('N', '75+')}",
        "oop N 75+": f"{oop('N', M)} for men and {oop('N', F)} for women in N",
        "oop N p99": (f"99th percentiles of {d(t3c.loc[('N', '75+', M), 'oop_p99'])} and "
                      f"{d(t3c.loc[('N', '75+', F), 'oop_p99'])}"),
        "medicaid N": (f"{t3c.loc[('N', '75+', M), 'medicaid_pct']:.0f}% and "
                       f"{t3c.loc[('N', '75+', F), 'medicaid_pct']:.0f}% of nursing-home person-years"),
        "eol ltc": (f"{d(t3e.loc[('ltc', '75+', M), 'eol_mean'])} for men and "
                    f"{d(t3e.loc[('ltc', '75+', F), 'eol_mean'])} for women"),
        "eol other": (f"{d(t3e.loc[('other', '75+', M), 'eol_mean'])} and "
                      f"{d(t3e.loc[('other', '75+', F), 'eol_mean'])}"),
    }
    per = T / "table3g_oop_persistence.csv"
    if per.exists():
        p = pd.read_csv(per).iloc[0]
        c["persistence"] = (f"permanent share of {p['permanent_share']:.3f} and an AR(1) coefficient of "
                            f"{p['annual_decay']:.3f}")
    return c


def model_checks():
    t7c = pd.read_csv(T / "table7c_mortality_calibration.csv").set_index("sex")
    c = {
        "e65 uncalibrated": (f"{t7c.loc[M, 'e65_uncalibrated']:.2f} years for men and "
                             f"{t7c.loc[F, 'e65_uncalibrated']:.2f} for women"),
        "multiplier male": (f"from {t7c.loc[M, 'death_multiplier_at_65']:.3f} at 65 to "
                            f"{t7c.loc[M, 'death_multiplier_at_95']:.3f} at 95 for men"),
        "multiplier female": (f"from {t7c.loc[F, 'death_multiplier_at_65']:.3f} to "
                              f"{t7c.loc[F, 'death_multiplier_at_95']:.3f} for women"),
    }
    return c


def validation_checks():
    g = pd.read_csv(T / "table7g_goodness_of_fit_summary.csv").set_index("from")
    t7 = pd.read_csv(T / "table7_mortality_validation.csv").set_index("sex")
    q = pd.read_csv(T / "table7_qx_validation.csv")
    pv = pd.read_csv(T / "table7b_prevalence_validation.csv")
    t7d = pd.read_csv(T / "table7d_spending_validation.csv").set_index("age_band")
    t7h = pd.read_csv(T / "table7h_medicaid_validation.csv").set_index("sex")
    lit = pd.read_csv(T / "table7e_literature_comparison.csv")
    lit_row = lambda src, frag: lit[(lit["source"].str.contains(src)) & (lit["quantity"].str.contains(frag))].iloc[0]
    k5, k1 = lit_row("Kelley", "last five years"), lit_row("Marshall", "last year")
    k1p = lit_row("Marshall", "95th")
    jones = lit_row("Jones", "mean")
    nh = lit_row("Hurd", "Ever a nursing-home stay")
    return {
        "gof H": f"largest gap {g.loc['H', 'max_abs_gap_pts']:.1f} points",
        "gof C": f"C ({g.loc['C', 'max_abs_gap_pts']:.1f})",
        "gof D": f"D ({g.loc['D', 'max_abs_gap_pts']:.1f})",
        "gof L": (f"expects {g.loc['L', 'exp_L_pct']:.1f}% to remain against {g.loc['L', 'obs_L_pct']:.1f}% observed "
                  f"and {g.loc['L', 'exp_X_pct']:.1f}% to die against {g.loc['L', 'obs_X_pct']:.1f}%"),
        "gof N": (f"expects {g.loc['N', 'exp_N_pct']:.1f}% to remain against {g.loc['N', 'obs_N_pct']:.1f}% and "
                  f"{g.loc['N', 'exp_X_pct']:.1f}% to die against {g.loc['N', 'obs_X_pct']:.1f}%, a gap of "
                  f"{g.loc['N', 'max_abs_gap_pts']:.1f} points"),
        "e65 calibrated": (f"{t7.loc[M, 'model_e65']:.2f} years for men and {t7.loc[F, 'model_e65']:.2f} for women "
                           f"against {t7.loc[M, 'life_table_e65_2023']:.2f} and {t7.loc[F, 'life_table_e65_2023']:.2f}"),
        "qx ratios": (f"ratios {q['ratio_to_life_table'].min():.2f} to {q['ratio_to_life_table'].max():.2f}"),
        "prevalence gap": f"largest gap in any cell is {(pv['model_pct'] - pv['observed_pct']).abs().max():.1f} percentage points",
        "spending ratio": (f"{t7d.loc['65-74', 'ratio_to_mcbs']:.2f} and {t7d.loc['75+', 'ratio_to_mcbs']:.2f} times "
                           f"the MCBS band mean"),
        "trustees ratio": (f"{t7d.loc['65-74', 'ratio_to_trustees']:.2f} and {t7d.loc['75+', 'ratio_to_trustees']:.2f} of "
                           f"Medicare's own per-beneficiary spending in 2024 "
                           f"({d(t7d.loc['65-74', 'trustees_per_beneficiary_2024'])})"),
        "medicaid validation": (f"{t7h.loc[M, 'model_ltc_person_years_on_medicaid_pct']:.1f}% of men's and "
                                f"{t7h.loc[F, 'model_ltc_person_years_on_medicaid_pct']:.1f}% of women's long-term-care "
                                f"person-years are on Medicaid, against "
                                f"{t7h.loc[M, 'hrs_ltc_person_years_on_medicaid_pct']:.1f}% in HRS"),
        "kelley": (f"{d(k5['model_male'])} for men and {d(k5['model_female'])} for women against Kelley et al. (2013) "
                   f"at {d(k5['published_2024_dollars'])}"),
        "marshall": (f"last-year spending of {d(k1['model_male'])} and {d(k1['model_female'])} against Marshall, "
                     f"McGarry and Skinner (2011) at {d(k1['published_2024_dollars'])}"),
        "marshall p95": (f"({d(k1p['model_male'])} and {d(k1p['model_female'])}) bracketing theirs "
                         f"({d(k1p['published_2024_dollars'])})"),
        "jones": (f"{d(jones['published_2024_dollars'])} per household including Medicaid payments, against "
                  f"{d(jones['model_male'])} and {d(jones['model_female'])}"),
        "nursing home use": (f"{nh['published']:.0f}% of people have a nursing-home stay, against "
                             f"{nh['model_male']:.0f}% of men and {nh['model_female']:.0f}% of women"),
    }


def result_checks():
    t2 = pd.read_csv(T / "table2_intensities.csv")
    hr = t2.dropna(subset=["hazard_ratio"]).set_index(["transition", "term"])
    t2c = pd.read_csv(T / "table2c_health_expectancies.csv")
    ref = t2c[(t2c["college"] == 0) & (t2c["nonwhite"] == 0)].set_index(["sex", "entry_state"])
    t4 = pd.read_csv(T / "table4_lifetime_costs.csv").set_index(["sex", "entry_state"])
    t4c = pd.read_csv(T / "table4c_lifetime_by_income.csv").set_index(["sex", "income_tertile"])
    t5 = pd.read_csv(T / "table5_tail_risk.csv").set_index(["sex", "entry_state", "level"])
    age = lambda j: hr.loc[(j, "age_per_10y"), "hazard_ratio"]
    fem = lambda j: hr.loc[(j, "female"), "hazard_ratio"]
    lr = t2["lr_test_vs_base"].dropna().iloc[0]
    df = int(t2["lr_df"].dropna().iloc[0])
    c = {
        "lr test": f"{lr:,.1f} on {df} degrees of freedom",
        "death age slope": (f"{age('H to X'):.2f} per decade from H, {age('C to X'):.2f} from C, "
                            f"{age('D to X'):.2f} from D, {age('L to X'):.2f} from L and {age('N to X'):.2f} from N"),
        "female mortality": (f"{min(fem(f'{j} to X') for j in 'HCDLN'):.2f} to "
                             f"{max(fem(f'{j} to X') for j in 'HCDLN'):.2f} of men's"),
        "college": (f"mortality from H (hazard ratio {hr.loc[('H to X', 'college'), 'hazard_ratio']:.2f}) and C "
                    f"({hr.loc[('C to X', 'college'), 'hazard_ratio']:.2f})"),
        "nonwhite": (f"from H to D ({hr.loc[('H to D', 'nonwhite'), 'hazard_ratio']:.2f}) and from C to D "
                     f"({hr.loc[('C to D', 'nonwhite'), 'hazard_ratio']:.2f})"),
        "e65 H male": (f"can expect {ref.loc[(M, 'H'), 'life_expectancy_65']:.2f} more years: "
                       f"{ref.loc[(M, 'H'), 'years_in_H']:.2f} in H, {ref.loc[(M, 'H'), 'years_in_C']:.2f} in C, "
                       f"{ref.loc[(M, 'H'), 'years_in_D']:.2f} in D, {ref.loc[(M, 'H'), 'years_in_L']:.2f} in L and "
                       f"{ref.loc[(M, 'H'), 'years_in_N']:.2f} in N"),
        "e65 H female": (f"can expect {ref.loc[(F, 'H'), 'life_expectancy_65']:.2f} years, with "
                         f"{ref.loc[(F, 'H'), 'years_in_L']:.2f} in L and {ref.loc[(F, 'H'), 'years_in_N']:.2f} in N"),
        "e65 N male": (f"can expect {ref.loc[(M, 'N'), 'life_expectancy_65']:.2f} more years, "
                       f"{ref.loc[(M, 'N'), 'years_in_N']:.2f} of them in the nursing home"),
        "medicare mix": f"{d(t4.loc[(M, P), 'pv_medicare_mean'])} for men and {d(t4.loc[(F, P), 'pv_medicare_mean'])} for women",
        "oop mix": (f"{d(t4.loc[(M, P), 'pv_oop_mean'])} and {d(t4.loc[(F, P), 'pv_oop_mean'])} with medians of "
                    f"{d(t4.loc[(M, P), 'pv_oop_median'])} and {d(t4.loc[(F, P), 'pv_oop_median'])}"),
        "premiums": f"{d(t4.loc[(M, P), 'pv_premium_mean'])} and {d(t4.loc[(F, P), 'pv_premium_mean'])}",
        "mc se": f"{d(t4.loc[(M, P), 'mc_se_oop'])} and {d(t4.loc[(F, P), 'mc_se_oop'])}",
        "medicare by entry": (f"is expected to cost Medicare {d(t4.loc[(M, LTC_LABEL['H']), 'pv_medicare_mean'])} over "
                              f"his life; one already in a nursing home"),
        "medicare N male": f"is expected to cost {d(t4.loc[(M, LTC_LABEL['N']), 'pv_medicare_mean'])}",
        "e65 entry": (f"live {t4.loc[(M, LTC_LABEL['N']), 'life_expectancy']:.1f} years rather than "
                      f"{t4.loc[(M, LTC_LABEL['H']), 'life_expectancy']:.1f}"),
        "medicare C": (f"{d(t4.loc[(M, LTC_LABEL['C']), 'pv_medicare_mean'])} for men and "
                       f"{d(t4.loc[(F, LTC_LABEL['C']), 'pv_medicare_mean'])} for women"),
        "oop by entry": (f"{d(t4.loc[(M, LTC_LABEL['H']), 'pv_oop_mean'])} for a man healthy at 65, "
                         f"{d(t4.loc[(M, LTC_LABEL['C']), 'pv_oop_mean'])} with chronic illness, "
                         f"{d(t4.loc[(M, LTC_LABEL['D']), 'pv_oop_mean'])} with disability, "
                         f"{d(t4.loc[(M, LTC_LABEL['L']), 'pv_oop_mean'])} in severe disability at home and "
                         f"{d(t4.loc[(M, LTC_LABEL['N']), 'pv_oop_mean'])} in a nursing home"),
        "medicaid by entry": (f"{t4.loc[(M, LTC_LABEL['L']), 'ever_medicaid_pct']:.1f}% reach Medicaid; starting in N, "
                              f"{t4.loc[(M, LTC_LABEL['N']), 'ever_medicaid_pct']:.1f}%"),
        "premium by entry": (f"from {d(t4.loc[(M, LTC_LABEL['H']), 'pv_premium_mean'])} to "
                             f"{d(t4.loc[(M, LTC_LABEL['N']), 'pv_premium_mean'])}"),
        "medicaid mix": (f"{t4.loc[(M, P), 'ever_medicaid_pct']:.1f}% of men and "
                         f"{t4.loc[(F, P), 'ever_medicaid_pct']:.1f}% of women reach Medicaid"),
        "medicaid age": (f"median age of {t4.loc[(M, P), 'median_age_medicaid']:.0f} and "
                         f"{t4.loc[(F, P), 'median_age_medicaid']:.0f}"),
        "income assets": f"median non-housing assets of {d(t4c.loc[(M, 'low'), 'median_assets'])} at 65",
        "income medicaid": (f"{t4c.loc[(M, 'low'), 'ever_medicaid_pct']:.0f}% of lives against "
                            f"{t4c.loc[(M, 'high'), 'ever_medicaid_pct']:.0f}%"),
        "income oop": (f"{d(t4c.loc[(M, 'low'), 'pv_oop_mean'])} against {d(t4c.loc[(M, 'high'), 'pv_oop_mean'])} in the "
                       f"highest tertile, and for women {d(t4c.loc[(F, 'low'), 'pv_oop_mean'])} against "
                       f"{d(t4c.loc[(F, 'high'), 'pv_oop_mean'])}"),
        "income medicare": (f"({d(t4c.loc[(M, 'low'), 'pv_medicare_mean'])} for men against "
                            f"{d(t4c.loc[(M, 'high'), 'pv_medicare_mean'])})"),
        "tail male": (f"VaR95 is {d(t5.loc[(M, P, 0.95), 'var'])} and CVaR95 {d(t5.loc[(M, P, 0.95), 'cvar'])}, "
                      f"{t5.loc[(M, P, 0.95), 'cvar_over_mean']:.1f} times the mean, with a Monte Carlo standard error of "
                      f"{d(t5.loc[(M, P, 0.95), 'cvar_mc_se'])}; CVaR99 is {d(t5.loc[(M, P, 0.99), 'cvar'])}"),
        "tail female": (f"VaR95 is {d(t5.loc[(F, P, 0.95), 'var'])}, CVaR95 {d(t5.loc[(F, P, 0.95), 'cvar'])}, "
                        f"{t5.loc[(F, P, 0.95), 'cvar_over_mean']:.1f} times the mean, and CVaR99 "
                        f"{d(t5.loc[(F, P, 0.99), 'cvar'])}"),
        "tail ltc male": (f"{t5.loc[(M, P, 0.95), 'share_of_tail_ever_ltc_pct']:.1f}% passed through long-term care "
                          f"against {t5.loc[(M, P, 0.95), 'share_of_all_ever_ltc_pct']:.1f}% of all men, and they spent "
                          f"{t5.loc[(M, P, 0.95), 'mean_years_ltc_in_tail']:.1f} years there against "
                          f"{t4.loc[(M, P), 'years_ltc']:.1f}"),
        "tail ltc female": (f"{t5.loc[(F, P, 0.95), 'share_of_tail_ever_ltc_pct']:.1f}% against "
                            f"{t5.loc[(F, P, 0.95), 'share_of_all_ever_ltc_pct']:.1f}%, and "
                            f"{t5.loc[(F, P, 0.95), 'mean_years_ltc_in_tail']:.1f} years against "
                            f"{t4.loc[(F, P), 'years_ltc']:.1f}"),
        "tail age": (f"dying at {t5.loc[(M, P, 0.95), 'mean_death_age_in_tail']:.1f} on average against "
                     f"{t5.loc[(M, P, 0.95), 'mean_death_age_all']:.1f}"),
        "tail eol": (f"{t5.loc[(M, P, 0.95), 'eol_share_of_tail_pv_pct']:.1f}% of the tail's present value for men and "
                     f"{t5.loc[(F, P, 0.95), 'eol_share_of_tail_pv_pct']:.1f}%"),
        "tail medicaid": (f"{t5.loc[(M, P, 0.95), 'share_of_tail_medicaid_pct']:.0f}% of the men and "
                          f"{t5.loc[(F, P, 0.95), 'share_of_tail_medicaid_pct']:.0f}% of the women in the tail"),
        "tail N entry": (f"CVaR95 of {d(t5.loc[(M, LTC_LABEL['N'], 0.95), 'cvar'])} against "
                         f"{d(t5.loc[(M, P, 0.95), 'cvar'])}; for women the figures are "
                         f"{d(t5.loc[(F, LTC_LABEL['N'], 0.95), 'cvar'])} against {d(t5.loc[(F, P, 0.95), 'cvar'])}"),
    }
    return c


def scenario_checks():
    t6 = pd.read_csv(T / "table6_scenarios.csv").set_index(["sex", "scenario"])
    t6b = pd.read_csv(T / "table6b_spend_down.csv").set_index(["sex", "income_tertile", "scenario"])
    name = {k: [s for _, s in t6.index if s.startswith(k)][0] for k in ("S1 shortfall from 2033, shift 25",
                                                                        "S1 shortfall from 2033, shift 50",
                                                                        "S1 shortfall from 2033, shift 100",
                                                                        "S1b", "S2", "S3")}
    chg = lambda k, col: (d(t6.loc[(M, name[k]), col]), d(t6.loc[(F, name[k]), col]))
    s0 = "S0 baseline"
    low = lambda sex, col: t6b.loc[(sex, "low", s0), col]
    return {
        "S1 25": f"{chg('S1 shortfall from 2033, shift 25', 'mean_change_vs_s0')[0]} for men and "
                 f"{chg('S1 shortfall from 2033, shift 25', 'mean_change_vs_s0')[1]} for women",
        "S1 50": f"{chg('S1 shortfall from 2033, shift 50', 'mean_change_vs_s0')[0]} and "
                 f"{chg('S1 shortfall from 2033, shift 50', 'mean_change_vs_s0')[1]}",
        "S1 100": f"{chg('S1 shortfall from 2033, shift 100', 'mean_change_vs_s0')[0]} and "
                  f"{chg('S1 shortfall from 2033, shift 100', 'mean_change_vs_s0')[1]}",
        "S1b": f"{chg('S1b', 'mean_change_vs_s0')[0]} and {chg('S1b', 'mean_change_vs_s0')[1]}",
        "S2 mean": f"{chg('S2', 'mean_change_vs_s0')[0]} and {chg('S2', 'mean_change_vs_s0')[1]}",
        "S2 cvar": f"CVaR95 rises by {chg('S2', 'cvar95_change_vs_s0')[0]} and {chg('S2', 'cvar95_change_vs_s0')[1]}",
        "S1 50 cvar": f"against {chg('S1 shortfall from 2033, shift 50', 'cvar95_change_vs_s0')[0]} and "
                      f"{chg('S1 shortfall from 2033, shift 50', 'cvar95_change_vs_s0')[1]}",
        "S3 mean": f"{chg('S3', 'mean_change_vs_s0')[0]} and {chg('S3', 'mean_change_vs_s0')[1]}",
        "S3 cvar": f"CVaR95 by {chg('S3', 'cvar95_change_vs_s0')[0]} and {chg('S3', 'cvar95_change_vs_s0')[1]}",
        "spend-down low": (f"{low(M, 'medicaid_at_65_pct'):.0f}% of men and {low(F, 'medicaid_at_65_pct'):.0f}% of women "
                           f"are already enrolled at 65 and a further {low(M, 'spend_down_pct'):.0f}% and "
                           f"{low(F, 'spend_down_pct'):.0f}% spend down to it, at a median age of "
                           f"{low(M, 'median_age_spend_down'):.0f} and {low(F, 'median_age_spend_down'):.0f}"),
        "spend-down middle": (f"{t6b.loc[(M, 'middle', s0), 'spend_down_pct']:.0f}% and "
                              f"{t6b.loc[(F, 'middle', s0), 'spend_down_pct']:.0f}% spend down"),
        "spend-down high": (f"{t6b.loc[(M, 'high', s0), 'spend_down_pct']:.0f}% and "
                            f"{t6b.loc[(F, 'high', s0), 'spend_down_pct']:.0f}%"),
        "no assets": f"{low(M, 'no_assets_at_65_pct'):.0f}% of the lowest tertile has no positive non-housing assets",
    }


def robustness_checks():
    f = T / "table8_robustness.csv"
    if not f.exists():
        return {}
    r = pd.read_csv(f).set_index("variant")
    m = lambda v, col: d(r.loc[v, col]) if v in r.index else "MISSING VARIANT"
    c = {
        "rob baseline": f"(men's out-of-pocket mean {m('baseline', 'male_pv_oop')} against",
        "rob independent": (f"falls from {m('baseline', 'male_cvar95_oop')} to {m('independent out-of-pocket draws', 'male_cvar95_oop')} "
                            f"and women's from {m('baseline', 'female_cvar95_oop')} to "
                            f"{m('independent out-of-pocket draws', 'female_cvar95_oop')}"),
        "rob independent mean": (f"({m('independent out-of-pocket draws', 'male_pv_oop')} and "
                                 f"{m('independent out-of-pocket draws', 'female_pv_oop')})"),
        "rob no eol": (f"lowers CVaR95 to {m('no end-of-life step', 'male_cvar95_oop')} and "
                       f"{m('no end-of-life step', 'female_cvar95_oop')}"),
        "rob all waves": (f"raises the mean to {m('out-of-pocket from all waves', 'male_pv_oop')} and "
                          f"{m('out-of-pocket from all waves', 'female_pv_oop')} and CVaR95 to "
                          f"{m('out-of-pocket from all waves', 'male_cvar95_oop')} and "
                          f"{m('out-of-pocket from all waves', 'female_cvar95_oop')}"),
        "rob medicare levels": (f"it is {m('Medicare not scaled to MCBS', 'male_pv_medicare')} for men; with it, "
                                f"{m('baseline', 'male_pv_medicare')}; using fee-for-service spending only, "
                                f"{m('Medicare from FFS only', 'male_pv_medicare')}"),
        "rob trustees level": f"would give {m('Medicare at Trustees level (x1.59)', 'male_pv_medicare')}",
        "rob uplift": (f"gives {m('D, L and N Medicare +25%', 'male_pv_medicare')}, and the functional cost gradient "
                       f"variant {m('functional cost gradient', 'male_pv_medicare')}"),
        "rob uncalibrated": (f"falls to {r.loc['mortality not calibrated', 'male_e65']:.1f} years for men and CVaR95 to "
                             f"{m('mortality not calibrated', 'male_cvar95_oop')}"),
        "rob improvement": (f"raises life expectancy to {r.loc['mortality improvement 1% a year', 'male_e65']:.1f} and "
                            f"{r.loc['mortality improvement 1% a year', 'female_e65']:.1f} years, the share ever in "
                            f"long-term care to {r.loc['mortality improvement 1% a year', 'male_ever_ltc_pct']:.0f}% and "
                            f"{r.loc['mortality improvement 1% a year', 'female_ever_ltc_pct']:.0f}%, and CVaR95 to "
                            f"{m('mortality improvement 1% a year', 'male_cvar95_oop')} and "
                            f"{m('mortality improvement 1% a year', 'female_cvar95_oop')}"),
        "rob discount": (f"raises men's CVaR95 to {m('discount 2%', 'male_cvar95_oop')} and at 4% lowers it to "
                         f"{m('discount 4%', 'male_cvar95_oop')}"),
        "rob spend-down": (f"from {r.loc['baseline', 'male_ever_medicaid_pct']:.0f}% and "
                           f"{r.loc['baseline', 'female_ever_medicaid_pct']:.0f}% to "
                           f"{r.loc['no spend-down', 'male_ever_medicaid_pct']:.0f}% and "
                           f"{r.loc['no spend-down', 'female_ever_medicaid_pct']:.0f}% and raises CVaR95 to "
                           f"{m('no spend-down', 'male_cvar95_oop')} and {m('no spend-down', 'female_cvar95_oop')}"),
        "rob income 0": (f"raises the Medicaid share to {r.loc['income meets 0% of out-of-pocket', 'male_ever_medicaid_pct']:.0f}% "
                         f"and {r.loc['income meets 0% of out-of-pocket', 'female_ever_medicaid_pct']:.0f}%"),
        "rob asset limit": (f"raises it to {r.loc['Medicaid asset limit $10,000', 'male_ever_medicaid_pct']:.0f}% and "
                            f"{r.loc['Medicaid asset limit $10,000', 'female_ever_medicaid_pct']:.0f}%"),
        **({} if not any("nursing home not its own state" in v for v in r.index) else {
            "rob refit nh": (
                f"gives {d(r.loc['nursing home not its own state (refit)', 'male_pv_oop']) } and "
                f"{d(r.loc['nursing home not its own state (refit)', 'female_pv_oop'])} with CVaR95 "
                f"{d(r.loc['nursing home not its own state (refit)', 'male_cvar95_oop'])} and "
                f"{d(r.loc['nursing home not its own state (refit)', 'female_cvar95_oop'])}"),
            "rob refit nh ltc": (
                f"{r.loc['nursing home not its own state (refit)', 'male_ever_ltc_pct']:.0f}% and "
                f"{r.loc['nursing home not its own state (refit)', 'female_ever_ltc_pct']:.0f}%"),
        }),
        "rob sex-only": (f"to {r.loc['sex-only model', 'male_ever_ltc_pct']:.0f}% and "
                         f"{r.loc['sex-only model', 'female_ever_ltc_pct']:.0f}% and CVaR95 to "
                         f"{m('sex-only model', 'male_cvar95_oop')} and {m('sex-only model', 'female_cvar95_oop')}"),
    }
    return c


def extension_checks():
    f = T / "table2d_model_extensions.csv"
    if not f.exists():
        return {}
    t = pd.read_csv(f)
    e65 = pd.read_csv(T / "table2d_model_extensions_e65.csv").set_index(["extension", "sex", "level"])
    lr = t.groupby("extension")[["lr_test_vs_full", "df"]].first()
    hr = t.set_index(["extension", "transition", "term"])["hazard_ratio"]
    c = {}
    if "income" in lr.index:
        c["ext income lr"] = f"{lr.loc['income', 'lr_test_vs_full']:,.1f} on {int(lr.loc['income', 'df'])} degrees of freedom"
        c["ext income hr"] = (f"from H to D (hazard ratio {hr[('income', 'H to D', 'low_income')]:.2f}), from C to D "
                              f"({hr[('income', 'C to D', 'low_income')]:.2f}), from C to a nursing home "
                              f"({hr[('income', 'C to N', 'low_income')]:.2f}) and from C to death "
                              f"({hr[('income', 'C to X', 'low_income')]:.2f})")
        c["ext income high"] = (f"to {hr[('income', 'C to N', 'high_income')]:.2f} and "
                                f"{hr[('income', 'C to X', 'high_income')]:.2f}")
        c["ext income e65"] = (f"expect {e65.loc[('income', 'male', 'low'), 'e65_from_C']:.1f} years and one in the "
                               f"highest {e65.loc[('income', 'male', 'high'), 'e65_from_C']:.1f}, and a woman "
                               f"{e65.loc[('income', 'female', 'low'), 'e65_from_C']:.1f} against "
                               f"{e65.loc[('income', 'female', 'high'), 'e65_from_C']:.1f}")
    if "duration" in lr.index:
        c["ext duration lr"] = (f"{lr.loc['duration', 'lr_test_vs_full']:,.1f} on "
                                f"{int(lr.loc['duration', 'df'])} degrees of freedom")
        c["ext duration hr"] = (f"from C to D is {hr[('duration', 'C to D', 'same_state_prev')]:.2f} of the intensity "
                                f"for a recent entrant, from D back to C {hr[('duration', 'D to C', 'same_state_prev')]:.2f}, "
                                f"from L to D {hr[('duration', 'L to D', 'same_state_prev')]:.2f} and from a nursing home "
                                f"back to D {hr[('duration', 'N to D', 'same_state_prev')]:.2f}")
        row = t[(t["extension"] == "duration") & (t["transition"] == "N to X")].iloc[0]
        c["ext duration death"] = (f"unchanged by the duration proxy (hazard ratio {row['hazard_ratio']:.2f}, interval "
                                   f"{row['hr_lo']:.2f} to {row['hr_hi']:.2f})")
        c["ext duration other"] = (f"({hr[('duration', 'L to X', 'same_state_prev')]:.2f}) and from disability "
                                   f"({hr[('duration', 'D to X', 'same_state_prev')]:.2f})")
    return c


def load():
    t1 = pd.read_csv(T / "table1_sample.csv").set_index("quantity")["value"]
    c = {}
    for fn in (lambda: sample_checks(t1), cost_checks, model_checks, validation_checks,
               result_checks, scenario_checks, robustness_checks, extension_checks):
        c.update(fn())
    return c


def cross_reference(text):
    tb = config.ROOT / "manuscript" / "tables.md"
    if not tb.exists():
        print("  tables.md not built yet; skipping the cross-reference check")
        return []
    rendered = set(re.findall(r"\*\*Table ([0-9A-Za-z]+)\.\*\*", tb.read_text()))
    tok = r"([0-9]+[a-f]?|A[0-9]+[a-f]?)"
    cited = set()
    for m in re.finditer(rf"Tables? {tok}(?:(?:,\s*|\s+and\s+){tok})*", text):
        cited.update(re.findall(tok, m.group(0)))
    problems = [f"Table {t} is cited in the prose but not rendered" for t in sorted(cited - rendered)]
    problems += [f"Table {t} is rendered but never cited" for t in sorted(rendered - cited)]
    print(f"  {len(rendered)} tables rendered, {len(cited)} cited")
    for p in problems:
        print(f"      {p}")
    return problems


def body_words(raw):
    body = raw.split("## 1. Introduction", 1)[1].split("## Declarations", 1)[0]
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"\$\$.*?\$\$", " ", body, flags=re.S)
    return len(re.findall(r"[A-Za-z0-9$%][^\s]*", body))


def main():
    raw = MS.read_text()
    text = raw.replace("**", "").replace("−", "-")
    checks = load()
    width = max(len(k) for k in checks)
    bad = [k for k, v in checks.items() if v.replace("−", "-") not in text]
    for k, v in checks.items():
        print(f"  {'ok ' if k not in bad else 'MISSING'}  {k:<{width}}  {v}")
    xref = cross_reference(text)
    figs = [p for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", raw) if not (config.ROOT / p).exists()]
    for p in figs:
        print(f"      figure not found: {p}")
    dashes = raw.count("—")
    holders = [h for h in ("ROBUSTNESS_RESULTS", "EXTENSIONS_RESULTS", "[CITE]", "[VERIFY]", "TODO") if h in raw]
    if dashes:
        print(f"  {dashes} em dash(es) in the prose")
    if holders:
        print(f"  placeholders left: {holders}")
    n = body_words(raw)
    new = re.sub(r"\*\*Word count\.\*\* [^ ]+ excluding", f"**Word count.** {n:,} excluding", raw)
    if new != raw:
        MS.write_text(new)
    print(f"  body word count {n:,}")
    if bad or xref or figs or dashes or holders:
        if bad:
            print(f"\n{len(bad)} figure(s) do not appear in {MS.name}.")
        sys.exit(1)
    print(f"\nAll {len(checks)} figures match the current tables.")


if __name__ == "__main__":
    main()
