# tests/test_anchor_sensitivity.py
from __future__ import annotations

import numpy as np

from gor_caf.datasets import load_nist_pblock_csv
from gor_caf.anchor_sensitivity import (
    list_admissible_anchor_pairs,
    build_anchor_sensitivity_table,
)


def test_admissible_anchor_pair_count_and_contains_canonical() -> None:
    pairs = list_admissible_anchor_pairs()
    # CAF-C2 admissible set size should be stable given the current definition.
    assert len(pairs) == 8
    assert any((p.i == 1 and p.j == 4) for p in pairs)  # canonical (p2,p5)


def test_anchor_sensitivity_table_contract_and_canonical_sanity() -> None:
    df = load_nist_pblock_csv("data/raw/nist_pblock_periods_2to5.csv")
    out = build_anchor_sensitivity_table(df, mode="admissible")

    # Expect 4 periods (2..5), 8 admissible anchor pairs each.
    assert len(out) == 4 * 8

    required_cols = {
        "period",
        "n",
        "anchor_i",
        "anchor_j",
        "anchor_span",
        "r_p3",
        "r_p4",
        "G3",
        "G4",
        "C_obs",
        "d_obs",
        "sign_ok",
        "slope",
        "intercept",
    }
    assert required_cols.issubset(set(out.columns))

    # Canonical pair exists for each period.
    canon = out[(out["anchor_i"] == 1) & (out["anchor_j"] == 4)].copy()
    assert set(canon["period"].tolist()) == {2, 3, 4, 5}

    # Canonical sign structure should hold (this is an invariant claim already made elsewhere).
    assert canon["sign_ok"].all()

    # d_obs is defined as abs(C-1) (finite in canonical runs for current dataset).
    assert np.isfinite(canon["C_obs"].to_numpy(dtype=float)).all()
    assert np.isfinite(canon["d_obs"].to_numpy(dtype=float)).all()

    # Conservative robustness check:
    # For periods 2–4, canonical should not be worse than the median anchor-pair deviation.
    for period in [2, 3, 4]:
        sub = out[out["period"] == period]
        d_med = float(sub["d_obs"].median())
        d_can = float(canon[canon["period"] == period]["d_obs"].iloc[0])
        assert d_can <= d_med
