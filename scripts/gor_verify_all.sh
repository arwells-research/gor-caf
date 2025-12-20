#!/usr/bin/env bash
set -euo pipefail

mkdir -p data/derived
# Optional: ensure a clean, fresh run each time (uncomment if you want)
# rm -f data/derived/*.csv data/derived/*.png 2>/dev/null || true

pytest -q -W error::UserWarning

python3 ./scripts/gor_analyze.py \
  --csv data/raw/nist_pblock_periods_2to5.csv >/dev/null

python3 ./scripts/gor_baseline_sensitivity.py \
  --csv data/raw/nist_pblock_periods_2to5.csv \
  --mode admissible >/dev/null

python3 ./scripts/gor_baseline_sensitivity.py \
  --csv data/raw/nist_pblock_periods_2to5.csv \
  --mode all >/dev/null

# CV plot (admissible only)
python3 ./scripts/gor_plot_cv.py \
  --summary_csv data/derived/baseline_sensitivity_admissible_summary.csv \
  --out_png data/derived/cv_vs_period_admissible.png >/dev/null

echo "OK: tests + CAF exhibit + baseline sensitivity (admissible/all) + CV plot (admissible)"