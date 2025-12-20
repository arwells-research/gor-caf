#!/usr/bin/env python3
# gor_plot_cv.py → Plot CV vs period (admissible only)
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Plot coefficient of variation (CV) vs period from admissible baseline summary CSV."
    )
    ap.add_argument(
        "--summary_csv",
        default="data/derived/baseline_sensitivity_admissible_summary.csv",
        help="Path to admissible summary CSV (must include columns: period, cv).",
    )
    ap.add_argument(
        "--out_png",
        default="data/derived/cv_vs_period_admissible.png",
        help="Output PNG path.",
    )
    ap.add_argument(
        "--title",
        default="Baseline Robustness (Admissible): CV vs Period",
        help="Plot title.",
    )
    ap.add_argument(
        "--ymax",
        type=float,
        default=None,
        help="Optional y-axis maximum. If omitted, matplotlib chooses.",
    )
    ap.add_argument(
        "--show",
        action="store_true",
        help="Show the plot interactively (does not block saving).",
    )
    args = ap.parse_args()

    summary_path = Path(args.summary_csv)
    if not summary_path.exists():
        raise SystemExit(f"ERROR: summary CSV not found: {summary_path}")

    df = pd.read_csv(summary_path)

    required = {"period", "cv"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(
            f"ERROR: summary CSV missing required columns {sorted(missing)}. "
            f"Found: {list(df.columns)}"
        )

    # Sort by period and coerce types
    df = df.sort_values("period").reset_index(drop=True)

    periods = df["period"].astype(int).to_numpy()
    cvs = df["cv"].astype(float).to_numpy()

    # Validate values (publication-facing plot; fail fast)
    if periods.size == 0:
        raise SystemExit("ERROR: summary CSV has no rows.")
    if not np.all(np.isfinite(cvs)):
        bad = np.where(~np.isfinite(cvs))[0].tolist()
        raise SystemExit(f"ERROR: CV contains non-finite values at rows {bad}.")
    if np.any(cvs < 0):
        bad = np.where(cvs < 0)[0].tolist()
        raise SystemExit(f"ERROR: CV contains negative values at rows {bad}.")

    out_path = Path(args.out_png)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure()
    plt.plot(periods, cvs, marker="o")
    plt.xlabel("Period (n)")
    plt.ylabel("Coefficient of Variation (CV)")
    plt.title(args.title)
    plt.xticks(periods)

    if args.ymax is not None:
        plt.ylim(top=float(args.ymax))

    plt.tight_layout()
    plt.savefig(out_path, dpi=200)

    if args.show:
        plt.show()

    plt.close()

    print(f"Wrote: {out_path}")
    print(f"Periods: {periods.min()}–{periods.max()} (n={periods.size})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())