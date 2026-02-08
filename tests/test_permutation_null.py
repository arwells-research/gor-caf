from __future__ import annotations

import numpy as np

from gor_caf.nulls import permutation_null_for_period


def test_permutation_null_deterministic() -> None:
    ies = np.array([8.0, 9.0, 10.0, 9.5, 11.0, 12.0], dtype=float)

    rng1 = np.random.default_rng(0)
    r1 = permutation_null_for_period(ies=ies, n_perm=200, eps=0.1, rng=rng1)

    rng2 = np.random.default_rng(0)
    r2 = permutation_null_for_period(ies=ies, n_perm=200, eps=0.1, rng=rng2)

    assert r1 == r2
    for v in [r1.p_sign_correct, r1.p_coh_close, r1.p_joint, r1.p_value_coh]:
        assert 0.0 <= v <= 1.0
