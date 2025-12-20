# Geometric Occupancy Rule (GOR) — Canonical Anchor Fit Verification

**Author:** A. R. Wells  
**Affiliation:** Dual-Frame Research Group  
**License:** MIT  
**Repository:** `arwells-research/gor-caf`  
**Status:** Verification & Analysis Pipeline (Foundational)

---

## Overview

This repository provides a clean, reproducible Python implementation of the **Geometric Occupancy Rule (GOR)** verification pipeline using the **Canonical Anchor Fit (CAF)**.

The goal of this project is **not** to fit chemical or many-body models, but to **isolate and test invariant geometric structure** present in atomic ionization energies.

Using raw **NIST First Ionization Energy (IE)** data for the *p-block* across Periods 2–5, the pipeline demonstrates:

- a persistent **sign-structured mid-shell residual** at \(p^3/p^4\)
- a stable **\(+3/-4\)** normalization that produces shell-scaled units \(G_n^{(3)}, G_n^{(4)}\)
- a **coherence ratio** \(C_n\) near unity for Periods 2–4 under CAF
- a **channel-selective breakdown** beginning at Period 5

This repository constitutes the **verification backbone** for the Geometric Occupancy Rule and the refinement of Background Phase Geometry (BPG).

---

## Scientific Context (Minimal)

The GOR framework proposes that:

- Atomic energetics encode **topological phase-space tiling constraints**
- The periodic table functions as a **topological phase diagram**
- Pauli exclusion corresponds to **topological incompressibility**
- Exchange/repulsion effects correspond to **discrete phase-cell bookkeeping**

This repository does **not** assume these claims — it tests the *data-level invariants* required for them to hold.

---

## What This Repository Does

✔ Loads **raw NIST IE data** (no preprocessing)  
✔ Applies a **single fixed linear operator** (CAF)  
✔ Extracts **geometric residuals**  
✔ Tests **robustness to baseline choice** (holdout baselines)  
✔ Separates **symmetry vs. collision channels**  
✔ Quantifies **coherence loss** at higher shells  

🚫 No chemical heuristics  
🚫 No Hartree–Fock / DFT fitting  
🚫 No parameter tuning in CAF  

---

## Repository Structure

NOTE: The tree below is shown in a plain indented format to avoid nested fenced code blocks.

    gor-caf/
    ├── pyproject.toml
    ├── LICENSE    
    ├── README.md
    ├── data/
    │   ├── raw/
    │   │   └── nist_pblock_periods_2to5.csv
    │   └── derived/
    │       ├── caf_exhibit.csv
    │       ├── baseline_sensitivity_admissible.csv
    │       ├── baseline_sensitivity_admissible_summary.csv
    │       ├── baseline_sensitivity_all.csv
    │       ├── baseline_sensitivity_all_summary.csv
    │       └── baseline_sensitivity_lambda_sweep.csv
    ├── scripts/
    │   ├── gor_analyze.py
    │   ├── gor_baseline_sensitivity.py
    │   ├── gor_baseline_sensitivity_sweep.py
    │   ├── gor_overlap_predict.py
    │   ├── gor_plot.py
    │   └── gor_verify_all.sh
    ├── src/
    │   └── gor_caf/
    │       ├── caf.py
    │       ├── datasets.py
    │       ├── metrics.py
    │       ├── plots.py
    │       ├── baseline_methods.py
    │       ├── baseline_methods_holdout.py
    │       └── geometric_kernels.py
    └── tests/
        ├── test_caf.py
        ├── test_baseline_holdout.py
        ├── test_baseline_methods.py
        └── test_baseline_methods_strict.py

---

## The Canonical Anchor Fit (CAF)

CAF is a fixed linear operator defined as follows:

1. Take the six p-block ionization energies \((p^1 \dots p^6)\).
2. Fit the unique straight line through the **\(p^2\)** and **\(p^5\)** values.
3. Subtract this line from all six points.

This removes the smooth radial background and exposes mid-shell residual structure.

### Baseline definition

Let the ionization energies be ordered as:

- index 0: \(p^1\)
- index 1: \(p^2\) (anchor)
- index 2: \(p^3\)
- index 3: \(p^4\)
- index 4: \(p^5\) (anchor)
- index 5: \(p^6\)

Define the baseline \(E_\text{base}(i)\) as the line through \((1, IE_{p^2})\) and \((4, IE_{p^5})\), and residuals:

\[
r_i = IE_i - E_\text{base}(i).
\]

The two residuals of interest are:

- \(r_{p^3}\) (symmetry peak; typically positive)
- \(r_{p^4}\) (collision dip; typically negative)

---

## Integer Invariants and Channel Units (CAF)

GOR tests the hypothesis that the \(p^3/p^4\) residuals admit a shell-scaled integer normalization:

- \(I_{p^3} = +3\)
- \(I_{p^4} = -4\)

Define two empirical channel units:

\[
G_n^{(3)}=\frac{r_{p^3}}{3}, \qquad
G_n^{(4)}=\frac{|r_{p^4}|}{4}.
\]

Define the CAF coherence ratio:

\[
C_n = \frac{G_n^{(3)}}{G_n^{(4)}}.
\]

Empirically (CAF), \(C_n \approx 1\) for Periods 2–4 and drops for Period 5, indicating that the symmetry channel degrades faster than the collision channel at higher shells.

---

## Data

The foundational dataset is the raw NIST first ionization energies (eV) for p-block periods 2–5:

- Period 2: B, C, N, O, F, Ne
- Period 3: Al, Si, P, S, Cl, Ar
- Period 4: Ga, Ge, As, Se, Br, Kr
- Period 5: In, Sn, Sb, Te, I, Xe

Stored at:

- `data/raw/nist_pblock_periods_2to5.csv`

No preprocessing is performed beyond loading the CSV.

---

## Installation

Create a virtual environment and install the package in editable mode:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -U pip
    pip install -e .[dev]

Dependencies are defined in `pyproject.toml`.

---

## Reproduce the CAF Exhibit Table

Run:

    python3 ./scripts/gor_analyze.py --csv data/raw/nist_pblock_periods_2to5.csv

This writes:

- `data/derived/caf_exhibit.csv`

The exhibit includes:

- \(r_{p^3}\), \(r_{p^4}\)
- \(G_n^{(3)}\), \(G_n^{(4)}\)
- \(C_n\)

---

## Baseline Sensitivity (Publication-Critical Stress Test)

To demonstrate that the observed mid-shell structure is not an artifact of CAF’s particular baseline choice, this repository includes a **holdout baseline family** that fits only the edge points \(\{p^1,p^2,p^5,p^6\}\), leaving \(\{p^3,p^4\}\) as genuine out-of-sample structure.

For each period, we report:

\[
\mathcal{R} \equiv \left|\frac{r_{p^3}}{r_{p^4}}\right|.
\]

This is *not* the same as the CAF coherence ratio \(C_n\). It is a robustness diagnostic for baseline choice.

### Criteria for “physically admissible” baselines

A holdout baseline is considered physically admissible if:

1. **Holdout construction**: The baseline is fit only to indices
   \(\{p^1, p^2, p^5, p^6\}\), leaving \(\{p^3, p^4\}\) as genuine
   out-of-sample predictions.

2. **Monotonicity**: The baseline is non-decreasing across the period,
   reflecting the monotonic increase of ionization energy with nuclear
   charge under smooth screening.

3. **Shape preservation**: Interpolation between holdout points avoids
   artificial oscillations and respects local monotonic structure.
   Implementations include:
   - PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)
   - Monotone minimum-curvature constrained optimization

4. **Exclusion of over-flexible methods**: Baselines whose degrees of
   freedom approach or exceed the number of data points (e.g. high-order
   polynomials or unconstrained splines) can absorb arbitrary structure
   and are excluded from robustness claims.

Baselines violating these criteria are included only in `--mode all`
as diagnostic contrasts and do not constitute admissible robustness tests.

### Run baseline sensitivity

Admissible-only:

    python3 ./scripts/gor_baseline_sensitivity.py \
      --csv data/raw/nist_pblock_periods_2to5.csv \
      --mode admissible

Writes:

- `data/derived/baseline_sensitivity_admissible.csv`
- `data/derived/baseline_sensitivity_admissible_summary.csv`

All baselines (includes diagnostics):

    python3 ./scripts/gor_baseline_sensitivity.py \
      --csv data/raw/nist_pblock_periods_2to5.csv \
      --mode all

Writes:

- `data/derived/baseline_sensitivity_all.csv`
- `data/derived/baseline_sensitivity_all_summary.csv`

Lambda sweep (continuous perturbation family):

    python3 ./scripts/gor_baseline_sensitivity_sweep.py \
      --csv data/raw/nist_pblock_periods_2to5.csv

Writes:

- `data/derived/baseline_sensitivity_lambda_sweep.csv`

---

### Why the holdout ratio is ~0.9, not 0.75

A common first expectation is: if \(p^3\) corresponds to “+3” and \(p^4\) to “−4”, then the raw residual ratio should be \(|r_{p^3}/r_{p^4}| \approx 3/4 = 0.75\).

That expectation is **not** the quantity being tested by the holdout ratio \(\mathcal{R}\).

- The integers \(+3\) and \(-4\) are used to define **channel units** \(G_n^{(3)}\) and \(G_n^{(4)}\).
- The CAF coherence ratio \(C_n = G_n^{(3)}/G_n^{(4)}\) is the diagnostic intended to approach unity when channels are locked.
- The holdout ratio \(\mathcal{R} = |r_{p^3}/r_{p^4}|\) is a **baseline robustness** statistic whose value depends on how the chosen baseline assigns the smooth background between the holdout anchors.

In other words:

- **CAF**: tests whether a fixed, anchor-defined operator produces channel units with \(C_n \approx 1\) (Periods 2–4) and degrades at Period 5.
- **Holdout baselines**: test whether the *existence and sign-structure* of \((r_{p^3}, r_{p^4})\) persists across defensible baseline families, without allowing the baseline to “eat” the mid-shell signal.

The fact that \(\mathcal{R}\) is stable across admissible baselines (and collapses at Period 5) is strong evidence that the mid-shell structure is real and that the Period 5 crossover is not a CAF artifact.

---

### Interpretation of the Period 5 crossover (holdout)

Under admissible holdout baselines, \(\mathcal{R}\) is higher and relatively stable in Periods 2–4, then drops in Period 5 with low variance across the baseline family.

A natural interpretation consistent with the channel picture is:

- collision penalties are more **local** (pairwise occupancy constraints)
- symmetry bonuses are more **global** (alignment with discrete axes)

As \(n\) increases, radial dilution and screening effects reduce global alignment fidelity faster than local collision penalties, producing a stable crossover rather than random noise.

---

## Plot the Channel Split (Optional)

After generating `data/derived/caf_exhibit.csv`, run:

    python3 ./scripts/gor_plot.py \
      --exhibit_csv data/derived/caf_exhibit.csv \
      --out_png data/derived/channel_split.png

This produces:

- `data/derived/channel_split.png`
- `data/derived/channel_split_ratio.png`

---

## Geometric Overlap Model (In Development)

To connect empirical shell scaling to a geometric kernel model, we implement an overlap construction:

\[
G_n \propto \int_0^\infty |R_{n1}(r)|^2 \, K_{\text{orb}}(r) \, r^2 \, dr
\]

where:
- \(R_{n1}(r)\) is the hydrogenic radial p-wavefunction (\(\ell=1\))
- \(K_{\text{orb}}(r)\) is a localized curvature / defect kernel
- the scale parameter can be anchored to a reference (e.g., Period 2)

Implementation:

- `src/gor_caf/geometric_kernels.py`
- `scripts/gor_overlap_predict.py`

Status: scaffolded and intended to be extended to multi-kernel comparison (Gaussian vs Yukawa vs delta+tail) and quantitative error reporting.

---

## Tests

Run regression tests (includes a strict “no UserWarning” mode):

    pytest -q
    pytest -q -W error::UserWarning

---

## One-command verification

Run the full pipeline:

    ./scripts/gor_verify_all.sh

This performs:

- strict tests
- CAF exhibit generation
- baseline sensitivity (admissible + all)

---

## License

MIT. See `LICENSE`.

---

## Citation

If you use this repository in research or derivative work, please cite it appropriately (software citation details can be added once the repository is archived).

---

## Notes on Scope

This repository is intentionally limited to **verification-grade operators and metrics**:

- CAF extraction
- integer-structure channel units and \(C_n\)
- baseline robustness diagnostics (holdout baselines)

Higher-level modeling (e.g., multi-kernel overlap fitting, coherence-length inference, group-theoretic derivations) should be layered on top of this verified base.