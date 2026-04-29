# The Spearman 0.85 Threshold: Origin, Application, and Empirical Assessment

## 1. Current Status

The Spearman rank correlation threshold of ρ > 0.85 is used in the model as the boundary for "recognisably the same rank order as pure IUSAF." It serves as a binding constraint in the Gini-optimal point identification: the Gini-optimal setting is defined as the TSAC weight that minimises the Gini coefficient while keeping Spearman rank correlation vs pure IUSAF above 0.85.

This threshold is a **design parameter, not an analytically derived value**. It was adopted during model development, endorsed by peer review as "a reasonable relaxation for moderate but not dominant," and subsequently treated as established. No empirical or analytical derivation was performed.

## 2. Where 0.85 Appears in the Codebase

| Location | Usage |
|----------|-------|
| `balance_analysis.py:133` | `spearman_moderate_threshold: float = 0.85` — hard-coded default parameter |
| `balance_analysis.py:176` | Binding constraint for Gini-optimal point identification |
| `balance_analysis.py:238` | Described as "threshold for moderate rather than dominant overlay" |
| `app.py:194` | UI label: "Gini-optimal point (minimises Gini, Spearman > 0.85)" |
| `update_figures.py:251` | Horizontal reference line on break-point timeline figure |
| `component-rationale.md` | Used as boundary for "recognisably the same rank order" |

## 3. Relationship to the Overlay Classification System

The model's sensitivity metrics (`sensitivity_metrics.py`) classify overlay strength using a separate tiered system based on Spearman and top-20 turnover:

| Classification | Spearman | Top-20 Turnover |
|---------------|----------|-----------------|
| Minimal overlay | ≥ 0.98 | ≤ 10% |
| Moderate overlay | ≥ 0.95 | ≤ 20% |
| Strong overlay | ≥ 0.90 | ≤ 40% |
| Dominant overlay | < 0.90 | > 40% |

This system does **not** use 0.85 as a boundary. The closest boundary is 0.90 (strong vs dominant). The 0.85 threshold exists in a separate analytical context — the Gini-optimal constraint — and is 5 percentage points below the overlay classification system's "dominant" boundary.

## 4. How 0.85 Determines the Gini-Optimal Point

The Gini-optimal point is identified by the function `_min_gini_above_spearman()`, which finds the TSAC weight that minimises Gini among all sweep points where Spearman exceeds 0.85. The constraint binds:

- **Unconstrained Gini minimum**: TSAC = 5.5%, where Spearman = 0.822 (fails the 0.85 threshold)
- **Constrained optimum**: TSAC = 5.0%, where Spearman = 0.852 (last point above 0.85)

The 0.85 threshold therefore directly determines the Gini-optimal setting. If the threshold were 0.90, the Gini-optimal would shift to TSAC ≈ 4.5% (Spearman = 0.871). If it were 0.80, the Gini-optimal would shift to TSAC ≈ 5.5% (the unconstrained minimum).

## 5. Empirical Assessment

### 5.1 Rank-Change Metrics Across the TSAC Sweep

The following analysis uses the TSAC fine sweep (SOSAC = 3%, TSAC 0–10% at 0.5 pp intervals), computing Spearman and detailed rank-change metrics among 142 eligible parties only. (Including ineligible parties with zero allocations inflates the correlation — see Section 6.)

| TSAC | Spearman ρ | Parties with Changed Rank | Mean |Rank Shift| | Max |Rank Shift| | Top-20 Turnover | Band Order Preserved? |
|------|-----------|-------------------------|------------------|----------------|------------------|-----------------------|
| 0.0% | 0.977 | 138 | 6.1 | 24 | 80% | YES |
| 0.5% | 0.952 | 138 | 10.0 | 29 | 80% | YES |
| 1.0% | 0.952 | 138 | 10.0 | 29 | 80% | YES |
| 1.5% | 0.951 | 138 | 10.1 | 29 | 80% | YES |
| 2.0% | 0.948 | 139 | 10.4 | 42 | 80% | YES |
| 2.5% | 0.945 | 140 | 10.6 | 48 | 80% | YES |
| **3.0%** | **0.929** | **140** | **11.4** | **84** | **80%** | **NO** |
| 3.5% | 0.917 | 140 | 11.9 | 104 | 80% | NO |
| 4.0% | 0.898 | 140 | 12.8 | 116 | 80% | NO |
| 4.5% | 0.871 | 140 | 13.6 | 139 | 90% | NO |
| **5.0%** | **0.852** | **140** | **14.2** | **139** | **90%** | **NO** |
| 5.5% | 0.822 | 140 | 15.5 | 140 | 90% | NO |
| 6.0% | 0.808 | 140 | 16.2 | 140 | 90% | NO |
| 7.5% | 0.762 | 141 | 18.2 | 140 | 100% | NO |
| 10.0% | 0.666 | 140 | 22.0 | 140 | 100% | NO |

### 5.2 No Natural Breakpoint at ρ = 0.85

The Spearman decline is smooth and monotonic. There is no inflection point, clustering, or discontinuity at ρ = 0.85 (TSAC = 5.0%). The mean rank shift increases gradually from 14.2 to 15.5 between TSAC = 5.0% and 5.5%. The number of parties with changed rank is essentially flat at 140 across the entire range. The top-20 turnover shifts from 90% to 90% — no change. **Nothing in the rank-change data distinguishes ρ = 0.85 from its neighbours.**

### 5.3 The Observable Structural Break: Band Order Overturn at ρ ≈ 0.93

The one clear structural discontinuity occurs at TSAC = 3.0% (ρ ≈ 0.929):

- **Band order inverts**: China (Band 6, lowest IUSAF weight) exceeds the mean allocation of Brazil, India, and Mexico (Band 5). The IUSAF's monotonic band ordering — Band 1 > Band 2 > Band 3 > Band 4 > Band 5 > Band 6 — is broken for the first time.
- **Max rank shift doubles**: From 48 positions (TSAC = 2.5%) to 84 positions (TSAC = 3.0%). This is the largest single-step jump in max displacement across the entire sweep.
- **This is a structural, not statistical, threshold**: It marks the point where the model's allocation logic no longer preserves the ordering implied by the IUSAF band structure.

### 5.4 Other Observable Breakpoints

| Breakpoint | TSAC | Spearman ρ | Signal |
|-----------|------|-----------|--------|
| Band order overturn | 3.0% | 0.929 | IUSAF band structure first inverts; max rank shift doubles |
| Top-20 full turnover | 7.5% | 0.762 | None of the pure-IUSAF top 20 remain in the top 20 |
| Component overturn (China) | 2.0% | 0.948 | TSAC component ≥ IUSAF component for China |
| Component overturn (Brazil) | 4.0% | 0.898 | TSAC component ≥ IUSAF component for Brazil |

None of these breakpoints occur at or near ρ = 0.85.

## 6. Technical Note: Eligible vs All-Party Spearman

The function `_spearman_by_party()` in `sensitivity_metrics.py` does not internally filter to eligible parties — it merges on all parties in the dataframes passed to it. However, all three call sites (lines 240, 303, 460) pass pre-filtered eligible-only dataframes, so the function produces correct values in practice. The separate `compute_spearman_vs_iusaf()` function in `band-analysis/break-points/analysis.py` also filters to eligible parties explicitly.

**The function should still be made self-filtering for robustness** — a future caller could pass unfiltered dataframes, producing inflated values (0.945 vs 0.852 at TSAC=5%). Adding an internal `_eligible()` filter or a prominent docstring warning would prevent this.

## 7. Assessment

The 0.85 threshold has three properties:

1. **It is a design choice, not an empirical finding.** No observable structural change in the allocation rankings occurs at or near ρ = 0.85.
2. **It directly determines the Gini-optimal setting.** Because the unconstrained Gini minimum (TSAC = 5.5%) fails the 0.85 threshold, the constrained optimum is pulled back to TSAC = 5.0%. Changing the threshold would change the recommended setting.
3. **It lacks independent justification.** The peer review endorsed it as "reasonable" but did not derive it. The overlay classification system uses different thresholds (0.98, 0.95, 0.90). The rationale document's description of ρ = 0.852 as "the model's boundary for recognisably the same rank order" attributes more analytical authority to the threshold than it currently possesses.

## 8. Options for Grounding the Threshold

### Option A: Adopt the band-order threshold (ρ ≈ 0.93)

The band order overturn at ρ ≈ 0.929 is the clearest empirical breakpoint. It marks the point where the model no longer preserves the structural ordering that the IUSAF band system is designed to produce. This threshold has a concrete policy meaning: "the allocation still respects the IUSAF band hierarchy." At ρ ≈ 0.93, the Gini-optimal would shift to approximately TSAC ≈ 2.5–3.0%.

**Advantage**: Empirically grounded, structurally meaningful, defensible in negotiation.
**Risk**: Restrictive — would exclude the current Gini-optimal setting (TSAC = 5%).

### Option B: Retain 0.85 with explicit framing as a design parameter

Acknowledge that 0.85 is a policy choice, not an analytical finding. Frame it as: "the model designer's judgement that a Spearman correlation of 0.85 represents the maximum acceptable departure from pure IUSAF while still being considered recognisably similar." This is honest but places the burden of justification on the design choice rather than on empirical evidence.

**Advantage**: Preserves current Gini-optimal setting; no code changes needed.
**Risk**: Vulnerable to challenge in negotiation — "why 0.85 and not 0.90 or 0.80?"

### Option C: Adopt the overlay classification boundary (ρ ≥ 0.90)

Align the Gini-optimal constraint with the existing overlay classification system, which marks ρ = 0.90 as the boundary between "strong overlay" and "dominant overlay." At ρ = 0.90, the Gini-optimal would shift to approximately TSAC ≈ 4.0%.

**Advantage**: Consistent with the model's own classification framework; avoids having two different Spearman thresholds for related concepts.
**Risk**: Still a design choice (why 0.90 and not 0.85?), but one backed by the overlay classification rationale.

### Option D: Multi-criterion approach

Instead of a single Spearman threshold, define the Gini-optimal as the TSAC weight that:
- Minimises Gini coefficient
- Preserves band order (Band 6 mean < Band 5 mean)
- Keeps Spearman above a minimum floor (e.g., 0.80)

This replaces a single arbitrary threshold with a bundle of concrete structural conditions.

**Advantage**: Each criterion has a clear policy meaning; the combination is more robust than any single threshold.
**Risk**: More complex to explain; the band-order constraint may dominate and effectively set TSAC ≤ 2.5%.

## 9. Recommendation

The 0.85 threshold should not be presented as an analytical finding. The current rationale document's framing of ρ = 0.852 as "the model's boundary for recognisably the same rank order" should be revised to acknowledge that this is a design parameter.

A defensible path forward is **Option C (adopt ρ ≥ 0.90)** or **Option D (multi-criterion)**, both of which provide clearer analytical grounding than the current 0.85. The band-order overturn at ρ ≈ 0.93 is the strongest empirical anchor point available and should be reported alongside any chosen threshold as a reference for what a structurally meaningful breakpoint looks like.

Regardless of which option is chosen, the Spearman calculation inconsistency (Section 6) should be resolved so that all code paths compute the eligible-only correlation.

---

## 10. Resolution

**Option D (multi-criterion) has been adopted**, implemented on the `optiond` branch (2026-04-18). The Gini-minimum constraint is now defined as:

- **Binding constraint**: IUSAF band-order preservation (Band 6 mean < Band 5 mean)
- **Safety floor**: Spearman ρ > 0.80 (diagnostic; not expected to bind)

This produces a Gini-minimum at TSAC ≈ 2.5% with Spearman ≈ 0.945, preserving the band hierarchy with margin. The `gini_optimal` label has been retired and replaced with `gini_minimum` throughout the codebase. See `optiond-threshold-revision-rationale.md` for the full specification.

---

*This document was prepared as part of the IUSAF Allocation Model v3 documentation. The empirical analysis uses the TSAC fine sweep (SOSAC = 3%, TSAC 0–10% at 0.5 pp intervals) with 142 eligible parties.*
