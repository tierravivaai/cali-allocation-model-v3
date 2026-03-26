# Comparative Sensitivity Report

## Introduction
This report compares baseline, equality, pure IUSAF, and stress scenarios while separating policy-overlay departure from local robustness.

## Baseline Scenario
Baseline is `balanced_baseline` with fund size `$1,000,000,000`, TSAC `5.00%`, SOSAC `3.00%`, and UN mode `band_inversion`.

## Benchmarks for Comparison
Comparison includes pure equality, pure IUSAF (raw and band), balanced variants, and constraint/eligibility alternatives.

## Mechanical validity
Several scenarios are mechanically valid and reproducible under the shared calculator and diagnostics framework.

## Relationship to pure IUSAF
Many scenarios depart materially from pure IUSAF where stewardship overlays are active (`departure_from_pure_iusaf_flag` count: `11/13`). Overlay classes observed: `{'dominant overlay': 10, 'minimal overlay': 2, 'strong overlay': 1}`.

Most policy-departed scenarios:
- terrestrial_max: overlay `dominant overlay`, Spearman vs pure IUSAF `0.4040`, local stability `moderately sensitive`
- exclude_hi_off_compare: overlay `dominant overlay`, Spearman vs pure IUSAF `0.8082`, local stability `unstable`
- balanced_baseline: overlay `dominant overlay`, Spearman vs pure IUSAF `0.8112`, local stability `moderately sensitive`

## Stability of the blended specification
The key question is whether blended settings remain locally stable under modest nearby parameter changes. Local instability flags appear in `5/13` scenarios. Local stability classes observed: `{'moderately sensitive': 7, 'unstable': 5, 'sensitive': 1}`.

## Distributional implications
SIDS totals range from `245.87m` to `545.27m`; LDC totals range from `252.83m` to `464.30m`.

## Caveats
Departure from pure IUSAF should be read as overlay strength, not instability. Stability conclusions should rely on local neighborhood tests.

## Conclusions
Reported warnings now distinguish material policy departure from true local sensitivity, supporting more precise review of blended-scenario robustness.
