# Change Log

## v4.3.0 — Party master consolidation (2026-04-25)

### Data loader: consolidated override table (peer review §2.3)

- Created `config/party_master.csv` as the single auditable source of truth for all name concordance and data overrides (60 entries covering name mappings, income groups, regions, LDC/SIDS flags, EU membership, and land area).
- Eliminated `LAND_AREA_NAME_MAP` Python dict (26 entries) — now handled via `wb_land_area_name` column in `party_master.csv`.
- Eliminated ~50 lines of `df.loc` manual patches for income groups, regions, LDC/SIDS flags, and land area — all replaced by `COALESCE(pm.income_group_override, ...)`, `COALESCE(NULLIF(pm.region_override, ''), ...)` etc. in the DuckDB SQL query.
- Added land area for Republic of Korea, Slovakia, United Kingdom, and Netherlands via `wb_land_area_name` mapping; Monaco, Cook Islands, Niue, and State of Palestine via `land_area_km2_override`.
- Each override row in `party_master.csv` includes a `reason` column for auditability.
- All 138 tests pass identically (same `base_data` DataFrame output).

### Config loading: robust path

- `load_band_config()` now uses `Path(__file__)`-relative path for `un_scale_bands.yaml`.

### Small-fixes.md audit

- Marked items 2, 3, 4, 6, 7, 8 as resolved/moot.
- Items 1 (isolated TSAC sweep) and 5 (TSAC overturn metadata) remain open.

---

## v4.2.2 — Small fixes (2026-04-25)

### Data loader: land area for high-income CBD parties
- Added 4 name mappings to `LAND_AREA_NAME_MAP` so the World Bank land-area CSV JOIN resolves correctly for countries whose CBD names differ from WB names:
  - `"Republic of Korea"` → `"Korea, Rep."`
  - `"Slovakia"` → `"Slovak Republic"`
  - `"United Kingdom of Great Britain and Northern Ireland"` → `"United Kingdom"`
  - `"Netherlands (Kingdom of the)"` → `"Netherlands"`
- Land area now flows from the authoritative World Bank source (97,600 / 48,080 / 241,930 / 33,670 km²) instead of being zero.
- No hard-coded manual patches needed; removed the previously added patches for these 4 countries.

### Config loading: robust path for `load_band_config()`
- Replaced CWD-dependent `os.path.join("config", "un_scale_bands.yaml")` with `Path(__file__).resolve().parent.parent.parent / "config" / "un_scale_bands.yaml"`.
- Band config now loads correctly regardless of working directory.

### Small-fixes.md audit
- Marked items 2 (Spearman threshold), 3 (`_spearman_by_party` self-filtering), 4 (Gini-optimal → Gini-minimum rename), and 7 (`use_container_width` deprecation) as resolved or moot.
- Marked items 6 (land area) and 8 (config path) as resolved.
- Items 1 (isolated TSAC sweep) and 5 (TSAC overturn metadata) remain open.

---

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

### Bug fix: LDC/SIDS tabs counted ineligible parties
- Fixed LDC Share and SIDS Share tabs showing country counts that summed to 196 (all CBD Parties) instead of the correct eligible total.
- The "Other Countries" row in both tabs used `is_cbd_party` alone instead of `is_cbd_party & eligible`, so excluded high-income parties were still counted.
- Updated `test_ldc_sids_total_sum` to verify both `exclude_hi=False` (sums to 196) and `exclude_hi=True` (sums to 142).
- Updated `test_sids_filtering_logic` to use the eligible mask.

### Scenario table and figure regeneration for Option D
- Updated `band-analysis/break-points/analysis.py`: replaced `even` scenario (TSAC=5%) with `gini_minimum` (TSAC=2.5%) and added `band_order_overturn` (TSAC=3.0%); replaced deprecated 0.85 threshold with safety floor 0.80; updated visualization labels.
- Regenerated scenario CSVs: `gini_minimum.csv`, `band_order_overturn.csv` (replacing `even.csv`).
- Updated `scripts/rank_panels_scenarios.py` and `scripts/rank_change_scenarios.py` with new scenario names and labels.
- Regenerated Word table documents in `model-tables/`.

### Git workflow
- Tagged main as `v3.final` (pre-Option D state).
- Merged `optiond` branch with `--no-ff` to preserve branch history.
- Tagged main as `v4.0`.

---

## v4.1 — Balance-point ranking tables, IPLC developed-country tables, DuckDB fix (2026-04-19)

### Balance-point ranking tables
- Added stewardship pool tables (E1, E2) by balance point and fund size in `model-tables/`.
- Added band-order preservation ranking tables (iusaf-band-order-preservation.docx, iusaf-breakpoint-summary.docx).
- Fixed DuckDB `StringDtype` incompatibility in `data_loader.py` that caused type errors when reading parquet columns.

### IPLC developed-country allocation tables
- Created `iplc-developed/` directory with specification, integration options analysis, and validation tests.
- Implemented `scripts/generate_iplc_developed_tables.py` for two scenarios:
  - **Option 1 (Raw Equality):** 9 developed countries' allocations under equality mode, filtered and tabulated.
  - **Option 2 (Banded IUSAF):** 9 developed countries added to IUSAF bands (Band 4: Denmark, Finland, NZ, Norway, Sweden; Band 5: Australia, Canada, Japan, Russia), with `exclude_hi` overridden only for these 9.
- Generated CSV and DOCX outputs for all 4 fund volumes ($50M, $200M, $500M, $1B) plus summary tables:
  - Per-fund-volume tables with UN Share, allocation, IPLC/State split.
  - Summary across all fund volumes.
  - IPLC-only summary with Cali Fund percentage row.
- Implemented `scripts/generate_iplc_md.py` for markdown table generation.
- Integration options analysis (A–D) documented in `iplc-developed/iplc-integration-options.md`:
  - **Option A:** Pre-deduction (top-slice) — deduct dev-country IPLC from fund before allocation.
  - **Option B:** Post-deduction (claw-back) — same result as A, worse politics.
  - **Option C:** Separate window — no model change, depends on external funding.
  - **Option D (recommended):** Unified pool with State-component return — dev countries receive IPLC only; their State component is redistributed to the 142.

---

## v4.2 — Banded TSAC app, calibration harness, sensitivity reports (2026-04-23, `terrestrial` branch)

### Banded TSAC Streamlit app (`src/banded_app.py`)
- Created `banded_app.py` as a parallel variant of `app.py` with `tsac_mode="banded"` (geometric_base_2 preset).
- All 6 `calculate_allocations` call sites pass `tsac_mode="banded"`.
- TSAC and SOSAC sliders extended to 0–30% range.
- Preset buttons replaced with three balance-point candidates:
  - **Strict:** TSAC=12%, SOSAC=3% — maximum TSAC where IUSAF remains dominant for every Party.
  - **Gini-minimum:** TSAC=12%, SOSAC=3% — coincides with Strict under banding.
  - **Boundary:** TSAC=13%, SOSAC=3% — structural ceiling where China crosses into TSAC-dominant territory.
- Added `active_balance_point` session state to track which balance point is active, with auto-clear on slider change or preset switch.
- Added balance-point info panel (`st.success`) displaying hardcoded Gini and Spearman metadata per balance point.
- Added Spearman-based overlay warning: `st.sidebar.error` at ρ<0.85 (dominant overlay), `st.sidebar.warning` at ρ<0.95 (moderate overlay); suppressed in equality mode.
- Updated page title, heading, and introductory markdown to identify the banded variant.
- Updated TSAC Interpretation sidebar to reference banded land-area categories.
- Updated notes section with banding explanation.
- `app.py` is not modified — both apps run independently.

### Model changes (`src/cali_model/`)
- `calculator.py`: added `tsac_mode`, `tsac_band_lower_bounds`, `tsac_band_weights` parameters to `calculate_allocations`; added `assign_tsac_band()` and `banded_tsac_weights()` functions; defaults to `tsac_mode="linear"` preserving backward compatibility.
- `sensitivity_metrics.py`: added `spearman_vs_pure_iusaf` and `tsac_balance_exceeded` metrics.
- `data_loader.py`: minor DuckDB `StringDtype` fix.

### Calibration harness (`scripts/calibrate_banded_tsac.py`)
- 6 preset configurations + linear baseline, each running a 176-scenario two-way grid (TSAC × SOSAC).
- Acceptance criteria (geometric_base_2): **PASS** — Gini=0.0647, max TSAC/IUSAF ratio=1.40×, moderate overlay=122/176 scenarios.
- Full grid CSVs, integrity checks, comparison plots output to `sensitivity-reports/v4-sensitivity-reports/calibration/`.

### Sensitivity reports
- v4 executive summary, technical annex, scale invariance analysis, two-way grid analysis.
- Coarse (176-scenario) and fine (441-scenario) TSAC×SOSAC grids with Gini and Spearman heatmaps.
- All outputs in `sensitivity-reports/v4-sensitivity-reports/`.

### Break-point analysis figures
- Added `break_point_timeline.svg`, `decision_boundaries.svg`, `party_distribution_heatmap.svg` to `band-analysis/break-points/figures/`.

### TSAC band assignments
- Added `tsac_banded/tsac_band_assignments.csv` with per-country land-area, band assignment, and banded weight.

### Tests
- `tests/test_banded_tsac.py`: 215 tests for banded TSAC logic (band assignment, weight normalisation, allocation correctness, edge cases).
- `tests/test_calibration_harness.py`: calibration harness validation.
- `tests/test_iplc_developed.py`: IPLC developed-country allocation tests (Option 1 and Option 2).
- `tests/test_v4_sensitivity.py`: v4 sensitivity framework validation.
- `tests/test_sensitivity_modules.py`: extended with Spearman and balance metrics tests.

### Git workflow
- Branch `terrestrial` parked at commit `e5b5c57` with full documentation.
- Branches `iplc` (merged into main) and `optiond` (merged into main as v4.0) deleted.
- `app.py` unchanged on all branches.
- `.gitignore` updated to exclude `banded_tsac_spec.html`.

---

## v4.2.1 — Main-branch maintenance (2026-04-24)

### Bug fix: DuckDB StringDtype incompatibility
- Fixed `data_loader.py` line 64: `select_dtypes(include=["string", "str"])` → `select_dtypes(include=["object"])`.
- The original commit `aa3038b` introduced the incompatible form; pandas 2.3+ rejects numpy string dtypes.
- Fix was previously only on the `terrestrial` branch; now applied to `main`.

### IPLC developed-country structural validation
- Added `iplc-developed/test_structural_validation.py`: 40 self-contained tests verifying 8 invariants across Option 1 (equality) and Option 2 (banded IUSAF) for 9 developed countries:
  1. IPLC + State = Total allocation
  2. IPLC = 50% of total
  3. Fund conservation (eligible sum = fund size)
  4. Scale invariance across fund sizes
  5. Band assignments (Band 4: Denmark, Finland, NZ, Norway, Sweden; Band 5: Australia, Canada, Japan, Russia)
  6. No non-SIDS HI leakage in Option 2 (HI SIDS correctly remain eligible under `exclude_except_sids` mode)
  7. Option 1 total > Option 2 total (equality produces larger pool for this mixed-income group)
  8. Cali Fund % constant across fund sizes
- Added `iplc-developed/validation_analysis.md` explaining why Option 1 and Option 2 IPLC pools are close (2.30% vs 2.11%): Band 4 countries gain relative to equality, Band 5 countries lose; the gains and losses partially cancel within the mixed-income 9-country group.
- Tests are self-contained (use calculator directly) and run on `main` without requiring the `terrestrial`-branch generation scripts.
