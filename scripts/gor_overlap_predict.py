# scripts/gor_overlap_predict.py

import argparse
import pandas as pd

from gor_caf.geometric_kernels import predict_G_from_overlap

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", choices=["gaussian", "yukawa", "delta_plus_tail"], default="gaussian")
    ap.add_argument("--r_bpg", type=float, default=0.00192)
    ap.add_argument("--out_csv", default="data/derived/overlap_predictions.csv")
    args = ap.parse_args()

    periods = [2, 3, 4, 5]
    preds = predict_G_from_overlap(periods, kernel_type=args.kernel, r_BPG=args.r_bpg)

    rows = []
    for p in periods:
        gp = preds[p]
        rows.append({"period": p, "n": gp.n, "D": gp.D, "G_pred": gp.G_pred})

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(df)
    print(f"\nWrote: {args.out_csv}")

if __name__ == "__main__":
    main()