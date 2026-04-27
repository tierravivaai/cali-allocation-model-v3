# Small Fixes and Follow-Ups

## Resolved (v4.0+)

2. ~~**Ground the Spearman threshold**~~ — **Resolved in v4.0.** Option D (band-order preservation + Spearman safety floor 0.80) was adopted. The arbitrary 0.85 threshold is replaced. See `optiond-threshold-revision-rationale.md`.

3. ~~**Make `_spearman_by_party()` self-filtering**~~ — **Resolved in v4.0.** `_eligible()` filter is now used throughout `sensitivity_metrics.py`. All callers of `_spearman_by_party` pass through filtered data.

4. ~~**Rename "Gini-optimal" → "Gini-minimum" in code and UI**~~ — **Resolved in v4.0.** All code, scenarios, and UI labels now use `gini_minimum`. No `gini_optimal` occurrences remain in `src/`.

7. ~~**Resolve `use_container_width` deprecation in Streamlit app**~~ — **Moot.** The app uses `st.plotly_chart(use_container_width=True)` which is not deprecated. No `st.pyplot` usage exists.

## Priority: High

1. **Generate isolated-TSAC sweep (SOSAC = 0%)** — A dedicated sweep with SOSAC = 0% is needed to verify provisional threshold values in setup (a) of the component rationale. Current values (order overturn ~2.95%, component overturn ~9.2%) are from ad hoc runs and require confirmation. See `docs/component-rationale.md` "Sensitivity Analysis Setups" and `docs/spearman-threshold-assessment.md`.

## Priority: Medium

5. **Reconcile TSAC overturn scenario metadata** — The `tsac_overturn.csv` was regenerated with SOSAC = 3%, giving TSAC = 1.80% (China component overturn). The rationale previously cited TSAC ~9.2% from an isolated-TSAC analysis. The scenario description in `band-analysis/break-points/readme.md` should be updated to reflect the current setup.

## Priority: Low

6. ~~**Add land area for 4 high-income parties**~~ — **Resolved via `config/party_master.csv`.** A consolidated override table now handles all name concordance and data patches. Republic of Korea, Slovakia, United Kingdom, and Netherlands get land area from the World Bank via `wb_land_area_name` mappings. Monaco, Cook Islands, Niue, and State of Palestine get manual values via `land_area_km2_override`.

8. ~~**Fix relative path in `load_band_config()`**~~ — **Resolved.** Changed from `os.path.join("config", ...)` (CWD-dependent) to `Path(__file__).resolve().parent.parent.parent / "config" / "un_scale_bands.yaml"` (robust, `__file__`-relative).

9. ~~**Consolidate manual overrides into auditable CSV (peer review §2.3)**~~ — **Resolved in v4.3.0.** Created `config/party_master.csv` as the single source of truth for all name concordance and data overrides. `data_loader.py` now uses DuckDB SQL JOINs against this table instead of ~50 lines of `df.loc` patches and the `LAND_AREA_NAME_MAP` Python dict. All 138 tests pass identically.

## Deferred

10. **Merge `manual_name_map.csv` into `party_master.csv`** — The UN Scale and CBD budget table name resolution (currently `data-raw/manual_name_map.csv`, ~40 entries mapping raw names to canonical CBD party names) could be consolidated into `party_master.csv` by populating the `un_scale_name` column and adding a `cbd_budget_name` column. This would eliminate the last separate concordance file and make the party master the single point of truth for all name mapping. The subtlety is that `manual_name_map.csv` is many-to-one (e.g. "Slovak Republic" and "Slovakia" both map to "Slovakia"), which means either multiple rows per canonical party (~100 rows total) or a parsed alias column. Recommend option 1 (multiple rows) for SQL JOIN simplicity. Not blocking; current dual-file approach works.
