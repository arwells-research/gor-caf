from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from gor_caf.caf import caf_baseline, channel_units


def caf_residuals_p2_p5(ies: np.ndarray) -> np.ndarray:
    """CAF residuals using anchors p2 and p5 (canonical implementation).

    ies: shape (6,), ordered [p1..p6]
    Anchors: p2 at index 1, p5 at index 4 (0-based)
    """
    return caf_baseline(np.asarray(ies, dtype=float), anchor_idx_p2=1, anchor_idx_p5=4).residuals


def caf_coherence_ratio(residuals: np.ndarray) -> float:
    """CAF coherence ratio C = (r_p3/3)/(abs(r_p4)/4), computed via canonical channel_units()."""
    _, _, c = channel_units(np.asarray(residuals, dtype=float))
    return float(c)


def caf_sign_event(residuals: np.ndarray) -> bool:
    """True iff r_p3 > 0 and r_p4 < 0."""
    r = np.asarray(residuals, dtype=float)
    if r.shape != (6,):
        raise ValueError(f"Expected residuals shape (6,), got {r.shape}")
    return (r[2] > 0.0) and (r[3] < 0.0)


@dataclass(frozen=True)
class PermNullResult:
    p_sign_correct: float
    p_coh_close: float
    p_joint: float
    p_value_coh: float
    C_obs: float
    d_obs: float


def permutation_null_for_period(
    ies: np.ndarray,
    n_perm: int,
    eps: float,
    rng: np.random.Generator,
) -> PermNullResult:
    """Compute permutation null statistics for one period.

    Null:
      shuffle the 6 IE values within the period, recompute CAF residuals + C.

    Metrics:
      p_sign_correct: P_null(r_p3 > 0 and r_p4 < 0)
      p_coh_close:    P_null(|C-1| <= eps)
      p_joint:        P_null(sign event AND |C-1| <= eps)

      p_value_coh:    P_null(|C-1| <= |C_obs-1|)  (empirical p-value for coherence closeness)

    Notes:
      - If C is NaN (e.g., r_p4 == 0), that sample is treated as not close.
    """
    ies = np.asarray(ies, dtype=float)
    if ies.shape != (6,):
        raise ValueError(f"ies must be shape (6,), got {ies.shape}")
    if n_perm <= 0:
        raise ValueError("n_perm must be positive")
    if eps < 0:
        raise ValueError("eps must be non-negative")

    res_obs = caf_residuals_p2_p5(ies)
    C_obs = caf_coherence_ratio(res_obs)
    d_obs = abs(C_obs - 1.0) if np.isfinite(C_obs) else float("inf")

    sign_hits = 0
    coh_hits = 0
    joint_hits = 0
    coh_le_obs = 0

    for _ in range(int(n_perm)):
        perm = rng.permutation(ies)
        res = caf_residuals_p2_p5(perm)
        C = caf_coherence_ratio(res)

        sign_ok = caf_sign_event(res)
        if sign_ok:
            sign_hits += 1

        if np.isfinite(C):
            d = abs(C - 1.0)
            coh_ok = (d <= eps)
            if coh_ok:
                coh_hits += 1
            if sign_ok and coh_ok:
                joint_hits += 1
            if d <= d_obs:
                coh_le_obs += 1

    n = float(n_perm)
    return PermNullResult(
        p_sign_correct=sign_hits / n,
        p_coh_close=coh_hits / n,
        p_joint=joint_hits / n,
        p_value_coh=coh_le_obs / n,
        C_obs=float(C_obs),
        d_obs=float(d_obs),
    )
