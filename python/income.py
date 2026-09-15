"""
RQ2 by income: expected lifetime cost and tail risk by household income
tertile.

Income position is relative: household income (h*itot) is ranked within
interview wave and age group with the analysis weights, and cut into
tertiles. A simulated 65-year-old in tertile k starts from the entry mix
(health state, education, race-ethnicity) of HRS respondents aged 64 to 66 in
tertile k of that age group, and at each later age draws out-of-pocket cost
from respondents in the same state, age band, sex and income tertile, so the
life keeps its relative income position. Medicare cost uses the condition mix
within the tertile's states. The transition model has no income term; income
reaches mortality and health only through the entry state, education and
race-ethnicity, so differences in life expectancy by income are understated.
End-of-life draws are not split by income.

Writes Table 4c.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

import config
import costs
import population as pop
import simulate as sim

N = int(os.environ.get("P5_INCOME_N", 60_000))
TERTILES = ("low", "middle", "high")


def weighted_tertile(g):
    o = np.argsort(g["hh_income"].to_numpy(float), kind="stable")
    w = g["w"].to_numpy(float)[o]
    cum = (np.cumsum(w) - 0.5 * w) / w.sum()
    out = np.empty(len(g), dtype=int)
    out[o] = np.minimum((cum * 3).astype(int), 2)
    return pd.Series(out, index=g.index)


def assign_tertiles(pw):
    pw = pw[pw["hh_income"].notna()].copy()
    pw["w"] = pop.person_weight(pw)
    pw = pw[pw["w"] > 0]
    entry = pw[pw["age"].between(64, 66.99)]
    pw.loc[entry.index, "tert_entry"] = entry.groupby("wave", group_keys=False).apply(weighted_tertile)
    old = pw[pw["age"] >= 65].copy()
    old["band"] = np.where(old["age"] < 75, 0, 1)
    pw.loc[old.index, "tert_cost"] = old.groupby(["wave", "band"], group_keys=False).apply(weighted_tertile)
    return pw


def cvar(x, level):
    q = np.quantile(x, level)
    return float(q), float(x[x >= q].mean())


def main():
    pw = assign_tertiles(pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl"))
    m = pop.load_model()
    _, base_draws = sim.cost_tables()
    eol = {k: v for k, v in base_draws.items() if k.startswith("EOL")}
    rng = np.random.default_rng(config.SEED + 11)
    rows = []
    for k, name in enumerate(TERTILES):
        mix = pop.entry_mix(pw[pw["tert_entry"] == k])
        _, draws, t3d = costs.state_costs(pw[pw["tert_cost"] == k])
        draws.update(eol)
        medicare = {(r["state"], r["age_band"]): r["medicare_annual"] for _, r in t3d.iterrows()}
        for sex in ("male", "female"):
            r = sim.run_population(m, sex, N, rng, medicare, draws, config.PRIMARY_DISCOUNT, mix=mix)
            pvo = r["pv_oop"]
            share = pop.cells_for(mix, sex)
            st = np.zeros(4)
            for s, _, w in share:
                st[s] += w
            q95, c95 = cvar(pvo, 0.95)
            _, c99 = cvar(pvo, 0.99)
            rows.append({"sex": sex, "income_tertile": name,
                         **{f"entry_share_{sim.S[s]}_pct": 100 * st[s] for s in range(4)},
                         "any_college_pct": 100 * sum(w for _, z, w in share if z[1]),
                         "life_expectancy": float((r["death_age"] - config.ENTRY_AGE).mean()),
                         "ever_ltc_pct": 100 * float(r["ever_l"].mean()),
                         "pv_medicare_mean": float(r["pv_medicare"].mean()),
                         "pv_oop_mean": float(pvo.mean()), "pv_oop_median": float(np.median(pvo)),
                         "var95": q95, "cvar95": c95, "cvar99": c99,
                         "share_of_tail_ever_ltc_pct": 100 * float(r["ever_l"][pvo >= q95].mean())})
            print(f"  {sex:<6} {name:<6} e65 {rows[-1]['life_expectancy']:.1f}  ever L {rows[-1]['ever_ltc_pct']:.0f}%  "
                  f"Medicare ${rows[-1]['pv_medicare_mean']:,.0f}  OOP ${pvo.mean():,.0f}  CVaR95 ${c95:,.0f}", flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(config.TABLES / "table4c_lifetime_by_income.csv", index=False)
    print("\nwrote table 4c")


if __name__ == "__main__":
    main()
