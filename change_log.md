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
- Renamed the TSAC=5% / SOSAC=3% reference scenario from `practical_balance_point` to `gini_optimal_point`, and renamed related floor/ceiling variants to the `gini_optimal_*` pattern. (Further renamed to `gini_minimum_point` in v4.0 — see below.)
- Renamed the corresponding balance-point label from `practical` to `gini_optimal` in balance-point analysis outputs and summaries. (Further renamed to `gini_minimum` in v4.0 — see below.)
- Corrected sweep-summary trigger attribution so Spearman and top-20 turnover threshold crossings are reported separately, rather than always being attributed to the Spearman trigger.
- Added `integrity_checks.csv` as a sensitivity-app export for reviewer-facing invariant checks.
- Regenerated the V3 sensitivity report pack so exported outputs now include the reviewer-facing `integrity_checks.csv` with one row per scenario (`14` rows total) and `all_checks_pass=PASS` for all standard library scenarios.

### Testing and quality
- Updated band inversion tests for the 6-band structure and China Band 6 expectation.
- Added dedicated tests for balance analysis and component ratio logic.
- Added coverage reporting via `pytest-cov` and `pytest.ini`.
- Fixed sensitivity warnings caused by constant-distribution Spearman calculations.
- Restored the local virtual environment to match `requirements.txt` and confirmed the full suite passes.
- Updated sensitivity, balance-analysis, UI, and reporting tests for the `gini_optimal` / `gini_optimal_point` rename. (Further renamed to `gini_minimum` in v4.0 — see below.)
- Added a reporting test to verify sweep summaries attribute Spearman and turnover triggers separately.
- Added integrity-check export tests covering schema completeness, valid-scenario pass behaviour, and deliberate non-conservation failure detection.

### Infrastructure and tooling
- Fixed Streamlit server connection issue causing CSV download errors
- Added regression tests in `tests/test_app_dataframes.py` to verify:
  - App initializes with valid dataframes
  - Streamlit renders dataframe elements needed for CSV export
  - App state remains consistent after parameter changes
- Updated `.gitignore` to exclude `sensitivity-reports/v2-sensitivity-reports`

### Current validated status (v3)
- Full automated test suite passing (`138` tests, including 3 new app dataframe tests).
- V3 sensitivity markdown and CSV outputs regenerated successfully, including `integrity_checks.csv`.

---

## v4.0 — Option D threshold revision (2026-04-18)

### Methodological change: band-order preservation replaces Spearman 0.85 threshold
- Assessed the hard-coded Spearman ρ=0.85 threshold and found no empirical structural break at that value; the only clear breakpoint is band-order overturn at ρ≈0.93 (TSAC=3.0%).
- Created `docs/spearman-threshold-assessment.md` documenting the assessment, four grounding options, and resolution.
- Deprecated `break_point_timeline.svg` and `decision_boundaries.svg` to `deprecated/spearman-0.85-threshold/` with explanatory README.
- Implemented Option D (multi-criterion approach): replaced the arbitrary Spearman constraint with a structural band-order preservation constraint plus a Spearman safety floor.
- Added `_band_mean()`, `_band_order_preserved()`, and `_min_gini_preserving_band_order()` in `balance_analysis.py` — the Gini-minimum now requires Band 5 mean allocation > Band 6 mean allocation, with a Spearman safety floor of 0.80.
- Added band-order columns to sweep output: `band_order_preserved`, `band6_mean_alloc_m`, `band5_mean_alloc_m`.
- Made `_spearman_by_party()` self-filtering with internal `_eligible()` calls so it is robust to unfiltered input (previously inflated ρ from 0.852 to 0.945 by including ineligible parties).

### Rename: gini_optimal → gini_minimum
- Renamed `gini_optimal` → `gini_minimum` across all code, UI, tests, and documentation to reflect that the constraint identifies the minimum Gini subject to structural constraints, not an unconstrained optimum.
- Renamed `gini_optimal_point` → `gini_minimum_point` in scenario definitions, balance-point labels, and reporting.

### Default baseline change
- Updated DEFAULT_BASELINE TSAC from 5% to 2.5% in `sensitivity_scenarios.py`.
- Updated preset button in `app.py` from TSAC=5% to TSAC=2.5%.
- Updated Combined Stewardship Position: 94.5% IUSAF, 2.5% TSAC, 3% SOSAC.

### Figure and reference line updates
- Replaced Spearman 0.85 horizontal reference line in `update_figures.py` with band-order overturn vertical line at TSAC=3%.
- Updated `sensitivity.py` reference line from 0.85 to 0.80 (Spearman safety floor).
- Updated `band-analysis/break-points/readme.md` with deprecation note for 0.85 threshold.

### Verified results at Gini-minimum (TSAC=2.5%, SOSAC=3%)
- Spearman ρ = 0.945 (safety floor 0.80 does not bind; slack = 0.145).
- Band-order margin = 5.4% (Band 5 mean 5.44M > Band 6 mean 5.15M).
- Band-order overturn at TSAC = 3.0% (Band 6 mean 5.74M > Band 5 mean 5.70M).
- Gini = 0.0886.

### Documentation updates
- Updated `docs/component-rationale.md` with band-order preservation framing, revised ranking trajectory table, and updated threshold summary.
- Added `optiond-threshold-revision-rationale.md` at repo root as implementation specification.

### Testing and quality
- All 138 tests passing after updates for renamed parameters, new constraint logic, and changed baseline values.
- Updated test assertions: TSAC baseline 0.025 (was 0.05), Spearman floor 0.80 (was 0.85), preset slider 2.5 (was 5).

### Git workflow
- Tagged main as `v3.final` (pre-Option D state).
- Merged `optiond` branch with `--no-ff` to preserve branch history.
- Tagged main as `v4.0`.
