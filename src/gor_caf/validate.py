from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import numpy as np
import pandas as pd


REQUIRED_COLS = ("n", "period", "p1", "p2", "p3", "p4", "p5", "p6")
P_COLS = ("p1", "p2", "p3", "p4", "p5", "p6")


@dataclass(frozen=True)
class DatasetValidationResult:
    ok: bool
    n_rows: int
    periods: Tuple[int, ...]
    problems: Tuple[str, ...]


def validate_nist_pblock_df(
    df: pd.DataFrame,
    *,
    expected_periods: Optional[Sequence[int]] = None,
    require_n_equals_period: bool = True,
    require_anchor_monotone: bool = True,
) -> DatasetValidationResult:
    problems: list[str] = []

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        problems.append(f"Missing required columns: {missing}")
        return DatasetValidationResult(
            ok=False,
            n_rows=int(len(df)),
            periods=tuple(),
            problems=tuple(problems),
        )

    n_rows = int(len(df))
    if n_rows == 0:
        problems.append("Dataset has zero rows.")
        return DatasetValidationResult(ok=False, n_rows=0, periods=tuple(), problems=tuple(problems))

    # Period integrity
    try:
        periods = tuple(int(x) for x in df["period"].tolist())
    except Exception as e:
        problems.append(f"Could not parse 'period' as int: {e}")
        periods = tuple()

    if len(set(periods)) != len(periods):
        problems.append("Duplicate period rows detected (expected one row per period).")

    if expected_periods is not None:
        exp = set(int(x) for x in expected_periods)
        got = set(periods)
        if got != exp:
            problems.append(f"Period set mismatch: expected={sorted(exp)} got={sorted(got)}")

    # n == period (optional contract)
    if require_n_equals_period:
        try:
            if not (df["n"].astype(int) == df["period"].astype(int)).all():
                problems.append("Contract violated: not all rows satisfy n == period.")
        except Exception as e:
            problems.append(f"Could not compare n == period: {e}")

    # Finite numeric checks
    for col in P_COLS:
        vals = pd.to_numeric(df[col], errors="coerce").to_numpy(dtype=float)
        if np.isnan(vals).any():
            problems.append(f"Non-numeric or missing values in column {col}.")
        if not np.isfinite(vals).all():
            problems.append(f"Non-finite values in column {col}.")

    # Basic anchor sanity (optional): p2 <= p5
    if require_anchor_monotone:
        try:
            p2 = pd.to_numeric(df["p2"], errors="coerce").to_numpy(dtype=float)
            p5 = pd.to_numeric(df["p5"], errors="coerce").to_numpy(dtype=float)
            bad = np.where(p2 > p5)[0]
            if bad.size > 0:
                problems.append(f"Anchor monotonic sanity failed (p2 > p5) on rows: {bad.tolist()}")
        except Exception as e:
            problems.append(f"Could not evaluate anchor monotonic sanity (p2<=p5): {e}")

    # Optional labels sanity
    if "labels" in df.columns:
        for idx, s in enumerate(df["labels"].tolist()):
            if pd.isna(s):
                continue
            if not isinstance(s, str):
                problems.append(f"labels is not a string at row {idx}")
                continue
            parts = [x.strip() for x in s.split(",") if x.strip()]
            if len(parts) != 6:
                problems.append(f"labels must contain 6 comma-separated symbols at row {idx}, got {len(parts)}")

    ok = len(problems) == 0
    return DatasetValidationResult(ok=ok, n_rows=n_rows, periods=tuple(sorted(set(periods))), problems=tuple(problems))
