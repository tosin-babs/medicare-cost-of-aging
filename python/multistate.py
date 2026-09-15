"""
Continuous-time multi-state Markov model for interval-censored panel data.

HRS respondents are interviewed about every two years. Their health state is
observed at each interview, transitions between interviews are not, and deaths
are dated to the month. This module fits transition intensities to data of
exactly that kind, with the same likelihood as R's msm package (Jackson 2011).

Model. States 0..K-2 are transient; state K-1 is death, absorbing. For each
allowed transition j -> k,

    log q_jk(a, z) = b0_jk + b1_jk * (a - age_centre) / 10 + g_jk' z,

a Gompertz-type age gradient (b1 is per 10 years of age) with log-linear
covariate effects. Within an observation interval the intensity matrix is held
at its value at the interval's midpoint age, the piecewise-constant
approximation msm uses.

Likelihood contributions, for an interval of length d starting in state r:
  * next state s observed at an interview:   P(d)[r, s],  P(d) = expm(Q d)
  * death at an exact time d:                sum_{k alive} P(d)[r, k] q_k,death
  * alive, state unknown (right-censored):   sum_{k alive} P(d)[r, k]

Estimation is maximum likelihood by BFGS, with a bounded trust-region fallback,
using exact gradients from PyTorch (torch.linalg.matrix_exp is
differentiable). Standard errors come from the inverse observed information,
also by automatic differentiation. Age enters per decade so that intercept and
slope gradients are of similar size. Parameter recovery is tested on simulated
panels in tests/test_multistate.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

OBS_STATE, OBS_DEATH_EXACT, OBS_CENSORED = 1, 3, 2
AGE_SCALE = 10.0
BOUNDS = {"intercept": (-15.0, 5.0), "age": (-3.0, 3.0), "covariate": (-6.0, 6.0)}


def _torch():
    import torch
    torch.set_num_threads(1)
    return torch


class MultiStateMarkov:
    """Fit and use a continuous-time Markov model on panel data.

    Parameters
    ----------
    n_states     number of states including the absorbing death state (last)
    allowed      list of (j, k) transitions with non-zero intensity
    covariates   names of covariate columns (numeric, already coded)
    age_centre   centring age for the Gompertz term
    """

    def __init__(self, n_states, allowed, covariates=(), age_centre=65.0):
        self.K = n_states
        self.allowed = list(allowed)
        self.covariates = list(covariates)
        self.age_centre = age_centre
        self.death = n_states - 1
        for j, k in self.allowed:
            if j == self.death:
                raise ValueError("death is absorbing")

    # ------------------------------------------------------------- params ----
    def _n_per_transition(self):
        return 2 + len(self.covariates)

    def param_names(self):
        names = []
        for j, k in self.allowed:
            names += [f"q{j}{k}:intercept", f"q{j}{k}:age_per_10y"]
            names += [f"q{j}{k}:{c}" for c in self.covariates]
        return names

    def _bounds(self):
        out = []
        for _ in self.allowed:
            out += [BOUNDS["intercept"], BOUNDS["age"]]
            out += [BOUNDS["covariate"]] * len(self.covariates)
        return out

    def _Q(self, theta, age, Z):
        """Batch of intensity matrices, one per interval."""
        torch = _torch()
        n = age.shape[0]
        m = self._n_per_transition()
        Q = torch.zeros((n, self.K, self.K), dtype=theta.dtype)
        for t, (j, k) in enumerate(self.allowed):
            b = theta[t * m:(t + 1) * m]
            eta = b[0] + b[1] * (age - self.age_centre) / AGE_SCALE
            if Z is not None and Z.shape[1]:
                eta = eta + Z @ b[2:]
            Q[:, j, k] = torch.exp(eta)
        return Q - torch.diag_embed(Q.sum(dim=2))

    # --------------------------------------------------------- likelihood ----
    def _neg_loglik(self, theta, r, s, d, age_mid, Z, obstype):
        torch = _torch()
        Q = self._Q(theta, age_mid, Z)
        P = torch.linalg.matrix_exp(Q * d[:, None, None])
        idx = torch.arange(len(r))
        ll = torch.zeros(len(r), dtype=theta.dtype)
        alive = list(range(self.K - 1))
        m1 = obstype == OBS_STATE
        if m1.any():
            ll[m1] = torch.log(torch.clamp(P[idx[m1], r[m1], s[m1]], min=1e-300))
        m3 = obstype == OBS_DEATH_EXACT
        if m3.any():
            q_death = Q[m3][:, alive, self.death]
            Pr = P[idx[m3], r[m3]][:, alive]
            ll[m3] = torch.log(torch.clamp((Pr * q_death).sum(dim=1), min=1e-300))
        m2 = obstype == OBS_CENSORED
        if m2.any():
            Pr = P[idx[m2], r[m2]][:, alive]
            ll[m2] = torch.log(torch.clamp(Pr.sum(dim=1), min=1e-300))
        return -ll.sum()

    def _tensors(self, intervals):
        torch = _torch()
        T = lambda a, dt=torch.float64: torch.as_tensor(np.array(a), dtype=dt)
        r = T(intervals["from_state"], torch.long)
        s = T(intervals["to_state"], torch.long)
        d = T(intervals["duration"])
        age = T(intervals["age_start"] + intervals["duration"] / 2.0)
        Z = (T(intervals[self.covariates].to_numpy(float))
             if self.covariates else torch.zeros((len(intervals), 0), dtype=torch.float64))
        ob = T(intervals["obstype"], torch.long)
        return r, s, d, age, Z, ob

    def fit(self, intervals, init=None, maxiter=1000):
        """Bounded maximum likelihood.

        intervals: one row per consecutive pair of observations with columns
        from_state, to_state, duration (years), age_start, obstype, and the
        covariates. For obstype 3 (exact death) to_state is the death state.
        """
        torch = _torch()
        from scipy.optimize import minimize
        args = self._tensors(intervals)
        x0 = np.asarray(self.crude_init(intervals) if init is None else init, float)

        def f(x):
            th = torch.tensor(x, dtype=torch.float64, requires_grad=True)
            nll = self._neg_loglik(th, *args)
            nll.backward()
            return float(nll.detach()), th.grad.detach().numpy().astype(float)

        # BFGS converges reliably on this likelihood. L-BFGS-B was tested and
        # rejected: its relative-reduction stopping rule trips after a single
        # tiny first step and it returns the starting values as "converged".
        # If BFGS reports failure or leaves the plausible parameter region, a
        # bounded trust-region method is used instead.
        lo = np.array([b[0] for b in self._bounds()])
        hi = np.array([b[1] for b in self._bounds()])
        res = minimize(f, x0, jac=True, method="BFGS",
                       options={"maxiter": maxiter, "gtol": 1e-5})
        self.method_ = "BFGS"
        if (not res.success or not np.all(np.isfinite(res.x))
                or np.any(res.x < lo) or np.any(res.x > hi)):
            res = minimize(f, np.clip(x0, lo, hi), jac=True, method="trust-constr",
                           bounds=self._bounds(), options={"maxiter": maxiter})
            self.method_ = "trust-constr"
        self.theta_ = res.x
        self.loglik_ = -res.fun
        self.converged_ = bool(res.success)
        self.message_ = str(res.message)
        self.n_obs_ = len(intervals)
        at_bound = [name for name, v, (lo, hi) in zip(self.param_names(), res.x, self._bounds())
                    if abs(v - lo) < 1e-6 or abs(v - hi) < 1e-6]
        self.at_bound_ = at_bound
        th = torch.tensor(res.x, dtype=torch.float64)
        H = torch.autograd.functional.hessian(lambda t: self._neg_loglik(t, *args), th).numpy()
        try:
            self.cov_ = np.linalg.inv(H)
            self.se_ = np.sqrt(np.clip(np.diag(self.cov_), 0, None))
        except np.linalg.LinAlgError:
            self.cov_, self.se_ = None, np.full(len(res.x), np.nan)
        self.aic_ = 2 * len(res.x) - 2 * self.loglik_
        return self

    def crude_init(self, intervals):
        """Starting values: log crude transition rates per person-year, flat in age."""
        m = self._n_per_transition()
        x0 = np.zeros(len(self.allowed) * m)
        time_in = intervals.groupby("from_state")["duration"].sum()
        for t, (j, k) in enumerate(self.allowed):
            n_jk = int(((intervals["from_state"] == j) & (intervals["to_state"] == k)).sum())
            rate = (n_jk + 0.5) / max(float(time_in.get(j, 1.0)), 1.0)
            x0[t * m] = np.log(rate)
        return x0

    # ----------------------------------------------------------- outputs ----
    def coef_table(self):
        out = pd.DataFrame({"parameter": self.param_names(), "estimate": self.theta_,
                            "se": self.se_})
        out["z"] = out["estimate"] / out["se"]
        slope = ~out["parameter"].str.contains("intercept")
        out["hazard_ratio"] = np.where(slope, np.exp(out["estimate"]), np.nan)
        out["hr_lo"] = np.where(slope, np.exp(out["estimate"] - 1.96 * out["se"]), np.nan)
        out["hr_hi"] = np.where(slope, np.exp(out["estimate"] + 1.96 * out["se"]), np.nan)
        return out

    def intensity_matrix(self, age, z=None, theta=None):
        torch = _torch()
        th = torch.as_tensor(np.array(self.theta_ if theta is None else theta), dtype=torch.float64)
        a = torch.as_tensor([float(age)], dtype=torch.float64)
        Z = (torch.as_tensor(np.atleast_2d(np.array(z, dtype=float)), dtype=torch.float64)
             if self.covariates else torch.zeros((1, 0), dtype=torch.float64))
        return self._Q(th, a, Z)[0].numpy()

    def transition_matrix(self, age, dt=1.0, z=None, theta=None):
        """P(age, age + dt) with Q held at the midpoint age."""
        from scipy.linalg import expm
        return expm(self.intensity_matrix(age + dt / 2.0, z, theta) * dt)

    def draw_parameters(self, n, seed=0):
        """Draws from the asymptotic normal of the estimates (parameter uncertainty)."""
        if self.cov_ is None:
            raise ValueError("no covariance matrix")
        rng = np.random.default_rng(seed)
        return rng.multivariate_normal(self.theta_, self.cov_, size=n)


def simulate_panel(model_Q, n_people, entry_ages, interview_gap, n_waves, z=None,
                   seed=0, step=1 / 24):
    """Simulate interval-censored panel data from an age-dependent intensity
    function model_Q(age, z_row) -> K x K matrix. Deaths are exactly timed;
    states are observed only at interviews. Used to test estimation."""
    from scipy.linalg import expm
    rng = np.random.default_rng(seed)
    rows = []
    K = model_Q(entry_ages[0], None if z is None else z[0]).shape[0]
    death = K - 1
    for i in range(n_people):
        zi = None if z is None else z[i]
        age = float(entry_ages[i])
        state = 0 if rng.random() < 0.6 else 1
        t_last, s_last, a_last = 0.0, state, age
        t = 0.0
        for wave in range(1, n_waves + 1):
            target = wave * interview_gap
            died = False
            while t < target - 1e-12:
                h = min(step, target - t)
                P = expm(model_Q(age + t + h / 2, zi) * h)
                p = np.clip(P[state], 0, None)
                new = rng.choice(K, p=p / p.sum())
                if new == death:
                    u = rng.random() * h
                    rows.append({"id": i, "from_state": s_last, "to_state": death,
                                 "duration": (t + u) - t_last, "age_start": a_last,
                                 "obstype": OBS_DEATH_EXACT, **_zdict(zi)})
                    died = True
                    break
                state = new
                t += h
            if died:
                break
            rows.append({"id": i, "from_state": s_last, "to_state": state,
                         "duration": target - t_last, "age_start": a_last,
                         "obstype": OBS_STATE, **_zdict(zi)})
            t_last, s_last, a_last = target, state, age + target
    return pd.DataFrame(rows)


def _zdict(zi):
    return {} if zi is None else {f"z{j}": float(v) for j, v in enumerate(np.atleast_1d(zi))}
