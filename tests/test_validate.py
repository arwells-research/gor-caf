from __future__ import annotations

from gor_caf.datasets import load_nist_pblock_csv
from gor_caf.validate import validate_nist_pblock_df


def test_validate_current_dataset_ok() -> None:
    df = load_nist_pblock_csv("data/raw/nist_pblock_periods_2to5.csv")
    res = validate_nist_pblock_df(
        df,
        expected_periods=[2, 3, 4, 5],
        require_n_equals_period=True,
        require_anchor_monotone=True,
    )
    assert res.ok, f"Validation unexpectedly failed: {res.problems}"
