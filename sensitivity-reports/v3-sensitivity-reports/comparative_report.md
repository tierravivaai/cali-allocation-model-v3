# Comparative Sensitivity Report

## Introduction
This report compares baseline, equality, pure IUSAF, and stress scenarios while separating policy-overlay departure from local robustness.

*In the codebase, the TSAC weight and SOSAC weight are stored under the internal parameter names `tsac_beta` and `sosac_gamma` respectively, following the conventional Greek-letter notation used in the original formula specification. Readers reviewing the source code will find these names throughout; they correspond exactly to the TSAC weight and SOSAC weight referred to in this document.*

## Baseline Scenario
Baseline is `gini_optimal_point` with fund size `$1,000,000,000`, TSAC `5.00%`, SOSAC `3.00%`, and UN mode `band_inversion`.

## Benchmarks for Comparison
Comparison includes pure equality, pure IUSAF (raw and band), gini-optimal variants, and constraint/eligibility alternatives.

## Mechanical validity
Several scenarios are mechanically valid and reproducible under the shared calculator and diagnostics framework.

## Relationship to pure IUSAF
Many scenarios depart materially from pure IUSAF where stewardship overlays are active (`departure_from_pure_iusaf_flag` count: `12/14`). Overlay classes observed: `{'dominant overlay': 9, 'strong overlay': 3, 'minimal overlay': 2}`.

Most policy-departed scenarios:
- pure_equality: overlay `dominant overlay`, Spearman vs pure IUSAF `0.0000`, local stability `stable`
- terrestrial_max: overlay `dominant overlay`, Spearman vs pure IUSAF `0.3919`, local stability `sensitive`
- exclude_hi_off_compare: overlay `dominant overlay`, Spearman vs pure IUSAF `0.8357`, local stability `unstable`

## Stability of the blended specification
The key question is whether blended settings remain locally stable under modest nearby parameter changes. Local instability flags appear in `5/14` scenarios. Local stability classes observed: `{'moderately sensitive': 5, 'unstable': 4, 'stable': 3, 'sensitive': 2}`.

## Distributional implications
SIDS totals range from `246.16m` to `545.27m`; LDC totals range from `254.50m` to `464.30m`.

## Caveats
Departure from pure IUSAF should be read as overlay strength, not instability. Stability conclusions should rely on local neighborhood tests.

## Conclusions
Reported warnings now distinguish material policy departure from true local sensitivity, supporting more precise review of blended-scenario robustness.
