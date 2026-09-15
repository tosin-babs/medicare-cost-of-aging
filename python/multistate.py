"""
Continuous-time multi-state Markov model for interval-censored panel data.

HRS respondents are interviewed about every two years. Their health state is
observed at each interview, transitions between interviews are not, and deaths
are dated to the month. This module fits transition intensities to data of
exactly that kind, with the likelihood of Kalbfleisch and Lawless (1985), as
implemented in R's msm (Jackson 2011).

Model. States 0..K-2 are transient; state K-1 is death, absorbing. For each
allowed transition j -> k,

    log q_jk(a, z) = b0_jk + b1_jk (a - age_centre)/10
                     + sum_m c_mjk max(0, a - knot_m)/10 + g_jk' z,

a Gompertz-type age gradient (per 10 years of age) that may bend at the knots,
which is a linear spline in log intensity, with log-linear covariate effects.

Within an interval the intensity matrix is piecewise constant: the interval is
split into pieces of at most `max_piece` years and Q is held at each piece's
midpoint age, so P(d) = prod_j expm(Q(a_j) s_j). Holding Q at the midpoint of
a long interval, as a single piece, misstates the age gradient.

Likelihood contributions, for an interval of length d starting in state r:
  * next state s observed at an interview:   P(d)[r, s]
  * death at an exact time d:                sum_k P(d)[r, k] q_k,death(a + d)
  * alive, state unknown (right-censored):   sum_k P(d)[r, k]
The death intensity is evaluated at the age at death, not at the interval
midpoint, which otherwise flattens the age gradient of mortality.

Estimation is maximum likelihood by BFGS with a bounded trust-region fallback,
with exact gradients from PyTorch (torch.linalg.matrix_exp is differentiable).
Two variance estimators are available: the inverse observed information, and a
sandwich clustered on households, which is the appropriate one when the model
is misspecified or when household members' outcomes are correlated. Parameter
recovery is tested on simulated panels in tests/test_multistate.py.
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

OBS_STATE, OBS_DEATH_EXACT, OBS_CENSORED = 1, 3, 2
AGE_SCALE = 10.0
BOUNDS = {"intercept": (-15.0, 5.0), "age": (-6.0, 6.0), "covariate": (-6.0, 6.0)}


def _torch():
    import torch
    torch.set_num_threads(int(os.environ.get("P5_TORCH_THREADS", "1")))
    return torch


class MultiStateMarkov:
    """Fit and use a continuous-time Markov model on panel data.

    Parameters
    ----------
    n_states     number of states including the absorbing death state (last)
    allowed      list of (j, k) transitions with non-zero intensity
    covariates   names of covariate columns (numeric, already coded)
    age_centre   centring age for the Gompertz term
    age_knots    ages at which the log-intensity age slope may change
    max_piece    longest piece, in years, over which Q is held constant
    """

    def __init__(self, n_states, allowed, covariates=(), age_centre=65.0, age_knots=(),
                 max_piece=2.0):
        self.K = n_states
        self.allowed = list(allowed)
        self.covariates = list(covariates)
        self.age_centre = age_centre
        self.age_knots = tuple(float(k) for k in age_knots)
        self.max_piece = float(max_piece)
        self.death = n_states - 1
        for j, k in self.allowed:
            if j == self.death:
                raise ValueError("death is absorbing")

    # ------------------------------------------------------------- params ----
    def _n_age(self):
        return 1 + len(self.age_knots)

    def _n_per_transition(self):
        return 1 + self._n_age() + len(self.covariates)

    def param_names(self):
        names = []
        for j, k in self.allowed:
            names += [f"q{j}{k}:intercept", f"q{j}{k}:age_per_10y"]
            names += [f"q{j}{k}:age_over_{int(a)}_per_10y" for a in self.age_knots]
            names += [f"q{j}{k}:{c}" for c in self.covariates]
        return names

    def _bounds(self):
        out = []
        for _ in self.allowed:
            out += [BOUNDS["intercept"]] + [BOUNDS["age"]] * self._n_age()
            out += [BOUNDS["covariate"]] * len(self.covariates)
        return out

    def _Q(self, theta, age, Z):
        """Batch of intensity matrices, one per row of age and Z."""
        torch = _torch()
        n = age.shape[0]
        m = self._n_per_transition()
        Q = torch.zeros((n, self.K, self.K), dtype=theta.dtype)
        for t, (j, k) in enumerate(self.allowed):
            b = theta[t * m:(t + 1) * m]
            eta = b[0] + b[1] * (age - self.age_centre) / AGE_SCALE
            for i, knot in enumerate(self.age_knots):
                eta = eta + b[2 + i] * torch.clamp(age - knot, min=0.0) / AGE_SCALE
            if Z is not None and Z.shape[1]:
                eta = eta + Z @ b[1 + self._n_age():]
            Q[:, j, k] = torch.exp(eta)
        return Q - torch.diag_embed(Q.sum(dim=2))

    # --------------------------------------------------------- likelihood ----
    def _interval_P(self, theta, age_start, d, Z):
        """P over each interval, splitting it into pieces of at most max_piece."""
        torch = _torch()
        n = age_start.shape[0]
        pieces = torch.clamp(torch.ceil(d / self.max_piece), min=1.0)
        P = torch.eye(self.K, dtype=theta.dtype).expand(n, self.K, self.K).clone()
        for j in range(int(pieces.max().item())):
            idx = torch.nonzero(pieces > j).squeeze(1)
            step = d[idx] / pieces[idx]
            mid = age_start[idx] + step * (j + 0.5)
            Pj = torch.linalg.matrix_exp(self._Q(theta, mid, Z[idx]) * step[:, None, None])
            P = P.index_copy(0, idx, torch.bmm(P[idx], Pj))
        return P

    def _loglik_vec(self, theta, r, s, d, age_start, Z, obstype):
        """Log-likelihood contribution of every observation."""
        torch = _torch()
        P = self._interval_P(theta, age_start, d, Z)
        n = len(r)
        idx = torch.arange(n)
        Pr = P[idx, r]                                   # row of P for the starting state
        alive = list(range(self.K - 1))
        ll = torch.zeros(n, dtype=theta.dtype)
        m1 = obstype == OBS_STATE
        if m1.any():
            j1 = idx[m1]
            ll = ll.index_copy(0, j1, torch.log(torch.clamp(Pr[j1, s[j1]], min=1e-300)))
        m3 = obstype == OBS_DEATH_EXACT
        if m3.any():
            j3 = idx[m3]
            q_death = self._Q(theta, age_start[j3] + d[j3], Z[j3])[:, alive, self.death]
            ll = ll.index_copy(0, j3, torch.log(torch.clamp(
                (Pr[j3][:, alive] * q_death).sum(dim=1), min=1e-300)))
        m2 = obstype == OBS_CENSORED
        if m2.any():
            j2 = idx[m2]
            ll = ll.index_copy(0, j2, torch.log(torch.clamp(
                Pr[j2][:, alive].sum(dim=1), min=1e-300)))
        return ll

    def _neg_loglik(self, theta, r, s, d, age_start, Z, obstype, weight=None):
        ll = self._loglik_vec(theta, r, s, d, age_start, Z, obstype)
        return -(ll if weight is None else ll * weight).sum()

    def _tensors(self, intervals, weight_col=None):
        torch = _torch()
        T = lambda a, dt=torch.float64: torch.as_tensor(np.array(a), dtype=dt)
        r = T(intervals["from_state"], torch.long)
        s = T(np.clip(intervals["to_state"].to_numpy(), 0, None), torch.long)
        d = T(intervals["duration"])
        age = T(intervals["age_start"])
        Z = (T(intervals[self.covariates].to_numpy(float))
             if self.covariates else torch.zeros((len(intervals), 0), dtype=torch.float64))
        ob = T(intervals["obstype"], torch.long)
        args = [r, s, d, age, Z, ob]
        if weight_col is not None:
            w = T(intervals[weight_col].to_numpy(float))
            args.append(w / w.mean())
        return tuple(args)

    def fit(self, intervals, init=None, maxiter=1000, weight_col=None, cluster_col=None,
            robust_se=False, gtol=1e-3):
        """Maximum likelihood.

        intervals: one row per observation with columns from_state, to_state,
        duration (years), age_start, obstype, and the covariates. obstype 1 is
        a transition to an observed state, 3 an exact death, 2 alive with the
        state unknown.
        """
        torch = _torch()
        from scipy.optimize import minimize
        args = self._tensors(intervals, weight_col)
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
        # gtol is on the gradient of a log likelihood of order 10^5, so 1e-3 is
        # a tight stopping rule; 1e-5 spent hundreds of iterations on
        # improvements far below a hundredth of a log-likelihood unit.
        res = minimize(f, x0, jac=True, method="BFGS",
                       options={"maxiter": maxiter, "gtol": gtol})
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
        self.at_bound_ = [name for name, v, (a, b) in zip(self.param_names(), res.x, self._bounds())
                          if abs(v - a) < 1e-6 or abs(v - b) < 1e-6]
        th = torch.tensor(res.x, dtype=torch.float64)
        H = torch.autograd.functional.hessian(lambda t: self._neg_loglik(t, *args), th).numpy()
        try:
            self.cov_ = np.linalg.inv(H)
            self.se_ = np.sqrt(np.clip(np.diag(self.cov_), 0, None))
        except np.linalg.LinAlgError:
            self.cov_, self.se_ = None, np.full(len(res.x), np.nan)
        self.cov_robust_, self.se_robust_ = None, None
        if robust_se and self.cov_ is not None:
            self.cov_robust_ = self.sandwich(intervals, args, self.cov_, cluster_col)
            self.se_robust_ = np.sqrt(np.clip(np.diag(self.cov_robust_), 0, None))
        self.aic_ = 2 * len(res.x) - 2 * self.loglik_
        return self

    def sandwich(self, intervals, args, bread, cluster_col=None):
        """Cluster-robust covariance: bread * meat * bread, clustered on
        households, with each observation's score from forward-mode automatic
        differentiation (one pass per parameter)."""
        torch = _torch()
        from torch.func import jvp
        th = torch.tensor(self.theta_, dtype=torch.float64)
        base = args[:6]
        w = args[6] if len(args) > 6 else None

        def f(t):
            ll = self._loglik_vec(t, *base)
            return ll if w is None else ll * w

        cols = []
        for j in range(len(self.theta_)):
            v = torch.zeros_like(th)
            v[j] = 1.0
            cols.append(jvp(f, (th,), (v,))[1])
        scores = torch.stack(cols, dim=1).numpy()
        key = cluster_col or ("household" if "household" in intervals else "hhidpn")
        g = pd.DataFrame(scores).groupby(intervals[key].to_numpy()).sum().to_numpy()
        n_c = len(g)
        self.n_clusters_ = n_c
        meat = g.T @ g * (n_c / max(n_c - 1, 1))
        return bread @ meat @ bread

    def crude_init(self, intervals):
        """Starting values: log crude transition rates per person-year, flat in age."""
        m = self._n_per_transition()
        x0 = np.zeros(len(self.allowed) * m)
        obs = intervals[intervals["obstype"] != OBS_CENSORED]
        time_in = intervals.groupby("from_state")["duration"].sum()
        for t, (j, k) in enumerate(self.allowed):
            n_jk = int(((obs["from_state"] == j) & (obs["to_state"] == k)).sum())
            rate = (n_jk + 0.5) / max(float(time_in.get(j, 1.0)), 1.0)
            x0[t * m] = np.log(rate)
        return x0

    # ----------------------------------------------------------- outputs ----
    def coef_table(self, robust=True):
        se = self.se_robust_ if (robust and getattr(self, "se_robust_", None) is not None) else self.se_
        out = pd.DataFrame({"parameter": self.param_names(), "estimate": self.theta_,
                            "se": se, "se_model": self.se_})
        out["se_type"] = ("cluster-robust" if (robust and getattr(self, "se_robust_", None) is not None)
                          else "observed information")
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

    def interval_probabilities(self, intervals, theta=None):
        """P(interval) from the starting state, per row (for goodness of fit)."""
        torch = _torch()
        th = torch.as_tensor(np.array(self.theta_ if theta is None else theta), dtype=torch.float64)
        r, s, d, age, Z, ob = self._tensors(intervals)
        out = []
        for i in range(0, len(intervals), 20_000):
            sl = slice(i, i + 20_000)
            P = self._interval_P(th, age[sl], d[sl], Z[sl])
            out.append(P[torch.arange(P.shape[0]), r[sl]].numpy())
        return np.vstack(out)

    def draw_parameters(self, n, seed=0, robust=True):
        """Draws from the asymptotic normal of the estimates (parameter uncertainty)."""
        cov = (self.cov_robust_ if (robust and getattr(self, "cov_robust_", None) is not None)
               else self.cov_)
        if cov is None:
            raise ValueError("no covariance matrix")
        rng = np.random.default_rng(seed)
        return rng.multivariate_normal(self.theta_, cov, size=n)


def simulate_panel(model_Q, n_people, entry_ages, interview_gap, n_waves, z=None,
                   seed=0, step=1 / 24):
    """Simulate a panel from a known Q, for testing the estimator: interviews
    every `interview_gap` years and exact death times."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_people):
        age0 = float(entry_ages[i])
        zi = None if z is None else np.atleast_1d(z[i])
        K = model_Q(age0, zi).shape[0]
        state, t, death_time = 0, 0.0, None
        path = [(0.0, state)]
        horizon = interview_gap * (n_waves - 1)
        while t < horizon:
            Q = model_Q(age0 + t, zi)
            rate = -Q[state, state]
            if rate > 0 and rng.random() < rate * step:
                probs = np.clip(Q[state].copy(), 0, None)
                probs[state] = 0.0
                probs = probs / probs.sum()
                state = int(rng.choice(K, p=probs))
                path.append((t, state))
                if state == K - 1:
                    death_time = t
                    break
            t += step
        def state_at(u):
            s = path[0][1]
            for tt, ss in path:
                if tt <= u:
                    s = ss
            return s
        seen = [(w * interview_gap, state_at(w * interview_gap)) for w in range(n_waves)
                if death_time is None or w * interview_gap < death_time]
        for (t0, s0), (t1, s1) in zip(seen, seen[1:]):
            rows.append({"hhidpn": i, "household": i, "from_state": int(s0), "to_state": int(s1),
                         "duration": t1 - t0, "age_start": age0 + t0, "obstype": OBS_STATE,
                         **_zdict(zi)})
        if death_time is not None and seen:
            t0, s0 = seen[-1]
            rows.append({"hhidpn": i, "household": i, "from_state": int(s0), "to_state": K - 1,
                         "duration": death_time - t0, "age_start": age0 + t0,
                         "obstype": OBS_DEATH_EXACT, **_zdict(zi)})
    return pd.DataFrame(rows)


def _zdict(zi):
    return {} if zi is None else {f"z{j}": float(v) for j, v in enumerate(np.atleast_1d(zi))}
