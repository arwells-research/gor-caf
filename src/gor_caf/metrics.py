from __future__ import annotations

import pandas as pd
import numpy as np

from .caf import caf_baseline, channel_units
from .datasets import row_to_ies


def compute_exhibit(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        ies = row_to_ies(r)
        caf = caf_baseline(ies)
        g3, g4, c = channel_units(caf.residuals)

        rows.append({
            "n": int(r["n"]),
            "period": int(r["period"]),
            "r_p3": float(caf.residuals[2]),
            "r_p4": float(caf.residuals[3]),
            "G3": float(g3),
            "G4": float(g4),
            "C": float(c),
            "slope": float(caf.slope),
        })

    out = pd.DataFrame(rows).sort_values(["n"]).reset_index(drop=True)
    return out