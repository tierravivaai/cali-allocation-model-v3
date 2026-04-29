"""
Fine-grained parameter sweeps and balance-point identification.

Balance condition: tsac_component_i / iusaf_component_i <= 1.0 for all eligible Parties i.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd


# Parameter naming convention
# ----------------------------
# The allocation formula weights are stored internally as:
#   tsac_beta    — the TSAC (Terrestrial Stewardship Allocation Component) weight
#   sosac_gamma  — the SOSAC (SIDS Ocean Stewardship Allocation Component) weight
# These names follow the convention used in the academic specification of the formula
# (Final_share = (1-β-γ)·IUSAF + β·TSAC + γ·SOSAC).
# Display labels in user-facing surfaces use “TSAC weight” and “SOSAC weight” for clarity.


def _band_mean(eligible_df: pd.DataFrame, band_prefix: str) -> float | None:
    """Mean per-party allocation for a band (e.g. 'Band 5' matches 'Band 5: ...')."""
    if eligible_df.empty or "un_band" not in eligible_df.columns:
        return None
    band = eligible_df[eligible_df["un_band"].str.startswith(band_prefix, na=False)]
    return float(band["total_allocation"].mean()) if not band.empty else None


def _band_order_preserved(eligible_df: pd.DataFrame) -> bool | None:
    """True if Band 6 mean allocation < Band 5 mean allocation."""
    b6 = _band_mean(eligible_df, "Band 6")
    b5 = _band_mean(eligible_df, "Band 5")
    if b6 is None or b5 is None:
        return None
    return b6 < b5


def run_fine_sweep(
    base_scenario: dict,
    base_df: "pd.DataFrame",
    run_scenario_fn: Callable,
    compute_metrics_fn: Callable,
    compute_component_ratios_fn: Callable,
    build_pure_iusaf_fn: Callable,
    sweep_param: str = "tsac_beta",
    values: list[float] | None = None,
) -> pd.DataFrame:
    if values is None:
        values = [round(x * 0.005, 3) for x in range(21)]

    rows = []
    for val in values:
        s = dict(base_scenario)
        s[sweep_param] = val
        s["scenario_id"] = f"{sweep_param}_fine_{val:.3f}"

        if float(s.get("tsac_beta", 0)) + float(s.get("sosac_gamma", 0)) >= 1.0:
            continue

        results = run_scenario_fn(base_df, s)
        iusaf_s = build_pure_iusaf_fn(s, keep_constraints=True)
        iusaf_results = run_scenario_fn(base_df, iusaf_s)
        eq_results = run_scenario_fn(
            base_df,
            {**iusaf_s, "equality_mode": True, "scenario_id": f"{s['scenario_id']}_eq"},
        )

        metrics = compute_metrics_fn(s, results, iusaf_results, eq_results)
        ratios = compute_component_ratios_fn(
            results,
            float(s.get("tsac_beta", 0.0)),
            float(s.get("sosac_gamma", 0.0)),
        )

        eligible = results[results["eligible"]]

        band1_alloc = None
        b1_pct_change = None
        if "un_band" in eligible.columns:
            b1 = eligible[eligible["un_band"].str.startswith("Band 1", na=False)]
            b1_ref = iusaf_results[
                iusaf_results["eligible"] & iusaf_results["un_band"].str.startswith("Band 1", na=False)
            ]
            if not b1.empty:
                band1_alloc = float(b1["total_allocation"].mean())
                if not b1_ref.empty:
                    ref_mean = float(b1_ref["total_allocation"].mean())
                    b1_pct_change = (
                        (float(b1["total_allocation"].mean()) - ref_mean) / ref_mean * 100
                        if ref_mean > 0
                        else None
                    )

        sids_total = (
            float(eligible.loc[eligible["is_sids"], "total_allocation"].sum())
            if "is_sids" in eligible.columns
            else None
        )
        if "UN LDC" in eligible.columns:
            ldc_mask = eligible["UN LDC"].eq("LDC")
        elif "is_ldc" in eligible.columns:
            ldc_mask = eligible["is_ldc"]
        else:
            ldc_mask = None
        ldc_total = float(eligible.loc[ldc_mask, "total_allocation"].sum()) if ldc_mask is not None else None

        max_sosac_ratio = None
        max_sosac_ratio_parties = None
        if not ratios["ratio_df"].empty and "sosac_iusaf_ratio" in ratios["ratio_df"].columns:
            finite_sosac = ratios["ratio_df"]["sosac_iusaf_ratio"].replace(float("inf"), np.nan).dropna()
            max_sosac_ratio = float(finite_sosac.max()) if not finite_sosac.empty else 0.0
            if not finite_sosac.empty:
                top_party_rows = ratios["ratio_df"].loc[
                    ratios["ratio_df"]["sosac_iusaf_ratio"].replace(float("inf"), np.nan) == max_sosac_ratio,
                    "party",
                ]
                parties = sorted(str(p) for p in top_party_rows.dropna().tolist())
                max_sosac_ratio_parties = ", ".join(parties) if parties else None

        rows.append(
            {
                "sweep_param": sweep_param,
                "sweep_value": val,
                "spearman_vs_pure_iusaf": metrics.get("spearman_vs_pure_iusaf"),
                "gini_coefficient": metrics.get("gini_coefficient"),
                "pct_below_equality": metrics.get("pct_below_equality"),
                "max_tsac_iusaf_ratio": ratios["max_tsac_iusaf_ratio"],
                "max_sosac_iusaf_ratio": max_sosac_ratio,
                "max_sosac_ratio_parties": max_sosac_ratio_parties,
                "china_tsac_iusaf_ratio": ratios["china_tsac_iusaf_ratio"],
                "brazil_tsac_iusaf_ratio": ratios["brazil_tsac_iusaf_ratio"],
                "n_parties_tsac_dominant": ratios["n_parties_tsac_dominant"],
                "tsac_balance_exceeded": ratios["tsac_balance_exceeded"],
                "band1_per_party_alloc_m": band1_alloc,
                "band1_pct_change_vs_iusaf": b1_pct_change,
                "sids_total_m": sids_total,
                "ldc_total_m": ldc_total,
                "band6_mean_alloc_m": _band_mean(eligible, "Band 6"),
                "band5_mean_alloc_m": _band_mean(eligible, "Band 5"),
                "band_order_preserved": _band_order_preserved(eligible),
            }
        )

    return pd.DataFrame(rows)


def identify_balance_points(
    tsac_sweep_df: pd.DataFrame,
    sosac_sweep_df: pd.DataFrame,
    spearman_safety_floor: float = 0.80,
) -> dict:
    """Identify balance points from sweep data.

    The Gini-minimum point is identified by minimising Gini subject to
    band-order preservation (Band 6 mean < Band 5 mean) and a Spearman
    safety floor of 0.80. The band-order constraint is expected to bind;
    the Spearman floor is a diagnostic safety check.
    """
    def _last_row_where(df: pd.DataFrame, col: str, threshold: float):
        if df.empty or col not in df.columns:
            return None
        mask = df[col].notna() & (df[col] <= threshold)
        return df[mask].iloc[-1] if mask.any() else None

    def _sosac_result(df: pd.DataFrame, col: str, threshold: float):
        if df.empty or col not in df.columns:
            return None
        valid_df = df[df[col].notna()].copy()
        if valid_df.empty:
            return None
        last_valid = valid_df.iloc[-1]
        if float(last_valid[col]) < threshold:
            return {
                "value": None,
                "above_range": True,
                "max_ratio_at_sweep_limit": float(last_valid[col]),
                "analytical_estimate": 0.174,
                "metrics": last_valid.to_dict(),
            }
        return _fmt(_last_row_where(valid_df, col, threshold))

    def _min_gini_preserving_band_order(df: pd.DataFrame, spearman_floor: float):
        """Minimise Gini subject to band-order preservation and Spearman floor."""
        if df.empty:
            return None

        # Band-order constraint: Band 6 mean < Band 5 mean
        band_order_ok = df["band_order_preserved"].fillna(True).astype(bool)

        # Spearman safety floor
        spearman_ok = df["spearman_vs_pure_iusaf"].notna() & (df["spearman_vs_pure_iusaf"] > spearman_floor)

        # Gini must be available
        gini_ok = df["gini_coefficient"].notna()

        mask = band_order_ok & spearman_ok & gini_ok
        if not mask.any():
            return None

        return df[mask].loc[df[mask]["gini_coefficient"].idxmin()]

    def _fmt(row):
        return {"value": float(row["sweep_value"]), "metrics": row.to_dict()} if row is not None else None

    return {
        "strict": _fmt(_last_row_where(tsac_sweep_df, "china_tsac_iusaf_ratio", 1.0)),
        "modified": _fmt(_last_row_where(tsac_sweep_df, "brazil_tsac_iusaf_ratio", 1.0)),
        "gini_minimum": _fmt(_min_gini_preserving_band_order(tsac_sweep_df, spearman_safety_floor)),
        "sosac": _sosac_result(sosac_sweep_df, "max_sosac_iusaf_ratio", 1.0),
    }


def generate_balance_point_summary(
    balance_points: dict,
    tsac_sweep_df: pd.DataFrame,
    sosac_sweep_df: pd.DataFrame,
    stewardship_forward_beta: float = 0.05,
    stewardship_forward_gamma: float = 0.03,
) -> str:
    def _tbl(m: dict) -> list[str]:
        rows = []
        fields = [
            ("sweep_value", "Parameter value", lambda v: f"**{v:.1%}**"),
            ("spearman_vs_pure_iusaf", "Spearman vs pure IUSAF", lambda v: f"{v:.4f}"),
            ("gini_coefficient", "Gini coefficient", lambda v: f"{v:.4f}"),
            ("china_tsac_iusaf_ratio", "China TSAC/IUSAF ratio", lambda v: f"{v:.3f}×"),
            ("brazil_tsac_iusaf_ratio", "Brazil TSAC/IUSAF ratio", lambda v: f"{v:.3f}×"),
            ("band1_per_party_alloc_m", "Band 1 per-Party ($m)", lambda v: f"${v:.3f}m"),
            ("band1_pct_change_vs_iusaf", "Band 1 change vs IUSAF", lambda v: f"{v:+.1f}%"),
            ("sids_total_m", "SIDS total ($m)", lambda v: f"${v:.1f}m"),
            ("ldc_total_m", "LDC total ($m)", lambda v: f"${v:.1f}m"),
        ]
        rows.append("| Metric | Value |")
        rows.append("|---|---|")
        for key, label, fmt in fields:
            val = m.get(key)
            if val is not None and not (isinstance(val, float) and np.isnan(val)):
                try:
                    rows.append(f"| {label} | {fmt(val)} |")
                except Exception:
                    pass
        return rows

    sections = [
        "# Balance Point Summary",
        "",
        "## What is a balance point?",
        "",
        "A parameter setting is **balanced** when, for every eligible Party, the IUSAF equity component is at least as large as the TSAC stewardship component. Formally: `tsac_component_i / iusaf_component_i ≤ 1.0` for all eligible Parties `i`.",
        "",
        f"The **gini-minimum point** (TSAC={stewardship_forward_beta:.0%}, SOSAC={stewardship_forward_gamma:.0%}) is the setting that minimises the Gini coefficient while preserving the IUSAF band hierarchy (Band 6 mean < Band 5 mean) and maintaining a Spearman rank correlation safety floor of 0.80 vs pure IUSAF. The band-order constraint binds; the Spearman floor is a diagnostic safety check. It coincides with what was previously called the gini-optimal point, which has been retired. The gini-minimum point is the default reference scenario.",
        "",
        "---",
        "",
        "## Results",
        "",
    ]

    bp_meta = {
        "strict": (
            "Strict balance point",
            "Highest TSAC weight where China's TSAC/IUSAF ratio ≤ 1.0. China (Band 6) is the binding constraint: largest land area, lowest IUSAF base.",
        ),
        "modified": (
            "Modified balance point",
            "Highest TSAC weight where Brazil's TSAC/IUSAF ratio ≤ 1.0. Treats China separately (addressed by Band 6 weight); requires IUSAF dominance for all Band 5 Parties (Brazil, India, Mexico).",
        ),
        "gini_minimum": (
            "Gini-minimum point",
            "TSAC weight that minimises the Gini coefficient while preserving the IUSAF band hierarchy (Band 6 mean < Band 5 mean) and maintaining a Spearman rank correlation safety floor of 0.80 vs pure IUSAF. The band-order constraint is expected to bind; the Spearman floor is a diagnostic safety check.",
        ),
        "sosac": (
            "SOSAC balance point",
            "Highest SOSAC weight (TSAC held at 0) where the SOSAC component does not exceed the IUSAF component for any SIDS Party.",
        ),
    }

    for key, (title, description) in bp_meta.items():
        sections.append(f"### {title}")
        sections.append("")
        sections.append(description)
        sections.append("")
        bp = balance_points.get(key)
        if bp is None:
            sections.append("*Not identified within sweep range (0–10%).*")
        elif bp.get("above_range"):
            parties = bp.get("metrics", {}).get("max_sosac_ratio_parties")
            parties_text = f", for {parties}" if parties else ""
            sections.append(
                "*The SOSAC balance point lies above the 0–10% sweep range. "
                f"At gamma=10%, the highest SOSAC/IUSAF ratio across all SIDS Parties is {bp['max_ratio_at_sweep_limit']:.3f}×{parties_text}. "
                f"The analytical balance point is approximately {bp['analytical_estimate']:.1%}.*"
            )
        else:
            if key == "gini_minimum":
                sections.append(
                    "*Note: this point is identified by a different criterion from the strict and modified balance points. "
                    "The band-order constraint (Band 6 mean < Band 5 mean) binds: the unconstrained Gini minimum would "
                    "occur at a higher TSAC where band order is already overturned, so the constrained optimum is the "
                    "last point where band order is preserved. "
                    "The Spearman safety floor (> 0.80) is slack at this point and does not bind. "
                    "This point does not satisfy the TSAC/IUSAF dominance balance condition — `tsac_balance_exceeded` may be `True`. "
                    "It is included here as a distributional optimum subject to structural preservation, not as a balanced setting in the TSAC/IUSAF sense.*"
                )
                sections.append("")
            sections.extend(_tbl(bp["metrics"]))
        sections.append("")

    sections += [
        "---",
        "",
        "## Choosing among balance points",
        "",
        "The selection among these points is a **policy judgement**, not a technical one.",
        "",
        "- The **strict point** most faithfully preserves the IUSAF equity foundation for all Parties including China.",
        "- The **modified point** accepts that China is treated separately through Band 6 and focuses on IUSAF dominance for Band 5 Parties.",
        "- The **Gini-minimum point** minimises the Gini coefficient within the constraint that the IUSAF band hierarchy is preserved (Band 6 mean < Band 5 mean) and a Spearman safety floor of 0.80 is maintained. It does not satisfy the TSAC/IUSAF balance condition and should not be read as a \"balanced\" setting in that sense. It is the default scenario in the application because it produces the most equal per-Party distribution measurable by Gini while respecting the band structure.",
        "",
        "## Note on China and TSAC",
        "",
        "Band 6 was introduced to give China a lower IUSAF base allocation than Band 5 Parties, reflecting its much larger UN assessed contribution (20% vs ~1.1–1.4% for Brazil, India, Mexico). However, China also receives a full TSAC allocation proportional to its land area (~9.6M km²), which partially offsets the Band 6 adjustment. At TSAC=5%, China's combined allocation exceeds Brazil's despite the Band 6 distinction. Parties may wish to consider whether a separate, lower TSAC coefficient for Band 6 is appropriate.",
        "",
        "---",
        "*Generated by logic/balance_analysis.py. All figures are illustrative modelling outputs.*",
    ]

    return "\n".join(sections)
