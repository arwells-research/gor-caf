from __future__ import annotations

import argparse

from gor_caf.datasets import load_nist_pblock_csv
from gor_caf.validate import validate_nist_pblock_df


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate a p-block NIST IE CSV against the repo's contract.")
    p.add_argument("--csv", required=True, help="Input CSV path.")
    p.add_argument(
        "--require-n-equals-period",
        action="store_true",
        help="Require n == period for all rows (default: off).",
    )
    p.add_argument(
        "--require-anchor-monotone",
        action="store_true",
        help="Require p2 <= p5 sanity check (default: off).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    df = load_nist_pblock_csv(args.csv)

    res = validate_nist_pblock_df(
        df,
        expected_periods=None,
        require_n_equals_period=bool(args.require_n_equals_period),
        require_anchor_monotone=bool(args.require_anchor_monotone),
    )

    print(f"ok={res.ok}  n_rows={res.n_rows}  periods={list(res.periods)}")
    if not res.ok:
        print("problems:")
        for p in res.problems:
            print(f"- {p}")


if __name__ == "__main__":
    main()
