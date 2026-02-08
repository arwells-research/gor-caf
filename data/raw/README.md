# Raw Data Provenance (NIST p-block IE)

This repository consumes **raw first ionization energies (IE)** for the p-block across
Periods 2–5.

## Source

- Source: NIST Atomic Spectra Database (ASD), First Ionization Energies.
- Dataset file: `nist_pblock_periods_2to5.csv`

## Retrieval / transcription

- Values were transcribed into a CSV **as-is** in **eV**.
- Retrieval date: **unknown / not recorded in the raw file** (update this line when the
  NIST extraction date is available).
- No smoothing, interpolation, normalization, or unit conversion is performed.

## Ordering / interpretation contract

Each CSV row represents one period and stores the six p-block entries in order:

- `p1` = p¹
- `p2` = p²
- `p3` = p³
- `p4` = p⁴
- `p5` = p⁵
- `p6` = p⁶

Columns:

- `period`: period number (2–5 in this dataset)
- `n`: shell index used by this repo (for the current dataset, `n == period`)
- `labels` (optional): comma-separated element symbols in the same order as p1..p6

The automated test suite enforces the schema and basic sanity checks.
