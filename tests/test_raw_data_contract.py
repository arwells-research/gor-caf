from __future__ import annotations

import numpy as np

from gor_caf.datasets import load_nist_pblock_csv


def test_raw_nist_pblock_contract() -> None:
    """Enforce the on-disk contract for the raw NIST p-block IE CSV.

    This test is intentionally conservative:
    - It validates required columns, shape, and basic sanity.
    - It does NOT encode any of the GOR claims (sign-structure, coherence, etc.).
    """

    path = "data/raw/nist_pblock_periods_2to5.csv"
    df = load_nist_pblock_csv(path)

    # Expected periods for this file.
    assert set(df["period"].tolist()) == {2, 3, 4, 5}

    # For this dataset, n is used as a shell index and equals the period.
    assert (df["n"] == df["period"]).all()

    # Required columns exist (load_nist_pblock_csv checks this), but we also
    # assert no missing values and finiteness.
    for col in ["p1", "p2", "p3", "p4", "p5", "p6"]:
        assert not df[col].isna().any(), f"Missing values in column {col}"
        vals = df[col].to_numpy(dtype=float)
        assert np.isfinite(vals).all(), f"Non-finite values in column {col}"

    # Basic anchor monotonic sanity: p2 should not exceed p5.
    assert (df["p2"] <= df["p5"]).all()

    # One row per period.
    assert len(df) == len(set(df["period"]))
