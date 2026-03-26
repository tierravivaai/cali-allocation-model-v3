# Change Log

## Since initiation of the v3 repo (2026-03-20)

### Allocation logic and configuration
- Introduced the 6-band UN scale configuration in `config/un_scale_bands.yaml`.
- Split the former top band so that:
  - Band 5 = `1.0% - 10.0%` with weight `0.75`
  - Band 6 = `> 10.0%` with weight `0.40`
- This separates China from Brazil, India, and Mexico in the banded IUSAF path.

### Main app updates
- Updated `app.py` sidebar band explanation from 5 bands to 6 bands.
- Renamed the preset button from `5. Balanced` to `5. Stewardship-Forward`.
- Updated preset help text to clarify that the 5% TSAC / 3% SOSAC setting is exploratory rather than a validated balance point.

### Sensitivity framework updates
- Renamed the sensitivity baseline from `balanced_baseline` to `stewardship_forward_baseline`.
- Added named balance-point scenarios:
  - `tsac_strict_balance`
  - `tsac_modified_balance`
- Updated named balance-point scenario values to match confirmed sweep results:
  - `tsac_strict_balance` = `1.5%`
  - `tsac_modified_balance` = `3.5%`
- Removed the legacy duplicate scenario `balanced_5_3` from the scenario library.
- Added fine-grained sweep ranges for TSAC and SOSAC at 0.5 percentage point intervals.
- Added a new `Balance Point Analysis` workflow in `sensitivity.py`.
- Replaced raw internal parameter names in key `sensitivity.py` reader-facing controls with clearer labels such as `TSAC weight` and `SOSAC weight`, while preserving internal `tsac_beta` / `sosac_gamma` naming in code.
- Fixed World Bank land-area name matching so CBD/UN party names align correctly with the FAOSTAT/World Bank land-area source.
- Switched land-area extraction to use the latest available non-null year automatically rather than relying on a fixed year assumption.

### New diagnostics and analysis
- Added Gini coefficient reporting for allocation distributions.
- Added per-Party component ratio diagnostics comparing TSAC and SOSAC against IUSAF.
- Added Band 1 change versus pure IUSAF diagnostics.
- Added `logic/balance_analysis.py` for:
  - fine sweeps
  - balance-point identification
  - balance-point markdown summary generation
- Corrected pure-SOSAC ratio handling so SOSAC/IUSAF ratios are computed even when TSAC is zero.
- Updated SOSAC balance-point detection and summary rendering so above-range cases are explicitly reported as lying beyond the scanned 0–10% sweep window, with sweep-limit ratio context and analytical estimate.
- Added an inline guard comment in `logic/sensitivity_metrics.py` to preserve correct pure-SOSAC ratio behaviour.
- Added module-level naming convention comments explaining that `tsac_beta` and `sosac_gamma` are the internal code names for the user-facing TSAC and SOSAC weights.
- Expanded effective TSAC land-pool coverage so all `142` eligible parties now have matched land-area data in the processed results.

### Reporting and exports
- Extended generated sensitivity outputs with:
  - `balance_point_summary.md`
  - `balance_points.csv`
  - `tsac_fine_sweep.csv`
  - `sosac_fine_sweep.csv`
  - `current_component_ratios.csv`
  - `one_way_sweep.csv`
- Generated a new report set in `sensitivity-reports/v3-sensitivity-reports/`.
- Added explanatory wording in reports clarifying that internal code parameters `tsac_beta` and `sosac_gamma` correspond to the user-facing TSAC and SOSAC weights.
- Refined the V3 balance-point outputs so SOSAC is now reported as above the scanned range rather than as an identified in-range point, with an analytical estimate of approximately `17.4%`.
- Regenerated V3 sensitivity outputs after the land-area matching fix so balance-point and scenario metrics reflect the corrected land-area denominator.
- Renamed the TSAC=5% / SOSAC=3% reference scenario from `practical_balance_point` to `gini_optimal_point`, and renamed related floor/ceiling variants to the `gini_optimal_*` pattern.
- Renamed the corresponding balance-point label from `practical` to `gini_optimal` in balance-point analysis outputs and summaries.
- Corrected sweep-summary trigger attribution so Spearman and top-20 turnover threshold crossings are reported separately, rather than always being attributed to the Spearman trigger.
- Added `integrity_checks.csv` as a sensitivity-app export for reviewer-facing invariant checks.
- Updated the Gini-optimal balance-point note to explain that the Spearman constraint binds: the unconstrained Gini minimum occurs at `5.5%`, but the constrained optimum is `5.0%` because Spearman must remain above `0.85`.
- Regenerated the V3 sensitivity report pack so exported outputs now include the reviewer-facing `integrity_checks.csv` with one row per scenario (`14` rows total) and `all_checks_pass=PASS` for all standard library scenarios.

### Testing and quality
- Updated band inversion tests for the 6-band structure and China Band 6 expectation.
- Added dedicated tests for balance analysis and component ratio logic.
- Added coverage reporting via `pytest-cov` and `pytest.ini`.
- Fixed sensitivity warnings caused by constant-distribution Spearman calculations.
- Restored the local virtual environment to match `requirements.txt` and confirmed the full suite passes.
- Updated sensitivity, balance-analysis, UI, and reporting tests for the `gini_optimal` / `gini_optimal_point` rename.
- Added a reporting test to verify sweep summaries attribute Spearman and turnover triggers separately.
- Added integrity-check export tests covering schema completeness, valid-scenario pass behaviour, and deliberate non-conservation failure detection.

### Current validated status
- Full automated test suite passing (`135` tests).
- V3 sensitivity markdown and CSV outputs regenerated successfully, including `integrity_checks.csv`.
