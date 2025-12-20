import numpy as np
from gor_caf.caf import caf_baseline, channel_units


def test_period2_residuals():
    # Period 2: B,C,N,O,F,Ne
    ies = np.array([8.2980, 11.2603, 14.5341, 13.6181, 17.4228, 21.5645])
    res = caf_baseline(ies).residuals
    assert abs(res[2] - 1.2196333333) < 1e-6
    assert abs(res[3] - (-1.7505333333)) < 1e-6

    g3, g4, c = channel_units(res)
    assert abs(g3 - 0.4065444444) < 1e-6
    assert abs(g4 - 0.4376333333) < 1e-6
    assert 0.92 < c < 0.94