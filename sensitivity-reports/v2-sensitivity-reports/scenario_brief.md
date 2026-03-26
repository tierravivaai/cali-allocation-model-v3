# Scenario Brief: balanced_baseline

## Purpose
This note summarises one sensitivity scenario with explicit separation between policy-overlay departure and local robustness.

## Scenario Definition
- Fund size: $1,000,000,000
- UN scale mode: `band_inversion`
- Exclude high income except SIDS: `True`
- TSAC: `5.00%` | SOSAC: `3.00%`
- IPLC share: `50%`
- Floor: `0.00%` | Ceiling: `off`

## Mechanical validity
The scenario is computed using the shared calculator and should be interpreted only if invariants pass (conservation, normalization, and non-negativity).

## Relationship to pure IUSAF
The selected scenario departs materially from the pure IUSAF baseline (`Spearman=0.8112`, `Top20 turnover=80.0%`). This reflects the intended effect of the stewardship overlay rather than a mechanical error. Overlay classification: **dominant overlay**.

## Stability of the blended specification
Within a narrow neighborhood around the selected blended baseline, results are **moderately sensitive** (`local min Spearman=0.9885`, `local max Top20 turnover=0.0%`). Small changes in TSAC/SOSAC may therefore produce bounded, visible, or large shifts depending on this local stability result.

## Distributional implications
SIDS total = `310.56m`; LDC total = `329.12m`; top-20 share = `17.59%`.

Largest gains versus pure IUSAF comparator:
- China: +6.66m
- Brazil: +5.89m
- India: +1.88m
- Argentina: +1.61m
- Kazakhstan: +1.58m

Largest losses versus pure IUSAF comparator:
- Gambia: -0.68m
- State of Palestine: -0.68m
- Burundi: -0.66m
- Lesotho: -0.66m
- Bhutan: -0.65m

## Caveats
Departure from pure IUSAF is expected when stewardship overlays are active and should not be treated as instability by itself.

## Bottom Line
Overlay assessment is **dominant overlay** while local blended stability is **moderately sensitive**.
