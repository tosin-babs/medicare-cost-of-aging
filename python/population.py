"""
The population the simulation starts from, and the mortality calibration.

Entry mix. A simulated 65-year-old is drawn from the weighted joint
distribution of health state, sex, education and race-ethnicity among HRS
respondents interviewed at ages 64 to 66, nursing-home residents included
through their own analysis weight. Simulating the reference person (no
college, non-Hispanic white) instead would understate life expectancy by
about a year, because education enters mortality strongly.

Calibration. The fitted model pools 1998 to 2022 and its all-cause mortality
at 65 to 80 runs above the 2023 US period life table. Actuarial practice for
a health-state model used to price or project is to keep the relative
structure (which states die faster, and by how much) and calibrate the level
to the population table. Death intensities from every live state are
multiplied by exp(c0 + c1 (age - 65) / 10), by sex, with c0 and c1 chosen to
minimize the lx-weighted squared log difference between the model's
one-year death probabilities for the entry mix and the 2023 table at ages
65 to 99. The uncalibrated model is kept as a reported robustness variant and
the size of the adjustment is reported with the validation.

Writes data/derived/mortality_calibration.json and Table 7c.
"""

from __future__ import annotations

import json
import pickle

import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.optimize import minimize

import config
from multistate import MultiStateMarkov

CAL_FILE = config.DERIVED / "mortality_calibration.json"
FIT_AGES = list(range(config.ENTRY_AGE, 100))
ALL_AGES = list(range(config.ENTRY_AGE, config.MAX_AGE))


def person_weight(df):
    """Respondent weight, or the nursing-home resident weight where the
    respondent weight is zero (HRS sets it to zero for residents)."""
    w = pd.to_numeric(df["wtresp"], errors="coerce").fillna(0.0)
    nh = pd.to_numeric(df["wtr_nh"], errors="coerce").fillna(0.0)
    return w.where(w > 0, nh)


def entry_mix(pw=None):
    """{sex: [(state, z, weight)]}, z = [female, college, nonwhite]."""
    if pw is None:
        pw = pd.read_pickle(config.DERIVED / "hrs_person_wave.pkl")
    e = pw[pw["age"].between(64, 66.99) & pw["state"].notna()].copy()
    e["w"] = person_weight(e)
    out = {}
    for fem, g in e.groupby("female"):
        cells = g.groupby([g["state"].astype(int), "college", "nonwhite"])["w"].sum()
        cells = cells / cells.sum()
        out["female" if fem else "male"] = [(int(s), [int(fem), int(c), int(nw)], float(p))
                                            for (s, c, nw), p in cells.items() if p > 0]
    return out


def cells_for(mix, sex, entry_state=None):
    cells = [c for c in mix[sex] if entry_state is None or c[0] == entry_state]
    tot = sum(c[2] for c in cells)
    return [(s, z, w / tot) for s, z, w in cells]


def scale_death(Q, f):
    Q = np.array(Q, dtype=float, copy=True)
    Q[:4, 4] *= f
    np.fill_diagonal(Q, 0.0)
    Q[np.diag_indices_from(Q)] = -Q.sum(axis=1)
    return Q


class Calibrated:
    """A fitted model with death intensities scaled by exp(c0 + c1 (age-65)/10)."""

    def __init__(self, model, coef=None):
        self.model = model
        self.coef = dict(coef or {})

    def factor(self, age, z):
        c0, c1 = self.coef.get("female" if z[0] else "male", (0.0, 0.0))
        return float(np.exp(c0 + c1 * (age - config.ENTRY_AGE) / 10.0))

    def intensity_matrix(self, age, z=None, theta=None):
        return scale_death(self.model.intensity_matrix(age, z, theta), self.factor(age, z))

    def transition_matrix(self, age, dt=1.0, z=None, theta=None):
        return expm(self.intensity_matrix(age + dt / 2.0, z, theta) * dt)

    def draw_parameters(self, n, seed=0):
        return self.model.draw_parameters(n, seed=seed)


def load_fitted(which="full"):
    with open(config.DERIVED / "msm_full.pkl", "rb") as fh:
        d = pickle.load(fh)
    if which == "full":
        m = MultiStateMarkov(5, d["allowed"], covariates=d["covariates"])
        m.theta_, m.cov_, m.se_ = d["theta"], d["cov"], d["se"]
    else:
        m = MultiStateMarkov(5, d["allowed"], covariates=["female"])
        m.theta_ = d["base_theta"]
    return m


def load_model(calibrated=True):
    m = load_fitted()
    if not calibrated or not CAL_FILE.exists():
        return Calibrated(m, {})
    coef = json.loads(CAL_FILE.read_text())["coef"]
    return Calibrated(m, {k: tuple(v) for k, v in coef.items()})


def _base(model, mix, sex, ages):
    zs = {tuple(z) for _, z, _ in mix[sex]}
    return {z: [np.asarray(model.intensity_matrix(a + 0.5, list(z)), float) for a in ages] for z in zs}


def _alive(mix, sex, base, coef, ages):
    c0, c1 = coef
    start = {}
    for s, z, w in mix[sex]:
        start.setdefault(tuple(z), np.zeros(5))[s] += w
    alive = np.zeros(len(ages) + 1)
    for z, p in start.items():
        alive[0] += p[:4].sum()
        for i, a in enumerate(ages):
            f = np.exp(c0 + c1 * (a + 0.5 - config.ENTRY_AGE) / 10.0)
            p = p @ expm(scale_death(base[z][i], f))
            alive[i + 1] += p[:4].sum()
    return alive / alive[0]


def life_table(model, mix, sex, coef=(0.0, 0.0)):
    """Model e65 and one-year qx at ages 65 to MAX_AGE-1 for the entry mix."""
    alive = _alive(mix, sex, _base(model, mix, sex, ALL_AGES), coef, ALL_AGES)
    e65 = float(np.sum(0.5 * (alive[:-1] + alive[1:])))
    qx = 1.0 - alive[1:] / np.maximum(alive[:-1], 1e-300)
    return e65, dict(zip(ALL_AGES, qx))


def calibrate(model, mix=None, lt=None):
    """Return ({sex: (c0, c1)}, rows) for an uncalibrated model."""
    mix = mix or entry_mix()
    lt = pd.read_csv(config.DERIVED / "lifetable_us_2023.csv") if lt is None else lt
    coef, rows = {}, []
    for sex in ("male", "female"):
        t = lt[lt["sex"] == sex].set_index("age")
        q_lt = t.loc[FIT_AGES, "qx"].to_numpy(float)
        w = t.loc[FIT_AGES, "lx"].to_numpy(float)
        w = w / w.sum()
        base = _base(model, mix, sex, FIT_AGES)

        def loss(c):
            al = _alive(mix, sex, base, c, FIT_AGES)
            q = 1.0 - al[1:] / al[:-1]
            return float(np.sum(w * (np.log(q) - np.log(q_lt)) ** 2))

        res = minimize(loss, x0=[0.0, 0.0], method="Nelder-Mead",
                       options={"xatol": 1e-5, "fatol": 1e-12, "maxiter": 2000})
        coef[sex] = (float(res.x[0]), float(res.x[1]))
        e_raw, _ = life_table(model, mix, sex)
        e_cal, _ = life_table(model, mix, sex, coef[sex])
        rows.append({"sex": sex, "c0": coef[sex][0], "c1_per_10y": coef[sex][1],
                     **{f"death_multiplier_at_{a}": float(np.exp(coef[sex][0] + coef[sex][1] * (a - 65) / 10))
                        for a in (65, 75, 85, 95)},
                     "e65_uncalibrated": e_raw, "e65_calibrated": e_cal,
                     "e65_life_table_2023": float(t.loc[65, "ex"]), "loss": res.fun})
    return coef, rows


def main():
    mix = entry_mix()
    for sex in ("male", "female"):
        tot = np.zeros(4)
        for s, z, w in mix[sex]:
            tot[s] += w
        col = sum(w for _, z, w in mix[sex] if z[1])
        nw = sum(w for _, z, w in mix[sex] if z[2])
        print(f"  entry mix, {sex}: H/C/D/L {np.round(tot, 3)}, any college {col:.3f}, "
              f"nonwhite or Hispanic {nw:.3f}")
    coef, rows = calibrate(load_fitted(), mix)
    CAL_FILE.write_text(json.dumps({"coef": coef, "fit_ages": [FIT_AGES[0], FIT_AGES[-1]],
                                    "target": "US period life table 2023, NCHS NVSR 74-6"}, indent=2))
    t = pd.DataFrame(rows)
    t.to_csv(config.TABLES / "table7c_mortality_calibration.csv", index=False)
    print("\n=== Mortality calibration to the 2023 US life table ===")
    print(t.round(3).to_string(index=False))
    print("\nwrote mortality_calibration.json and table 7c")


if __name__ == "__main__":
    main()
