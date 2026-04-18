# Deprecated: Spearman 0.85 Threshold Figures

## What was deprecated

- `break_point_timeline.svg` — Visualised the Spearman 0.85 threshold as a horizontal reference line, implying it was an empirically grounded boundary.
- `decision_boundaries.svg` — Visualised the Spearman 0.85 threshold as a decision boundary, implying it was an analytically derived threshold.

## Why

The Spearman 0.85 threshold was adopted as a design parameter during model development. Empirical analysis (see `docs/spearman-threshold-assessment.md`) found that no observable structural change in the allocation rankings occurs at or near ρ = 0.85. The one clear empirical breakpoint is the band-order overturn at ρ ≈ 0.929 (TSAC = 3.0%).

The 0.85 threshold is being replaced by a multi-criterion approach (Option D) that will use concrete structural conditions rather than a single arbitrary Spearman cut-off. See `small-fixes.md` item 2 for the pending implementation.

## Date

Deprecated: 2026-04-18

## Replacement

Figures will be regenerated on a new branch implementing Option D, using the band-order overturn threshold and other structural criteria as reference lines.
