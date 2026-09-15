"""
Mortality calibration and the lifetime-cost engine on a toy six-state model.

    ../.venv/bin/python -m pytest -q tests
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

pytest.importorskip("torch")
import config  # noqa: E402
import population as pop  # noqa: E402
import simulate as sim  # noqa: E402

S = list(config.LIVE_STATES)
K = len(config.STATES)


class Toy:
    """Fixed transitions among live states and Gompertz death by state."""

    def intensity_matrix(self, age, z=None, theta=None):
        Q = np.zeros((K, K))
        Q[0, 1], Q[1, 2], Q[2, 1], Q[2, 3], Q[3, 2], Q[3, 4], Q[4, 3] = 0.10, 0.05, 0.10, 0.06, 0.03, 0.05, 0.02
        for j, b in enumerate((0.005, 0.010, 0.030, 0.080, 0.150)):
            Q[j, K - 1] = b * np.exp(0.09 * (age - 65))
        Q[np.diag_indices(K)] = -Q.sum(axis=1)
        return Q


def toy_bundle(permanent=0.0, phi=0.0):
    medicare = {(s, b): 1000.0 * (i + 1) * (1.3 if b == "75+" else 1.0)
                for i, s in enumerate(S) for b in ("65-74", "75+")}
    draws = {}
    for i, s in enumerate(S):
        for b in ("65-74", "75+"):
            for sx in ("M", "F"):
                draws[f"{s}|{b}|{sx}"] = (np.array([0.0, 500.0, 4000.0 * (i + 1)]), np.array([0.3, 0.6, 0.1]))
    for b in ("65-74", "75+"):
        for sx in ("M", "F"):
            draws[f"EOL|{b}|{sx}"] = (np.array([0.0, 20000.0]), np.array([0.5, 0.5]))
    return {"medicare": medicare, "income_factor": 1.0, "draws": sim.Drawer(draws, permanent, phi),
            "decedent_multiplier": 1.0, "level": 1.0}


def toy_sample():
    rows = []
    for state, college, w in ((0, 0, 0.5), (1, 0, 0.3), (2, 1, 0.2)):
        for fem in (0, 1):
            rows.append({"state": state, "female": fem, "college": college, "nonwhite": 0, "w": w,
                         "hh_income": 30000.0, "assets": 1e9, "medicaid": 0, "tertile": 1})
    return pd.DataFrame(rows)


def test_scale_death_keeps_generator():
    Q = Toy().intensity_matrix(80)
    R = pop.scale_death(Q, 0.6)
    assert np.allclose(R.sum(axis=1), 0.0)
    assert np.allclose(R[:K - 1, K - 1], 0.6 * Q[:K - 1, K - 1])
    off = ~np.eye(K, dtype=bool)
    off[:, K - 1] = False
    assert np.allclose(R[off], Q[off])


def test_scale_death_subset_of_states():
    Q = Toy().intensity_matrix(80)
    R = pop.scale_death(Q, 0.5, states=("H", "C"))
    assert np.allclose(R[:2, K - 1], 0.5 * Q[:2, K - 1])
    assert np.allclose(R[2:K - 1, K - 1], Q[2:K - 1, K - 1])


def test_uncalibrated_wrapper_is_identity():
    m = pop.Calibrated(Toy(), {})
    assert np.allclose(m.transition_matrix(70, 1.0, [0, 0, 0]), expm(Toy().intensity_matrix(70.5)))


def test_lower_death_multiplier_raises_life_expectancy():
    mix = pop.entry_mix(sample=toy_sample())
    e0, _ = pop.life_table(Toy(), mix, "male")
    e1, _ = pop.life_table(pop.Calibrated(Toy(), {"male": (np.log(0.7), 0.0)}), mix, "male")
    assert e1 > e0 + 0.5


def test_calibration_recovers_a_known_multiplier():
    """Calibrate a model to its own scaled life table and recover the scaling."""
    truth = pop.Calibrated(Toy(), {"male": (-0.3, 0.1), "female": (-0.3, 0.1)})
    mix = pop.entry_mix(sample=toy_sample())
    rows = []
    for sex in ("male", "female"):
        e, q = pop.life_table(truth, mix, sex)
        alive = np.cumprod([1.0] + [1 - q[a] for a in pop.ALL_AGES])
        for i, a in enumerate(pop.ALL_AGES):
            rows.append({"sex": sex, "age": a, "qx": q[a], "lx": alive[i], "ex": e if a == 65 else np.nan})
    coef, _ = pop.calibrate(Toy(), mix, lt=pd.DataFrame(rows))
    assert coef["male"][0] == pytest.approx(-0.3, abs=0.02)
    assert coef["male"][1] == pytest.approx(0.1, abs=0.02)


def test_simulation_matches_recursion():
    m = pop.Calibrated(Toy(), {})
    bundle = toy_bundle()
    sample = toy_sample()
    rng = np.random.default_rng(1)
    cache = {}
    r = sim.run_population(m, "male", 60_000, rng, bundle, 0.03, sample=sample, cache=cache,
                           spend_down=False)
    om, em = sim.cost_means(bundle, "male")
    a = sim.analytic(pop.cells_for(pop.entry_mix(sample=sample), "male"), cache, bundle, om, em, 0.03)
    for key, i in (("pv_medicare", 0), ("pv_oop", 1), ("pv_premium", 2)):
        x = r[key]
        assert abs(x.mean() - a[i]) < 4 * x.std() / np.sqrt(len(x)) + 1e-6, (key, x.mean(), a[i])


def test_persistence_keeps_the_mean_and_raises_the_tail():
    m = pop.Calibrated(Toy(), {})
    sample = toy_sample()
    out = {}
    for rho in (0.0, 0.6):
        bundle = toy_bundle(permanent=rho, phi=0.5)
        r = sim.run_population(m, "male", 40_000, np.random.default_rng(3), bundle, 0.03,
                               sample=sample, spend_down=False)
        out[rho] = r["pv_oop"]
    assert abs(out[0.6].mean() - out[0.0].mean()) < 4 * out[0.0].std() / np.sqrt(40_000) * 2
    assert sim.cvar(out[0.6], 0.95)[1] > sim.cvar(out[0.0], 0.95)[1]


def test_spend_down_moves_poor_lives_onto_medicaid():
    m = pop.Calibrated(Toy(), {})
    bundle = toy_bundle()
    sample = toy_sample().assign(assets=500.0, hh_income=1000.0)
    r = sim.run_population(m, "male", 5_000, np.random.default_rng(4), bundle, 0.03, sample=sample)
    # with assets below the limit, every life that needs long-term care spends down
    assert r["ever_ltc"].mean() > 0.05
    assert (r["ever_medicaid"] >= r["ever_ltc"]).all()
    assert np.nanmin(r["age_medicaid"]) >= config.ENTRY_AGE
    r2 = sim.run_population(m, "male", 5_000, np.random.default_rng(4), bundle, 0.03, sample=sample,
                            spend_down=False)
    assert r2["ever_medicaid"].mean() == 0.0


def test_payable_share_path():
    assert sim.payable_share(2030) == 1.0
    assert sim.payable_share(2033) == pytest.approx(0.89)
    assert sim.payable_share(2050) == pytest.approx(0.85)
    assert 0.85 < sim.payable_share(2075) < 0.93
