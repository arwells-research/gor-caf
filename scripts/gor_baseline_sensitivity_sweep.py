#!/usr/bin/env python3
# gor_baseline_sensitivity_sweep.py → Continuous robustness test (primary)
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from gor_caf.datasets import load_nist_pblock_csv, row_to_ies
from gor_caf.baseline_methods_holdout import holdout_monotone_min_curv_0145


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Penalty sweep for holdout monotone-min-curvature baseline (anchors 0,1,4,5)."
    )
    ap.add_argument("--csv", required=True, help="Path to NIST p-block CSV (periods 2–5)")
    ap.add_argument(
        "--lambdas",
        nargs="+",
        type=float,
        default=[0.0, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0],
        help="Curvature penalty strengths to sweep",
    )
    ap.add_argument(
        "--out_csv",
        default="data/derived/baseline_sensitivity_lambda_sweep.csv",
        help="Output CSV path",
    )
    args = ap.parse_args()

    df = load_nist_pblock_csv(args.csv).sort_values(["n"]).reset_index(drop=True)
    lambdas = [float(x) for x in args.lambdas]

    rows = []
    for _, r in df.iterrows():
        ies = row_to_ies(r)
        for lam in lambdas:
            baseline, residuals = holdout_monotone_min_curv_0145(ies, degree=3, lambda_curv=lam)
            r_p3 = float(residuals[2])
            r_p4 = float(residuals[3])
            ratio = float(abs(r_p3 / r_p4)) if r_p4 != 0 else float("nan")
            rows.append(
                {
                    "n": int(r["n"]),
                    "period": int(r["period"]),
                    "lambda_curv": lam,
                    "r_p3": r_p3,
                    "r_p4": r_p4,
                    "ratio_abs_rp3_rp4": ratio,
                }
            )

    out = pd.DataFrame(rows).sort_values(["n", "lambda_curv"]).reset_index(drop=True)
    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    summary = (
        out.groupby(["n", "period"])["ratio_abs_rp3_rp4"]
        .agg(["mean", "std", "min", "max", "count"])
        .reset_index()
        .sort_values(["n"])
    )

    print("\nPer-period summary across lambda sweep:")
    print(summary)
    print(f"\nWrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())