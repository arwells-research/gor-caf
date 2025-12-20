# src/gor_caf/geometric_kernels.py

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Literal, Dict

from scipy.special import genlaguerre, factorial
from scipy.integrate import trapezoid


KernelType = Literal["gaussian", "yukawa", "delta_plus_tail"]


def hydrogenic_radial(n: int, ell: int, r: np.ndarray, Z: float = 1.0) -> np.ndarray:
    """
    Hydrogenic radial wavefunction R_{n,ell}(r) in atomic units (a0 = 1).

    Notes:
    - r is in Bohr radii.
    - Returns R(r) such that ψ(r,θ,φ) = R(r) Y_{ell m}(θ,φ).
    """
    if n <= 0 or ell < 0 or ell >= n:
        raise ValueError("Require n>=1 and 0<=ell<n")

    a0 = 1.0
    rho = 2.0 * Z * r / (n * a0)

    # Normalization
    norm = np.sqrt((2*Z/(n*a0))**3 * factorial(n-ell-1) / (2*n*factorial(n+ell)))

    L = genlaguerre(n-ell-1, 2*ell+1)(rho)
    R = norm * np.exp(-rho/2.0) * rho**ell * L
    return R


def gaussian_kernel(r: np.ndarray, r_BPG: float) -> np.ndarray:
    return np.exp(-(r / r_BPG) ** 2)


def yukawa_kernel(r: np.ndarray, r_BPG: float) -> np.ndarray:
    r_safe = np.where(r < 1e-12, 1e-12, r)
    return np.exp(-r_safe / r_BPG) / r_safe


def delta_plus_tail_kernel(r: np.ndarray, r_BPG: float, alpha: float = 2.0) -> np.ndarray:
    return np.exp(-(r / r_BPG) ** alpha) / (1.0 + r / r_BPG)


def compute_overlap_integral(
    n: int,
    ell: int,
    kernel_type: KernelType,
    r_BPG: float,
    Z: float = 1.0,
    r_max: float | None = None,
) -> float:
    """
    D(n,ell) = ∫ |R_{n,ell}(r)|^2 * K(r) * r^2 dr

    Dimensionless in atomic units; compares across n via ratios.
    """
    if r_BPG <= 0:
        raise ValueError("r_BPG must be positive")

    if r_max is None:
        r_max = 50.0 * n  # safely beyond turning point

    # Resolve near-origin sharply (kernel localized) + coarse tail
    r_near = np.linspace(0.0, 10.0 * r_BPG, 4000)
    r_far = np.linspace(10.0 * r_BPG, r_max, 8000)
    r = np.concatenate([r_near, r_far])

    R = hydrogenic_radial(n, ell, r, Z=Z)

    if kernel_type == "gaussian":
        K = gaussian_kernel(r, r_BPG)
    elif kernel_type == "yukawa":
        K = yukawa_kernel(r, r_BPG)
    elif kernel_type == "delta_plus_tail":
        K = delta_plus_tail_kernel(r, r_BPG)
    else:
        raise ValueError(f"Unknown kernel_type={kernel_type}")

    integrand = (R * R) * K * (r * r)
    return float(trapezoid(integrand, r))


@dataclass(frozen=True)
class GPrediction:
    period: int
    n: int
    D: float
    G_pred: float


def predict_G_from_overlap(
    periods: list[int],
    kernel_type: KernelType,
    r_BPG: float,
    G_ref: float = 0.437633,   # empirical G4 for n=2 from your gor_analyze output
    ref_period: int = 2,
) -> Dict[int, GPrediction]:
    """
    Predict G_n scaling from overlap ratios. Normalized to ref_period.
    """
    Ds: Dict[int, float] = {}
    for p in periods:
        n = p
        D = compute_overlap_integral(n=n, ell=1, kernel_type=kernel_type, r_BPG=r_BPG)
        Ds[p] = D

    D_ref = Ds[ref_period]
    out: Dict[int, GPrediction] = {}
    for p in periods:
        G_pred = G_ref * (Ds[p] / D_ref)
        out[p] = GPrediction(period=p, n=p, D=Ds[p], G_pred=G_pred)
    return out