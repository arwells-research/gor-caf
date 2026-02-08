# CSV Contract: `data/raw/nist_pblock_periods_2to5.csv`

This document defines the minimal on-disk contract for the raw NIST first-ionization-energy
p-block dataset consumed by this repository.

## Intent

- The file is treated as **raw input**.
- Analyses in this repository must not rely on undocumented preprocessing.
- The test suite enforces this contract.

## File location

- `data/raw/nist_pblock_periods_2to5.csv`

## Shape

- One row per period.
- Exactly **6** p-block entries per period.

## Required columns

| Column | Type | Meaning |
|---|---:|---|
| `period` | int | Period number. For this file: {2, 3, 4, 5}. |
| `n` | int | Shell index used by this repo. For this file: `n == period`. |
| `p1` | float | First ionization energy for p¹ entry (eV). |
| `p2` | float | First ionization energy for p² entry (eV). |
| `p3` | float | First ionization energy for p³ entry (eV). |
| `p4` | float | First ionization energy for p⁴ entry (eV). |
| `p5` | float | First ionization energy for p⁵ entry (eV). |
| `p6` | float | First ionization energy for p⁶ entry (eV). |

## Optional columns

| Column | Type | Meaning |
|---|---:|---|
| `labels` | string | Comma-separated element symbols in the same order as p1..p6. |

Analyses must not assume optional columns exist.

## Basic sanity constraints (enforced by tests)

- No missing values in required columns.
- All `p1..p6` values must be finite floats.
- `p2 <= p5` for each period (anchor monotonic sanity).
- For this dataset, `n == period`.

## Ordering rule (interpretation)

Within each row, the six values correspond to the period’s p-block sequence in increasing
atomic number:

- `p1`: p¹
- `p2`: p²
- `p3`: p³
- `p4`: p⁴
- `p5`: p⁵
- `p6`: p⁶

The `labels` column (when present) must list element symbols in this same order.
