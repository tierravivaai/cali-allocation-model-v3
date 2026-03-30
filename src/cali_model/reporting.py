from __future__ import annotations

import pandas as pd

from cali_model.balance_analysis import generate_balance_point_summary  # noqa: F401


def classify_overlay_strength(spearman_vs_pure_iusaf: float, top20_turnover_vs_pure_iusaf: float) -> str:
    if spearman_vs_pure_iusaf >= 0.98 and top20_turnover_vs_pure_iusaf <= 0.10:
        return "minimal overlay"
    if spearman_vs_pure_iusaf >= 0.95 and top20_turnover_vs_pure_iusaf <= 0.20:
        return "moderate overlay"
    if spearman_vs_pure_iusaf >= 0.90 or top20_turnover_vs_pure_iusaf <= 0.40:
        return "strong overlay"
    return "dominant overlay"


def classify_local_stability(local_min_spearman: float, local_max_top20_turnover: float) -> str:
    if local_min_spearman >= 0.99 and local_max_top20_turnover <= 0.05:
        return "stable"
    if local_min_spearman >= 0.97 and local_max_top20_turnover <= 0.10:
        return "moderately sensitive"
    if local_min_spearman >= 0.94 and local_max_top20_turnover <= 0.20:
        return "sensitive"
    return "unstable"


def render_overlay_interpretation(metrics: dict) -> str:
    label = metrics.get("overlay_strength_label", "moderate overlay")
    return (
        f"The selected scenario departs {('only slightly' if label == 'minimal overlay' else 'moderately' if label == 'moderate overlay' else 'materially')} "
        f"from the pure IUSAF baseline (`Spearman={metrics['spearman_vs_pure_iusaf']:.4f}`, `Top20 turnover={metrics['top20_turnover_vs_pure_iusaf']:.1%}`). "
        "This reflects the intended effect of the stewardship overlay rather than a mechanical error. "
        f"Overlay classification: **{label}**."
    )


def render_local_stability_interpretation(metrics: dict) -> str:
    label = metrics.get("local_stability_label", "not_evaluated")
    return (
        f"Within a narrow neighborhood around the selected blended baseline, results are **{label}** "
        f"(`local min Spearman={metrics.get('local_min_spearman_vs_baseline', float('nan')):.4f}`, "
        f"`local max Top20 turnover={metrics.get('local_max_top20_turnover_vs_baseline', float('nan')):.1%}`). "
        "Small changes in TSAC/SOSAC may therefore produce bounded, visible, or large shifts depending on this local stability result."
    )


def _format_scenario_definition(metrics: dict) -> str:
    return (
        f"- Fund size: ${metrics['fund_size']:,.0f}\n"
        f"- UN scale mode: `{metrics['un_scale_mode']}`\n"
        f"- Exclude high income except SIDS: `{metrics['exclude_hi']}`\n"
        f"- TSAC: `{metrics['tsac_beta']:.2%}` | SOSAC: `{metrics['sosac_gamma']:.2%}`\n"
        f"- IPLC share: `{metrics['iplc_share']:.0f}%`\n"
        f"- Floor: `{metrics['floor_pct']:.2f}%` | Ceiling: `{metrics['ceiling_pct'] if metrics['ceiling_pct'] is not None else 'off'}`"
    )


def generate_scenario_brief(metrics: dict, top_gainers: pd.DataFrame, top_losers: pd.DataFrame) -> str:
    gainers_txt = "\n".join([f"- {r.party}: {r.allocation_delta_m:+.2f}m" for r in top_gainers.itertuples(index=False)]) or "- No positive deltas"
    losers_txt = "\n".join([f"- {r.party}: {r.allocation_delta_m:+.2f}m" for r in top_losers.itertuples(index=False)]) or "- No negative deltas"

    return f"""# Scenario Brief: {metrics['scenario_id']}

## Purpose
This note summarises one sensitivity scenario with explicit separation between policy-overlay departure and local robustness.

## Scenario Definition
{_format_scenario_definition(metrics)}

## Mechanical validity
The scenario is computed using the shared calculator and should be interpreted only if invariants pass (conservation, normalization, and non-negativity).

## Relationship to pure IUSAF
{render_overlay_interpretation(metrics)}

## Stability of the blended specification
{render_local_stability_interpretation(metrics)}

## Distributional implications
SIDS total = `{metrics['sids_total']:.2f}m`; LDC total = `{metrics['ldc_total']:.2f}m`; top-20 share = `{metrics['top20_share']:.2%}`.

Largest gains versus pure IUSAF comparator:
{gainers_txt}

Largest losses versus pure IUSAF comparator:
{losers_txt}

## Caveats
Departure from pure IUSAF is expected when stewardship overlays are active and should not be treated as instability by itself.

## Bottom Line
Overlay assessment is **{metrics['overlay_strength_label']}** while local blended stability is **{metrics.get('local_stability_label', 'not_evaluated')}**.
"""


def generate_sweep_summary(sweep_name: str, sweep_df: pd.DataFrame, metric_column: str) -> str:
    strongest = sweep_df.iloc[(sweep_df[metric_column] - sweep_df[metric_column].median()).abs().idxmax()]
    trigger_lines = []

    def _explain_departure_trigger(row) -> str:
        reasons = []
        if row.get("spearman_vs_pure_iusaf", 1.0) < 0.95:
            reasons.append(
                f"`spearman_vs_pure_iusaf={row['spearman_vs_pure_iusaf']:.4f}` (threshold: < 0.95)"
            )
        if row.get("top20_turnover_vs_pure_iusaf", 0.0) > 0.20:
            reasons.append(
                f"`top20_turnover_vs_pure_iusaf={row['top20_turnover_vs_pure_iusaf']:.4f}` (threshold: > 0.20)"
            )
        if not reasons:
            return "trigger criterion not identified"
        return "; ".join(reasons)

    if "departure_from_pure_iusaf_flag" in sweep_df.columns:
        flagged = sweep_df[sweep_df["departure_from_pure_iusaf_flag"] == True]
    else:
        flagged = sweep_df[
            (sweep_df.get("spearman_vs_pure_iusaf", pd.Series(dtype=float)) < 0.95)
            | (sweep_df.get("top20_turnover_vs_pure_iusaf", pd.Series(dtype=float)) > 0.20)
        ]
    if not flagged.empty:
        row = flagged.iloc[0]
        trigger_lines.append(
            f"- departure-from-pure-IUSAF threshold: first triggered at `{row['scenario_id']}`. Trigger: {_explain_departure_trigger(row)}."
        )

    def _first_threshold(metric_col: str, label: str, mask_fn, formatter) -> None:
        if metric_col in sweep_df.columns:
            flagged = sweep_df[mask_fn(sweep_df[metric_col])]
            if not flagged.empty:
                row = flagged.iloc[0]
                trigger_lines.append(f"- {label}: first triggered at `{row['scenario_id']}` (`{metric_col}={formatter(row[metric_col])}`).")

    if "pct_below_equality" in sweep_df.columns:
        eq = sweep_df[sweep_df["pct_below_equality"] > 60]
        if not eq.empty:
            trigger_lines.append(f"- equality-distance threshold: first triggered at `{eq.iloc[0]['scenario_id']}` (`pct_below_equality={eq.iloc[0]['pct_below_equality']:.1f}%`).")
    _first_threshold("local_min_spearman_vs_baseline", "Local min Spearman vs baseline threshold", lambda s: s < 0.94, lambda v: f"{v:.4f}")
    _first_threshold("local_max_top20_turnover_vs_baseline", "Local top-20 turnover vs baseline threshold", lambda s: s > 0.20, lambda v: f"{v:.1%}")
    _first_threshold("local_max_abs_share_delta", "Local max absolute share-delta threshold", lambda s: s > 0.005, lambda v: f"{v:.3%}")
    if "dominance_flag" in sweep_df.columns:
        dom = sweep_df[sweep_df["dominance_flag"] == True]
        if not dom.empty:
            trigger_lines.append(f"- stewardship-dominance threshold: first triggered at `{dom.iloc[0]['scenario_id']}` (`tsac+sosac={(dom.iloc[0]['tsac_beta'] + dom.iloc[0]['sosac_gamma']):.2%}`).")

    trigger_text = "\n".join(trigger_lines) if trigger_lines else "- No configured threshold triggers were crossed in this sweep."

    return f"""# Sweep Summary: {sweep_name}

## Purpose of Sweep
This summary reviews controlled parameter variation and distinguishes policy-overlay departure from local sensitivity.

## Sweep Design
The sweep includes `{len(sweep_df)}` scenarios and tracks `{metric_column}` with trigger-specific warning logic.

## Mechanical validity
Interpretation assumes conservation and non-negativity checks are satisfied for the included runs.

## Relationship to pure IUSAF
`{metric_column}` ranges from `{sweep_df[metric_column].min():.4f}` to `{sweep_df[metric_column].max():.4f}`. This captures overlay departure strength, not local instability.

## Stability of the blended specification
Local stability is evaluated separately where local-neighborhood diagnostics are available.

## Distributional implications
Largest deviation in this sweep appears at `{strongest['scenario_id']}` (`{metric_column}={strongest[metric_column]:.4f}`).

## Caveats
Trigger attribution below reports the actual threshold source and should not be interpreted as a single generic structural-break mechanism.

### Thresholds / Tipping Points
{trigger_text}

## Bottom Line
The sweep indicates where policy overlay departs from pure IUSAF and, separately, where local stability warnings emerge.
"""


def generate_comparative_report(metrics_df: pd.DataFrame, baseline_id: str = "gini_optimal_point") -> str:
    baseline = metrics_df[metrics_df["scenario_id"] == baseline_id]
    baseline_row = baseline.iloc[0] if not baseline.empty else metrics_df.iloc[0]

    overlay_counts = metrics_df["overlay_strength_label"].value_counts(dropna=False).to_dict() if "overlay_strength_label" in metrics_df.columns else {}
    local_counts = metrics_df["local_stability_label"].value_counts(dropna=False).to_dict() if "local_stability_label" in metrics_df.columns else {}
    departure_n = int(metrics_df.get("departure_from_pure_iusaf_flag", pd.Series(dtype=bool)).sum()) if "departure_from_pure_iusaf_flag" in metrics_df else 0
    instability_n = int(metrics_df.get("local_blended_instability_flag", pd.Series(dtype=bool)).sum()) if "local_blended_instability_flag" in metrics_df else 0

    top_departure = metrics_df.nsmallest(min(3, len(metrics_df)), "spearman_vs_pure_iusaf")
    top_departure_lines = "\n".join(
        [
            f"- {r.scenario_id}: overlay `{r.overlay_strength_label}`, Spearman vs pure IUSAF `{r.spearman_vs_pure_iusaf:.4f}`, local stability `{r.local_stability_label}`"
            for r in top_departure.itertuples(index=False)
        ]
    )

    return f"""# Comparative Sensitivity Report

## Introduction
This report compares baseline, equality, pure IUSAF, and stress scenarios while separating policy-overlay departure from local robustness.

*In the codebase, the TSAC weight and SOSAC weight are stored under the internal parameter names `tsac_beta` and `sosac_gamma` respectively, following the conventional Greek-letter notation used in the original formula specification. Readers reviewing the source code will find these names throughout; they correspond exactly to the TSAC weight and SOSAC weight referred to in this document.*

## Baseline Scenario
Baseline is `{baseline_row['scenario_id']}` with fund size `${baseline_row['fund_size']:,.0f}`, TSAC `{baseline_row['tsac_beta']:.2%}`, SOSAC `{baseline_row['sosac_gamma']:.2%}`, and UN mode `{baseline_row['un_scale_mode']}`.

## Benchmarks for Comparison
Comparison includes pure equality, pure IUSAF (raw and band), gini-optimal variants, and constraint/eligibility alternatives.

## Mechanical validity
Several scenarios are mechanically valid and reproducible under the shared calculator and diagnostics framework.

## Relationship to pure IUSAF
Many scenarios depart materially from pure IUSAF where stewardship overlays are active (`departure_from_pure_iusaf_flag` count: `{departure_n}/{len(metrics_df)}`). Overlay classes observed: `{overlay_counts}`.

Most policy-departed scenarios:
{top_departure_lines}

## Stability of the blended specification
The key question is whether blended settings remain locally stable under modest nearby parameter changes. Local instability flags appear in `{instability_n}/{len(metrics_df)}` scenarios. Local stability classes observed: `{local_counts}`.

## Distributional implications
SIDS totals range from `{metrics_df['sids_total'].min():.2f}m` to `{metrics_df['sids_total'].max():.2f}m`; LDC totals range from `{metrics_df['ldc_total'].min():.2f}m` to `{metrics_df['ldc_total'].max():.2f}m`.

## Caveats
Departure from pure IUSAF should be read as overlay strength, not instability. Stability conclusions should rely on local neighborhood tests.

## Conclusions
Reported warnings now distinguish material policy departure from true local sensitivity, supporting more precise review of blended-scenario robustness.
"""


def generate_local_stability_markdown(metrics: dict, local_table: pd.DataFrame) -> str:
    lines = [
        "# Local Stability Narrative",
        "",
        "## Mechanical validity",
        "Local checks are interpreted only after core conservation and non-negativity diagnostics pass.",
        "",
        "## Relationship to pure IUSAF",
        render_overlay_interpretation(metrics),
        "",
        "## Stability of the blended specification",
        render_local_stability_interpretation(metrics),
        "",
        "## Distributional implications",
        "Neighbor scenarios show how small parameter adjustments re-rank countries and shift shares.",
        "",
        "## Caveats",
        "Local stability is neighborhood-specific and should be revisited if baseline settings or admissible parameter ranges change.",
        "",
        "## Adjacent scenario checks",
    ]
    if local_table.empty:
        lines.append("No adjacent scenarios were generated.")
    else:
        lines.append("```csv")
        lines.append(local_table.to_csv(index=False).strip())
        lines.append("```")
    return "\n".join(lines)


def generate_technical_annex() -> str:
    return """# Technical Annex

## Data and Eligibility Rules
Data are loaded from the same repository sources used by the main app. Eligibility follows CBD Party status, with optional high-income exclusion preserving SIDS where configured.

## Formula Specification
Final Share = (1 - beta - gamma) * IUSAF + beta * TSAC + gamma * SOSAC.

*In the codebase, the TSAC weight and SOSAC weight are stored under the internal parameter names `tsac_beta` and `sosac_gamma` respectively, following the conventional Greek-letter notation used in the original formula specification. Readers reviewing the source code will find these names throughout; they correspond exactly to the TSAC weight and SOSAC weight referred to in this document.*

## Historical note: stewardship-forward baseline
Prior to the completion of the fine-grained TSAC sweep, sensitivity analysis used a provisional reference scenario called the stewardship-forward baseline (TSAC=5%, SOSAC=3%). This was a development placeholder used before balance points had been formally identified. The sweep confirmed that TSAC=5% is precisely the gini-optimal point — the setting that minimises the Gini coefficient while keeping Spearman rank correlation above 0.85. The stewardship-forward baseline was accordingly retired and replaced by the gini-optimal point, which has identical parameter values. Any outputs generated before this change that reference the stewardship-forward baseline are equivalent to outputs referencing the gini-optimal point.

## Raw vs Band Inversion
Raw inversion uses reciprocal UN shares. Band inversion applies configured UN-share bands and weights before normalization.

## TSAC and SOSAC Treatment
TSAC is proportional to land area among eligible countries. SOSAC is equal-share across eligible SIDS. If no SIDS are eligible and SOSAC > 0, SOSAC is reallocated to IUSAF.

## IPLC Split
Total allocations are split into State and IPLC components by configured IPLC share.

## Floor and Ceiling Handling
Floor and ceiling constraints are applied on normalized shares with iterative reconciliation to preserve feasibility and conservation.

## No-SIDS Fallback
When no eligible SIDS exist, SOSAC weight is reassigned to IUSAF to preserve conservation and avoid invalid shares.

## Integrity Tests
Diagnostics include conservation of shares and money, component consistency, non-negativity, and mode-specific checks.

## Sensitivity Ranges
Fund size anchors: 50m, 200m, 500m, 1bn. TSAC: 0-15%. SOSAC: 0-10%. IPLC: 50/60/70/80. Floor: off, 0.05%, 0.10%, 0.25%. Ceiling: off, 1%, 2%, 5%.

## Departure and Local-Stability Criteria
Departure from pure IUSAF is flagged when Spearman vs pure IUSAF < 0.95 or top-20 turnover > 20%.
Local blended instability is flagged when local min Spearman vs baseline < 0.94, local max top-20 turnover > 20%, or local max absolute share delta > 0.5 percentage points.

## Exported Outputs
App exports scenario-level metrics, country-level results, country deltas, group summaries, and markdown reports for scenario briefs, sweep summaries, comparative analysis, and this annex.
"""
