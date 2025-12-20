import numpy as np

from gor_caf.baseline_methods import compare_baselines


def test_compare_baselines_returns_expected_methods_and_finite_ratios():
    # Period 2: B,C,N,O,F,Ne (eV)
    ies = np.array([8.2980, 11.2603, 14.5341, 13.6181, 17.4228, 21.5645])
    res = compare_baselines(ies)

    # Ensure presence of the canonical baseline and at least 3 stress tests
    assert "CAF" in res
    assert "Quadratic" in res
    assert "MonotoneMinCurv" in res

    # Ratios should be finite and positive for these methods
    for k, v in res.items():
        assert np.isfinite(v.ratio_abs_rp3_rp4), f"{k} produced non-finite ratio"
        assert v.ratio_abs_rp3_rp4 > 0.0