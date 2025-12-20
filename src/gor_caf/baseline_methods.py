from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Tuple

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.optimize import minimize

from .caf import caf_baseline as caf_operator


BaselineFn = Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]]


@dataclass(frozen=True)
class BaselineResult:
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


def caf_baseline(ie_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Canonical Anchor Fit baseline: line through p^2 and p^5.
    Provided here for baseline comparison only; canonical implementation lives in caf.py.
    """
    ie_data = _validate_ie(ie_data)
    res = caf_operator(ie_data)
    return res.baseline, res.residuals


def quadratic_baseline(ie_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Least-squares quadratic fit to all 6 points.
    """
    ie_data = _validate_ie(ie_data)
    x = np.arange(6, dtype=float)
    coeffs = np.polyfit(x, ie_data, deg=2)
    baseline = np.polyval(coeffs, x)
    return baseline, ie_data - baseline


def spline_baseline(ie_data: np.ndarray, s: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Smoothing spline baseline (cubic). This is NOT the canonical baseline.

    Notes:
      - Kept intentionally simple to stress-test baseline dependence.
      - 's' controls smoothing. Larger s -> smoother.
    """
    ie_data = _validate_ie(ie_data)
    x = np.arange(6, dtype=float)
    spline = UnivariateSpline(x, ie_data, s=float(s), k=3)
    baseline = spline(x)
    return baseline, ie_data - baseline


def monotone_min_curvature_baseline(
    ie_data: np.ndarray,
    degree: int = 3,
    lambda_curv: float = 0.1,
    maxiter: int = 2000,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit a monotone-increasing polynomial baseline with a minimal-curvature penalty.

    - Fits a polynomial of given `degree` to all 6 p-block points (indices 0..5),
      with an L2 data term plus a curvature regularizer on discrete second diffs.
    - Enforces monotonicity via inequality constraints: baseline[i+1] - baseline[i] >= 0.

    Returns:
        baseline: shape (6,)
        residuals: ie_data - baseline

    Notes:
        Uses SLSQP (no quasi-Newton Hessian updates), so it is robust under
        `pytest -W error::UserWarning`.
    """
    ie_data = np.asarray(ie_data, dtype=float)
    if ie_data.shape != (6,):
        raise ValueError(f"ie_data must be shape (6,), got {ie_data.shape}")

    if degree < 1:
        raise ValueError("degree must be >= 1")

    x = np.arange(6, dtype=float)

    # Initial guess: low-degree polyfit (up to quadratic), then pad to requested degree.
    init = np.polyfit(x, ie_data, deg=min(2, degree))
    if init.size < degree + 1:
        init = np.concatenate([np.zeros(degree + 1 - init.size, dtype=float), init])

    def poly(coeffs: np.ndarray) -> np.ndarray:
        return np.polyval(coeffs, x)

    def objective(coeffs: np.ndarray) -> float:
        y = poly(coeffs)
        # Data fidelity term
        err = y - ie_data
        # Discrete curvature penalty
        curv = np.diff(y, n=2)  # length 4
        return float(np.sum(err**2) + float(lambda_curv) * np.sum(curv**2))

    # Inequality constraints for monotonicity: y[i+1] - y[i] >= 0 for i=0..4
    cons = [{"type": "ineq", "fun": lambda c, i=i: poly(c)[i + 1] - poly(c)[i]} for i in range(5)]

    res = minimize(
        objective,
        init,
        method="SLSQP",
        constraints=cons,
        options={"maxiter": int(maxiter), "ftol": 1e-12},
    )

    if not res.success:
        # Hard fallback: least-squares linear fit (always monotone if slope>=0).
        # If slope < 0 (rare here), clamp slope to 0.
        slope, intercept = np.polyfit(x, ie_data, 1)
        if slope < 0:
            slope = 0.0
            intercept = float(np.mean(ie_data))
        baseline = slope * x + intercept
        return baseline, ie_data - baseline

    baseline = poly(res.x)
    return baseline, ie_data - baseline

def compare_baselines(ie_data: np.ndarray) -> Dict[str, BaselineResult]:
    """
    Compare multiple baselines and report the key invariant candidate:
      ratio = |r_p3 / r_p4|

    p^3 index = 2, p^4 index = 3 for the ordered [p1..p6] vector.
    """
    ie_data = _validate_ie(ie_data)

    methods: Dict[str, BaselineFn] = {
        "CAF": caf_baseline,
        "Quadratic": quadratic_baseline,
        "Spline_s0p5": lambda x: spline_baseline(x, s=0.5),
        "MonotoneMinCurv": monotone_min_curvature_baseline,
    }

    out: Dict[str, BaselineResult] = {}
    for name, fn in methods.items():
        baseline, residuals = fn(ie_data)
        r_p3 = float(residuals[2])
        r_p4 = float(residuals[3])
        ratio = float(abs(r_p3 / r_p4)) if r_p4 != 0 else float("nan")
        out[name] = BaselineResult(
            baseline=np.asarray(baseline, dtype=float),
            residuals=np.asarray(residuals, dtype=float),
            r_p3=r_p3,
            r_p4=r_p4,
            ratio_abs_rp3_rp4=ratio,
        )
    return out