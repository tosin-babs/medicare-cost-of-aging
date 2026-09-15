"""
Robustness: each variant changes one decision and reports the headline
quantities for the population mix at 65: life expectancy, the share ever in
long-term-care need, expected lifetime Medicare and out-of-pocket cost, and
CVaR95 of lifetime out-of-pocket cost.

Variants that change only costs, discounting, growth, calibration or the
end-of-life step reuse the fitted model. Variants that change the state
definition or the sample refit the transition model with the sex-only
covariate set on the rebuilt interval file, recompute the entry mix and the
state costs from the rebuilt panel, and recalibrate mortality, so each
compares like with like. The sex-only model on the baseline panel is
reported for that comparison.

  discount 2% / 4%             discount rate
  Trustees real growth         real cost growth at the Part B per beneficiary rate
  D and L Medicare +25%        uplift for facility, hospice and institutional
                               events the MCBS Cost Supplement excludes
  mortality not calibrated     the fitted model's own mortality
  no end-of-life step          ordinary draws in the year of death
  sex-only model               covariates female only (reference for refits)
  L at 2+ ADLs                 alternative long-term-care threshold (refit)
  nursing home not L           residence does not define L (refit)
  waves 9-16 only              2008-2022 panel (refit)

Writes Table 8. N lives per sex from P5_ROBUST_N (default 40,000); refits
skipped with P5_ROBUST_REFIT=0.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

import build_hrs
import config
import costs
import population as pop
import simulate as sim
from fit_transitions import ALLOWED
from multistate import MultiStateMarkov

N = int(os.environ.get("P5_ROBUST_N", 40_000))
REFIT = os.environ.get("P5_ROBUST_REFIT", "1") == "1"


class SexOnly:
    """A female-only model that accepts the three-covariate z."""

    def __init__(self, m):
        self.m = m

    def intensity_matrix(self, age, z=None, theta=None):
        return self.m.intensity_matrix(age, [z[0]], theta)

    def draw_parameters(self, n, seed=0):
        return self.m.draw_parameters(n, seed=seed)


def headline(model, medicare, draws, label, mix, disc=config.PRIMARY_DISCOUNT, growth=0.0, eol=True):
    rng = np.random.default_rng(config.SEED + 7)
    out = {"variant": label}
    for sex in ("male", "female"):
        r = sim.run_population(model, sex, N, rng, medicare, draws, disc, growth=growth, mix=mix, eol=eol)
        pvo = r["pv_oop"]
        out[f"{sex}_e65"] = float((r["death_age"] - config.ENTRY_AGE).mean())
        out[f"{sex}_ever_ltc_pct"] = 100 * float(r["ever_l"].mean())
        out[f"{sex}_pv_medicare"] = float(r["pv_medicare"].mean())
        out[f"{sex}_pv_oop"] = float(pvo.mean())
        out[f"{sex}_cvar95_oop"] = cvar95(pvo)
    print(f"  {label:<28} e65 {out['male_e65']:.1f}/{out['female_e65']:.1f}  "
          f"ever L {out['male_ever_ltc_pct']:.0f}/{out['female_ever_ltc_pct']:.0f}%  "
          f"PV Medicare ${out['male_pv_medicare']:,.0f}/${out['female_pv_medicare']:,.0f}  "
          f"PV OOP ${out['male_pv_oop']:,.0f}/${out['female_pv_oop']:,.0f}  "
          f"CVaR95 ${out['male_cvar95_oop']:,.0f}/${out['female_cvar95_oop']:,.0f}", flush=True)
    return out


def cvar95(x):
    q = np.quantile(x, 0.95)
    return float(x[x >= q].mean())


def medicare_dict(t3d):
    return {(r["state"], r["age_band"]): r["medicare_annual"] for _, r in t3d.iterrows()}


def refit(label, raw, eol_draws, adl_ltc_min=None, nursing_home_is_l=None, min_wave=None):
    saved = (config.ADL_LTC_MIN, config.ADL_DISABILITY, config.NURSING_HOME_IS_L)
    if adl_ltc_min is not None:
        config.ADL_LTC_MIN = adl_ltc_min
        config.ADL_DISABILITY = (1, adl_ltc_min - 1)
    if nursing_home_is_l is not None:
        config.NURSING_HOME_IS_L = nursing_home_is_l
    try:
        people = raw[["hhidpn", "ragender", "raracem", "rahispan", "raeduc", "radyear", "radmonth"]].copy()
        for c in people.columns[1:]:
            people[c] = pd.to_numeric(people[c], errors="coerce")
        people["female"] = (people["ragender"] == 2).astype(int)
        people["college"] = (people["raeduc"] >= 4).astype(int)
        people["nonwhite"] = ((people["raracem"] != 1) | (people["rahispan"] == 1)).astype(int)
        long = build_hrs.assign_state(build_hrs.to_long(raw))
        long = long[long["age"] >= 50]
        if min_wave is not None:
            long = long[long["wave"] >= min_wave]
        long = long.merge(people[["hhidpn", "female", "college", "nonwhite"]], on="hhidpn")
        iv = build_hrs.build_intervals(long, people).merge(people[["hhidpn", "female"]], on="hhidpn")
    finally:
        config.ADL_LTC_MIN, config.ADL_DISABILITY, config.NURSING_HOME_IS_L = saved
    m = MultiStateMarkov(5, ALLOWED, covariates=["female"]).fit(iv)
    print(f"  refit {label}: {len(iv):,} intervals, loglik {m.loglik_:,.1f}, "
          f"{m.method_}, converged {m.converged_}", flush=True)
    model = SexOnly(m)
    mix = pop.entry_mix(long)
    coef, _ = pop.calibrate(model, mix)
    _, draws, t3d = costs.state_costs(long)
    draws.update(eol_draws)
    return pop.Calibrated(model, coef), mix, medicare_dict(t3d), draws


def main():
    mix = pop.entry_mix()
    m = pop.load_model()
    medicare, draws = sim.cost_tables()
    eol_draws = {k: v for k, v in draws.items() if k.startswith("EOL")}
    rows = [headline(m, medicare, draws, "baseline", mix)]
    for d in (0.02, 0.04):
        rows.append(headline(m, medicare, draws, f"discount {int(100 * d)}%", mix, disc=d))
    g = config.TR_PER_BENEFICIARY_GROWTH_REAL["B"]
    rows.append(headline(m, medicare, draws, f"Trustees real growth {100 * g:.1f}%", mix, growth=g))
    up = {k: (v * 1.25 if k[0] in ("D", "L") else v) for k, v in medicare.items()}
    rows.append(headline(m, up, draws, "D and L Medicare +25%", mix))
    t3d = pd.read_csv(config.TABLES / "table3d_medicare_by_state.csv")
    raw_med = {(r["state"], r["age_band"]): r["medicare_mix_only"] for _, r in t3d.iterrows()}
    rows.append(headline(m, raw_med, draws, "Medicare not scaled to MCBS", mix))
    rows.append(headline(pop.load_model(calibrated=False), medicare, draws, "mortality not calibrated", mix))
    rows.append(headline(m, medicare, draws, "no end-of-life step", mix, eol=False))
    base = SexOnly(pop.load_fitted("base"))
    coef, _ = pop.calibrate(base, mix)
    rows.append(headline(pop.Calibrated(base, coef), medicare, draws, "sex-only model", mix))
    pd.DataFrame(rows).to_csv(config.TABLES / "table8_robustness.csv", index=False)
    if REFIT:
        raw = build_hrs.load()
        for lab, kw in (("L at 2+ ADLs (refit)", {"adl_ltc_min": 2}),
                        ("nursing home not L (refit)", {"nursing_home_is_l": False}),
                        ("waves 9-16 only (refit)", {"min_wave": 9})):
            model, vmix, vmed, vdraws = refit(lab, raw, eol_draws, **kw)
            rows.append(headline(model, vmed, vdraws, lab, vmix))
            pd.DataFrame(rows).to_csv(config.TABLES / "table8_robustness.csv", index=False)
    print("\nwrote table 8")


if __name__ == "__main__":
    main()
