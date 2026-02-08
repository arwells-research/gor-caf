# src/gor_caf/anchor_sensitivity.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple, Dict, Any

import numpy as np
import pandas as pd

from gor_caf.caf import caf_baseline, channel_units
from gor_caf.datasets import row_to_ies


P3_IDX = 2  # p^3
P4_IDX = 3  # p^4


@dataclass(frozen=True)
class AnchorPair:
    """Anchor pair in 0-based p-index coordinates (0..5)."""
    i: int
    j: int

    def __post_init__(self) -> None:
        if not (0 <= self.i < self.j <= 5):
            raise ValueError(f"Invalid AnchorPair(i={self.i}, j={self.j}); require 0 <= i < j <= 5")

    @property
    def span(self) -> int:
        return self.j - self.i


def list_all_anchor_pairs() -> List[AnchorPair]:
    return [AnchorPair(i, j) for i in range(6) for j in range(i + 1, 6)]


def is_admissible_anchor_pair(pair: AnchorPair) -> bool:
    """CAF-C2 admissibility criteria (anchor-pair level).

    1) Non-degeneracy: anchors must be separated enough to bracket interior points (span >= 2).
    2) Mid-shell coverage: at least one of {p^3, p^4} lies strictly between anchors.

    Indices are 0-based: p^3=2, p^4=3.
    """
    if pair.span < 2:
        return False

    between = set(range(pair.i + 1, pair.j))
    return (P3_IDX in between) or (P4_IDX in between)


def list_admissible_anchor_pairs() -> List[AnchorPair]:
    return [p for p in list_all_anchor_pairs() if is_admissible_anchor_pair(p)]


def compute_metrics_for_ies(ies: np.ndarray, pair: AnchorPair) -> Dict[str, Any]:
    """Compute CAF + channel metrics for a given anchor pair on one 6-vector.

    Returns a dict with:
      - C_obs, d_obs
      - sign_ok (r_p3 > 0 and r_p4 < 0)
      - residuals at p3/p4 (for debugging / auditing)
      - anchor indices and span
    """
    ies = np.asarray(ies, dtype=float)
    caf = caf_baseline(ies, anchor_idx_p2=pair.i, anchor_idx_p5=pair.j)
    r = caf.residuals

    g3, g4, c = channel_units(r)
    d = abs(c - 1.0) if np.isfinite(c) else float("inf")

    sign_ok = (r[P3_IDX] > 0.0) and (r[P4_IDX] < 0.0)

    return {
        "anchor_i": int(pair.i),
        "anchor_j": int(pair.j),
        "anchor_span": int(pair.span),
        "r_p3": float(r[P3_IDX]),
        "r_p4": float(r[P4_IDX]),
        "G3": float(g3),
        "G4": float(g4),
        "C_obs": float(c),
        "d_obs": float(d),
        "sign_ok": bool(sign_ok),
        "slope": float(caf.slope),
        "intercept": float(caf.intercept),
    }


def build_anchor_sensitivity_table(
    df: pd.DataFrame,
    *,
    mode: str = "admissible",
) -> pd.DataFrame:
    """Build the anchor sensitivity table for all rows in df.

    Parameters
    ----------
    df:
      DataFrame with at least columns: period, n, p1..p6
    mode:
      "admissible" => only admissible anchor pairs (CAF-C2 definition)
      "all"        => all anchor pairs (15 total); useful as diagnostics

    Returns
    -------
    DataFrame with rows keyed by (period, n, anchor_i, anchor_j).
    """
    if mode not in {"admissible", "all"}:
        raise ValueError("mode must be one of {'admissible','all'}")

    pairs: List[AnchorPair]
    if mode == "admissible":
        pairs = list_admissible_anchor_pairs()
    else:
        pairs = list_all_anchor_pairs()

    rows: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        ies = row_to_ies(row)
        period = int(row["period"])
        n = int(row["n"])

        for pair in pairs:
            m = compute_metrics_for_ies(ies, pair)
            m.update({"period": period, "n": n})
            rows.append(m)

    out = pd.DataFrame(rows)
    out = out.sort_values(["period", "anchor_i", "anchor_j"]).reset_index(drop=True)
    return out
