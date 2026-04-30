# Banded TSAC: Implementation Specification

## Purpose

Replace the linear land-area weighting in TSAC with a log₁₀-banded scheme that mirrors the existing IUSAF banding methodology. This addresses v4 finding 3.6 (Band 6 / China dominance) by making the TSAC weight structure consistent with the rest of the model.

## Background

Current TSAC weight for Party *i*:

> w_i = A_i / Σ A_j

where `A_i` is the terrestrial land area of Party *i* in km².

This produces excessive concentration at the top: under linear weighting, China holds roughly 12% of the TSAC pool and the top-10 Parties together hold roughly 46%. As a consequence, the TSAC component first exceeds the IUSAF component for China at β ≥ 2%, and reaches a maximum ratio of 10.6× at the grid corner.

The proposed change replaces direct land-area weighting with a banded scheme, where Parties are assigned to one of six bands by order of magnitude of land area, and each band has a flat per-Party weight. This mirrors the existing IUSAF six-band log₁₀ structure.

## Specification

### Step 1: Band assignment

For each eligible Party with terrestrial land area `A_i` (km²), assign band `b_i ∈ {1, 2, 3, 4, 5, 6}` as follows:

| Band | Range (km²) | Description |
|------|-------------|-------------|
| 1 | A < 10³ | Very small |
| 2 | 10³ ≤ A < 10⁴ | Small |
| 3 | 10⁴ ≤ A < 10⁵ | Medium-small |
| 4 | 10⁵ ≤ A < 10⁶ | Medium |
| 5 | 10⁶ ≤ A < 10⁷ | Large |
| 6 | A ≥ 10⁷ | Very large |

Band numbering follows the existing IUSAF convention: higher band number = higher magnitude.

Boundary convention: lower bound inclusive (≥), upper bound exclusive (<).

### Step 2: Per-band weight assignment

Each band `b` is assigned a positive weight `W_b`. These are policy parameters and must be configurable at runtime. The default proposal is a geometric progression with base 2:

> W_1 = 1, W_2 = 2, W_3 = 4, W_4 = 8, W_5 = 16, W_6 = 32

The default is illustrative; the band weights are intended to be calibrated against the v4 grid metrics (see Test Plan §4) and are expected to be set during the methodological review process.

Constraints on `W_b`:

- `W_b > 0` for all b
- `W_{b+1} ≥ W_b` (monotonicity — higher bands have ≥ weight than lower bands)

### Step 3: Per-Party unnormalised weight

For each Party *i* with band `b_i`:

> u_i = W_{b_i}

### Step 4: Normalisation

Normalise across all eligible Parties:

> w_i = u_i / Σ_j u_j

The resulting `w_i` is the Party's TSAC weight, replacing the current land-area-derived value. Downstream use of `w_i` (in the final share blend) is unchanged.

## Reference implementation (Python)

```python
import numpy as np
from typing import Sequence

# Default band lower bounds in km² (inclusive)
DEFAULT_BAND_LOWER_BOUNDS = (0.0, 1e3, 1e4, 1e5, 1e6, 1e7)

# Default per-band weights (geometric, base=2)
DEFAULT_BAND_WEIGHTS = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0)


def assign_band(land_area_km2: float,
                lower_bounds: Sequence[float] = DEFAULT_BAND_LOWER_BOUNDS) -> int:
    """Return band index (1..N) for a Party's land area."""
    if land_area_km2 < 0:
        raise ValueError(f"Land area must be non-negative, got {land_area_km2}")
    band = 1
    for i, lb in enumerate(lower_bounds):
        if land_area_km2 >= lb:
            band = i + 1
    return band


def banded_tsac_weights(land_areas: np.ndarray,
                        band_weights: Sequence[float] = DEFAULT_BAND_WEIGHTS,
                        lower_bounds: Sequence[float] = DEFAULT_BAND_LOWER_BOUNDS
                        ) -> np.ndarray:
    """Compute normalised TSAC weights using log-banded land area.

    Parameters
    ----------
    land_areas : np.ndarray
        Land area in km² for each eligible Party.
    band_weights : Sequence[float]
        Weight assigned to each band, ordered from band 1 to band N.
    lower_bounds : Sequence[float]
        Lower bound (inclusive) of each band, in km², ordered ascending.

    Returns
    -------
    np.ndarray
        Normalised weights summing to 1.0, same length as land_areas.
    """
    if len(band_weights) != len(lower_bounds):
        raise ValueError("band_weights and lower_bounds must be the same length")
    if any(w <= 0 for w in band_weights):
        raise ValueError("All band weights must be strictly positive")
    if any(band_weights[i + 1] < band_weights[i] for i in range(len(band_weights) - 1)):
        raise ValueError("Band weights must be non-decreasing")

    bands = np.array([assign_band(a, lower_bounds) for a in land_areas])
    weights = np.array([band_weights[b - 1] for b in bands], dtype=float)
    total = weights.sum()
    if total == 0:
        raise ValueError("Sum of weights is zero — check inputs")
    return weights / total
```

## Integration

The current TSAC weight computation lives in `src/cali_model/sensitivity_scenarios.py` (and possibly `src/cali_model/calculator.py`). Locate the existing function that produces the TSAC weight vector — currently a normalised land-area vector — and replace its body with a call to `banded_tsac_weights`.

The calling signature must remain unchanged: input is a vector of land areas, output is a vector of normalised weights summing to 1.0. Downstream code (the final-share blend, grid generation, integrity checks) requires no changes.

## Validation invariants

The implementation must satisfy all of the following. These should be added to the existing integrity-check framework in `src/cali_model/sensitivity_metrics.py`.

1. **Sum to one**: `|Σ w_i − 1.0| < 1e-12`
2. **Non-negativity**: `w_i ≥ 0` for all *i*
3. **Band monotonicity**: for any two Parties *i*, *j* with `b_i > b_j`, `w_i ≥ w_j`
4. **Scale invariance**: weights are independent of the unit of land area — calling the function with land areas in km² and m² produces identical normalised weights
5. **Determinism**: identical inputs produce bit-identical outputs across runs

## Test plan

1. **Uniform-weights sanity**: with all `W_b` set to 1.0, the function returns `1/N` for each of *N* Parties.
2. **One-Party-per-band**: synthetic input with exactly one Party in each band and default weights — verify each output equals `W_b / Σ W_b`.
3. **Boundary cases**: a Party with `A = 1e6` exactly is assigned to band 5 (lower bound inclusive). A Party with `A = 999,999` is in band 4.
4. **Reproduction of v4 grid**: re-run the v4 sensitivity scenarios with banded TSAC weights replacing the linear ones. Regenerate `tsac_sosac_grid_coarse.csv`, `tsac_sosac_grid_fine.csv`, and the four heatmaps. Compare against the current v4 outputs along four headline metrics:
    - Location of gini-minimum on the two-way surface
    - β at which TSAC/IUSAF ratio first crosses 1.0 for any Party (currently 2%)
    - Maximum TSAC/IUSAF ratio across the grid (currently 10.6×)
    - Number of scenarios in the moderate-overlay zone (currently 35/176)
5. **Integrity checks**: re-run all nine integrity check categories on the sampled scenarios. All must continue to pass.

## Outputs to regenerate

The following v4 artefacts depend on the TSAC weight definition and must be regenerated after the change:

- `tsac_sosac_grid_coarse.csv`
- `tsac_sosac_grid_fine.csv`
- `tsac_sosac_heatmap_gini_coarse.png`
- `tsac_sosac_heatmap_gini_fine.png`
- `tsac_sosac_heatmap_spearman_coarse.png`
- `tsac_sosac_heatmap_spearman_fine.png`
- `integrity_checks.csv`
- `scale_invariance.csv`
- `country_results.csv`

The IUSAF-side artefacts (`fig_e1_un_scale_raw_inversion_data.csv`, `fig_e1_generate.py`) are unaffected — banding applies to TSAC only.

## Configuration

Expose the following parameters in the scenario configuration alongside existing β and γ:

- `tsac_band_lower_bounds`: tuple of 6 floats (defaults as above)
- `tsac_band_weights`: tuple of 6 floats (defaults as above)

This permits what-if analysis: changing the geometric base, adjusting individual band weights, or collapsing bands by setting adjacent weights equal.

## Calibration harness

The per-band weights `W_1 … W_6` are policy parameters, not technical defaults, and must be set by the methodological review group after inspecting the distributional consequences. The implementer does **not** select these values. Instead, the implementer builds a calibration harness that allows a human to sweep candidate configurations and compare them against the v4 grid metrics.

### Harness specification

Build a script `scripts/calibrate_banded_tsac.py` that:

1. Accepts as input a set of candidate band-weight configurations. Two formats must be supported:
    - A named preset (e.g. `geometric_base_2`, `geometric_base_1.5`, `linear_progression`, `flat`, `capped_top`)
    - An explicit tuple `(W_1, W_2, W_3, W_4, W_5, W_6)` passed via CLI or config file
2. For each configuration, re-runs the coarse two-way grid (176 scenarios) with banded TSAC weights computed from that configuration.
3. For each configuration, computes and reports the following headline metrics:
    - Gini-minimum location on the two-way surface (β, γ, Gini value)
    - β at which the TSAC/IUSAF ratio first crosses 1.0 for any Party
    - Maximum TSAC/IUSAF ratio across the grid and the binding Party at that point
    - Number of scenarios in the moderate-overlay zone (ρ ≥ 0.85)
    - SIDS total ($m) and LDC total ($m) at the gini-minimum point
    - Top-10 Parties by TSAC share, with shares
4. Outputs a comparison table (`calibration_results.csv`) with one row per configuration, and produces side-by-side headline-metric plots (`calibration_comparison.png`).
5. Runs all nine integrity checks on a sample from each configuration's grid and reports pass/fail.

### Suggested preset configurations

The harness should ship with at least the following presets for the group to compare:

| Preset name | (W_1, W_2, W_3, W_4, W_5, W_6) | Rationale |
|-------------|----------------------------------|-----------|
| `flat` | (1, 1, 1, 1, 1, 1) | Equal per-Party weight; floor benchmark |
| `geometric_base_1.5` | (1, 1.5, 2.25, 3.4, 5.1, 7.6) | Gentle progression |
| `geometric_base_2` | (1, 2, 4, 8, 16, 32) | Moderate progression |
| `geometric_base_3` | (1, 3, 9, 27, 81, 243) | Steep progression (approaches linear) |
| `capped_top` | (1, 2, 4, 8, 16, 16) | Geometric but top band capped at Band 5 weight |
| `linear_progression` | (1, 2, 3, 4, 5, 6) | Linear in band index |

The harness must make it trivial to add further presets — a simple dictionary entry — so the group can iterate during review.

### Acceptance criteria for calibration

The group should select the band-weight configuration using the following criteria, in order of priority:

1. **Primary**: TSAC/IUSAF ratio remains ≤ 2.0 across the entire two-way grid. This is the direct response to v4 finding 3.6.
2. **Secondary**: The moderate-overlay zone (ρ ≥ 0.85) contains at least as many scenarios as under the current (linear) TSAC specification.
3. **Tertiary**: Gini-minimum on the two-way surface is at least as low as under the current specification (i.e. the change does not worsen the best achievable distributional outcome).
4. **Subjective**: Distribution of TSAC shares among top-10 Parties is judged reasonable by the review group — not a purely technical criterion.

A configuration satisfying criteria 1–3 and judged acceptable under criterion 4 is a candidate for adoption. If no preset satisfies all criteria, the harness supports arbitrary explicit tuples so the group can iterate toward one that does.

### Deliverables from calibration

The implementer delivers:

- The calibration harness script and its outputs for the six presets above
- A brief written summary (1 page) noting which presets satisfy criteria 1–3 and flagging any that dominate others across all metrics
- A recommendation is **not** required and should not be made; the selection is a group decision

The group then selects a configuration, which is recorded in the v4.1 methodology documentation and used as the default `tsac_band_weights` going forward.

## Out of scope

This specification covers replacing the linear land-area weighting with a banded scheme only. The following are explicit non-goals:

- Replacing land area with a multi-indicator stewardship index (deferred to v5+ workstream)
- Changing IUSAF or SOSAC weight computation
- Changing the final-share blend formula `(1 − β − γ) · IUSAF + β · TSAC + γ · SOSAC`
- Changing the floor/ceiling mechanism

## Documentation updates required

The following documents must be updated to reflect the new TSAC computation once implementation is complete:

- `technical_annex.md` — formula specification section
- `executive_summary.md` — methodology paragraph and findings list
- Any methodology section in the v4 reports that describes TSAC weights as proportional to land area

---

*Implementation specification — banded TSAC v1*
