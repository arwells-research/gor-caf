from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from gor_caf.datasets import load_nist_pblock_csv, row_to_ies
from gor_caf.nulls import permutation_null_for_period


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Permutation null ensemble for GOR-CAF (within-period shuffles).")
    p.add_argument("--csv", required=True, help="Input CSV (raw NIST p-block IE).")
    p.add_argument("--n-perm", type=int, default=10000, help="Permutations per period (default: 10000).")
    p.add_argument("--eps", type=float, default=0.10, help="Closeness threshold for |C-1| <= eps (default: 0.10).")
    p.add_argument("--seed", type=int, default=0, help="RNG seed (default: 0).")
    p.add_argument("--out-csv", required=True, help="Output summary CSV path.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    df = load_nist_pblock_csv(args.csv)

    rng = np.random.default_rng(args.seed)

    rows = []
    for _, row in df.iterrows():
        ies = row_to_ies(row)
        period = int(row["period"])
        n = int(row["n"])

        res = permutation_null_for_period(
            ies=ies,
            n_perm=args.n_perm,
            eps=float(args.eps),
            rng=rng,
        )

        rows.append(
            {
                "period": period,
                "n": n,
                "n_perm": int(args.n_perm),
                "eps": float(args.eps),
                "seed": int(args.seed),
                "C_obs": float(res.C_obs),
                "d_obs": float(res.d_obs),
                "p_sign_correct": float(res.p_sign_correct),
                "p_coh_close": float(res.p_coh_close),
                "p_joint": float(res.p_joint),
                "p_value_coh": float(res.p_value_coh),
            }
        )

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_df = pd.DataFrame(rows).sort_values(["period"]).reset_index(drop=True)
    out_df.to_csv(out_path, index=False)
    print(f"Wrote: {out_path}  rows={len(out_df)}")


if __name__ == "__main__":
    main()
