from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Tuple

import numpy as np
from scipy.interpolate import UnivariateSpline, PchipInterpolator
from scipy.optimize import minimize


BaselineFn = Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]]


@dataclass(frozen=True)
class HoldoutBaselineResult:
    baseline: np.ndarray
    residuals: np.ndarray
    r_p3: float
    r_p4: float
    ratio_abs_rp3_rp4: float  # |r_p3 / r_p4|


def _validate_ie(ie_data: np.ndarray) -> np.ndarray:
    x = np.asarray(ie_data, dtype=float)
    if x.shape != (6,):
        raise ValueError(f"ie_data must be shape (6,), got {x.shape}")
    return x


def _fit_on_masked_points(x: np.ndarray, y: np.ndarray, mask_idx: np.ndarray, deg: int) -> np.ndarray:
    coeffs = np.polyfit(x[mask_idx], y[mask_idx], deg=deg)
    return np.polyval(coeffs, x)


def holdout_linear_endpoints(ie_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit a line using only {p1, p6} endpoints (indices 0 and 5).
    Evaluate across all 6 indices, then compute residuals.
    """
    ie_data = _validate_ie(ie_data)
    x = np.arange(6, dtype=float)
    mask = np.array([0, 5], dtype=int)
    baseline = _fit_on_masked_points(x, ie_data, mask, deg=1)
    return baseline, ie_data - baseline


def holdout_quadratic_0145(ie_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Quadratic fit using only indices {0,1,4,5} = {p1,p2,p5,p6}.
    This prevents the baseline from 'learning' p3/p4 sawtooth directly.
    """
    ie_data = _validate_ie(ie_data)
    x = np.arange(6, dtype=float)
    mask = np.array([0, 1, 4, 5], dtype=int)
    baseline = _fit_on_masked_points(x, ie_data, mask, deg=2)
    return baseline, ie_data - baseline


def holdout_spline_0145(ie_data: np.ndarray, s: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
    """
    Cubic smoothing spline fit using only indices {0,1,4,5}.
    We fit the spline on 4 points, then evaluate across all 6.
    """
    ie_data = _validate_ie(ie_data)
    x = np.arange(6, dtype=float)
    mask = np.array([0, 1, 4, 5], dtype=int)
    spline = UnivariateSpline(x[mask], ie_data[mask], s=float(s), k=3)
    baseline = spline(x)
    return baseline, ie_data - baseline


def holdout_pchip_0145(ie_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Deterministic monotone-preserving cubic interpolant (PCHIP) using only indices {0,1,4,5}.
    This is a strong 'physically plausible' baseline: smooth-ish, monotone if anchors are monotone.
    """
    ie_data = _validate_ie(ie_data)
    x = np.arange(6, dtype=float)
    mask = np.array([0, 1, 4, 5], dtype=int)
    pchip = PchipInterpolator(x[mask], ie_data[mask], extrapolate=True)
    baseline = pchip(x)
    return baseline, ie_data - baseline

def holdout_monotone_min_curv_0145(
    ie_data: np.ndarray,
    degree: int = 3,
    lambda_curv: float = 0.1,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Monotone increasing polynomial baseline fit ONLY on indices {0,1,4,5}.

    This version is *fully analytic* (quadratic objective + linear constraints):
      - exact gradient
      - exact Hessian
      - monotonicity enforced via LinearConstraint

    This avoids quasi-Newton "delta_grad == 0.0" warnings and is robust/deterministic.
    """
    from scipy.optimize import minimize, LinearConstraint

    ie_data = _validate_ie(ie_data)
    x = np.arange(6, dtype=float)
    mask = np.array([0, 1, 4, 5], dtype=int)

    if degree < 1:
        raise ValueError("degree must be >= 1")

    # Polynomial parameterization:
    # coeffs are highest-power-first, as in np.polyval/np.polyfit
    p = degree + 1

    # Build Vandermonde: y = V @ c
    V = np.vander(x, N=p, increasing=False)  # shape (6, p)

    # Selection matrix for held-in points {0,1,4,5}
    Vh = V[mask, :]               # shape (4, p)
    dh = ie_data[mask].astype(float)  # shape (4,)

    # Curvature penalty: second differences on y (length 4)
    # curv = y[i+2] - 2 y[i+1] + y[i] for i=0..3
    D2 = np.zeros((4, 6), dtype=float)
    for i in range(4):
        D2[i, i]     = 1.0
        D2[i, i + 1] = -2.0
        D2[i, i + 2] = 1.0
    B = D2 @ V  # shape (4, p)

    # Quadratic objective:
    # f(c) = ||Vh c - dh||^2 + lambda * ||B c||^2
    #      = c^T Q c - 2 b^T c + const
    Q = (Vh.T @ Vh) + float(lambda_curv) * (B.T @ B)    # shape (p, p)
    b = (Vh.T @ dh)                                     # shape (p,)

    def objective(c: np.ndarray) -> float:
        # c^T Q c - 2 b^T c + const (const omitted)
        return float(c @ (Q @ c) - 2.0 * (b @ c))

    def grad(c: np.ndarray) -> np.ndarray:
        # ∇ = 2(Qc - b)
        return 2.0 * (Q @ c - b)

    def hess(c: np.ndarray) -> np.ndarray:
        # Hessian is constant: 2Q
        return 2.0 * Q

    # Monotonicity constraints on all 6 baseline points:
    # y[i+1] - y[i] >= 0  for i=0..4
    D1 = np.zeros((5, 6), dtype=float)
    for i in range(5):
        D1[i, i]     = -1.0
        D1[i, i + 1] = 1.0
    A = D1 @ V  # shape (5, p) so that A c = diff(y)

    lc = LinearConstraint(A, lb=np.zeros(5), ub=np.full(5, np.inf))

    # Initial guess: low-degree fit on held-in points, padded to requested degree
    init_deg = min(2, degree)
    init = np.polyfit(x[mask], ie_data[mask], deg=init_deg)
    if len(init) < p:
        init = np.concatenate([np.zeros(p - len(init), dtype=float), init])

    res = minimize(
        objective,
        init,
        method="trust-constr",
        jac=grad,
        hess=hess,
        constraints=[lc],
        options={"maxiter": 2000, "gtol": 1e-12, "xtol": 1e-12},
    )

    if not res.success or not np.all(np.isfinite(res.x)):
        # fallback: masked quadratic (existing behavior)
        return holdout_quadratic_0145(ie_data)

    baseline = V @ res.x
    return baseline, ie_data - baseline


def compare_holdout_baselines(ie_data: np.ndarray) -> Dict[str, HoldoutBaselineResult]:
    """
    Compare hold-out baselines that do NOT use p3/p4 for fitting.
    Reports ratio = |r_p3 / r_p4|, where p3 index = 2, p4 index = 3.
    """
    ie_data = _validate_ie(ie_data)
    methods: Dict[str, BaselineFn] = {
        "Holdout_Line_05": holdout_linear_endpoints,
        "Holdout_Quad_0145": holdout_quadratic_0145,
        "Holdout_PCHIP_0145": holdout_pchip_0145,
        "Holdout_Spline_0145": lambda x: holdout_spline_0145(x, s=0.2),
        "Holdout_MonotoneMinCurv_0145": holdout_monotone_min_curv_0145,
    }

    out: Dict[str, HoldoutBaselineResult] = {}
    for name, fn in methods.items():
        baseline, residuals = fn(ie_data)
        r_p3 = float(residuals[2])
        r_p4 = float(residuals[3])
        ratio = float(abs(r_p3 / r_p4)) if r_p4 != 0 else float("nan")
        out[name] = HoldoutBaselineResult(
            baseline=np.asarray(baseline, dtype=float),
            residuals=np.asarray(residuals, dtype=float),
            r_p3=r_p3,
            r_p4=r_p4,
            ratio_abs_rp3_rp4=ratio,
        )
    return out