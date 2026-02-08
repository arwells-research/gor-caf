from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run the full GOR-CAF audit pipeline on an arbitrary dataset CSV.")
    p.add_argument("--csv", required=True, help="Input CSV path.")
    p.add_argument("--tag", required=True, help="Dataset tag (e.g., p2to5, p2to6). Used in output filenames.")
    p.add_argument("--n-perm", type=int, default=20000, help="Permutations per period for null (default: 20000).")
    p.add_argument("--eps", type=float, default=0.10, help="Null tolerance eps for |C-1|<=eps (default: 0.10).")
    p.add_argument("--seed", type=int, default=0, help="RNG seed for null (default: 0).")
    p.add_argument("--out-dir", default="data/derived", help="Output directory (default: data/derived).")
    return p.parse_args()


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=None)
    if r.returncode != 0:
        raise SystemExit(r.returncode)


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv = args.csv
    tag = args.tag

    run([sys.executable, "./scripts/gor_analyze.py", "--csv", csv])

    run(
        [
            sys.executable,
            "./scripts/gor_null_permutation.py",
            "--csv",
            csv,
            "--n-perm",
            str(int(args.n_perm)),
            "--eps",
            str(float(args.eps)),
            "--seed",
            str(int(args.seed)),
            "--out-csv",
            str(out_dir / f"null_permutation_summary_{tag}.csv"),
        ]
    )

    run(
        [
            sys.executable,
            "./scripts/gor_anchor_sensitivity.py",
            "--csv",
            csv,
            "--mode",
            "admissible",
            "--out-csv",
            str(out_dir / f"anchor_sensitivity_admissible_{tag}.csv"),
        ]
    )

    run([sys.executable, "./scripts/gor_baseline_sensitivity.py", "--csv", csv, "--mode", "admissible"])
    run([sys.executable, "./scripts/gor_baseline_sensitivity.py", "--csv", csv, "--mode", "all"])

    # CV plot expects the default admissible summary filename; if you later want per-tag isolation,
    # we can extend baseline_sensitivity to accept an output prefix. For CAF-C3 we keep changes minimal.
    run(
        [
            sys.executable,
            "./scripts/gor_plot_cv.py",
            "--summary_csv",
            str(out_dir / "baseline_sensitivity_admissible_summary.csv"),
            "--out_png",
            str(out_dir / f"cv_vs_period_admissible_{tag}.png"),
        ]
    )

    print(f"OK: ran pipeline for tag={tag} using csv={csv} outputs in {out_dir}")


if __name__ == "__main__":
    main()
