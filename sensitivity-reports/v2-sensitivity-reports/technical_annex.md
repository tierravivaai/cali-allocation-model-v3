# Technical Annex

## Data and Eligibility Rules
Data are loaded from the same repository sources used by the main app. Eligibility follows CBD Party status, with optional high-income exclusion preserving SIDS where configured.

## Formula Specification
Final Share = (1 - beta - gamma) * IUSAF + beta * TSAC + gamma * SOSAC.

## Raw vs Band Inversion
Raw inversion uses reciprocal UN shares. Band inversion applies configured UN-share bands and weights before normalization.

## TSAC and SOSAC Treatment
TSAC is proportional to land area among eligible countries. SOSAC is equal-share across eligible SIDS. If no SIDS are eligible and SOSAC > 0, SOSAC is reallocated to IUSAF.

## IPLC Split
Total allocations are split into State and IPLC components by configured IPLC share.

## Floor and Ceiling Handling
Floor and ceiling constraints are applied on normalized shares with iterative reconciliation to preserve feasibility and conservation.

## No-SIDS Fallback
When no eligible SIDS exist, SOSAC weight is reassigned to IUSAF to preserve conservation and avoid invalid shares.

## Integrity Tests
Diagnostics include conservation of shares and money, component consistency, non-negativity, and mode-specific checks.

## Sensitivity Ranges
Fund size anchors: 50m, 200m, 500m, 1bn. TSAC: 0-15%. SOSAC: 0-10%. IPLC: 50/60/70/80. Floor: off, 0.05%, 0.10%, 0.25%. Ceiling: off, 1%, 2%, 5%.

## Departure and Local-Stability Criteria
Departure from pure IUSAF is flagged when Spearman vs pure IUSAF < 0.95 or top-20 turnover > 20%.
Local blended instability is flagged when local min Spearman vs baseline < 0.94, local max top-20 turnover > 20%, or local max absolute share delta > 0.5 percentage points.

## Exported Outputs
App exports scenario-level metrics, country-level results, country deltas, group summaries, and markdown reports for scenario briefs, sweep summaries, comparative analysis, and this annex.
