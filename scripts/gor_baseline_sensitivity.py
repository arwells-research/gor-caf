#!/usr/bin/env python3
# gor_baseline_sensitivity.py → Discrete baseline comparison (holdout baselines)
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from gor_caf.datasets import load_nist_pblock_csv, row_to_ies
from gor_caf.baseline_methods_holdout import compare_holdout_baselines


ADMISSIBLE_DEFAULT = {
    # Shape-preserving / monotone baselines intended to not "eat" mid-shell structure
    "Holdout_PCHIP_0145",
    "Holdout_MonotoneMinCurv_0145",
}

DIAGNOSTIC_DEFAULT = {
    # Included for diagnostic contrast only (can absorb structure by construction)
    "Holdout_Quad_0145",
    "Holdout_Spline_0145",
    "Holdout_Line_05",  # weakly constrained; often collapses ratios
}


def _default_out_paths(mode: str) -> tuple[str, str]:
    base = f"data/derived/baseline_sensitivity_{mode}.csv"
    summ = f"data/derived/baseline_sensitivity_{mode}_summary.csv"
    return base, summ


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Baseline sensitivity study for GOR/CAF.\n"
            "Reports ratio = |r_p3 / r_p4| across a baseline family."
        )
    )
    ap.add_argument("--csv", required=True, help="Path to NIST p-block CSV (periods 2–5)")
    ap.add_argument(
        "--mode",
        choices=["admissible", "all"],
        default="admissible",
        help="Which baseline family to summarize: admissible (default) or all (includes diagnostics).",
    )
    ap.add_argument(
        "--out_csv",
        default=None,
        help="Output CSV path (per-period, per-method ratios). Default is mode-suffixed under data/derived/.",
    )
    ap.add_argument(
        "--out_summary_csv",
        default=None,
        help="Output CSV path (per-period mean/std across methods). Default is mode-suffixed under data/derived/.",
    )
    args = ap.parse_args()

    df = load_nist_pblock_csv(args.csv).sort_values(["n"]).reset_index(drop=True)

    if args.mode == "admissible":
        include = set(ADMISSIBLE_DEFAULT)
    else:
        include = set(ADMISSIBLE_DEFAULT) | set(DIAGNOSTIC_DEFAULT)

    out_csv_default, out_summary_default = _default_out_paths(args.mode)
    out_csv = args.out_csv or out_csv_default
    out_summary_csv = args.out_summary_csv or out_summary_default

    rows = []
    for _, r in df.iterrows():
        ies = row_to_ies(r)
        results = compare_holdout_baselines(ies)

        for method, br in results.items():
            if method not in include:
                continue
            rows.append(
                {
                    "n": int(r["n"]),
                    "period": int(r["period"]),
                    "method": method,
                    "r_p3": float(br.r_p3),
                    "r_p4": float(br.r_p4),
                    "ratio_abs_rp3_rp4": float(br.ratio_abs_rp3_rp4),
                }
            )

    out = pd.DataFrame(rows).sort_values(["n", "method"]).reset_index(drop=True)

    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    summary = (
        out.groupby(["n", "period"])["ratio_abs_rp3_rp4"]
        .agg(["mean", "std", "min", "max", "count"])
        .reset_index()
        .sort_values(["n"])
        .reset_index(drop=True)
    )

    # Quantitative robustness metric:
    #   CV = std / mean across the chosen baseline family for each period.
    # If mean is 0 (should not happen), set CV to NaN defensively.
    summary["cv"] = summary["std"] / summary["mean"]
    summary.loc[summary["mean"] == 0, "cv"] = float("nan")

    summary_path = Path(out_summary_csv)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)

    pd.set_option("display.width", 140)
    pd.set_option("display.max_columns", None)

    print("\nPer-period, per-baseline ratios (|r_p3/r_p4|):")
    print(out)
    print("\nPer-period summary across baselines:")
    print(summary)
    print("\nCV robustness (std/mean) by period:")
    print(summary[["n", "period", "cv"]])

    print(f"\nWrote: {out_path}")
    print(f"Wrote: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())