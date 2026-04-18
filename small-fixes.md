# Small Fixes and Follow-Ups

## Priority: High

1. **Generate isolated-TSAC sweep (SOSAC = 0%)** — A dedicated sweep with SOSAC = 0% is needed to verify provisional threshold values in setup (a) of the component rationale. Current values (order overturn ~2.95%, component overturn ~9.2%) are from ad hoc runs and require confirmation. See `docs/component-rationale.md` "Sensitivity Analysis Setups" and `docs/spearman-threshold-assessment.md`.

2. **Ground the Spearman threshold** — The 0.85 threshold is a design parameter, not an analytical finding. Decide which option to adopt (band-order threshold ~0.93, retain 0.85 as design choice, align with overlay classification at 0.90, or multi-criterion). See `docs/spearman-threshold-assessment.md` Section 8.

## Priority: Medium

3. **Make `_spearman_by_party()` self-filtering** — The function in `sensitivity_metrics.py` does not filter to eligible parties internally. All current callers pass pre-filtered dataframes, so results are correct in practice. However, a future caller passing unfiltered data would get inflated values (0.945 vs 0.852 at TSAC=5%). Add internal `_eligible()` filter or docstring warning.

4. **Rename "Gini-optimal" → "Gini-minimum" in code and UI** — The rationale document uses "Gini-minimum" throughout, but the codebase still uses "Gini-optimal" in `balance_analysis.py`, `sensitivity_scenarios.py`, and `app.py`. The peer review flagged that "optimal" carries normative weight in a policy context.

5. **Reconcile TSAC overturn scenario metadata** — The `tsac_overturn.csv` was regenerated with SOSAC = 3%, giving TSAC = 1.80% (China component overturn). The rationale previously cited TSAC ~9.2% from an isolated-TSAC analysis. The scenario description in `band-analysis/break-points/readme.md` should be updated to reflect the current setup.

## Priority: Low

6. **Add land area for 4 high-income parties** — Republic of Korea, Netherlands, Slovakia, and United Kingdom have zero land area in the base dataset. All are excluded by default, but completeness matters for credibility. Peer review flagged as MEDIUM priority.

7. **Resolve `use_container_width` deprecation in Streamlit app** — The app uses `st.pyplot(use_container_width=True)` which is deprecated. Should migrate to `st.pyplot(use_container_width=True)` replacement or Plotly native resizing.

8. **Fix relative path in `load_band_config()`** — Uses `os.path.join("config", "un_scale_bands.yaml")` which assumes CWD is repo root. Should use `__file__`-relative paths for robustness.
