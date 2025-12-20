#!/usr/bin/env python3
# gor_analyze.py → Primary CAF extraction
from __future__ import annotations

import argparse
from pathlib import Path

from gor_caf.datasets import load_nist_pblock_csv
from gor_caf.metrics import compute_exhibit


def main() -> int:
    ap = argparse.ArgumentParser(description="GOR/CAF analysis (Periods 2–5 p-block)")
    ap.add_argument("--csv", required=True, help="Path to NIST p-block CSV")
    ap.add_argument("--out_csv", default="data/derived/caf_exhibit.csv", help="Output CSV path")
    args = ap.parse_args()

    df = load_nist_pblock_csv(args.csv)
    exhibit = compute_exhibit(df)

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    exhibit.to_csv(out_path, index=False)

    # Pretty print
    with pd.option_context("display.max_columns", None, "display.width", 120):
        print(exhibit)

    print(f"\nWrote: {out_path}")
    return 0


if __name__ == "__main__":
    import pandas as pd
    raise SystemExit(main())