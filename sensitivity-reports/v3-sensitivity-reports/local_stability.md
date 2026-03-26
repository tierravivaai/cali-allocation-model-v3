# Local Stability Narrative

## Mechanical validity
Local checks are interpreted only after core conservation and non-negativity diagnostics pass.

## Relationship to pure IUSAF
The selected scenario departs materially from the pure IUSAF baseline (`Spearman=0.8520`, `Top20 turnover=90.0%`). This reflects the intended effect of the stewardship overlay rather than a mechanical error. Overlay classification: **dominant overlay**.

## Stability of the blended specification
Within a narrow neighborhood around the selected blended baseline, results are **moderately sensitive** (`local min Spearman=0.9892`, `local max Top20 turnover=10.0%`). Small changes in TSAC/SOSAC may therefore produce bounded, visible, or large shifts depending on this local stability result.

## Distributional implications
Neighbor scenarios show how small parameter adjustments re-rank countries and shift shares.

## Caveats
Local stability is neighborhood-specific and should be revisited if baseline settings or admissible parameter ranges change.

## Adjacent scenario checks
```csv
scenario_id,parameter_changed,new_value,spearman_vs_baseline,top20_turnover_vs_baseline,mean_abs_share_delta_vs_baseline,max_abs_share_delta_vs_baseline
local_tsac_beta_0.04,tsac_beta,0.04,0.9892160355413987,0.1,8.315134314292906e-05,0.0011774966753452009
local_tsac_beta_0.06,tsac_beta,0.06,0.9921414950019908,0.1,8.315134314292883e-05,0.0011774966753452
local_sosac_gamma_0.02,sosac_gamma,0.02,0.9983780045684109,0.0,9.79391552497709e-05,0.00020241764487288847
local_sosac_gamma_0.04,sosac_gamma,0.04,0.9951465873132297,0.0,9.793915524977087e-05,0.0002024176448728876
local_iplc_share_pct_60,iplc_share_pct,60.0,1.0,0.0,0.0,0.0
local_floor_pct_0.05,floor_pct,0.05,1.0,0.0,0.0,0.0
local_ceiling_pct_1.0,ceiling_pct,1.0,1.0,0.0,0.0,0.0
```