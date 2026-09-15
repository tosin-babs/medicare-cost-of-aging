"""
Check that the manuscript's headline numbers still match the analysis output.

The prose is written by hand, so a rerun that moves an estimate leaves the text
stale unless someone notices. This reads the current tables, formats each
headline figure the way the manuscript writes it, and fails if the string is
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


def d(x):
    return f"${x:,.0f}"


def load():
    t1 = pd.read_csv(T / "table1_sample.csv").set_index("quantity")["value"]
    t2 = pd.read_csv(T / "table2_intensities.csv")
    hr = t2.dropna(subset=["hazard_ratio"]).set_index(["transition", "term"])
    t3d = pd.read_csv(T / "table3d_medicare_by_state.csv").set_index(["state", "age_band"])
    t3c = pd.read_csv(T / "table3c_oop_by_state.csv").set_index(["state", "age_band", "sex"])
    t3e = pd.read_csv(T / "table3e_end_of_life_oop.csv").set_index(["age_band", "sex"])
    t3a = pd.read_csv(T / "table3a_mcbs_costs.csv").set_index("cell")
    t4 = pd.read_csv(T / "table4_lifetime_costs.csv").set_index(["sex", "entry_state"])
    t4b = pd.read_csv(T / "table4b_parameter_uncertainty.csv").set_index(["sex", "entry_state"])
    t4c = pd.read_csv(T / "table4c_lifetime_by_income.csv").set_index(["sex", "income_tertile"])
    t5 = pd.read_csv(T / "table5_tail_risk.csv").set_index(["sex", "entry_state", "level"])
    t6 = pd.read_csv(T / "table6_scenarios.csv")
    t6 = t6[t6["entry_state"] == "Population mix"].set_index(["sex", "scenario"])
    t6b = pd.read_csv(T / "table6b_spend_down.csv").set_index(["sex", "income_tertile", "scenario"])
    t7 = pd.read_csv(T / "table7_mortality_validation.csv").set_index("sex")
    t7q = pd.read_csv(T / "table7_qx_validation.csv").set_index(["sex", "age"])
    t7b = pd.read_csv(T / "table7b_prevalence_validation.csv").set_index(["sex", "age_band", "state"])
    t7c = pd.read_csv(T / "table7c_mortality_calibration.csv").set_index("sex")
    t7d = pd.read_csv(T / "table7d_spending_validation.csv").set_index("age_band")

    M, F, P = "male", "female", "Population mix"
    s1 = lambda x: f"S1 Part A payable 89% from 2033, shift {x}%"
    s2, s3 = "S2 shortfall on long-term-care state", "S3 real growth 1.7% and shift 50%"
    n_eol = int(t3e["n"].sum())
    lr = t2["lr_test_vs_base"].dropna().iloc[0]
    c = {
        "respondents": f"{int(float(t1['Respondents with at least one classified interview'])):,} respondents",
        "person-interviews": f"{int(float(t1['Person-interviews with a classified state'])):,} classified",
        "intervals": f"{int(float(t1['Intervals between interviews'])):,} intervals",
        "deaths": f"{int(float(t1['Deaths with an exact date'])):,} deaths",
        "share H": f"{float(t1['Weighted share of person-interviews in Healthy, %']):.1f}% of person-interviews",
        "share L": f"{float(t1['Weighted share of person-interviews in Long-term-care need, %']):.1f}% in L",
        "total intervals": "213,552 intervals",
        "exit decedents": f"{n_eol:,} decedents",
        "MCBS n": f"{int(t3a.loc['All', 'n']):,} beneficiary-years",
        "MCBS Medicare": f"{d(t3a.loc['All', 'medicare_total_mean'])} (standard error {d(t3a.loc['All', 'medicare_total_se'])})",
        "MA share": f"{100 * t3a.loc['All', 'share_in_ma']:.1f}% of beneficiary-years",
        "Part A share": f"{100 * t3a.loc['All', 'part_a_share_of_total']:.1f}% of all-payer",
        "LR": f"{lr:,.1f} on 24 degrees of freedom",
        "HR age H-X": f"{hr.loc[('H to X', 'age_per_10y'), 'hazard_ratio']:.2f} per decade",
        "HR age C-X": f"{hr.loc[('C to X', 'age_per_10y'), 'hazard_ratio']:.2f} from C",
        "HR age D-X": f"D ({hr.loc[('D to X', 'age_per_10y'), 'hazard_ratio']:.2f})",
        "HR age L-X": f"L ({hr.loc[('L to X', 'age_per_10y'), 'hazard_ratio']:.2f})",
        "HR college C-D": f"C to D (hazard ratio {hr.loc[('C to D', 'college'), 'hazard_ratio']:.2f})",
        "HR college C-L": f"C to L ({hr.loc[('C to L', 'college'), 'hazard_ratio']:.2f})",
        "HR nonwhite C-L": f"C to L ({hr.loc[('C to L', 'nonwhite'), 'hazard_ratio']:.2f})",
        "HR C-L age": f"({hr.loc[('C to L', 'age_per_10y'), 'hazard_ratio']:.2f} per decade, interval {hr.loc[('C to L', 'age_per_10y'), 'hr_lo']:.2f} to {hr.loc[('C to L', 'age_per_10y'), 'hr_hi']:.2f})",
        "e65 fitted M": f"{t7.loc[M, 'model_e65_uncalibrated']:.2f} years for men",
        "e65 fitted F": f"{t7.loc[F, 'model_e65_uncalibrated']:.2f} for women",
        "e65 table": f"{t7.loc[M, 'life_table_e65_2023']:.2f} and {t7.loc[F, 'life_table_e65_2023']:.2f}",
        "e65 calibrated": f"{t7.loc[M, 'model_e65']:.2f} years for men and {t7.loc[F, 'model_e65']:.2f} for women",
        "multiplier M": f"{t7c.loc[M, 'death_multiplier_at_65']:.2f} at 65 to {t7c.loc[M, 'death_multiplier_at_95']:.2f} at 95",
        "multiplier F": f"{t7c.loc[F, 'death_multiplier_at_65']:.2f} to {t7c.loc[F, 'death_multiplier_at_95']:.2f} for women",
        "qx95": f"{t7q.loc[(M, 95), 'model_qx']:.4f} for men against {t7q.loc[(M, 95), 'life_table_qx']:.4f}",
        "prev L 90 F": f"({t7b.loc[(F, '90-99', 'L'), 'model_pct']:.1f}% against {t7b.loc[(F, '90-99', 'L'), 'observed_pct']:.1f}%)",
        "spend ratio before": f"{t7d.loc['65-74', 'ratio_before_scaling']:.3f} and {t7d.loc['75+', 'ratio_before_scaling']:.3f}",
        "spend ratio after": f"{t7d.loc['65-74', 'ratio']:.3f} and {t7d.loc['75+', 'ratio']:.3f}",
        "scale factors": f"{t3d.loc[('C', '65-74'), 'mcbs_scale_factor']:.2f} and {t3d.loc[('C', '75+'), 'mcbs_scale_factor']:.2f}",
        "medicare H 65": d(t3d.loc[("H", "65-74"), "medicare_annual"]),
        "medicare L 65": d(t3d.loc[("L", "65-74"), "medicare_annual"]),
        "medicare H 75": d(t3d.loc[("H", "75+"), "medicare_annual"]),
        "medicare L 75": d(t3d.loc[("L", "75+"), "medicare_annual"]),
        "oop L75 M": d(t3c.loc[("L", "75+", M), "oop_mean"]),
        "oop L75 F": d(t3c.loc[("L", "75+", F), "oop_mean"]),
        "oop L75 p99 M": d(t3c.loc[("L", "75+", M), "oop_p99"]),
        "oop L75 p99 F": d(t3c.loc[("L", "75+", F), "oop_p99"]),
        "eol 75 M": d(t3e.loc[("75+", M), "eol_mean"]),
        "eol 75 F": d(t3e.loc[("75+", F), "eol_mean"]),
        "eol p99 M": d(t3e.loc[("75+", M), "eol_p99"]),
        "eol p99 F": d(t3e.loc[("75+", F), "eol_p99"]),
        "e65 mix M": f"{t4.loc[(M, P), 'life_expectancy']:.1f} more years",
        "e65 mix F": f"{t4.loc[(F, P), 'life_expectancy']:.1f} years, with",
        "years L M": f"{t4.loc[(M, P), 'years_in_L']:.2f} in long-term-care need",
        "years L F": f"{t4.loc[(F, P), 'years_in_L']:.2f} in long-term-care need",
        "years H M": f"{t4.loc[(M, P), 'years_in_H']:.2f} healthy",
        "years C M": f"{t4.loc[(M, P), 'years_in_C']:.2f} with chronic illness",
        "years D M": f"{t4.loc[(M, P), 'years_in_D']:.2f} with disability",
        "years D F": f"{t4.loc[(F, P), 'years_in_D']:.2f} in disability",
        "e65 L M": f"{t4.loc[(M, 'L'), 'life_expectancy']:.1f} years for men",
        "e65 L F": f"{t4.loc[(F, 'L'), 'life_expectancy']:.1f} for women",
        "e65 H M": f"rather than {t4.loc[(M, 'H'), 'life_expectancy']:.1f}",
        "ever L M": f"{t4.loc[(M, P), 'ever_ltc_pct']:.1f}% of men",
        "ever L F": f"{t4.loc[(F, P), 'ever_ltc_pct']:.1f}% of women",
        "medicare mix M": d(t4.loc[(M, P), "pv_medicare_mean"]),
        "medicare mix F": d(t4.loc[(F, P), "pv_medicare_mean"]),
        "medicare mix M lo": d(t4b.loc[(M, P), "pv_medicare_lo"]),
        "medicare mix M hi": d(t4b.loc[(M, P), "pv_medicare_hi"]),
        "oop mix M": d(t4.loc[(M, P), "pv_oop_mean"]),
        "oop mix F": d(t4.loc[(F, P), "pv_oop_mean"]),
        "oop analytic M": d(t4.loc[(M, P), "pv_oop_analytic"]),
        "oop mix M lo": d(t4b.loc[(M, P), "pv_oop_lo"]),
        "oop mix M hi": d(t4b.loc[(M, P), "pv_oop_hi"]),
        "oop median M": d(t4.loc[(M, P), "pv_oop_median"]),
        "oop median F": d(t4.loc[(F, P), "pv_oop_median"]),
        "premium M": d(t4.loc[(M, P), "pv_premium_mean"]),
        "premium F": d(t4.loc[(F, P), "pv_premium_mean"]),
        "eol pv M": d(t4.loc[(M, P), "pv_eol_increment_mean"]),
        "eol pv F": d(t4.loc[(F, P), "pv_eol_increment_mean"]),
        "medicare H M": d(t4.loc[(M, "H"), "pv_medicare_mean"]),
        "medicare L M": d(t4.loc[(M, "L"), "pv_medicare_mean"]),
        "medicare C M": d(t4.loc[(M, "C"), "pv_medicare_mean"]),
        "medicare C F": d(t4.loc[(F, "C"), "pv_medicare_mean"]),
        "oop H M": d(t4.loc[(M, "H"), "pv_oop_mean"]),
        "oop L M": d(t4.loc[(M, "L"), "pv_oop_mean"]),
        "income L at 65 low M": f"{t4c.loc[(M, 'low'), 'entry_share_L_pct']:.1f}% of men",
        "income L at 65 low F": f"{t4c.loc[(F, 'low'), 'entry_share_L_pct']:.1f}% of women in the lowest",
        "income L at 65 high": f"{t4c.loc[(M, 'high'), 'entry_share_L_pct']:.1f}% in the highest",
        "income ever L": f"{t4c.loc[(M, 'low'), 'ever_ltc_pct']:.1f}% of men against {t4c.loc[(M, 'high'), 'ever_ltc_pct']:.1f}%",
        "income oop low": f"{d(t4c.loc[(M, 'low'), 'pv_oop_mean'])} for men and {d(t4c.loc[(F, 'low'), 'pv_oop_mean'])} for women",
        "income oop high": f"{d(t4c.loc[(M, 'high'), 'pv_oop_mean'])} and {d(t4c.loc[(F, 'high'), 'pv_oop_mean'])}",
        "income e65": f"{t4c.loc[(M, 'low'), 'life_expectancy']:.1f} against {t4c.loc[(M, 'high'), 'life_expectancy']:.1f} years",
        "VaR95 M": d(t5.loc[(M, P, 0.95), "var"]),
        "CVaR95 M": d(t5.loc[(M, P, 0.95), "cvar"]),
        "CVaR99 M": d(t5.loc[(M, P, 0.99), "cvar"]),
        "VaR95 F": d(t5.loc[(F, P, 0.95), "var"]),
        "CVaR95 F": d(t5.loc[(F, P, 0.95), "cvar"]),
        "CVaR99 F": d(t5.loc[(F, P, 0.99), "cvar"]),
        "CVaR ratio M": f"{t5.loc[(M, P, 0.95), 'cvar_over_mean']:.1f} times the mean",
        "CVaR ratio F": f"{t5.loc[(F, P, 0.95), 'cvar_over_mean']:.1f} times for women",
        "tail LTC M": f"{t5.loc[(M, P, 0.95), 'share_of_tail_ever_ltc_pct']:.1f}% passed through L",
        "tail LTC F": f"{t5.loc[(F, P, 0.95), 'share_of_tail_ever_ltc_pct']:.1f}% against {t5.loc[(F, P, 0.95), 'share_of_all_ever_ltc_pct']:.1f}%",
        "tail death age": f"{t5.loc[(M, P, 0.95), 'mean_death_age_in_tail']:.1f} on average against {t5.loc[(M, P, 0.95), 'mean_death_age_all']:.1f}",
        "tail eol": f"{t5.loc[(M, P, 0.95), 'eol_share_of_tail_pv_pct']:.1f}% of the tail's present value for men and {t5.loc[(F, P, 0.95), 'eol_share_of_tail_pv_pct']:.1f}%",
        "CVaR95 L M": d(t5.loc[(M, "L", 0.95), "cvar"]),
        "CVaR95 L F": d(t5.loc[(F, "L", 0.95), "cvar"]),
        "S1 25": f"{d(t6.loc[(M, s1(25)), 'mean_change_vs_s0'])} for men and {d(t6.loc[(F, s1(25)), 'mean_change_vs_s0'])} for women",
        "S1 50": f"{d(t6.loc[(M, s1(50)), 'mean_change_vs_s0'])} and {d(t6.loc[(F, s1(50)), 'mean_change_vs_s0'])}",
        "S1 50 abstract": f"{d(t6.loc[(M, s1(50)), 'mean_change_vs_s0'])} for men and {d(t6.loc[(F, s1(50)), 'mean_change_vs_s0'])} for women",
        "S1 100": f"{d(t6.loc[(M, s1(100)), 'mean_change_vs_s0'])} and {d(t6.loc[(F, s1(100)), 'mean_change_vs_s0'])}",
        "S1 100 cvar": f"{d(t6.loc[(M, s1(100)), 'cvar95_change_vs_s0'])} and {d(t6.loc[(F, s1(100)), 'cvar95_change_vs_s0'])}",
        "S2 cvar": f"{d(t6.loc[(M, s2), 'cvar95_change_vs_s0'])} for men and {d(t6.loc[(F, s2), 'cvar95_change_vs_s0'])} for women",
        "S3 mean": f"{d(t6.loc[(M, s3), 'mean_change_vs_s0'])} and {d(t6.loc[(F, s3), 'mean_change_vs_s0'])}",
        "S3 cvar": f"{d(t6.loc[(M, s3), 'cvar95_change_vs_s0'])} and {d(t6.loc[(F, s3), 'cvar95_change_vs_s0'])}",
        "no assets low": f"{t6b.loc[(M, 'low', 'S0 baseline'), 'pct_no_positive_assets']:.1f}% of households",
        "exhaust low": f"{t6b.loc[(M, 'low', 'S0 baseline'), 'pct_exhausting_assets']:.1f}% of men and {t6b.loc[(F, 'low', 'S0 baseline'), 'pct_exhausting_assets']:.1f}% of women",
        "exhaust age": f"median age of {t6b.loc[(M, 'low', 'S0 baseline'), 'median_age_at_exhaustion']:.0f} and {t6b.loc[(F, 'low', 'S0 baseline'), 'median_age_at_exhaustion']:.0f}",
        "exhaust middle": f"{t6b.loc[(M, 'middle', 'S0 baseline'), 'pct_exhausting_assets']:.1f}% and {t6b.loc[(F, 'middle', 'S0 baseline'), 'pct_exhausting_assets']:.1f}%",
        "exhaust high": f"{t6b.loc[(M, 'high', 'S0 baseline'), 'pct_exhausting_assets']:.1f}% and {t6b.loc[(F, 'high', 'S0 baseline'), 'pct_exhausting_assets']:.1f}%",
    }
    rob = T / "table8_robustness.csv"
    if rob.exists():
        r = pd.read_csv(rob).set_index("variant")
        for v, key in (("discount 2%", "rob d2"), ("discount 4%", "rob d4"), ("mortality not calibrated", "rob uncal"),
                       ("no end-of-life step", "rob eol")):
            if v in r.index:
                c[key] = f"{d(r.loc[v, 'male_cvar95_oop'])}"
    return c


def cross_reference(text):
    tb = config.ROOT / "manuscript" / "tables.md"
    rendered = set(re.findall(r"\*\*Table ([0-9A-Za-z]+)\.\*\*", tb.read_text()))
    cited = set()
    for m in re.finditer(r"Tables? ([0-9]+[a-f]?|A[0-9]+)(?:\s+and\s+([0-9]+[a-f]?|A[0-9]+))?", text):
        cited.update(g for g in m.groups() if g)
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
    text = raw.replace("**", "")
    checks = load()
    width = max(len(k) for k in checks)
    bad = [k for k, v in checks.items() if v not in text]
    for k, v in checks.items():
        print(f"  {'ok ' if k not in bad else 'MISSING'}  {k:<{width}}  {v}")
    xref = cross_reference(text)
    figs = [p for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", raw) if not (config.ROOT / p).exists()]
    for p in figs:
        print(f"      figure not found: {p}")
    dashes = raw.count("—")
    holders = [h for h in ("ROBUSTNESS_PARAGRAPH", "[CITE]", "[VERIFY]", "TODO") if h in raw]
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
            print(f"\n{len(bad)} headline figure(s) do not appear in {MS.name}.")
        sys.exit(1)
    print(f"\nAll {len(checks)} headline figures match the current tables.")


if __name__ == "__main__":
    main()
