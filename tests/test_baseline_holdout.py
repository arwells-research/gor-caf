import numpy as np

from gor_caf.baseline_methods_holdout import compare_holdout_baselines


def test_holdout_baselines_do_not_crash_and_produce_finite_ratios():
    # Period 2: B,C,N,O,F,Ne (eV)
    ies = np.array([8.2980, 11.2603, 14.5341, 13.6181, 17.4228, 21.5645])
    res = compare_holdout_baselines(ies)
    assert len(res) >= 3
    for name, r in res.items():
        assert np.isfinite(r.ratio_abs_rp3_rp4), f"{name} produced non-finite ratio"
        assert r.ratio_abs_rp3_rp4 > 0.0
