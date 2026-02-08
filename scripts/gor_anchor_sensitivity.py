# scripts/gor_anchor_sensitivity.py
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from gor_caf.datasets import load_nist_pblock_csv
from gor_caf.anchor_sensitivity import build_anchor_sensitivity_table


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="CAF-C2: anchor-pair sensitivity map for CAF coherence (p-block p1..p6)."
    )
    p.add_argument("--csv", required=True, help="Input CSV (raw NIST p-block IE).")
    p.add_argument(
        "--mode",
        default="admissible",
        choices=["admissible", "all"],
        help="Anchor-pair set to evaluate (default: admissible).",
    )
    p.add_argument(
        "--out-csv",
        required=True,
        help="Output CSV path (recommended under data/derived/).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    df = load_nist_pblock_csv(args.csv)

    out = build_anchor_sensitivity_table(df, mode=args.mode)

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    print(f"Wrote: {out_path}  rows={len(out)}  mode={args.mode}")


if __name__ == "__main__":
    main()
