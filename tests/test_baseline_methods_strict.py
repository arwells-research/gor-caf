import numpy as np
import warnings

from gor_caf.baseline_methods import compare_baselines, BaselineResult


def test_compare_baselines_no_warnings_strict():
    # Period 2: B,C,N,O,F,Ne (eV)
    ies = np.array([8.2980, 11.2603, 14.5341, 13.6181, 17.4228, 21.5645])

    # Hard gate: no UserWarning allowed
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        res = compare_baselines(ies)

    # Must include at least CAF + key stress-test methods
    assert "CAF" in res
    assert any("Monotone" in k for k in res.keys())
    assert any("Spline" in k for k in res.keys())

    # Results must be BaselineResult objects with finite ratio
    for k, v in res.items():
        assert isinstance(v, BaselineResult)
        assert v.baseline.shape == (6,)
        assert v.residuals.shape == (6,)
        assert np.isfinite(v.ratio_abs_rp3_rp4)