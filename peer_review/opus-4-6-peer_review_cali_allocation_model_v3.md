---
output:
  word_document: default
  html_document: default
---
# Peer Review: Cali Fund Allocation Model v3

**Reviewer:** Independent technical review  
**Date:** 30 March 2026  
**Scope:** Architecture, mathematical correctness, sensitivity framework, documentation, and readiness for a critical technical and policy audience

---

## Executive Summary

This is a serious, well-constructed piece of policy-support modelling. The mathematical core is sound, the sensitivity framework is rigorous and unusually self-aware for a policy tool, and the documentation reads like the work of someone who expects hostile scrutiny and has prepared accordingly. The test suite (138 tests, all passing) is substantially more thorough than is typical for a tool of this kind.

The model is, in my assessment, broadly fit for presentation to a technical and policy audience. The recommendations below are offered in the spirit of hardening the work against the specific kinds of criticism it will face — not as indications of fundamental deficiency.

There are, however, several issues that range from important to critical, and I would recommend addressing at least the high-priority items before release.

---

## 1. Mathematical Correctness

### 1.1 Core Formula — Verified Correct

The three-component blending formula is correctly implemented:

```
Final Share = (1 - β - γ) × IUSAF + β × TSAC + γ × SOSAC
```

I verified against the calculator source (`calculator.py`, lines 207–211) that:

- IUSAF shares are normalised to sum to 1.0 across eligible parties
- TSAC shares are normalised to sum to 1.0 across eligible parties with land area > 0
- SOSAC shares are normalised to sum to 1.0 across eligible SIDS (equal share)
- The blended final share is re-normalised (line 217–219) — this is a belt-and-braces step that is mathematically unnecessary when components are individually normalised, but it is harmless and provides an extra safety net

**Confirmed via runtime:** On a $1bn fund with TSAC=5%, SOSAC=3%, final shares sum to exactly 1.0 and total allocation sums to exactly $1,000M.

### 1.2 Band Inversion — Verified Correct

The six-band structure correctly assigns per-party weights (not per-band weights), ensuring that a party's allocation is proportional to its band weight. The YAML configuration is consistent with the documentation. Band assignment logic uses half-open intervals `(min, max]`, which is a clean design.

**Monotonicity under pure IUSAF is confirmed:**

| Band | Mean allocation ($M) |
|------|---------------------|
| Band 1 | 8.525 |
| Band 2 | 7.389 |
| Band 3 | 6.252 |
| Band 4 | 5.399 |
| Band 5 | 4.263 |
| Band 6 | 2.273 |

This is strictly decreasing, as required.

### 1.3 Band Monotonicity Breaks Under Blending — Important Issue

**Under the gini-optimal point (TSAC=5%, SOSAC=3%), band-level monotonicity breaks:**

| Band | Mean allocation ($M) |
|------|---------------------|
| Band 1 | 8.413 |
| Band 2 | 7.203 |
| Band 3 | 6.115 |
| Band 4 | 5.692 |
| Band 5 | **6.750** |
| Band 6 | **8.093** |

Band 5 and Band 6 parties receive *more* on average than Band 3 and Band 4 parties. This is because TSAC (land-area-proportional) heavily benefits large-landmass parties in Bands 5 and 6 (Brazil: $9.26M, China: $8.09M).

**This is not a bug** — the model documentation correctly notes that TSAC is a separate adjustment. However, it is a finding that a sceptical audience *will* seize on: "Why does China receive more than most developing countries despite being placed in the lowest band?" The balance-point summary already acknowledges this for China specifically, but the broader band-level inversion is not prominently flagged.

**Recommendation (HIGH):** Add an explicit discussion in the technical note and AHTEG report about the loss of band-level monotonicity under blended scenarios. Frame it as a known and expected consequence of the stewardship overlay, not a flaw — but it must be addressed transparently before a sceptical reviewer discovers it independently.

### 1.4 SOSAC Fallback — Verified Correct

When no SIDS are eligible and γ > 0, the SOSAC weight is correctly reallocated to the IUSAF component (calculator.py, lines 201–204). The test `test_sosac_fallback_no_sids` confirms component amounts match the expected reallocation.

### 1.5 Floor/Ceiling Logic — Verified Correct

The iterative constraint algorithm in `_apply_floor_ceiling_shares` correctly handles the redistribution problem. It iterates until convergence, fixing parties at floor or ceiling and redistributing the remainder proportionally. Edge cases (infeasible floor, infeasible ceiling) are handled with fallback to equal shares. The test suite covers these cases well.

### 1.6 EU Handling — Verified Correct

The European Union has un_share=0.0, is correctly included as a CBD Party, and receives 0 allocation. It is excluded from land area calculations. EU Member States are handled individually with their own UN shares.

---

## 2. Architecture and Code Quality

### 2.1 Separation of Concerns — Good

The codebase follows a clean separation:

- `calculator.py` — pure calculation logic
- `data_loader.py` — data ingestion with DuckDB
- `sensitivity_metrics.py` — diagnostic computation
- `sensitivity_scenarios.py` — scenario definitions
- `balance_analysis.py` — fine-grained sweep logic
- `reporting.py` — narrative generation

Both Streamlit apps (`app.py` and `sensitivity.py`) correctly delegate to the shared logic layer, preventing logic drift between the main app and the sensitivity tool.

### 2.2 App.py Size — Moderate Concern

At 1,527 lines, `app.py` is a monolithic Streamlit file mixing UI layout, session state management, and some inline computation. While this is common in Streamlit projects, it creates maintenance risk. The negotiation dashboard section in particular (Plotly visualisations) could be extracted.

**Recommendation (LOW):** Consider extracting the negotiation dashboard tab into a separate module. This is cosmetic but would improve maintainability.

### 2.3 Data Loader Hardcoding — Moderate Concern

`data_loader.py` contains approximately 40 lines of hardcoded manual fixes for party names, income groups, and land areas (lines 162–211). While each fix is individually defensible — and this kind of concordance patching is normal in international data work — the pattern creates a maintenance burden and an audit risk.

**Recommendation (MEDIUM):** Move all manual overrides into a single CSV or YAML file (e.g., `config/manual_overrides.csv`) with columns like `party, field, value, reason`. This would make the override logic auditable and would allow a reviewer to inspect all manual interventions in one place without reading code.

### 2.4 Relative Path Dependency

`load_band_config()` uses `os.path.join("config", "un_scale_bands.yaml")` — a relative path that assumes the working directory is the repo root. This works under Streamlit's default behaviour but is fragile.

**Recommendation (LOW):** Use `__file__`-relative paths or a configuration constant for the project root.

### 2.5 Missing Land Area for 4 Parties

Four CBD parties have zero land area in the base dataset: Republic of Korea, Netherlands, Slovakia, and United Kingdom. All four are high-income and excluded from the eligible pool when `exclude_high_income=True`, so this does not affect the default allocation. However, if a user toggles off the high-income exclusion, these four parties would receive zero TSAC allocation despite having land area — a data gap rather than a logic error.

**Recommendation (MEDIUM):** Add land area values for these four countries (readily available from the same World Bank dataset). Even if they are excluded by default, completeness matters for credibility and for the `exclude_hi_off_compare` scenario in the sensitivity analysis.

---

## 3. Sensitivity Framework

### 3.1 Overall Design — Excellent

The sensitivity framework is unusually well-designed for a policy tool. The conceptual distinction between *overlay departure from pure IUSAF* and *local stability of the blended specification* is analytically precise and is exactly the right framing for a model that deliberately introduces stewardship adjustments. This distinction will be valuable in deflecting the predictable criticism that "the model is unstable" — the correct response is "the model intentionally departs from pure IUSAF; the question is whether it does so stably."

### 3.2 Structural Break Rules — Well Calibrated

The five structural break rules are sensible:

- Stewardship total > 20%
- Spearman vs pure IUSAF < 0.95
- Top-20 turnover vs pure IUSAF > 20%
- % below equality > 60%
- Median % of equality < 90%

These thresholds are conservative and defensible. The Spearman threshold of 0.95 is an appropriate choice for "modest departure"; the 0.85 threshold used for the gini-optimal constraint is a reasonable relaxation for "moderate but not dominant."

### 3.3 Balance Point Analysis — Thoughtful

The three balance points (strict, modified, gini-optimal) and the separate SOSAC analysis are well-conceived. The honest acknowledgement that the gini-optimal point does *not* satisfy the TSAC/IUSAF balance condition is commendable — this is the kind of transparency that builds credibility.

### 3.4 Gini-Optimal Point Framing — Needs Careful Handling

The gini-optimal point (TSAC=5%, SOSAC=3%) is described as the point that "minimises the Gini coefficient while keeping Spearman rank correlation vs pure IUSAF above 0.85." This is technically precise. However, a policy audience may hear "optimal" and interpret it as "recommended" or "best."

The balance point summary already contains a caveat, but the word "optimal" carries normative weight in a policy context.

**Recommendation (MEDIUM):** Consider whether the label "gini-optimal" is the right public-facing term. "Gini-minimising constrained point" is more precise. Alternatively, keep the label but ensure that every document that uses it includes the caveat that "optimal" refers to a mathematical property of the Gini distribution, not a policy endorsement. The current documentation does this internally, but the label will travel without the caveat.

### 3.5 Integrity Checks — Comprehensive

The `integrity_checks.csv` output covers conservation of shares, conservation of money, non-negativity, component consistency, IPLC split, band monotonicity, floor/ceiling binding, and SOSAC allocation. All 14 standard library scenarios pass all checks. This is exactly the kind of artefact a reviewer needs to see.

### 3.6 Coverage Gap: Two-Way Grid Sweep

The sensitivity plan calls for two-way grid sweeps (TSAC × SOSAC, floor × ceiling, etc.), but the generated reports in `v3-sensitivity-reports/` contain only one-way sweeps and fine sweeps. The code infrastructure for `two_way_grid` exists in `sensitivity_scenarios.py` but does not appear to be exercised in the generated outputs.

**Recommendation (MEDIUM):** Generate and include at least a TSAC × SOSAC heatmap in the sensitivity report pack. This is the single most informative two-dimensional diagnostic for the model — it shows how the two stewardship parameters interact, which a one-way sweep cannot reveal.

### 3.7 Scale Invariance Not Explicitly Tested

The sensitivity plan correctly identifies that "fund size changes must change monetary values only; share distribution should remain unchanged." This property (scale invariance of shares) is structurally guaranteed by the formula but is not explicitly tested in the test suite.

**Recommendation (LOW):** Add a simple parametric test that runs the same scenario at two different fund sizes and asserts that `final_share` vectors are identical.

---

## 4. Documentation Quality

### 4.1 Technical Note (CBD/AHEGF) — Strong

The CBD technical note is well-structured and reads like a genuine international policy document. The framing of Band 6, the explanation of why raw inversion fails, and the treatment of monotonicity requirements are all handled with appropriate care.

One gap: the note discusses monotonicity under pure IUSAF but does not explicitly address what happens to band-level ordering under blended scenarios (see finding 1.3 above). A sceptical reader who runs the numbers will notice.

### 4.2 Explainer Document — Strong

The explainer is well-paced and accessible. The figures (referenced as fig_e1, fig_e2, fig_e3) provide good visual support. The IPLC treatment section correctly distinguishes between formula allocation and disbursement pathways.

### 4.3 AHTEG Report Structure — Good Skeleton

The report structure document is a detailed outline rather than a finished report. The sections on TSAC, SOSAC, and boundary sensitivity are well-conceived. The candid acknowledgement of difficulties ("people may not understand or trust log scales") is appropriate.

### 4.4 README — Comprehensive

The README is thorough and well-organised. The floor/ceiling documentation is unusually detailed for a README, which is appropriate given the audience.

### 4.5 Change Log — Excellent

The change log is detailed, precise, and tracks both functional changes and the reasoning behind them. The entry about the gini-optimal rename and the Spearman constraint binding is exactly the level of detail a reviewer needs.

---

## 5. Test Suite

### 5.1 Coverage — Good

138 tests covering core logic, UI behaviour, sensitivity metrics, balance analysis, and reporting. Coverage is 79% overall, with the calculator at 89% and data loader at 100%.

### 5.2 Missing Test Categories

**Property-based tests:** The model has strong mathematical invariants (shares sum to 1, allocations sum to fund size, monotonicity under pure IUSAF) that would benefit from property-based testing with randomised parameters. The existing tests use fixed parameters.

**Regression tests for specific party allocations:** The test suite verifies structural properties (sums, ranks, eligibility) but does not pin specific allocation values for named parties. A regression test asserting that "under the gini-optimal scenario, Brazil receives $X.XXXM ± tolerance" would catch inadvertent changes to the data or logic.

**Recommendation (MEDIUM):** Add 3–5 regression tests pinning specific party allocations under the gini-optimal scenario. This is cheap to implement and provides a valuable safety net.

---

## 6. Potential Lines of Attack and Preparedness

### 6.1 "Band weights are arbitrary"

**Preparedness: Good.** The documentation explains the rationale for each weight and notes the defensible range for Band 6. The band analysis directory contains historical mobility analysis and crossover risk assessment, which directly addresses boundary sensitivity.

**Gap:** The technical note does not explicitly address *how* the specific weights 1.50, 1.30, 1.10, 0.95, 0.75, 0.40 were chosen. Was there a systematic optimisation, or were they set by judgement? The documentation implies the latter. A critic may ask: "Why 1.50 and not 1.60?" A brief explanation of the design rationale for the weight sequence would strengthen the defence.

### 6.2 "TSAC rewards geography, not biodiversity"

**Preparedness: Moderate.** The documentation correctly frames TSAC as a stewardship proxy, not a biodiversity index. However, the criticism that land area is a crude proxy for biodiversity responsibility is predictable and is not directly rebutted in the current materials.

**Recommendation (MEDIUM):** Add a paragraph in the technical note explicitly acknowledging that land area is an imperfect proxy but was chosen for its objectivity, availability, and non-contestability. Reference the design principle that simplicity and transparency are more important than precision in a multilateral allocation formula where any composite index would be politically contested.

### 6.3 "China benefits twice — Band 6 gives it a lower IUSAF, but TSAC gives it back"

**Preparedness: Good.** The balance point summary explicitly flags this issue and notes that at TSAC=5%, China's combined allocation exceeds Brazil's. This is honest and well-handled.

**Remaining risk:** The suggestion that "Parties may wish to consider whether a separate, lower TSAC coefficient for Band 6 is appropriate" is buried in the balance point summary. It should be surfaced more prominently if the authors consider it a genuine design option.

### 6.4 "The model has too many parameters"

**Preparedness: Strong.** The three-parameter design (β, γ, fund size) with floor/ceiling as optional constraints is actually quite parsimonious for an allocation model of this kind. The sensitivity framework's ability to show stability across parameter ranges is the best defence against this criticism.

### 6.5 "Why this model and not GEF STAR or another established approach?"

**Preparedness: Partial.** The reference directory contains a GEF STAR document, suggesting awareness of the comparison. However, the documentation does not explicitly position the IUSAF model relative to GEF STAR or other allocation mechanisms. A brief comparison in the AHTEG report would pre-empt this question.

---

## 7. Priority Recommendations Summary

### Critical (address before release)

1. **Document band-level monotonicity loss under blending** (§1.3). A reviewer will find this within minutes. Pre-empt it with an explicit, transparent discussion.

### High Priority

2. **Add missing land area data** for Republic of Korea, Netherlands, Slovakia, UK (§2.5). Even though they are excluded by default, the gap is visible in the data and undermines completeness claims.

3. **Generate a TSAC × SOSAC two-way heatmap** for the sensitivity report pack (§3.6). This is the most informative diagnostic missing from the current outputs.

### Medium Priority

4. **Move manual data overrides to a config file** (§2.3). Improves auditability.
5. **Reconsider the "gini-optimal" label** for policy-facing use (§3.4).
6. **Add regression tests pinning specific party allocations** (§5.2).
7. **Add an explicit paragraph on why land area was chosen as the TSAC proxy** (§6.2).
8. **Discuss the weight selection rationale** for the band weight sequence (§6.1).

### Low Priority

9. Extract the negotiation dashboard from `app.py` (§2.2).
10. Use `__file__`-relative paths in the config loader (§2.4).
11. Add a scale-invariance test (§3.7).

---

## 8. Overall Assessment

The model is mathematically sound, well-tested, and supported by documentation that is substantially more rigorous and self-aware than is typical for policy-support tools. The sensitivity framework in particular reflects a sophisticated understanding of what a critical reviewer will look for.

The principal risk is not mathematical error but *presentational surprise*: a reviewer who expects band monotonicity to hold universally will be disconcerted when the blended allocations show Band 6 receiving more than Band 3. This is an expected consequence of the design, but it must be explained before it is discovered.

With the critical and high-priority recommendations addressed, the model is ready for scrutiny by a technical and policy audience.

---

*This review was conducted on the basis of the full source code at github.com/tierravivaai/cali-allocation-model-v3 (main branch), all uploaded documentation, and runtime verification of the mathematical properties described above. All 138 tests pass. The reviewer ran independent validation of party counts (196), eligible party counts (142), share normalisation, allocation totals, and band monotonicity under both pure IUSAF and blended scenarios.*
