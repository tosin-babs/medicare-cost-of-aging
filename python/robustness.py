"""
Robustness: each variant changes one decision and reports the headline
quantities for the population mix at 65: life expectancy, the share ever
needing long-term care, the share reaching Medicaid, expected lifetime
Medicare and out-of-pocket cost, and the tail of out-of-pocket cost with its
Monte Carlo standard error.

Variants that change costs, discounting, growth, calibration, persistence or
the spend-down rule reuse the fitted model. Variants that change the state
definitions or the sample refit the transition model with the sex-only
covariate set on the rebuilt interval file, recompute the entry sample, the
state costs and the calibration from that panel, and are compared with the
sex-only row rather than the baseline.

  discount 2% / 4%              discount rate
  Trustees real growth          real cost growth at the Part B per-beneficiary rate
  D, L and N Medicare +25%      uplift for the facility, hospice and
                                institutional events the Cost Supplement omits
  functional cost gradient      Medicare 1.5x C in D and 2.5x C in L and N,
                                rescaled to the same overall level
  Medicare not scaled to MCBS   condition-count cell means as they come
  Medicare from FFS only        MCBS cells from fee-for-service beneficiaries
  Medicare at Trustees level    level scaled to per-beneficiary spending in
                                Table V.D1 rather than to the MCBS mean
  no end-of-life concentration  Medicare flat in the year of death
  mortality not calibrated      the fitted model's own mortality
  calibration on H and C only   the multiplier spares the disabled states
  mortality improvement 1%      death intensities fall 1% a year from 65
  independent out-of-pocket     no persistence across years
  no end-of-life step           ordinary draws in the year of death
  end of life not by state      one exit distribution for everyone
  out-of-pocket from all waves  1998 onward rather than 2006 onward
  no spend-down                 Medicaid status fixed at 65
  income pays 0% / 20%          share of income met before assets are drawn on
  Medicaid asset limit $10,000  a more generous eligibility test
  sex-only model                covariates female only (reference for refits)
  nursing home not its own state, L at 2+ ADLs, dementia counts as
  long-term care, waves 9-16 only, weighted likelihood            (refits)

Writes Table 8. Lives per sex from P5_ROBUST_N (default 40,000); refits are
skipped with P5_ROBUST_REFIT=0 and can be run one at a time with
P5_ROBUST_ONLY=<name>.
"""

from __future__ import annotations

import fcntl
import json
import os

import numpy as np
import pandas as pd

import build_hrs
import config
import costs as costmod
import population as pop
import simulate as sim
from fit_transitions import ALLOWED
from multistate import MultiStateMarkov

N = int(os.environ.get("P5_ROBUST_N", 40_000))
REFIT = os.environ.get("P5_ROBUST_REFIT", "1") == "1"
ONLY = os.environ.get("P5_ROBUST_ONLY")
MAXITER = int(os.environ.get("P5_FIT_MAXITER", 4000))
OUT = config.TABLES / "table8_robustness.csv"


class SexOnly:
    """A female-only model that accepts the three-covariate z."""

    def __init__(self, m):
        self.m = m

    def intensity_matrix(self, age, z=None, theta=None):
        return self.m.intensity_matrix(age, [z[0]], theta)

    def draw_parameters(self, n, seed=0, robust=True):
        return self.m.draw_parameters(n, seed=seed, robust=robust)


def headline(model, bundle, label, sample, disc=config.PRIMARY_DISCOUNT, **kw):
    out = {"variant": label}
    for sex in ("male", "female"):
        rng = np.random.default_rng(config.SEED + 7)
        r = sim.run_population(model, sex, N, rng, bundle, disc, sample=sample, **kw)
        pv = r["pv_oop"]
        q95, c95 = sim.cvar(pv, 0.95)
        boot = np.array([sim.cvar(pv[rng.integers(0, len(pv), len(pv))], 0.95)[1] for _ in range(100)])
        out[f"{sex}_e65"] = float((r["death_age"] - config.ENTRY_AGE).mean())
        out[f"{sex}_ever_ltc_pct"] = 100 * float(r["ever_ltc"].mean())
        out[f"{sex}_ever_medicaid_pct"] = 100 * float(r["ever_medicaid"].mean())
        out[f"{sex}_pv_medicare"] = float(r["pv_medicare"].mean())
        out[f"{sex}_pv_oop"] = float(pv.mean())
        out[f"{sex}_cvar95_oop"] = c95
        out[f"{sex}_cvar95_mc_se"] = float(boot.std(ddof=1))
    print(f"  {label:<34} e65 {out['male_e65']:.1f}/{out['female_e65']:.1f}  "
          f"LTC {out['male_ever_ltc_pct']:.0f}/{out['female_ever_ltc_pct']:.0f}%  "
          f"Medicaid {out['male_ever_medicaid_pct']:.0f}/{out['female_ever_medicaid_pct']:.0f}%  "
          f"Medicare ${out['male_pv_medicare']:,.0f}/${out['female_pv_medicare']:,.0f}  "
          f"OOP ${out['male_pv_oop']:,.0f}/${out['female_pv_oop']:,.0f}  "
          f"CVaR95 ${out['male_cvar95_oop']:,.0f}/${out['female_cvar95_oop']:,.0f}", flush=True)
    return out


def medicare_dict(t3d, col="medicare_annual"):
    d = {(r["state"], r["age_band"]): r[col] for _, r in t3d.iterrows()}
    # A variant can empty a state: pooling the nursing home into L leaves no N
    # observations, and no life can then occupy N. Fill so the bundle still has
    # every cell the simulation looks up.
    for st in config.LIVE_STATES:
        for band in costmod.BANDS:
            if (st, band) not in d:
                d[(st, band)] = d.get(("L", band), max(v for (_, b), v in d.items() if b == band))
    return d


def with_medicare(bundle, medicare):
    b = dict(bundle)
    b["medicare"] = medicare
    return b


def functional_gradient(bundle):
    """Medicare 1.5x the chronic state in D and 2.5x in L and N, holding the
    weighted level fixed: what a functional gradient of the size reported in
    claims studies would do, as an assumption rather than an estimate."""
    t3d = pd.read_csv(config.TABLES / "table3d_medicare_by_state.csv").set_index(["state", "age_band"])
    mult = {"H": 0.5, "C": 1.0, "D": 1.5, "L": 2.5, "N": 2.5}
    med = {}
    for band in costmod.BANDS:
        base = t3d.loc[("C", band), "medicare_annual"]
        w = {s: t3d.loc[(s, band), "weight"] for s in config.LIVE_STATES}
        raw = {s: mult[s] * base for s in config.LIVE_STATES}
        old = sum(w[s] * t3d.loc[(s, band), "medicare_annual"] for s in config.LIVE_STATES)
        new = sum(w[s] * raw[s] for s in config.LIVE_STATES)
        for s in config.LIVE_STATES:
            med[(s, band)] = raw[s] * old / new
    return med


def refit(label, raw, sample_cols, adl_ltc_min=None, nursing_home_is_l=False,
          dementia=False, min_wave=None, weighted=False):
    saved = (config.ADL_LTC_MIN, config.ADL_DISABILITY)
    if adl_ltc_min is not None:
        config.ADL_LTC_MIN = adl_ltc_min
        config.ADL_DISABILITY = (1, adl_ltc_min - 1)
    try:
        people = build_hrs.person_table(raw)
        long = build_hrs.assign_state(build_hrs.to_long(raw), nursing_home_is_l=nursing_home_is_l,
                                      dementia_is_ltc=dementia)
        long = long[long["age"] >= 50]
        if min_wave is not None:
            long = long[long["wave"] >= min_wave]
        long = long.merge(people[["hhidpn", "female", "college", "nonwhite", "household"]], on="hhidpn")
        iv = build_hrs.build_intervals(long, people, build_hrs.known_alive_dates(raw))
        iv = iv.merge(people[["hhidpn", "female", "college", "nonwhite", "household"]], on="hhidpn")
        iv = iv[iv["nonwhite"].notna()]
    finally:
        config.ADL_LTC_MIN, config.ADL_DISABILITY = saved
    if weighted:
        w = pop.person_weight(long).groupby(long["hhidpn"]).mean()
        iv = iv.assign(weight=iv["hhidpn"].map(w).fillna(0.0))
        iv = iv[iv["weight"] > 0]
    allowed = ALLOWED
    if nursing_home_is_l:
        # The variant folds the nursing home into L, so N has no observations.
        # Estimating its intensities from nothing sends them to extreme values
        # and the matrix exponential then returns negative occupancy; drop the
        # state from the model instead.
        n = config.STATES.index("N")
        allowed = [(j, k) for j, k in ALLOWED if n not in (j, k)]
    m = MultiStateMarkov(len(config.STATES), allowed, covariates=["female"],
                         age_knots=config.AGE_KNOTS, max_piece=config.MAX_PIECE_YEARS)
    # Start from the fitted sex-only model where the transitions are the same:
    # the variants move the state boundaries, not the model's structure.
    init = None
    if allowed == ALLOWED:
        init = pd.read_pickle(config.DERIVED / "msm_full.pkl")["base_theta"]
    m.fit(iv, init=init, weight_col="weight" if weighted else None, maxiter=MAXITER)
    print(f"  refit {label}: {len(iv):,} observations, loglik {m.loglik_:,.1f}, "
          f"{m.method_}, converged {m.converged_} ({m.message_})", flush=True)
    if m.at_bound_:
        print(f"    {len(m.at_bound_)} parameters at a bound: {m.at_bound_[:6]}", flush=True)
    model = SexOnly(m)
    sample = pop.entry_sample(long)
    mix = pop.entry_mix(sample=sample)
    coef, _ = pop.calibrate(model, mix)
    cal = pop.Calibrated(model, coef)
    _, draws, t3d = costmod.state_costs(long)
    _, eol = costmod.end_of_life(long)
    draws.update(eol)
    b = sim.cost_bundle()
    b["draws"] = sim.Drawer(draws, b["draws"].permanent, b["draws"].phi)
    b["medicare"] = medicare_dict(t3d)
    return cal, sample, sim.decedent_adjustment(cal, mix, b)


def main():
    sample = pop.entry_sample()
    mix = pop.entry_mix(sample=sample)
    model = pop.load_model()
    bundle = sim.decedent_adjustment(model, mix, sim.cost_bundle())
    rows = []

    def save():
        """A single-variant run (P5_ROBUST_ONLY) merges into the existing table
        instead of replacing it; the lock lets several such runs share the file."""
        df = pd.DataFrame(rows)
        with open(OUT.with_suffix(".lock"), "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if ONLY and OUT.exists():
                old = pd.read_csv(OUT)
                df = pd.concat([old[~old["variant"].isin(df["variant"])], df], ignore_index=True)
            df.to_csv(OUT, index=False)

    def add(*a, **kw):
        if ONLY and ONLY not in a[2]:
            return
        rows.append(headline(*a, **kw))
        save()

    add(model, bundle, "baseline", sample)
    for d in (0.02, 0.04):
        add(model, bundle, f"discount {int(100 * d)}%", sample, disc=d)
    g = config.TR_PER_BENEFICIARY_GROWTH_REAL["B"]
    add(model, bundle, f"Trustees real growth {100 * g:.1f}%", sample, growth=g)
    up = {k: (v * 1.25 if k[0] in ("D", "L", "N") else v) for k, v in bundle["medicare"].items()}
    add(model, with_medicare(bundle, up), "D, L and N Medicare +25%", sample)
    add(model, with_medicare(bundle, functional_gradient(bundle)), "functional cost gradient", sample)
    t3d = pd.read_csv(config.TABLES / "table3d_medicare_by_state.csv")
    add(model, with_medicare(bundle, medicare_dict(t3d, "medicare_mix_only")),
        "Medicare not scaled to MCBS", sample)
    _, _, t3d_ffs = costmod.state_costs(pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl"),
                                        medicare_col="medicare_ffs_only_mean")
    add(model, with_medicare(bundle, medicare_dict(t3d_ffs)), "Medicare from FFS only", sample)
    t7d = pd.read_csv(config.TABLES / "table7d_spending_validation.csv") if (
        config.TABLES / "table7d_spending_validation.csv").exists() else None
    if t7d is not None:
        f = float(config.TR_PER_BENEFICIARY_2024["total"] / t7d["model_medicare_per_person_year"].mean())
        b = dict(bundle)
        b["level"] = bundle["level"] * f
        add(model, b, f"Medicare at Trustees level (x{f:.2f})", sample)
    add(model, sim.cost_bundle(), "no end-of-life concentration", sample)
    add(pop.load_model(calibrated=False), bundle, "mortality not calibrated", sample)
    coef_hc, _ = pop.calibrate(pop.load_fitted(), mix, states=("H", "C"))
    add(pop.Calibrated(pop.load_fitted(), coef_hc, states=("H", "C")), bundle,
        "calibration on H and C only", sample)
    coef = {k: tuple(v) for k, v in json.loads(pop.CAL_FILE.read_text())["coef"].items()}
    add(pop.Calibrated(pop.load_fitted(), coef, improvement=0.01), bundle,
        "mortality improvement 1% a year", sample)
    plain = sim.decedent_adjustment(model, mix, sim.cost_bundle(persistence=False))
    add(model, plain, "independent out-of-pocket draws", sample)
    add(model, bundle, "no end-of-life step", sample, eol=False)
    b = dict(bundle)
    b["draws"] = sim.Drawer({k: (v, np.diff(np.concatenate([[0.0], cw])))
                             for k, (v, cw) in bundle["draws"].tab.items() if "|ltc|" not in k
                             and "|other|" not in k},
                            bundle["draws"].permanent, bundle["draws"].phi)
    add(model, b, "end of life not by state", sample)
    pw = pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl")
    _, draws_all, t3d_all = costmod.state_costs(pw, min_wave=4)
    _, eol_all = costmod.end_of_life(pw, min_year=1998)
    draws_all.update(eol_all)
    b = dict(bundle)
    b["draws"] = sim.Drawer(draws_all, bundle["draws"].permanent, bundle["draws"].phi)
    b["medicare"] = medicare_dict(t3d_all)
    add(model, b, "out-of-pocket from all waves", sample)
    add(model, bundle, "no spend-down", sample, spend_down=False)
    for share in (0.0, 0.20):
        saved = config.OOP_FROM_INCOME_SHARE
        config.OOP_FROM_INCOME_SHARE = share
        add(model, bundle, f"income meets {int(100 * share)}% of out-of-pocket", sample)
        config.OOP_FROM_INCOME_SHARE = saved
    saved = config.MEDICAID_ASSET_LIMIT
    config.MEDICAID_ASSET_LIMIT = 10_000.0
    add(model, bundle, "Medicaid asset limit $10,000", sample)
    config.MEDICAID_ASSET_LIMIT = saved
    base = SexOnly(pop.load_fitted("base"))
    coef_b, _ = pop.calibrate(base, mix)
    add(pop.Calibrated(base, coef_b), bundle, "sex-only model", sample)

    if REFIT:
        raw = build_hrs.load()
        for lab, kw in (("nursing home not its own state (refit)", {"nursing_home_is_l": True}),
                        ("L at 2+ ADLs (refit)", {"adl_ltc_min": 2}),
                        ("dementia counts as long-term care (refit)", {"dementia": True}),
                        ("waves 9-16 only (refit)", {"min_wave": 9}),
                        ("weighted likelihood (refit)", {"weighted": True})):
            if ONLY and ONLY not in lab:
                continue
            cal, vsample, vbundle = refit(lab, raw, None, **kw)
            rows.append(headline(cal, vbundle, lab, vsample))
            save()
    print(f"\nwrote {OUT.name} with {len(rows)} variants")


if __name__ == "__main__":
    main()
