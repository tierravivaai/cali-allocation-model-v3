# Threshold Revision: Band-Order Preservation as Structural Constraint

## Status

This document specifies a methodological revision to the Gini-optimal balance-point definition. It supersedes the previous Spearman ≥ 0.85 constraint. The revision is to be implemented on a feature branch, merged to main, and tagged as a minor version increment.

## 1. Empirical Finding

The previous Gini-optimal definition used Spearman rank correlation ≥ 0.85 as the binding constraint. Empirical assessment of the TSAC fine sweep (see `docs/spearman-threshold-assessment.md`) established three findings:

1. **The 0.85 threshold was a design parameter, not an analytically derived value.** It was adopted during development, endorsed by peer review as "reasonable," and subsequently treated as established. No empirical derivation was performed.

2. **No structural break occurs at ρ = 0.85.** Across the TSAC sweep from 0% to 10% at 0.5 pp intervals, Spearman declines smoothly and monotonically. Mean rank shift, number of parties with changed rank, and top-20 turnover show no inflection, clustering, or discontinuity at ρ = 0.85. Nothing in the rank-change data distinguishes this value from its neighbours.

3. **The one clear structural discontinuity occurs at TSAC = 3.0% (ρ ≈ 0.929).** At this point, the IUSAF band hierarchy inverts for the first time: China (Band 6, lowest IUSAF weight) exceeds the mean allocation of Brazil, India, and Mexico (Band 5). The maximum rank shift doubles from 48 to 84 positions — the largest single-step jump in the sweep. This is the point at which the allocation formula no longer preserves the ordering implied by the IUSAF band structure.

The 0.85 threshold directly determined the Gini-optimal setting, because the unconstrained Gini minimum (TSAC = 5.5%) fails the threshold and the constrained optimum was pulled back to TSAC = 5.0%. A threshold with no empirical grounding should not be load-bearing for a headline parameter.

## 2. Revised Definition

The Gini-optimal balance point is redefined as:

> **The TSAC weight that minimises the Gini coefficient of the final allocation, subject to the structural constraint that the IUSAF band hierarchy is preserved — specifically, that the mean allocation of Band 6 parties remains below the mean allocation of Band 5 parties. A Spearman rank correlation floor of 0.80 is retained as a diagnostic safety check; the floor is not expected to bind under normal parameter configurations.**

The binding constraint is structural (band-order preservation), not statistical (a Spearman threshold). Spearman is reported alongside the optimum as a diagnostic, not as the definition of the optimum.

### Rationale for the Revised Definition

**Band-order preservation is a structural property of the IUSAF band system.** The six-band structure exists to differentiate parties by inverted sovereign capacity in a smoothed, policy-legible way. The band weights (1.00, 0.95, 0.90, 0.85, 0.75, 0.40) encode a monotonic ordering: higher bands receive higher weight per party. If the final allocation inverts this ordering — if Band 6 parties receive more than Band 5 parties on average — the formula has ceased to respect the differentiation that the band structure is designed to produce. Preventing this is a structural requirement, not a statistical preference.

**Band-order preservation is binary, not arbitrary.** A Spearman threshold invites the question "why 0.85 and not 0.90 or 0.80?" and any answer is a design choice. Band-order preservation does not have this vulnerability: either the band-mean ordering holds or it does not. The constraint is a direct statement about what the band structure is for.

**The Spearman floor provides a safety check without load-bearing work.** A Spearman floor of 0.80 is retained to catch pathological configurations — for example, parameter combinations where band-order technically holds but rank correlation has collapsed due to other effects. Under normal sweep conditions the band-order constraint binds first, and the Spearman floor is slack. This is the intended design.

## 3. Expected Outcomes

Based on the TSAC fine sweep (SOSAC = 3%), the revised definition is expected to produce:

- **Gini-optimal at TSAC ≈ 2.5%.** This is the last sweep point before band-order overturn at TSAC = 3.0%. Exact value subject to confirmation on regenerated sweep.
- **Spearman at the constrained optimum ≈ 0.945.** This clears the overlay classification's "moderate overlay" tier (ρ ≥ 0.95 is the boundary) by a small margin. Worth reporting as diagnostic context.
- **Band-order margin.** At the constrained optimum, Band 6 mean should sit below Band 5 mean with some margin. If the margin is tight, a buffered variant of the constraint (e.g., require Band 6 mean ≤ Band 5 mean − ε) should be considered. Regenerate and inspect before finalising.
- **Allocation effects.** Primary effects are on parties with TSAC share > IUSAF share (large-area countries): China (largest decrease, Band 6), Brazil/India/Mexico (smaller decreases, Band 5). Reciprocal gains accrue to parties with IUSAF share > TSAC share (small-area low-band parties). Absolute magnitudes are small — low millions of USD for the largest-affected parties on a USD 1bn fund.

## 4. Broader Context and Alternatives

This revision adopts one defensible point in a space of possible parameter choices. Other configurations are also defensible and are noted here for transparency:

- **Flatter band gradient.** The Band 5/6 step (0.75 → 0.40) is the steepest in the scale. Softening this step would raise China's IUSAF share directly, without relying on TSAC as a compensation mechanism. This is a legitimate alternative and may be considered in future revisions.
- **Higher Spearman floor.** Adopting ρ ≥ 0.90 (aligned with the overlay classification's "strong overlay" boundary) would produce a Gini-optimal at TSAC ≈ 4.0%. This preserves more of the original stewardship weight but retains a chosen threshold as load-bearing.
- **Raw equality fallback.** Any party or coalition that finds the revised formula unacceptable overall retains the option of advocating for equal splits (1/n) across eligible parties. This null option bounds the stakes of any parameter choice: the model is an offer to parties, not an imposition. The model's legitimacy rests on producing allocations that parties find preferable to equal splits on considered balance.

The revision does not claim the revised formula is uniquely correct. It claims the revised formula is more empirically grounded than the previous one and that the band-order constraint has a clearer structural meaning than an unanchored Spearman threshold.

## 5. Implementation Specification

The following changes are required. Implement on a feature branch (suggested name: `threshold-revision`). Commit in logical chunks. Regenerate outputs after code changes complete.

### 5.1 Code Changes

**`logic/balance_analysis.py`**
- Remove the hard-coded `spearman_moderate_threshold: float = 0.85` default parameter.
- Rename `_min_gini_above_spearman()` to `_min_gini_preserving_band_order()`.
- Implement the revised function: minimise Gini across sweep points subject to (a) Band 6 mean ≤ Band 5 mean, and (b) Spearman ≥ 0.80 safety floor. Both constraints must hold; band-order is expected to bind.
- Update the descriptive comment at line 238 ("threshold for moderate rather than dominant overlay") to describe the new constraint.
- Update balance-point summary rendering to report: Gini at optimum, Spearman at optimum (diagnostic), Band 6 mean vs Band 5 mean (structural check), constraint that binds.

**`logic/sensitivity_metrics.py`**
- Per `small-fixes.md` item 3: add internal `_eligible()` filter to `_spearman_by_party()` so the function is self-filtering. This is a correctness improvement independent of the threshold revision but should be bundled into this change since it touches related code.

**`src/app.py`**
- Update UI label at line 194 from "Gini-optimal point (minimises Gini, Spearman > 0.85)" to "Gini-minimum point (minimises Gini, preserves IUSAF band order)."
- Per `small-fixes.md` item 4: rename "Gini-optimal" to "Gini-minimum" throughout `app.py`. Do this consistently in `balance_analysis.py` and `sensitivity_scenarios.py` as well.

**`sensitivity_scenarios.py`**
- Rename `gini_optimal_point` scenario to `gini_minimum_point`. Update floor/ceiling variants from `gini_optimal_*` pattern to `gini_minimum_*` pattern.
- Update scenario TSAC value from 5% to the new constrained optimum (expected ≈ 2.5%, confirm against regenerated sweep).
- Update scenario description to reference band-order preservation rather than Spearman > 0.85.

**`update_figures.py`**
- Replace the Spearman = 0.85 horizontal reference line at line 251 with a vertical reference line at the band-order overturn TSAC (3.0%), labelled as "band-order overturn." The Spearman trace can remain on the figure as a diagnostic but should not carry a reference line at 0.85.

### 5.2 Test Changes

Update the following test files to assert the new definition:

- `tests/test_balance_analysis.py`: Update tests that assert on the specific Gini-optimal TSAC value. Add a test that asserts band-order preservation at the constrained optimum (Band 6 mean < Band 5 mean). Add a test that asserts the Spearman floor is slack at the constrained optimum (ρ > 0.80).
- `tests/test_component_ratios.py`: Review for references to the old threshold.
- UI tests and reporting tests referencing `gini_optimal_*` labels: update to `gini_minimum_*`.
- Add a test that asserts `_spearman_by_party()` returns eligible-only correlation when passed unfiltered dataframes (regression test for the self-filtering fix).

### 5.3 Documentation Changes

- **`docs/spearman-threshold-assessment.md`**: Add a brief "Resolution" section at the end noting that Option D has been adopted and referencing this document.
- **`docs/component-rationale.md`**: Revise any framing of ρ = 0.852 as "the model's boundary for recognisably the same rank order." Replace with framing of band-order preservation as the structural constraint. Retain the empirical data table as useful context.
- **`README.md`**: Update the "Gini-Optimal Point preset" references to "Gini-Minimum Point preset." Update the preset values from TSAC 0.05 to the new value (expected 0.025, confirm). Update methodology section language where applicable.
- **`change_log.md`**: Add a new entry under "Allocation logic and configuration" documenting the threshold revision with cross-reference to the assessment document and this rationale document.

### 5.4 Regeneration

After code and test changes are complete and tests pass:

- Regenerate `sensitivity-reports/v3-sensitivity-reports/` with the new constraint definition. Confirm the new Gini-minimum TSAC value and the allocation tables reflect the revision.
- Regenerate `balance_point_summary.md`, `balance_points.csv`, `tsac_fine_sweep.csv`, `integrity_checks.csv`.
- Confirm the `integrity_checks.csv` pass rate remains 100% across standard library scenarios.

### 5.5 Pre-Merge Verification

Before merging to main:

1. Confirm full test suite passes (target: all 138+ tests, accounting for test updates and additions).
2. Manually inspect regenerated balance-point summary and confirm: Gini-minimum TSAC value matches expectations, band-order constraint binds as expected, Spearman floor is slack, band-order margin is comfortable (not razor-thin).
3. If band-order margin is razor-thin at the constrained optimum (e.g., Band 6 mean within 1% of Band 5 mean), flag for review before merge — a buffered constraint variant may be warranted.
4. Inspect figures: break-point timeline figure should show the revised reference line at TSAC = 3.0% (band-order overturn) rather than at ρ = 0.85.
5. Confirm `app.py` and `sensitivity.py` both launch and display the revised labels correctly.

### 5.6 Merge and Tag

- Merge with `git merge --no-ff` to preserve branch structure in the log.
- Tag post-merge state as `v4.0` (breaking change: headline Gini-optimal value shifts; UI labels change; scenario names change).
- Tag pre-merge state as `v3.final` for reference before merging, so the state with the 0.85 threshold remains identifiable in the history.

## 6. Notes for the Implementer

- Work against this specification. Where the specification is ambiguous or implementation surfaces an unexpected issue, flag rather than assume.
- Commit in logical chunks: (1) the self-filtering fix to `_spearman_by_party()`, (2) the core constraint logic change in `balance_analysis.py`, (3) the rename from `gini_optimal` to `gini_minimum` across code and UI, (4) the scenario updates, (5) the figure and reference-line updates, (6) test updates, (7) documentation updates, (8) regenerated outputs.
- The rename from `gini_optimal` to `gini_minimum` is a separate concern from the threshold revision but is bundled here because both touch the same labels and doing them in one pass avoids a stratigraphy of half-renames.
- Do not rewrite history on main. The 0.85 period is part of the repo's honest development history and is referenced by the assessment document. The revision supersedes it; it does not erase it.
- If any step produces unexpected results (e.g., Gini-minimum TSAC at a value other than ≈ 2.5%, or band-order constraint not binding, or Spearman floor binding unexpectedly), stop and surface the discrepancy rather than accommodating it silently.

## 7. Cross-References

- Assessment: `docs/spearman-threshold-assessment.md`
- Small fixes (items 3 and 4 are bundled into this work): `small-fixes.md`
- Component rationale (requires revision): `docs/component-rationale.md`
- Current change log: `change_log.md`
- SOSAC rationale (unchanged by this revision): `sosac-rationale.md`
