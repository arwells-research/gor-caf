from __future__ import annotations

import pandas as pd
import numpy as np


def load_nist_pblock_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"n", "period", "p1", "p2", "p3", "p4", "p5", "p6"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    return df


def row_to_ies(row: pd.Series) -> np.ndarray:
    return np.array([row["p1"], row["p2"], row["p3"], row["p4"], row["p5"], row["p6"]], dtype=float)