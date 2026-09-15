"""
Mortality calibration and the lifetime-cost engine on a toy model.

    ../.venv/bin/python -m pytest -q tests
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

pytest.importorskip("torch")
import population as pop  # noqa: E402
import simulate as sim  # noqa: E402

S = ("H", "C", "D", "L")


class Toy:
    """Five states with fixed transitions among live states and Gompertz death."""

    def intensity_matrix(self, age, z=None, theta=None):
        Q = np.zeros((5, 5))
        Q[0, 1], Q[1, 2], Q[2, 1], Q[2, 3], Q[3, 2] = 0.10, 0.05, 0.10, 0.08, 0.03
        for j, b in enumerate((0.005, 0.010, 0.030, 0.120)):
            Q[j, 4] = b * np.exp(0.09 * (age - 65))
        Q[np.diag_indices(5)] = -Q.sum(axis=1)
        return Q


def toy_costs():
    medicare = {(s, b): 1000.0 * (i + 1) * (1.3 if b == "75+" else 1.0) for i, s in enumerate(S) for b in ("65-74", "75+")}
    draws = {}
    for i, s in enumerate(S):
        for b in ("65-74", "75+"):
            draws[f"{s}|{b}|M"] = (np.array([0.0, 500.0, 4000.0 * (i + 1)]), np.array([0.3, 0.6, 0.1]))
    for b in ("65-74", "75+"):
        draws[f"EOL|{b}|M"] = (np.array([0.0, 20000.0]), np.array([0.5, 0.5]))
    return medicare, draws


MIX = {"male": [(0, [0, 0, 0], 0.5), (1, [0, 0, 0], 0.3), (2, [0, 1, 0], 0.2)]}


def test_scale_death_keeps_generator():
    Q = Toy().intensity_matrix(80)
    R = pop.scale_death(Q, 0.6)
    assert np.allclose(R.sum(axis=1), 0.0)
    assert np.allclose(R[:4, 4], 0.6 * Q[:4, 4])
    off = ~np.eye(5, dtype=bool)
    off[:, 4] = False
    assert np.allclose(R[off], Q[off])


def test_uncalibrated_wrapper_is_identity():
    m = pop.Calibrated(Toy(), {})
    assert np.allclose(m.transition_matrix(70, 1.0, [0, 0, 0]), expm(Toy().intensity_matrix(70.5)))


def test_lower_death_multiplier_raises_life_expectancy():
    e0, _ = pop.life_table(Toy(), MIX, "male")
    e1, _ = pop.life_table(pop.Calibrated(Toy(), {"male": (np.log(0.7), 0.0)}), MIX, "male")
    assert e1 > e0 + 0.5


def test_calibration_recovers_a_known_multiplier():
    """Calibrate a model to its own scaled life table and recover the scaling."""
    import pandas as pd
    truth = pop.Calibrated(Toy(), {"male": (-0.3, 0.1), "female": (-0.3, 0.1)})
    mix = {"male": MIX["male"], "female": [(s, [1, z[1], z[2]], w) for s, z, w in MIX["male"]]}
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
    medicare, draws = toy_costs()
    rng = np.random.default_rng(1)
    cache = {}
    r = sim.run_population(m, "male", 60_000, rng, medicare, draws, 0.03, mix=MIX, cache=cache)
    om, em = sim.cost_means(draws, "male")
    a = sim.analytic(pop.cells_for(MIX, "male"), cache, medicare, om, em, 0.03)
    for key, i in (("pv_medicare", 0), ("pv_oop", 1), ("pv_premium", 2)):
        x = r[key]
        assert abs(x.mean() - a[i]) < 4 * x.std() / np.sqrt(len(x)) + 1e-6, (key, x.mean(), a[i])


def test_end_of_life_step_adds_expected_increment():
    m = pop.Calibrated(Toy(), {})
    medicare, draws = toy_costs()
    cache = {}
    sim.run_population(m, "male", 10, np.random.default_rng(0), medicare, draws, 0.03, mix=MIX, cache=cache)
    om, em = sim.cost_means(draws, "male")
    cells = pop.cells_for(MIX, "male")
    with_eol = sim.analytic(cells, cache, medicare, om, em, 0.03, eol=True)[1]
    without = sim.analytic(cells, cache, medicare, om, em, 0.03, eol=False)[1]
    assert with_eol > without
