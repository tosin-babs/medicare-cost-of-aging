"""
RQ2 and RQ3: lifetime Medicare and out-of-pocket cost from age 65, by
microsimulation, with the analytical check and tail measures.

Each simulated life is drawn at 65 from the HRS entry mix (health state,
education and race-ethnicity by sex; population.py), steps a year at a time
through P(age, age + 1) from the calibrated model, and accrues in each year
alive the state's Medicare cost (costs.py), an out-of-pocket amount drawn from
the state's empirical HRS distribution for that age band and sex, and the
standard Part B premium. In the year of death the ordinary out-of-pocket draw
is replaced by a draw from the exit-interview end-of-life distribution. Costs
are 2024 dollars discounted at config.PRIMARY_DISCOUNT.

Two kinds of uncertainty are reported. Process uncertainty is the spread of
outcomes across lives at the point estimates; it is what the tail measures
describe. Parameter uncertainty is the spread of the expected values across
draws of the transition parameters from their asymptotic normal distribution.

Analytical check. Expected present values have a closed form by forward
recursion on the state distribution, including the end-of-life replacement,
and must agree with the simulation means to simulation error.

Writes Tables 4 (expected lifetime cost), 4b (parameter uncertainty), 5 (tail
of lifetime OOP and decomposition by path) and the per-life arrays used by
the scenario step.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from population import cells_for, entry_mix, load_model

S = {0: "H", 1: "C", 2: "D", 3: "L"}
# Standard Part B premium, 2024: $174.70 a month (CMS, "2024 Medicare Parts A
# & B Premiums and Deductibles", 12 October 2023). Paid by nearly all
# enrollees, including Medicare Advantage members; income-related surcharges
# and Part D and Medigap premiums are not included.
PART_B_PREMIUM_MONTHLY_2024 = 174.70
PREMIUM = 12 * PART_B_PREMIUM_MONTHLY_2024
AGES = list(range(config.ENTRY_AGE, config.MAX_AGE))
ENTRIES = [0, 1, 2, 3, None]


def ageband(a):
    return "65-74" if a < 75 else "75+"


def label(entry):
    return "Population mix" if entry is None else S[entry]


def annual_matrices(m, z, theta=None):
    return {a: m.transition_matrix(a, 1.0, z, theta) for a in AGES}


def cost_tables():
    t3d = pd.read_csv(config.TABLES / "table3d_medicare_by_state.csv")
    medicare = {(r["state"], r["age_band"]): r["medicare_annual"] for _, r in t3d.iterrows()}
    draws = pd.read_pickle(config.DERIVED / "oop_draws.pkl")
    return medicare, draws


def cost_means(draws, sex):
    k = "F" if sex == "female" else "M"
    oop = {(S[s], b): float(np.dot(*draws[f"{S[s]}|{b}|{k}"])) for s in range(4) for b in ("65-74", "75+")}
    eol = {b: float(np.dot(*draws[f"EOL|{b}|{k}"])) for b in ("65-74", "75+")}
    return oop, eol


def simulate(m, z, sex, entry_state, n, rng, medicare, draws, disc, growth=0.0,
             theta=None, P=None, eol=True):
    """Simulate n lives from one entry state and covariate vector."""
    P = P or annual_matrices(m, z, theta)
    state = np.full(n, entry_state, dtype=int)
    alive = np.ones(n, bool)
    pv_m, pv_o, pv_e, pv_p = (np.zeros(n) for _ in range(4))
    ever_l = np.zeros(n, bool)
    death_age = np.full(n, float(config.MAX_AGE))
    oop_by_year = np.zeros((len(AGES), n), dtype=np.float32)
    med_by_year = np.zeros_like(oop_by_year)
    state_by_year = np.full(oop_by_year.shape, 4, dtype=np.int8)
    sk = "F" if sex == "female" else "M"
    for i, a in enumerate(AGES):
        g = (1 + growth) ** i
        v = g / (1 + disc) ** i
        band = ageband(a)
        o_year = np.zeros(n)
        for s in range(4):
            idx = np.flatnonzero(alive & (state == s))
            if len(idx) == 0:
                continue
            vals, probs = draws[f"{S[s]}|{band}|{sk}"]
            o_year[idx] = rng.choice(vals, size=len(idx), p=probs)
            mc = medicare[(S[s], band)]
            med_by_year[i, idx] = mc * g
            pv_m[idx] += mc * v
        pv_o[alive] += o_year[alive] * v
        pv_p[alive] += PREMIUM * v
        oop_by_year[i] = o_year * g
        ever_l |= alive & (state == 3)
        state_by_year[i, alive] = state[alive]
        u = rng.random(n)
        new = np.minimum((u[:, None] > np.cumsum(P[a][state], axis=1)).sum(axis=1), 4)
        died = alive & (new == 4)
        if eol and died.any():
            vals, probs = draws[f"EOL|{band}|{sk}"]
            e = rng.choice(vals, size=int(died.sum()), p=probs)
            extra = e - o_year[died]
            pv_o[died] += extra * v
            pv_e[died] += extra * v
            oop_by_year[i, died] = e * g
        death_age[died] = a + 0.5
        alive &= ~died
        state = np.where(alive, new, 4)
        if not alive.any():
            break
    return {"pv_medicare": pv_m, "pv_oop": pv_o, "pv_eol_increment": pv_e, "pv_premium": pv_p,
            "death_age": death_age, "ever_l": ever_l, "oop_by_year": oop_by_year,
            "med_by_year": med_by_year, "state_by_year": state_by_year}


def run_population(m, sex, n, rng, medicare, draws, disc, growth=0.0, entry_state=None,
                   mix=None, cache=None, eol=True):
    """Simulate n lives drawn from the entry mix (optionally one entry state)."""
    mix = mix or entry_mix()
    cache = {} if cache is None else cache
    cells = cells_for(mix, sex, entry_state)
    counts = rng.multinomial(n, np.array([c[2] for c in cells]))
    parts = []
    for (s, z, _), k in zip(cells, counts):
        if k == 0:
            continue
        key = tuple(z)
        if key not in cache:
            cache[key] = annual_matrices(m, z)
        parts.append(simulate(m, z, sex, s, int(k), rng, medicare, draws, disc, growth,
                              P=cache[key], eol=eol))
    return {k: np.concatenate([p[k] for p in parts], axis=-1) for k in parts[0]}


def analytic(cells, Ps, medicare, oop_mean, eol_mean, disc, growth=0.0, eol=True):
    """Expected PV of (Medicare, OOP, premium) by forward recursion."""
    out = np.zeros(3)
    starts = {}
    for s, z, w in cells:
        starts.setdefault(tuple(z), np.zeros(5))[s] += w
    for z, p in starts.items():
        P = Ps[z]
        for i, a in enumerate(AGES):
            v = (1 + growth) ** i / (1 + disc) ** i
            band = ageband(a)
            live = p[:4]
            om = np.array([oop_mean[(S[s], band)] for s in range(4)])
            out[0] += v * sum(live[s] * medicare[(S[s], band)] for s in range(4))
            out[1] += v * live @ om
            if eol:
                out[1] += v * (live * P[a][:4, 4]) @ (eol_mean[band] - om)
            out[2] += v * live.sum() * PREMIUM
            p = p @ P[a]
    return out


def cvar(x, level):
    q = np.quantile(x, level)
    return float(q), float(x[x >= q].mean())


def main():
    rng = np.random.default_rng(config.SEED)
    m = load_model()
    medicare, draws = cost_tables()
    mix = entry_mix()
    n, disc = config.N_SIMULATIONS, config.PRIMARY_DISCOUNT

    rows, tails, store = [], [], {}
    for sex in ("male", "female"):
        cache = {}
        om, em = cost_means(draws, sex)
        for entry in ENTRIES:
            r = run_population(m, sex, n, rng, medicare, draws, disc, entry_state=entry, mix=mix, cache=cache)
            apv = analytic(cells_for(mix, sex, entry), cache, medicare, om, em, disc)
            lab = label(entry)
            store[(sex, lab)] = r
            pvo, pvm, pvp = r["pv_oop"], r["pv_medicare"], r["pv_premium"]
            e = float((r["death_age"] - config.ENTRY_AGE).mean())
            yrs = np.array([(r["state_by_year"] == k).sum(axis=0).mean() for k in range(4)])
            yrs = yrs * e / yrs.sum()
            rows.append({"sex": sex, "entry_state": lab, "n": len(pvo), "life_expectancy": e,
                         **{f"years_in_{S[k]}": yrs[k] for k in range(4)},
                         "ever_ltc_pct": 100 * float(r["ever_l"].mean()),
                         "pv_medicare_mean": pvm.mean(), "pv_medicare_analytic": apv[0],
                         "pv_oop_mean": pvo.mean(), "pv_oop_analytic": apv[1],
                         "pv_oop_median": np.median(pvo), "pv_oop_sd": pvo.std(),
                         "mc_se_oop": pvo.std() / np.sqrt(len(pvo)),
                         "pv_eol_increment_mean": r["pv_eol_increment"].mean(),
                         "pv_premium_mean": pvp.mean(), "pv_premium_analytic": apv[2],
                         "pv_household_mean": (pvo + pvp).mean()})
            for lvl in config.TAIL_LEVELS:
                q, c = cvar(pvo, lvl)
                tail = pvo >= q
                tails.append({"sex": sex, "entry_state": lab, "level": lvl, "var": q, "cvar": c,
                              "cvar_over_mean": c / pvo.mean(),
                              "share_of_tail_ever_ltc_pct": 100 * float(r["ever_l"][tail].mean()),
                              "share_of_all_ever_ltc_pct": 100 * float(r["ever_l"].mean()),
                              "mean_death_age_in_tail": float(r["death_age"][tail].mean()),
                              "mean_death_age_all": float(r["death_age"].mean()),
                              "eol_share_of_tail_pv_pct": 100 * float(r["pv_eol_increment"][tail].sum() / pvo[tail].sum())})
    t4 = pd.DataFrame(rows)
    t4.to_csv(config.TABLES / "table4_lifetime_costs.csv", index=False)
    t5 = pd.DataFrame(tails)
    t5.to_csv(config.TABLES / "table5_tail_risk.csv", index=False)
    pd.to_pickle(store, config.DERIVED / "sim_lives.pkl")

    # Parameter uncertainty: analytic expected values across parameter draws,
    # calibration held fixed.
    rows = []
    thetas = m.draw_parameters(200, seed=config.SEED)
    for sex in ("male", "female"):
        om, em = cost_means(draws, sex)
        zs = sorted({tuple(z) for _, z, _ in mix[sex]})
        vals = {e: [] for e in ENTRIES}
        for th in thetas:
            Ps = {z: annual_matrices(m, list(z), th) for z in zs}
            for e in ENTRIES:
                vals[e].append(analytic(cells_for(mix, sex, e), Ps, medicare, om, em, disc))
        for e in ENTRIES:
            v = np.array(vals[e])
            rows.append({"sex": sex, "entry_state": label(e),
                         "pv_medicare_lo": np.percentile(v[:, 0], 2.5), "pv_medicare_hi": np.percentile(v[:, 0], 97.5),
                         "pv_oop_lo": np.percentile(v[:, 1], 2.5), "pv_oop_hi": np.percentile(v[:, 1], 97.5),
                         "pv_premium_lo": np.percentile(v[:, 2], 2.5), "pv_premium_hi": np.percentile(v[:, 2], 97.5)})
    t4b = pd.DataFrame(rows)
    t4b.to_csv(config.TABLES / "table4b_parameter_uncertainty.csv", index=False)

    with pd.option_context("display.width", 250, "display.float_format", "{:,.0f}".format):
        print("=== Expected lifetime cost from 65, PV at 3%, 2024 dollars ===")
        print(t4[["sex", "entry_state", "life_expectancy", "ever_ltc_pct", "pv_medicare_mean",
                  "pv_medicare_analytic", "pv_oop_mean", "pv_oop_analytic", "pv_oop_median",
                  "pv_eol_increment_mean", "pv_premium_mean", "pv_premium_analytic"]].to_string(index=False))
        print(t4[["sex", "entry_state", "years_in_H", "years_in_C", "years_in_D", "years_in_L"]]
              .to_string(index=False, float_format="{:,.2f}".format))
        print("\n=== Parameter uncertainty (95% intervals of expected values) ===")
        print(t4b.to_string(index=False))
    with pd.option_context("display.width", 250, "display.float_format", "{:,.1f}".format):
        print("\n=== Tail of lifetime OOP, 95% ===")
        print(t5[t5["level"] == 0.95].drop(columns="level").to_string(index=False))
    print("\nwrote tables 4, 4b, 5 and sim_lives.pkl")


if __name__ == "__main__":
    main()
