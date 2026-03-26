# Local Stability Narrative

## Mechanical validity
Local checks are interpreted only after core conservation and non-negativity diagnostics pass.

## Relationship to pure IUSAF
The selected scenario departs materially from the pure IUSAF baseline (`Spearman=0.8112`, `Top20 turnover=80.0%`). This reflects the intended effect of the stewardship overlay rather than a mechanical error. Overlay classification: **dominant overlay**.

## Stability of the blended specification
Within a narrow neighborhood around the selected blended baseline, results are **moderately sensitive** (`local min Spearman=0.9885`, `local max Top20 turnover=0.0%`). Small changes in TSAC/SOSAC may therefore produce bounded, visible, or large shifts depending on this local stability result.

## Distributional implications
Neighbor scenarios show how small parameter adjustments re-rank countries and shift shares.

## Caveats
Local stability is neighborhood-specific and should be revisited if baseline settings or admissible parameter ranges change.

## Adjacent scenario checks
```csv
scenario_id,parameter_changed,new_value,spearman_vs_baseline,top20_turnover_vs_baseline,mean_abs_share_delta_vs_baseline,max_abs_share_delta_vs_baseline
local_tsac_beta_0.04,tsac_beta,0.04,0.9885255282889537,0.0,9.077579690758953e-05,0.001356946472189563
local_tsac_beta_0.06,tsac_beta,0.06,0.9972875472425844,0.0,9.077579690758889e-05,0.001356946472189563
local_sosac_gamma_0.02,sosac_gamma,0.02,0.9975432808101304,0.0,9.802433432129936e-05,0.0002025248338351016
local_sosac_gamma_0.04,sosac_gamma,0.04,0.9948727515883781,0.0,9.802433432129955e-05,0.00020252483383509986
local_iplc_share_pct_60,iplc_share_pct,60.0,1.0,0.0,0.0,0.0
local_floor_pct_0.05,floor_pct,0.05,1.0,0.0,0.0,0.0
local_ceiling_pct_1.0,ceiling_pct,1.0,0.999998951911059,0.0,1.4854372446241866e-05,0.00091122130025581
```