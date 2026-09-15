"""
RQ2 and RQ3: lifetime Medicare and household cost from age 65, by
microsimulation, with an analytical check and tail measures.

Each simulated life is a draw, with the analysis weight, from HRS respondents
aged 64 to 66, carrying that person's health state, sex, education,
race-ethnicity, household income, non-housing assets and Medicaid status. The
life steps a year at a time through P(age, age + 1) from the calibrated model
and in each year alive accrues:

  Medicare        the state's cost (costs.py), higher in the lowest income
                  tertile by the MCBS income relativity, and concentrated in
                  the last year of life so that decedents account for the
                  25.1% of Medicare spending that Riley and Lubitz (2010)
                  measured, holding the overall level fixed
  out of pocket   a draw from the empirical HRS distribution for the state,
                  age band, sex, Medicaid status and income tertile, with
                  persistence across years through a Gaussian copula whose
                  permanent and decaying parts are estimated in costs.py; in
                  the year of death the draw comes from the exit-interview
                  distribution for that person's long-term-care status
  premiums        the standard Part B and base Part D premiums, except in
                  years on Medicaid, which pays them for dual eligibles

Medicaid spend-down. Households meet out-of-pocket costs from income up to
config.OOP_FROM_INCOME_SHARE of income and from assets beyond that. A life
whose non-housing assets fall below the Medicaid limit while it needs
long-term care goes onto Medicaid, and from then on draws from the Medicaid
out-of-pocket distribution and pays no premium. This is the spend-down the
research question asks about; the share of lives reaching it, the age at
which they do and the effect on the tail are reported by income tertile.

Financing scenarios (RQ4) are applied inside the simulation with common
random numbers, so scenario differences are not simulation noise. A scenario
adds to a life's out-of-pocket cost either a share of the Hospital Insurance
shortfall on its own Medicare spending, or the cohort's whole shortfall
spread over person-years in long-term care, and may add real cost growth.

Analytical check. With spend-down and persistence switched off the expected
present values have a closed form by forward recursion, which the simulation
means must match.

Writes Tables 4 (expected lifetime cost), 4b (parameter uncertainty), 4c (by
income tertile), 5 (tail risk), 6 (scenarios), 6b (spend-down) and the
per-life arrays the exhibits use.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

import config
import costs as costmod
from population import Calibrated, cells_for, entry_mix, entry_sample, load_model

S = dict(enumerate(config.STATES))
LIVE = len(config.STATES) - 1
DEAD = config.DEAD
LTC = [config.STATES.index(s) for s in config.LTC_STATES]
AGES = list(range(config.ENTRY_AGE, config.MAX_AGE))
PREMIUM = 12 * (config.PART_B_PREMIUM_MONTHLY_2024 + config.PART_D_PREMIUM_MONTHLY_2024)
ENTRIES = [0, 1, 2, 3, 4, None]
COHORT_YEAR = 2026


def label(entry):
    return "Population mix" if entry is None else config.STATE_LABELS[S[entry]]


def payable_share(year):
    """Interpolated Trustees path for the share of Part A benefits payable."""
    pts = sorted(config.HI_PAYABLE_PATH.items())
    if year < pts[0][0]:
        return 1.0
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return float(np.interp(year, xs, ys))


def annual_matrices(m, z, theta=None):
    return {a: m.transition_matrix(a, 1.0, z, theta) for a in AGES}


class Drawer:
    """Empirical draws with persistence: each life has a permanent component
    and an AR(1) component, combined into a latent normal whose quantile picks
    from the cell's weighted empirical distribution. Marginals are unchanged,
    so every expected value is the same as under independent draws."""

    def __init__(self, draws, permanent=0.0, phi=0.0):
        self.permanent = float(permanent)
        self.phi = float(phi)
        self.tab = {}
        for k, (v, p) in draws.items():
            o = np.argsort(v, kind="stable")
            self.tab[k] = (np.asarray(v, float)[o], np.cumsum(np.asarray(p, float)[o]))

    def means(self, keys):
        out = {}
        for k in keys:
            v, cw = self.tab[k]
            out[k] = float(np.dot(v, np.diff(np.concatenate([[0.0], cw]))))
        return out

    def resolve(self, state, band, sex, medicaid, tertile):
        """Most specific cell available for this life."""
        if medicaid:
            k = costmod.oop_key(state, band, sex, 1)
            if k in self.tab:
                return k
        else:
            k = costmod.oop_key(state, band, sex, 0, tertile)
            if k in self.tab:
                return k
            k = costmod.oop_key(state, band, sex, 0)
            if k in self.tab:
                return k
        return costmod.oop_key(state, band, sex)

    def eol_key(self, state, band, sex):
        k = f"EOL|{'ltc' if state in LTC else 'other'}|{band}|{sex}"
        return k if k in self.tab else f"EOL|{band}|{sex}"

    def start_latent(self, n, rng):
        perm = np.sqrt(self.permanent) * rng.standard_normal(n)
        trans = np.sqrt(1 - self.permanent) * rng.standard_normal(n)
        return perm, trans

    def step(self, trans, rng):
        if self.phi == 0.0:
            return np.sqrt(1 - self.permanent) * rng.standard_normal(len(trans))
        return self.phi * trans + np.sqrt((1 - self.permanent) * (1 - self.phi ** 2)) * rng.standard_normal(len(trans))

    def draw(self, key, u, rng, n=None):
        """u is the latent normal; None means an independent draw of n values."""
        v, cw = self.tab[key]
        q = rng.random(n) if u is None else np.clip(_ndtr(u), 1e-12, 1 - 1e-12)
        return v[np.minimum(np.searchsorted(cw, q * cw[-1], side="right"), len(v) - 1)]


def _ndtr(x):
    from scipy.special import ndtr
    return ndtr(x)


def cost_bundle(medicare_col="medicare_annual", persistence=True, min_wave=None):
    """Everything the simulation needs about costs."""
    t3d = pd.read_csv(config.TABLES / "table3d_medicare_by_state.csv")
    medicare = {(r["state"], r["age_band"]): r[medicare_col] for _, r in t3d.iterrows()}
    income_factor = float(t3d["income_factor_low_tertile"].iloc[0])
    draws = pd.read_pickle(config.DERIVED / "oop_draws.pkl")
    pers = json.loads((config.DERIVED / "oop_persistence.json").read_text())
    d = Drawer(draws, pers["permanent"] if persistence else 0.0,
               pers["phi"] if persistence else 0.0)
    return {"medicare": medicare, "income_factor": income_factor, "draws": d,
            "decedent_multiplier": 1.0, "level": 1.0}


def decedent_adjustment(model, mix, bundle, share=None):
    """Concentrate Medicare spending in the last year of life, holding the
    overall level fixed: decedents take `share` of spending (Riley and Lubitz
    2010), survivors the rest."""
    share = config.MEDICARE_DECEDENT_SHARE if share is None else share
    A = B = 0.0
    for sex in ("male", "female"):
        for s0, z, w0 in mix[sex]:
            P = annual_matrices(model, z)
            p = np.zeros(len(config.STATES))
            p[s0] = w0
            for a in AGES:
                band = costmod.band_of(a).item()
                d_prob = P[a][:LIVE, DEAD]
                for s in range(LIVE):
                    m = bundle["medicare"][(S[s], band)]
                    A += p[s] * d_prob[s] * m
                    B += p[s] * (1 - d_prob[s]) * m
                p = p @ P[a]
    M = share * B / ((1 - share) * A)
    scale = (A + B) / (M * A + B)
    bundle = dict(bundle)
    bundle["decedent_multiplier"], bundle["level"] = float(M), float(scale)
    return bundle


def ltc_charge_schedule(model, mix, bundle, hi_share, shift):
    """Dollars of Hospital Insurance shortfall per person-year in long-term
    care, by year from 65, when the whole cohort shortfall falls there."""
    tot = np.zeros(len(AGES))
    ltc_years = np.zeros(len(AGES))
    for sex in ("male", "female"):
        for s0, z, w0 in mix[sex]:
            P = annual_matrices(model, z)
            p = np.zeros(len(config.STATES))
            p[s0] = w0
            for i, a in enumerate(AGES):
                band = costmod.band_of(a).item()
                short = 1 - payable_share(COHORT_YEAR + i)
                for s in range(LIVE):
                    tot[i] += p[s] * bundle["medicare"][(S[s], band)] * bundle["level"] * hi_share * short
                ltc_years[i] += p[LTC].sum()
                p = p @ P[a]
    return shift * tot / np.maximum(ltc_years, 1e-9)


def simulate_cell(model, z, sex, lives, rng, bundle, disc, *, growth=0.0, eol=True,
                  spend_down=True, scenario=None, P=None):
    """Simulate the lives in one covariate cell. `lives` is a DataFrame with
    state, hh_income, assets, medicaid and tertile."""
    P = P or annual_matrices(model, z)
    n = len(lives)
    sk = "F" if sex == "female" else "M"
    draws = bundle["draws"]
    state = lives["state"].to_numpy(int).copy()
    income = lives["hh_income"].to_numpy(float)
    assets = lives["assets"].to_numpy(float)
    medicaid = lives["medicaid"].to_numpy(bool).copy()
    tertile = lives["tertile"].to_numpy(int)
    alive = np.ones(n, bool)
    pv_m, pv_o, pv_e, pv_p, pv_short = (np.zeros(n) for _ in range(5))
    ever_ltc = np.zeros(n, bool)
    ever_medicaid = medicaid.copy()
    age_medicaid = np.where(medicaid, float(config.ENTRY_AGE), np.nan)
    years_ltc = np.zeros(n)
    death_age = np.full(n, float(config.MAX_AGE))
    oop_by_year = np.zeros((len(AGES), n), dtype=np.float32)
    med_by_year = np.zeros_like(oop_by_year)
    state_by_year = np.full(oop_by_year.shape, DEAD, dtype=np.int8)
    mcd_by_year = np.zeros(oop_by_year.shape, dtype=bool)
    perm, trans = draws.start_latent(n, rng)
    scen = scenario or {}
    shift, hi_share = scen.get("shift", 0.0), scen.get("hi_share", config.HI_SHARE_OF_MEDICARE)
    ltc_charge = scen.get("ltc_charge")
    med_factor = np.where(tertile == 0, bundle["income_factor"], 1.0) * bundle["level"]

    for i, a in enumerate(AGES):
        year = COHORT_YEAR + i
        g = (1 + growth) ** i
        v = g / (1 + disc) ** i
        band = costmod.band_of(a).item()
        latent = perm + trans
        o_year = np.zeros(n)
        med_year = np.zeros(n)
        for s in range(LIVE):
            for mcd in (False, True):
                idx = np.flatnonzero(alive & (state == s) & (medicaid == mcd))
                if len(idx) == 0:
                    continue
                for t in np.unique(tertile[idx]):
                    j = idx[tertile[idx] == t]
                    key = draws.resolve(S[s], band, sk, mcd, int(t))
                    o_year[j] = draws.draw(key, latent[j] if draws.permanent or draws.phi else None,
                                           rng, len(j))
                med_year[idx] = bundle["medicare"][(S[s], band)] * med_factor[idx]
        ever_ltc |= alive & np.isin(state, LTC)
        years_ltc += (alive & np.isin(state, LTC)).astype(float)
        state_by_year[i, alive] = state[alive]
        mcd_by_year[i, alive] = medicaid[alive]

        u = rng.random(n)
        new = np.minimum((u[:, None] > np.cumsum(P[a][state], axis=1)).sum(axis=1), DEAD)
        died = alive & (new == DEAD)
        if eol and died.any():
            for s in range(LIVE):
                j = np.flatnonzero(died & (state == s))
                if len(j):
                    e = draws.draw(draws.eol_key(s, band, sk), latent[j], rng)
                    pv_e[j] += (e - o_year[j]) * v
                    o_year[j] = e
        med_year[died] *= bundle["decedent_multiplier"]

        # the Hospital Insurance shortfall, if the scenario passes it on
        short = np.zeros(n)
        if alive.any() and (shift or ltc_charge is not None):
            gap = 1 - payable_share(year)
            if ltc_charge is not None:
                short = np.where(alive & np.isin(state, LTC), ltc_charge[i] * g, 0.0)
            else:
                short = np.where(alive, shift * hi_share * med_year * gap, 0.0)
            short[medicaid] = 0.0        # Medicaid covers cost sharing for dual eligibles

        total_oop = (o_year + short) * g
        pv_o[alive] += (o_year[alive] + short[alive]) * v
        pv_short[alive] += short[alive] * v
        pv_m[alive] += med_year[alive] * v
        prem = np.where(medicaid, 0.0, PREMIUM)
        pv_p[alive] += prem[alive] * v
        oop_by_year[i] = total_oop
        med_by_year[i] = med_year * g

        if spend_down:
            from_income = np.minimum(total_oop, config.OOP_FROM_INCOME_SHARE * income)
            assets = np.where(alive, assets - (total_oop - from_income), assets)
            newly = (alive & ~medicaid & (assets < config.MEDICAID_ASSET_LIMIT)
                     & np.isin(state, LTC))
            medicaid |= newly
            age_medicaid = np.where(newly & np.isnan(age_medicaid), float(a), age_medicaid)
            ever_medicaid |= newly

        death_age[died] = a + 0.5
        alive &= ~died
        state = np.where(alive, new, DEAD)
        trans = draws.step(trans, rng)
        if not alive.any():
            break

    return {"pv_medicare": pv_m, "pv_oop": pv_o, "pv_eol_increment": pv_e, "pv_premium": pv_p,
            "pv_shortfall": pv_short, "death_age": death_age, "ever_ltc": ever_ltc,
            "ever_medicaid": ever_medicaid, "age_medicaid": age_medicaid,
            "years_ltc": years_ltc, "entry_state": lives["state"].to_numpy(int),
            "tertile": tertile, "assets": lives["assets"].to_numpy(float),
            "oop_by_year": oop_by_year, "med_by_year": med_by_year,
            "state_by_year": state_by_year, "medicaid_by_year": mcd_by_year}


def run_population(model, sex, n, rng, bundle, disc, *, sample=None, entry_state=None,
                   tertile=None, cache=None, keep_years=False, **kw):
    """Simulate n lives drawn from the HRS entry sample."""
    e = entry_sample() if sample is None else sample
    e = e[e["female"] == (1 if sex == "female" else 0)]
    if entry_state is not None:
        e = e[e["state"] == entry_state]
    if tertile is not None:
        e = e[e["tertile"] == tertile]
    if not len(e):
        raise ValueError("no entry records for this cell")
    cache = {} if cache is None else cache
    idx = rng.choice(len(e), size=n, p=(e["w"] / e["w"].sum()).to_numpy())
    lives = e.iloc[idx].reset_index(drop=True)
    parts = []
    for (college, nonwhite), g in lives.groupby(["college", "nonwhite"]):
        z = [1 if sex == "female" else 0, int(college), int(nonwhite)]
        key = tuple(z)
        if key not in cache:
            cache[key] = annual_matrices(model, z)
        parts.append(simulate_cell(model, z, sex, g, rng, bundle, disc, P=cache[key], **kw))
    out = {}
    for k in parts[0]:
        arrs = [p[k] for p in parts]
        out[k] = np.concatenate(arrs, axis=-1) if arrs[0].ndim == 1 else np.concatenate(arrs, axis=1)
    if not keep_years:
        for k in ("oop_by_year", "med_by_year", "state_by_year", "medicaid_by_year"):
            out.pop(k)
    return out


def analytic(cells, Ps, bundle, oop_mean, eol_mean, disc, growth=0.0, eol=True, medicaid=False,
             med_factor=1.0):
    """Expected PV of (Medicare, out of pocket, premiums) by forward recursion,
    with spend-down and persistence off: the check on the simulation."""
    out = np.zeros(3)
    starts = {}
    for s, z, w in cells:
        starts.setdefault(tuple(z), np.zeros(len(config.STATES)))[s] += w
    for z, p in starts.items():
        P = Ps[z]
        for i, a in enumerate(AGES):
            v = (1 + growth) ** i / (1 + disc) ** i
            band = costmod.band_of(a).item()
            live = p[:LIVE]
            om = np.array([oop_mean[(S[s], band)] for s in range(LIVE)])
            med = (np.array([bundle["medicare"][(S[s], band)] for s in range(LIVE)])
                   * bundle["level"] * med_factor)
            d_prob = P[a][:LIVE, DEAD]
            out[0] += v * (live * med * (1 + d_prob * (bundle["decedent_multiplier"] - 1))).sum()
            out[1] += v * live @ om
            if eol:
                em = np.array([eol_mean[(S[s], band)] for s in range(LIVE)])
                out[1] += v * (live * d_prob) @ (em - om)
            out[2] += v * live.sum() * (0.0 if medicaid else PREMIUM)
            p = p @ P[a]
    return out


def expected_pv(Ps, bundle, sample, sex, disc, entry_state=None, **kw):
    """Exact expected PV over the entry population, weighting the recursion by
    income tertile and Medicaid status because both change the cost draws (and
    the low tertile the Medicare level), exactly as the simulation does."""
    from population import entry_mix
    sub = sample[sample["female"] == (1 if sex == "female" else 0)]
    if entry_state is not None:
        sub = sub[sub["state"] == entry_state]
    out, tot = np.zeros(3), 0.0
    for (t, m), g in sub.groupby(["tertile", "medicaid"]):
        w = float(g["w"].sum())
        if w <= 0 or not len(g):
            continue
        om, em = cost_means(bundle, sex, medicaid=bool(m), tertile=int(t))
        f = bundle["income_factor"] if int(t) == 0 else 1.0
        cells = cells_for(entry_mix(sample=g), sex)
        out += w * np.asarray(analytic(cells, Ps, bundle, om, em, disc, medicaid=bool(m),
                                       med_factor=f, **kw))
        tot += w
    return out / tot


def cost_means(bundle, sex, medicaid=False, tertile=None):
    """Cell means of the draws, for the analytic recursion."""
    d = bundle["draws"]
    sk = "F" if sex == "female" else "M"
    keys = {}
    for s in range(LIVE):
        for b in costmod.BANDS:
            keys[(S[s], b)] = d.resolve(S[s], b, sk, medicaid, tertile)
    means = d.means(set(keys.values()))
    oop = {k: means[v] for k, v in keys.items()}
    ekeys = {(S[s], b): d.eol_key(s, b, sk) for s in range(LIVE) for b in costmod.BANDS}
    emeans = d.means(set(ekeys.values()))
    return oop, {k: emeans[v] for k, v in ekeys.items()}


def cvar(x, level):
    q = np.quantile(x, level)
    return float(q), float(x[x >= q].mean())


def tail_row(pvo, r, level, rng, reps=200):
    q, c = cvar(pvo, level)
    boot = np.array([cvar(pvo[rng.integers(0, len(pvo), len(pvo))], level)[1] for _ in range(reps)])
    tail = pvo >= q
    return {"level": level, "var": q, "cvar": c, "cvar_mc_se": float(boot.std(ddof=1)),
            "cvar_over_mean": c / pvo.mean(),
            "share_of_tail_ever_ltc_pct": 100 * float(r["ever_ltc"][tail].mean()),
            "share_of_all_ever_ltc_pct": 100 * float(r["ever_ltc"].mean()),
            "share_of_tail_medicaid_pct": 100 * float(r["ever_medicaid"][tail].mean()),
            "mean_death_age_in_tail": float(r["death_age"][tail].mean()),
            "mean_death_age_all": float(r["death_age"].mean()),
            "mean_years_ltc_in_tail": float(r["years_ltc"][tail].mean()),
            "eol_share_of_tail_pv_pct": 100 * float(r["pv_eol_increment"][tail].sum() / pvo[tail].sum())}


def summarise(r, sex, lab, extra=None):
    pvo, pvm, pvp = r["pv_oop"], r["pv_medicare"], r["pv_premium"]
    e = float((r["death_age"] - config.ENTRY_AGE).mean())
    row = {"sex": sex, "entry_state": lab, "n": len(pvo), "life_expectancy": e,
           "ever_ltc_pct": 100 * float(r["ever_ltc"].mean()),
           "years_ltc": float(r["years_ltc"].mean()),
           "ever_medicaid_pct": 100 * float(r["ever_medicaid"].mean()),
           "median_age_medicaid": float(np.nanmedian(r["age_medicaid"]))
           if np.isfinite(r["age_medicaid"]).any() else np.nan,
           "pv_medicare_mean": pvm.mean(), "pv_oop_mean": pvo.mean(),
           "pv_oop_median": np.median(pvo), "pv_oop_sd": pvo.std(),
           "mc_se_oop": pvo.std() / np.sqrt(len(pvo)),
           "pv_eol_increment_mean": r["pv_eol_increment"].mean(),
           "pv_premium_mean": pvp.mean(), "pv_household_mean": (pvo + pvp).mean()}
    return {**row, **(extra or {})}


def main():
    rng = np.random.default_rng(config.SEED)
    model = load_model()
    sample = entry_sample()
    mix = entry_mix(sample=sample)
    bundle = decedent_adjustment(model, mix, cost_bundle())
    n, disc = config.N_SIMULATIONS, config.PRIMARY_DISCOUNT
    print(f"Medicare decedent multiplier {bundle['decedent_multiplier']:.2f}, "
          f"level rescaling {bundle['level']:.3f} "
          f"(last year of life = {100 * config.MEDICARE_DECEDENT_SHARE:.1f}% of spending)")

    rows, tails, store = [], [], {}
    for sex in ("male", "female"):
        cache = {}
        for entry in ENTRIES:
            r = run_population(model, sex, n, rng, bundle, disc, sample=sample,
                               entry_state=entry, cache=cache, keep_years=entry is None)
            lab = label(entry)
            if entry is None:
                store[(sex, lab)] = r
            rows.append(summarise(r, sex, lab))
            for lvl in config.TAIL_LEVELS:
                tails.append({"sex": sex, "entry_state": lab, **tail_row(r["pv_oop"], r, lvl, rng)})
    t4 = pd.DataFrame(rows)
    t4.to_csv(config.TABLES / "table4_lifetime_costs.csv", index=False)
    t5 = pd.DataFrame(tails)
    t5.to_csv(config.TABLES / "table5_tail_risk.csv", index=False)
    pd.to_pickle(store, config.DERIVED / "sim_lives.pkl")

    # --- by income tertile (RQ2)
    rows = []
    for sex in ("male", "female"):
        cache = {}
        for t in (0, 1, 2):
            r = run_population(model, sex, n // 2, rng, bundle, disc, sample=sample,
                               tertile=t, cache=cache)
            q95, c95 = cvar(r["pv_oop"], 0.95)
            _, c99 = cvar(r["pv_oop"], 0.99)
            sub = sample[(sample["female"] == (1 if sex == "female" else 0)) & (sample["tertile"] == t)]
            rows.append(summarise(r, sex, ["low", "middle", "high"][t], {
                "var95": q95, "cvar95": c95, "cvar99": c99,
                "median_income": float(np.median(sub["hh_income"])),
                "median_assets": float(np.median(sub["assets"])),
                "medicaid_at_65_pct": 100 * float(np.average(sub["medicaid"], weights=sub["w"])),
                "entry_share_ltc_pct": 100 * float(np.average(np.isin(sub["state"], LTC), weights=sub["w"]))}))
    t4c = pd.DataFrame(rows).rename(columns={"entry_state": "income_tertile"})
    t4c.to_csv(config.TABLES / "table4c_lifetime_by_income.csv", index=False)

    # --- analytic check, with spend-down and persistence off
    plain = cost_bundle(persistence=False)
    plain = decedent_adjustment(model, mix, plain)
    rows = []
    for sex in ("male", "female"):
        cache = {}
        r = run_population(model, sex, n, rng, plain, disc, sample=sample, cache=cache,
                           spend_down=False)
        a = expected_pv(cache, plain, sample, sex, disc)
        rows.append({"sex": sex, "pv_medicare_sim": r["pv_medicare"].mean(), "pv_medicare_exact": a[0],
                     "pv_oop_sim": r["pv_oop"].mean(), "pv_oop_exact": a[1],
                     "mc_se_oop": r["pv_oop"].std() / np.sqrt(n)})
    t4d = pd.DataFrame(rows)
    t4d.to_csv(config.TABLES / "table4d_analytic_check.csv", index=False)

    # --- parameter uncertainty: exact expected values over parameter draws
    rows = []
    thetas = model.draw_parameters(200, seed=config.SEED)
    for sex in ("male", "female"):
        zs = sorted({tuple(z) for _, z, _ in mix[sex]})
        vals = {e: [] for e in ENTRIES}
        for th in thetas:
            Ps = {z: annual_matrices(model, list(z), th) for z in zs}
            for e in ENTRIES:
                vals[e].append(expected_pv(Ps, plain, sample, sex, disc, entry_state=e))
        for e in ENTRIES:
            v = np.array(vals[e])
            rows.append({"sex": sex, "entry_state": label(e),
                         "pv_medicare_lo": np.percentile(v[:, 0], 2.5),
                         "pv_medicare_hi": np.percentile(v[:, 0], 97.5),
                         "pv_oop_lo": np.percentile(v[:, 1], 2.5),
                         "pv_oop_hi": np.percentile(v[:, 1], 97.5)})
    pd.DataFrame(rows).to_csv(config.TABLES / "table4b_parameter_uncertainty.csv", index=False)

    with pd.option_context("display.width", 260, "display.float_format", "{:,.0f}".format):
        print("\n=== Expected lifetime cost from 65, PV at 3%, 2024 dollars ===")
        print(t4[["sex", "entry_state", "life_expectancy", "ever_ltc_pct", "years_ltc",
                  "ever_medicaid_pct", "pv_medicare_mean", "pv_oop_mean", "pv_oop_median",
                  "pv_premium_mean", "pv_eol_increment_mean"]].to_string(index=False))
        print("\n=== By income tertile ===")
        print(t4c[["sex", "income_tertile", "median_income", "median_assets", "entry_share_ltc_pct",
                   "life_expectancy", "ever_ltc_pct", "ever_medicaid_pct", "pv_medicare_mean",
                   "pv_oop_mean", "cvar95"]].to_string(index=False))
        print("\n=== Analytic check (spend-down and persistence off) ===")
        print(t4d.to_string(index=False))
    with pd.option_context("display.width", 260, "display.float_format", "{:,.1f}".format):
        print("\n=== Tail of lifetime out-of-pocket cost, 95% ===")
        print(t5[t5["level"] == 0.95].drop(columns="level").to_string(index=False))
    print("\nwrote tables 4, 4b, 4c, 4d, 5 and sim_lives.pkl")


if __name__ == "__main__":
    main()
