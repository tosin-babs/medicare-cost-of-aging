"""
Parameter recovery for the multi-state estimator on simulated panel data.

    ../.venv/bin/python -m pytest -q tests
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

pytest.importorskip("torch")
from multistate import MultiStateMarkov, simulate_panel  # noqa: E402

# Three states: 0 healthy, 1 ill, 2 dead. Healthy -> ill, ill -> healthy,
# healthy -> dead, ill -> dead, each with a Gompertz age slope.
ALLOWED = [(0, 1), (0, 2), (1, 0), (1, 2)]
TRUE = {(0, 1): (np.log(0.08), 0.03), (0, 2): (np.log(0.01), 0.09),
        (1, 0): (np.log(0.15), -0.02), (1, 2): (np.log(0.04), 0.08)}


def true_Q(age, z=None):
    Q = np.zeros((3, 3))
    for (j, k), (b0, b1) in TRUE.items():
        Q[j, k] = np.exp(b0 + b1 * (age - 65))
    Q -= np.diag(Q.sum(axis=1))
    return Q


@pytest.fixture(scope="module")
def fitted():
    rng = np.random.default_rng(11)
    n = 2500
    ages = rng.uniform(55, 80, n)
    data = simulate_panel(true_Q, n, ages, interview_gap=2.0, n_waves=6, seed=3,
                          step=1 / 12)
    m = MultiStateMarkov(3, ALLOWED).fit(data)
    return m, data


def test_converges(fitted):
    m, _ = fitted
    assert m.converged_
    assert np.all(np.isfinite(m.se_))


def test_recovers_intercepts_and_slopes(fitted):
    m, _ = fitted
    assert not m.at_bound_, m.at_bound_
    est = m.theta_.reshape(len(ALLOWED), 2)
    se = m.se_.reshape(len(ALLOWED), 2)
    for t, key in enumerate(ALLOWED):
        b0, b1 = TRUE[key]
        slope, slope_se = est[t, 1] / 10, se[t, 1] / 10     # per decade -> per year
        # Within four standard errors, plus a small allowance for the
        # midpoint approximation over two-year intervals.
        assert abs(est[t, 0] - b0) < 4 * se[t, 0] + 0.05, (key, est[t, 0], b0)
        assert abs(slope - b1) < 4 * slope_se + 0.01, (key, slope, b1)


def test_transition_matrix_is_stochastic(fitted):
    m, _ = fitted
    P = m.transition_matrix(70, dt=1.0)
    assert np.allclose(P.sum(axis=1), 1.0, atol=1e-10)
    assert (P >= -1e-12).all()
    assert P[2, 2] == pytest.approx(1.0)


def test_exact_death_contributes(fitted):
    _, data = fitted
    assert (data["obstype"] == 3).sum() > 100
