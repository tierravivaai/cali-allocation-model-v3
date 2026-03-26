# Sweep Summary: one-way sweep

## Purpose of Sweep
This summary reviews controlled parameter variation and distinguishes policy-overlay departure from local sensitivity.

## Sweep Design
The sweep includes `16` scenarios and tracks `spearman_vs_pure_iusaf` with trigger-specific warning logic.

## Mechanical validity
Interpretation assumes conservation and non-negativity checks are satisfied for the included runs.

## Relationship to pure IUSAF
`spearman_vs_pure_iusaf` ranges from `0.4460` to `0.9771`. This captures overlay departure strength, not local instability.

## Stability of the blended specification
Local stability is evaluated separately where local-neighborhood diagnostics are available.

## Distributional implications
Largest deviation in this sweep appears at `tsac_beta_sweep_0.15` (`spearman_vs_pure_iusaf=0.4460`).

## Caveats
Trigger attribution below reports the actual threshold source and should not be interpreted as a single generic structural-break mechanism.

### Thresholds / Tipping Points
- departure-from-pure-IUSAF threshold: first triggered at `tsac_beta_sweep_0.0`. `spearman_vs_pure_iusaf=0.9771`
- equality-distance threshold: first triggered at `tsac_beta_sweep_0.15` (`pct_below_equality=60.6%`).

## Bottom Line
The sweep indicates where policy overlay departs from pure IUSAF and, separately, where local stability warnings emerge.
