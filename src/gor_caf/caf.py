from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class CAFResult:
    baseline: np.ndarray  # shape (6,)
    residuals: np.ndarray # shape (6,)
    slope: float
    intercept: float


def caf_baseline(ies: np.ndarray, anchor_idx_p2: int = 1, anchor_idx_p5: int = 4) -> CAFResult:
    """
    Canonical Anchor Fit (CAF) baseline:
      Fit the unique line through p^2 (index 1) and p^5 (index 4) and subtract it.

    ies must be length-6 array ordered [p1,p2,p3,p4,p5,p6].
    """
    ies = np.asarray(ies, dtype=float)
    if ies.shape != (6,):
        raise ValueError(f"ies must be shape (6,), got {ies.shape}")

    x = np.arange(6, dtype=float)
    x2, x5 = float(anchor_idx_p2), float(anchor_idx_p5)
    y2, y5 = float(ies[anchor_idx_p2]), float(ies[anchor_idx_p5])

    if x5 == x2:
        raise ValueError("anchor indices must be distinct")

    slope = (y5 - y2) / (x5 - x2)
    intercept = y2 - slope * x2

    baseline = slope * x + intercept
    residuals = ies - baseline
    return CAFResult(baseline=baseline, residuals=residuals, slope=slope, intercept=intercept)


def channel_units(residuals: np.ndarray) -> tuple[float, float, float]:
    """
    Returns (G3, G4, C) where:
      G3 = r_p3 / 3
      G4 = |r_p4| / 4
      C  = G3 / G4
    using p3 index=2, p4 index=3.
    """
    r = np.asarray(residuals, dtype=float)
    if r.shape != (6,):
        raise ValueError(f"residuals must be shape (6,), got {r.shape}")

    r_p3 = r[2]
    r_p4 = r[3]
    g3 = r_p3 / 3.0
    g4 = abs(r_p4) / 4.0
    c = (g3 / g4) if g4 != 0 else np.nan
    return g3, g4, c