#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pandas as pd
from gor_caf.plots import plot_channel_split


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exhibit_csv", default="data/derived/caf_exhibit.csv")
    ap.add_argument("--out_png", default="data/derived/channel_split.png")
    args = ap.parse_args()

    df = pd.read_csv(args.exhibit_csv)
    plot_channel_split(df, out_png=args.out_png)
    print(f"Wrote: {args.out_png} and {args.out_png.replace('.png','_ratio.png')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())