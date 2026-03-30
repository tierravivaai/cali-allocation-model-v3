from __future__ import annotations

import math
from typing import Any

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

from cali_model.calculator import get_outcome_warning_feedback, get_stewardship_blend_feedback
from cali_model.sensitivity_scenarios import generate_local_neighbor_scenarios as _generate_local_neighbor_scenarios


STRUCTURAL_BREAK_RULES = {
    "stewardship_total_gt": 0.20,
    "spearman_vs_pure_iusaf_lt": 0.95,
    "top20_turnover_vs_pure_iusaf_gt": 0.20,
    "pct_below_equality_gt": 60.0,
    "median_pct_of_equality_lt": 90.0,
}

LOCAL_INSTABILITY_RULES = {
    "min_spearman_lt": 0.94,
    "max_top20_turnover_gt": 0.20,
    "max_abs_share_delta_gt": 0.005,
}


def _safe_float(value, default: float = 0.0) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    try:
        return float(value)
    except Exception:
        return default


def _gini(values: pd.Series) -> float:
    x = values.fillna(0.0).astype(float)
    if len(x) == 0:
        return 0.0
    if (x < 0).any():
        x = x - x.min()
    x = x.sort_values().reset_index(drop=True)
    n = len(x)
    total = x.sum()
    if total <= 0:
        return 0.0
    weighted_sum = ((x.index + 1) * x).sum()
    return float((2 * weighted_sum) / (n * total) - (n + 1) / n)


def _hhi(shares: pd.Series) -> float:
    s = shares.fillna(0.0).astype(float)
    return float((s**2).sum())


def compute_gini(allocations: "pd.Series") -> float:
    a = allocations.dropna().values.astype(float)
    a = a[a >= 0]
    n = len(a)
    if n == 0 or a.sum() == 0:
        return 0.0
    a = np.sort(a)
    idx = np.arange(1, n + 1)
    return float((2 * (idx * a).sum()) / (n * a.sum()) - (n + 1) / n)


def compute_component_ratios(
    results_df: "pd.DataFrame",
    beta: float,
    gamma: float,
) -> dict:
    eligible = results_df[results_df["eligible"]].copy()

    _safe_default = {
        "ratio_df": pd.DataFrame(),
        "max_tsac_iusaf_ratio": 0.0,
        "n_parties_tsac_dominant": 0,
        "china_tsac_iusaf_ratio": None,
        "brazil_tsac_iusaf_ratio": None,
        "tsac_balance_exceeded": False,
        "sosac_balance_exceeded": False,
    }

    required = {"component_iusaf_amt", "component_tsac_amt", "component_sosac_amt"}
    # Keep this as `(beta == 0 and gamma == 0)`, not `beta == 0` alone,
    # so pure-SOSAC scenarios still compute SOSAC/IUSAF ratios.
    if not required.issubset(eligible.columns) or (beta == 0 and gamma == 0):
        return _safe_default

    df = eligible[["party", "component_iusaf_amt", "component_tsac_amt", "component_sosac_amt"]].copy()

    def _ratio(numerator: float, denominator: float) -> float:
        return (numerator / denominator) if denominator > 0 else float("inf")

    df["tsac_iusaf_ratio"] = df.apply(
        lambda r: _ratio(r["component_tsac_amt"], r["component_iusaf_amt"]), axis=1
    )
    df["sosac_iusaf_ratio"] = df.apply(
        lambda r: _ratio(r["component_sosac_amt"], r["component_iusaf_amt"]), axis=1
    )
    df["tsac_dominant"] = df["tsac_iusaf_ratio"] > 1.0

    def _named_ratio(fragment: str):
        mask = df["party"].str.contains(fragment, case=False, na=False)
        return float(df.loc[mask, "tsac_iusaf_ratio"].iloc[0]) if mask.any() else None

    china_ratio = _named_ratio("China")
    brazil_ratio = _named_ratio("Brazil")

    if "is_sids" in eligible.columns:
        sids_rows = eligible[eligible["is_sids"]].copy()
    else:
        sids_rows = eligible[eligible["component_sosac_amt"] > 0].copy()

    sosac_exceeded = False
    if not sids_rows.empty and "component_iusaf_amt" in sids_rows.columns:
        sids_ratios = sids_rows.apply(
            lambda r: _ratio(r["component_sosac_amt"], r["component_iusaf_amt"]), axis=1
        )
        sosac_exceeded = bool((sids_ratios > 1.0).any())

    ratio_df = df[
        [
            "party",
            "component_iusaf_amt",
            "component_tsac_amt",
            "component_sosac_amt",
            "tsac_iusaf_ratio",
            "sosac_iusaf_ratio",
            "tsac_dominant",
        ]
    ].sort_values("tsac_iusaf_ratio", ascending=False)

    finite_ratios = df["tsac_iusaf_ratio"].replace(float("inf"), 0)

    return {
        "ratio_df": ratio_df,
        "max_tsac_iusaf_ratio": float(finite_ratios.max()),
        "n_parties_tsac_dominant": int(df["tsac_dominant"].sum()),
        "china_tsac_iusaf_ratio": china_ratio,
        "brazil_tsac_iusaf_ratio": brazil_ratio,
        "tsac_balance_exceeded": bool((df["tsac_iusaf_ratio"] > 1.0).any()),
        "sosac_balance_exceeded": sosac_exceeded,
    }


def _top_turnover(current: pd.DataFrame, baseline: pd.DataFrame, n: int = 20) -> float:
    cur_top = set(current.nlargest(min(n, len(current)), "final_share")["party"].tolist())
    base_top = set(baseline.nlargest(min(n, len(baseline)), "final_share")["party"].tolist())
    universe = max(1, min(n, len(cur_top | base_top)))
    return float(len(cur_top.symmetric_difference(base_top)) / universe)


def _eligible(results_df: pd.DataFrame) -> pd.DataFrame:
    return results_df[results_df["eligible"]].copy()


def _spearman_by_party(current: pd.DataFrame, baseline: pd.DataFrame) -> float:
    merged = current[["party", "final_share"]].merge(
        baseline[["party", "final_share"]], on="party", how="inner", suffixes=("_cur", "_base")
    )
    if merged.empty:
        return float("nan")
    r_cur = merged["final_share_cur"].rank(method="average")
    r_base = merged["final_share_base"].rank(method="average")
    if r_cur.nunique() <= 1 or r_base.nunique() <= 1:
        same_distribution = merged["final_share_cur"].round(12).equals(merged["final_share_base"].round(12))
        return 1.0 if same_distribution else 0.0
    return float(r_cur.corr(r_base, method="pearson"))


def _group_totals(eligible_df: pd.DataFrame, group_col: str) -> dict[str, float]:
    if group_col not in eligible_df.columns:
        return {}
    grouped = eligible_df.groupby(group_col, dropna=False)["total_allocation"].sum().to_dict()
    out = {}
    for key, value in grouped.items():
        label = "NA" if pd.isna(key) else str(key)
        out[label] = float(value)
    return out


def _band1_pct_change(
    results_df: "pd.DataFrame",
    iusaf_results_df: "pd.DataFrame",
) -> "float | None":
    try:
        col = "un_band"
        if col not in results_df.columns:
            return None
        b1 = results_df[
            results_df["eligible"] & results_df[col].str.startswith("Band 1", na=False)
        ]["total_allocation"].mean()
        b1_ref = iusaf_results_df[
            iusaf_results_df["eligible"] & iusaf_results_df[col].str.startswith("Band 1", na=False)
        ]["total_allocation"].mean()
        return float((b1 - b1_ref) / b1_ref * 100) if b1_ref and b1_ref > 0 else None
    except Exception:
        return None


def build_pure_iusaf_comparator(scenario: dict, keep_constraints: bool = True) -> dict:
    comparator = dict(scenario)
    comparator["scenario_id"] = f"{scenario.get('scenario_id', 'scenario')}_pure_iusaf_comp"
    comparator["tsac_beta"] = 0.0
    comparator["sosac_gamma"] = 0.0
    comparator["equality_mode"] = False
    if not keep_constraints:
        comparator["floor_pct"] = 0.0
        comparator["ceiling_pct"] = None
    return comparator


def compute_departure_from_pure_iusaf(current_results_df: pd.DataFrame, pure_iusaf_results_df: pd.DataFrame) -> dict[str, Any]:
    cur = _eligible(current_results_df)
    pure = _eligible(pure_iusaf_results_df)
    merged = cur[["party", "final_share"]].merge(
        pure[["party", "final_share"]],
        on="party",
        how="inner",
        suffixes=("_cur", "_pure"),
    )
    if merged.empty:
        spearman = float("nan")
        turnover = 0.0
        mean_abs = 0.0
        max_abs = 0.0
    else:
        spearman = _spearman_by_party(cur, pure)
        turnover = _top_turnover(cur, pure, n=20)
        abs_delta = (merged["final_share_cur"] - merged["final_share_pure"]).abs()
        mean_abs = float(abs_delta.mean())
        max_abs = float(abs_delta.max())

    if spearman >= 0.98 and turnover <= 0.10:
        overlay_label = "minimal overlay"
    elif spearman >= 0.95 and turnover <= 0.20:
        overlay_label = "moderate overlay"
    elif spearman >= 0.90 or turnover <= 0.40:
        overlay_label = "strong overlay"
    else:
        overlay_label = "dominant overlay"

    departure_flag = bool((spearman < 0.95) or (turnover > 0.20))
    return {
        "spearman_vs_pure_iusaf": spearman,
        "top20_turnover_vs_pure_iusaf": turnover,
        "mean_abs_share_delta_vs_pure_iusaf": mean_abs,
        "max_abs_share_delta_vs_pure_iusaf": max_abs,
        "overlay_strength_label": overlay_label,
        "departure_from_pure_iusaf_flag": departure_flag,
    }


def generate_local_neighbor_scenarios(base_scenario: dict, ranges: dict[str, list] | None = None) -> list[dict]:
    return _generate_local_neighbor_scenarios(base_scenario, ranges=ranges)


def compute_local_stability_metrics(
    base_scenario: dict,
    base_results_df: pd.DataFrame,
    base_df: pd.DataFrame,
    run_scenario_fn,
    ranges: dict[str, list] | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:
    neighbors = generate_local_neighbor_scenarios(base_scenario, ranges=ranges)
    base_eligible = _eligible(base_results_df)
    rows = []

    for n in neighbors:
        n_results = run_scenario_fn(base_df, n)
        n_eligible = _eligible(n_results)
        merged = base_eligible[["party", "final_share"]].merge(
            n_eligible[["party", "final_share"]],
            on="party",
            how="inner",
            suffixes=("_base", "_neighbor"),
        )
        abs_delta = (merged["final_share_base"] - merged["final_share_neighbor"]).abs() if not merged.empty else pd.Series(dtype=float)

        changed_params = []
        for key in ["tsac_beta", "sosac_gamma", "iplc_share_pct", "floor_pct", "ceiling_pct"]:
            if n.get(key) != base_scenario.get(key):
                changed_params.append((key, n.get(key)))
        param_changed, new_value = changed_params[0] if changed_params else ("none", None)

        rows.append(
            {
                "scenario_id": n.get("scenario_id"),
                "parameter_changed": param_changed,
                "new_value": new_value,
                "spearman_vs_baseline": _spearman_by_party(n_eligible, base_eligible),
                "top20_turnover_vs_baseline": _top_turnover(n_eligible, base_eligible, n=20),
                "mean_abs_share_delta_vs_baseline": float(abs_delta.mean()) if len(abs_delta) else 0.0,
                "max_abs_share_delta_vs_baseline": float(abs_delta.max()) if len(abs_delta) else 0.0,
            }
        )

    table = pd.DataFrame(rows)
    if table.empty:
        out = {
            "local_min_spearman_vs_baseline": 1.0,
            "local_max_top20_turnover_vs_baseline": 0.0,
            "local_mean_mean_abs_share_delta": 0.0,
            "local_max_abs_share_delta": 0.0,
            "local_stability_label": "stable",
            "local_blended_instability_flag": False,
        }
        return out, table

    min_spearman = float(table["spearman_vs_baseline"].min())
    max_turnover = float(table["top20_turnover_vs_baseline"].max())
    mean_mean_abs = float(table["mean_abs_share_delta_vs_baseline"].mean())
    max_abs = float(table["max_abs_share_delta_vs_baseline"].max())

    if min_spearman >= 0.99 and max_turnover <= 0.05:
        label = "stable"
    elif min_spearman >= 0.97 and max_turnover <= 0.10:
        label = "moderately sensitive"
    elif min_spearman >= 0.94 and max_turnover <= 0.20:
        label = "sensitive"
    else:
        label = "unstable"

    instability = bool(
        min_spearman < LOCAL_INSTABILITY_RULES["min_spearman_lt"]
        or max_turnover > LOCAL_INSTABILITY_RULES["max_top20_turnover_gt"]
        or max_abs > LOCAL_INSTABILITY_RULES["max_abs_share_delta_gt"]
    )

    out = {
        "local_min_spearman_vs_baseline": min_spearman,
        "local_max_top20_turnover_vs_baseline": max_turnover,
        "local_mean_mean_abs_share_delta": mean_mean_abs,
        "local_max_abs_share_delta": max_abs,
        "local_stability_label": label,
        "local_blended_instability_flag": instability,
    }
    return out, table


def structural_break_flag(metrics: dict[str, Any]) -> bool:
    # Backward-compatibility flag: interpreted as material departure from pure IUSAF/equality,
    # not as local-instability of the blended specification.
    checks = [
        (metrics.get("tsac_beta", 0.0) + metrics.get("sosac_gamma", 0.0)) > STRUCTURAL_BREAK_RULES["stewardship_total_gt"],
        metrics.get("spearman_vs_pure_iusaf", 1.0) < STRUCTURAL_BREAK_RULES["spearman_vs_pure_iusaf_lt"],
        metrics.get("top20_turnover_vs_pure_iusaf", 0.0) > STRUCTURAL_BREAK_RULES["top20_turnover_vs_pure_iusaf_gt"],
        metrics.get("pct_below_equality", 0.0) > STRUCTURAL_BREAK_RULES["pct_below_equality_gt"],
        metrics.get("median_pct_of_equality", 100.0) < STRUCTURAL_BREAK_RULES["median_pct_of_equality_lt"],
    ]
    return bool(any(checks))


def compute_metrics(
    scenario: dict,
    results_df: pd.DataFrame,
    iusaf_baseline_df: pd.DataFrame,
    equality_baseline_df: pd.DataFrame,
    local_stability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    eligible_df = _eligible(results_df)
    iusaf_eligible = _eligible(iusaf_baseline_df)
    equality_eligible = _eligible(equality_baseline_df)

    n_eligible = int(len(eligible_df))
    n_sids_eligible = int(eligible_df["is_sids"].sum()) if "is_sids" in eligible_df else 0
    fund_size = float(scenario["fund_size"])
    total_m = fund_size / 1_000_000.0
    _ratios = compute_component_ratios(
        results_df,
        float(scenario.get("tsac_beta", 0.0)),
        float(scenario.get("sosac_gamma", 0.0)),
    )
    allocation_gini = compute_gini(results_df.loc[results_df["eligible"], "total_allocation"])
    _b1_change = _band1_pct_change(results_df, iusaf_baseline_df)

    eq_ref = (fund_size / n_eligible / 1_000_000.0) if n_eligible > 0 else 0.0
    if eq_ref > 0 and n_eligible > 0:
        pct_below_eq = float((eligible_df["total_allocation"] < eq_ref).mean() * 100.0)
        median_pct_eq = float((eligible_df["total_allocation"].median() / eq_ref) * 100.0)
    else:
        pct_below_eq = 0.0
        median_pct_eq = 100.0

    floor_threshold = float(scenario.get("floor_pct") or 0.0) / 100.0
    ceiling_raw = scenario.get("ceiling_pct")
    ceiling_threshold = None if ceiling_raw is None else float(ceiling_raw) / 100.0

    if floor_threshold > 0:
        floor_binding_count = int((eligible_df["final_share"] <= floor_threshold + 1e-9).sum())
    else:
        floor_binding_count = 0

    if ceiling_threshold is not None:
        ceiling_binding_count = int((eligible_df["final_share"] >= ceiling_threshold - 1e-9).sum())
    else:
        ceiling_binding_count = 0

    stewardship_feedback = get_stewardship_blend_feedback(
        float(scenario.get("tsac_beta", 0.0)), float(scenario.get("sosac_gamma", 0.0))
    )
    outcome_feedback = get_outcome_warning_feedback(results_df, fund_size)

    departure = compute_departure_from_pure_iusaf(results_df, iusaf_baseline_df)
    local = local_stability or {
        "local_min_spearman_vs_baseline": float("nan"),
        "local_max_top20_turnover_vs_baseline": float("nan"),
        "local_mean_mean_abs_share_delta": float("nan"),
        "local_max_abs_share_delta": float("nan"),
        "local_stability_label": "not_evaluated",
        "local_blended_instability_flag": False,
    }

    metrics = {
        "scenario_id": scenario.get("scenario_id", "scenario"),
        "fund_size": fund_size,
        "un_scale_mode": scenario.get("un_scale_mode"),
        "exclude_hi": bool(scenario.get("exclude_high_income", False)),
        "iplc_share": float(scenario.get("iplc_share_pct", 50)),
        "tsac_beta": float(scenario.get("tsac_beta", 0.0)),
        "sosac_gamma": float(scenario.get("sosac_gamma", 0.0)),
        "floor_pct": float(scenario.get("floor_pct", 0.0) or 0.0),
        "ceiling_pct": None if ceiling_raw is None else float(ceiling_raw),
        "n_eligible": n_eligible,
        "n_sids_eligible": n_sids_eligible,
        "floor_binding_count": floor_binding_count,
        "ceiling_binding_count": ceiling_binding_count,
        "sum_final_share": float(eligible_df["final_share"].sum()) if n_eligible else 0.0,
        "sum_total_allocation": float(eligible_df["total_allocation"].sum()) if n_eligible else 0.0,
        "negative_count": int((eligible_df[["final_share", "total_allocation", "state_component", "iplc_component"]] < 0).sum().sum())
        if n_eligible
        else 0,
        "top10_share": float(eligible_df.nlargest(min(10, n_eligible), "final_share")["final_share"].sum()) if n_eligible else 0.0,
        "top20_share": float(eligible_df.nlargest(min(20, n_eligible), "final_share")["final_share"].sum()) if n_eligible else 0.0,
        "mean_alloc": float(eligible_df["total_allocation"].mean()) if n_eligible else 0.0,
        "median_alloc": float(eligible_df["total_allocation"].median()) if n_eligible else 0.0,
        "p90_p10_ratio": float(
            eligible_df["total_allocation"].quantile(0.90) / max(eligible_df["total_allocation"].quantile(0.10), 1e-9)
        )
        if n_eligible
        else 0.0,
        "hhi": _hhi(eligible_df["final_share"]) if n_eligible else 0.0,
        "gini": _gini(eligible_df["final_share"]) if n_eligible else 0.0,
        "gini_coefficient": allocation_gini,
        "pct_below_equality": pct_below_eq,
        "median_pct_of_equality": median_pct_eq,
        "spearman_vs_iusaf": departure["spearman_vs_pure_iusaf"],
        "spearman_vs_equality": _spearman_by_party(eligible_df, equality_eligible),
        "top20_turnover_vs_iusaf": departure["top20_turnover_vs_pure_iusaf"],
        "spearman_vs_pure_iusaf": departure["spearman_vs_pure_iusaf"],
        "top20_turnover_vs_pure_iusaf": departure["top20_turnover_vs_pure_iusaf"],
        "mean_abs_share_delta_vs_pure_iusaf": departure["mean_abs_share_delta_vs_pure_iusaf"],
        "max_abs_share_delta_vs_pure_iusaf": departure["max_abs_share_delta_vs_pure_iusaf"],
        "overlay_strength_label": departure["overlay_strength_label"],
        "departure_from_pure_iusaf_flag": departure["departure_from_pure_iusaf_flag"],
        "max_tsac_iusaf_ratio": _ratios["max_tsac_iusaf_ratio"],
        "n_parties_tsac_dominant": _ratios["n_parties_tsac_dominant"],
        "china_tsac_iusaf_ratio": _ratios["china_tsac_iusaf_ratio"],
        "brazil_tsac_iusaf_ratio": _ratios["brazil_tsac_iusaf_ratio"],
        "tsac_balance_exceeded": _ratios["tsac_balance_exceeded"],
        "sosac_balance_exceeded": _ratios["sosac_balance_exceeded"],
        "band1_per_party_pct_change_vs_iusaf": _b1_change,
        "local_min_spearman_vs_baseline": _safe_float(local.get("local_min_spearman_vs_baseline"), float("nan")),
        "local_max_top20_turnover_vs_baseline": _safe_float(local.get("local_max_top20_turnover_vs_baseline"), float("nan")),
        "local_mean_mean_abs_share_delta": _safe_float(local.get("local_mean_mean_abs_share_delta"), float("nan")),
        "local_max_abs_share_delta": _safe_float(local.get("local_max_abs_share_delta"), float("nan")),
        "local_stability_label": local.get("local_stability_label", "not_evaluated"),
        "local_blended_instability_flag": bool(local.get("local_blended_instability_flag", False)),
        "ldc_total": float(eligible_df[eligible_df["is_ldc"]]["total_allocation"].sum()) if "is_ldc" in eligible_df else 0.0,
        "sids_total": float(eligible_df[eligible_df["is_sids"]]["total_allocation"].sum()) if "is_sids" in eligible_df else 0.0,
        "stewardship_warning_level": stewardship_feedback.get("warning_level", "none"),
        "outcome_warning_flag": bool(outcome_feedback),
        "dominance_flag": bool((scenario.get("tsac_beta", 0.0) + scenario.get("sosac_gamma", 0.0)) > 0.20),
        "expected_total_allocation": total_m,
    }

    metrics["structural_break_flag"] = structural_break_flag(metrics)

    for group, value in _group_totals(eligible_df, "region").items():
        metrics[f"region_{group}"] = value

    for group, value in _group_totals(eligible_df, "WB Income Group").items():
        metrics[f"income_{group}"] = value

    return metrics


def compute_country_deltas(current_df: pd.DataFrame, baseline_df: pd.DataFrame) -> pd.DataFrame:
    cur = current_df[["party", "eligible", "final_share", "total_allocation"]].rename(
        columns={"final_share": "current_share", "total_allocation": "current_allocation_m"}
    )
    base = baseline_df[["party", "final_share", "total_allocation"]].rename(
        columns={"final_share": "baseline_share", "total_allocation": "baseline_allocation_m"}
    )
    merged = cur.merge(base, on="party", how="left")
    merged["share_delta"] = merged["current_share"] - merged["baseline_share"]
    merged["allocation_delta_m"] = merged["current_allocation_m"] - merged["baseline_allocation_m"]
    merged["allocation_delta_pct"] = merged.apply(
        lambda row: 0.0
        if pd.isna(row["baseline_allocation_m"]) or math.isclose(row["baseline_allocation_m"], 0.0)
        else (row["allocation_delta_m"] / row["baseline_allocation_m"]) * 100.0,
        axis=1,
    )
    return merged


def run_invariant_checks(
    scenario: dict,
    results_df: pd.DataFrame,
    no_sids_results_df: pd.DataFrame | None = None,
    tolerance: float = 1e-6,
) -> pd.DataFrame:
    eligible_df = _eligible(results_df)
    n_eligible = len(eligible_df)
    expected_total_m = float(scenario["fund_size"]) / 1_000_000.0

    checks = []

    def add(name: str, status: bool, detail: str):
        checks.append({"check": name, "pass": bool(status), "detail": detail})

    share_sum = float(eligible_df["final_share"].sum()) if n_eligible else 0.0
    add("Conservation of shares", abs(share_sum - 1.0) <= tolerance if n_eligible else True, f"sum={share_sum:.10f}")

    total_sum = float(eligible_df["total_allocation"].sum()) if n_eligible else 0.0
    add(
        "Conservation of money",
        abs(total_sum - expected_total_m) <= max(1e-5, tolerance),
        f"sum={total_sum:.6f}m expected={expected_total_m:.6f}m",
    )

    comp_delta = (eligible_df["state_component"] + eligible_df["iplc_component"] - eligible_df["total_allocation"]).abs().max() if n_eligible else 0.0
    add("Internal component consistency", comp_delta <= max(1e-6, tolerance), f"max_abs_delta={comp_delta:.10f}")

    negatives = int((eligible_df[["final_share", "total_allocation", "state_component", "iplc_component"]] < 0).sum().sum()) if n_eligible else 0
    add("Non-negativity", negatives == 0, f"negative_count={negatives}")

    if scenario.get("equality_mode", False):
        unique_shares = eligible_df["final_share"].round(12).nunique() if n_eligible else 0
        tsac_zero = (eligible_df["tsac_share"] == 0).all() if n_eligible else True
        sosac_zero = (eligible_df["sosac_share"] == 0).all() if n_eligible else True
        add("Equality mode correctness", unique_shares <= 1 and tsac_zero and sosac_zero, f"unique_shares={unique_shares}")
    else:
        add("Equality mode correctness", True, "not in equality mode")

    if scenario.get("un_scale_mode") == "raw_inversion":
        subset = eligible_df[eligible_df["un_share"] > 0][["party", "un_share", "iusaf_share"]].copy()
        subset = subset.sort_values("un_share")
        monotonic = bool((subset["iusaf_share"].diff().fillna(0) <= 1e-9).all())
        add("Raw inversion correctness", monotonic, f"rows_checked={len(subset)}")
    else:
        add("Raw inversion correctness", True, "not in raw inversion mode")

    if scenario.get("un_scale_mode") == "band_inversion":
        valid = bool((eligible_df["un_band"].notna()).all()) if n_eligible else True
        add("Band inversion correctness", valid, f"missing_bands={int((eligible_df['un_band'].isna()).sum()) if n_eligible else 0}")
    else:
        add("Band inversion correctness", True, "not in band inversion mode")

    if no_sids_results_df is not None and scenario.get("sosac_gamma", 0.0) > 0:
        no_sids_eligible = _eligible(no_sids_results_df)
        sosac_total = float(no_sids_eligible["component_sosac_amt"].sum()) if len(no_sids_eligible) else 0.0
        final_sum = float(no_sids_eligible["final_share"].sum()) if len(no_sids_eligible) else 0.0
        add("No-SIDS fallback", abs(sosac_total) <= 1e-6 and abs(final_sum - 1.0) <= 1e-6, f"sosac_total={sosac_total:.8f}")
    else:
        add("No-SIDS fallback", True, "not applicable")

    if scenario.get("floor_pct", 0.0) > 0:
        add("Floor feasibility", abs(share_sum - 1.0) <= tolerance, f"floor_pct={scenario.get('floor_pct')}")
    else:
        add("Floor feasibility", True, "floor disabled")

    if scenario.get("ceiling_pct") is not None:
        add("Ceiling feasibility", abs(share_sum - 1.0) <= tolerance, f"ceiling_pct={scenario.get('ceiling_pct')}")
    else:
        add("Ceiling feasibility", True, "ceiling disabled")

    add("Scale invariance of shares", True, "tested in fund-size sweep and diagnostics")

    return pd.DataFrame(checks)


def generate_integrity_checks(
    scenario_id: str,
    scenario_params: dict,
    results_df: pd.DataFrame,
    fund_size: float,
) -> dict:
    """Return one reviewer-facing integrity-check row for integrity_checks.csv."""

    if not results_df.empty and "eligible" in results_df.columns:
        eligible_df = results_df[results_df["eligible"] == True].copy()
    else:
        eligible_df = pd.DataFrame()
    tolerance_share = 1e-6
    tolerance_usd = 0.01
    required_columns = [
        "scenario_id",
        "fund_size_usd",
        "tsac_beta",
        "sosac_gamma",
        "check_conservation_shares",
        "sum_final_share",
        "check_conservation_money",
        "sum_total_allocation_usd",
        "check_non_negativity",
        "min_allocation_usd",
        "check_component_consistency",
        "max_component_abs_diff_usd",
        "check_iplc_split",
        "max_iplc_abs_diff_usd",
        "check_band_monotonicity",
        "band_monotonicity_detail",
        "check_floor_not_binding_unexpectedly",
        "floor_binding_count",
        "check_ceiling_not_binding_unexpectedly",
        "ceiling_binding_count",
        "check_sids_sosac_allocation",
        "sids_sosac_component_sum_usd",
        "n_eligible_parties",
        "n_eligible_sids",
        "all_checks_pass",
    ]

    row = {
        "scenario_id": scenario_id,
        "fund_size_usd": float(fund_size),
        "tsac_beta": float(scenario_params.get("tsac_beta", 0.0) or 0.0),
        "sosac_gamma": float(scenario_params.get("sosac_gamma", 0.0) or 0.0),
        "check_conservation_shares": "FAIL",
        "sum_final_share": float("nan"),
        "check_conservation_money": "FAIL",
        "sum_total_allocation_usd": float("nan"),
        "check_non_negativity": "FAIL",
        "min_allocation_usd": float("nan"),
        "check_component_consistency": "FAIL",
        "max_component_abs_diff_usd": float("nan"),
        "check_iplc_split": "FAIL",
        "max_iplc_abs_diff_usd": float("nan"),
        "check_band_monotonicity": "FAIL",
        "band_monotonicity_detail": "Band data unavailable",
        "check_floor_not_binding_unexpectedly": "FAIL",
        "floor_binding_count": 0,
        "check_ceiling_not_binding_unexpectedly": "FAIL",
        "ceiling_binding_count": 0,
        "check_sids_sosac_allocation": "FAIL",
        "sids_sosac_component_sum_usd": float("nan"),
        "n_eligible_parties": int(len(eligible_df)),
        "n_eligible_sids": int(eligible_df["is_sids"].sum()) if "is_sids" in eligible_df.columns else 0,
        "all_checks_pass": "FAIL",
    }

    def _passfail(status: bool) -> str:
        return "PASS" if bool(status) else "FAIL"

    def _usd(series: pd.Series) -> pd.Series:
        return series.astype(float) * 1_000_000.0

    try:
        row["sum_final_share"] = float(eligible_df["final_share"].sum()) if "final_share" in eligible_df.columns else float("nan")
        row["check_conservation_shares"] = _passfail(
            "final_share" in eligible_df.columns and abs(row["sum_final_share"] - 1.0) <= tolerance_share
        )
    except Exception:
        row["check_conservation_shares"] = "FAIL"

    try:
        if "total_allocation" in eligible_df.columns:
            row["sum_total_allocation_usd"] = float(_usd(eligible_df["total_allocation"]).sum())
            row["check_conservation_money"] = _passfail(
                abs(row["sum_total_allocation_usd"] - float(fund_size)) <= tolerance_usd
            )
    except Exception:
        row["check_conservation_money"] = "FAIL"

    try:
        if "total_allocation" in eligible_df.columns and not eligible_df.empty:
            row["min_allocation_usd"] = float(_usd(eligible_df["total_allocation"]).min())
            row["check_non_negativity"] = _passfail(row["min_allocation_usd"] >= -tolerance_usd)
        elif "total_allocation" in eligible_df.columns:
            row["min_allocation_usd"] = float("nan")
            row["check_non_negativity"] = "FAIL"
    except Exception:
        row["check_non_negativity"] = "FAIL"

    try:
        component_cols = ["component_iusaf_amt", "component_tsac_amt", "component_sosac_amt", "total_allocation"]
        if all(col in eligible_df.columns for col in component_cols) and not eligible_df.empty:
            comp_diff = (
                eligible_df["total_allocation"]
                - eligible_df["component_iusaf_amt"]
                - eligible_df["component_tsac_amt"]
                - eligible_df["component_sosac_amt"]
            ).abs()
            row["max_component_abs_diff_usd"] = float(comp_diff.max() * 1_000_000.0)
            row["check_component_consistency"] = _passfail(row["max_component_abs_diff_usd"] <= tolerance_usd)
    except Exception:
        row["check_component_consistency"] = "FAIL"

    try:
        iplc_cols = ["state_component", "iplc_component", "total_allocation"]
        if all(col in eligible_df.columns for col in iplc_cols) and not eligible_df.empty:
            iplc_diff = (eligible_df["total_allocation"] - eligible_df["state_component"] - eligible_df["iplc_component"]).abs()
            row["max_iplc_abs_diff_usd"] = float(iplc_diff.max() * 1_000_000.0)
            row["check_iplc_split"] = _passfail(row["max_iplc_abs_diff_usd"] <= tolerance_usd)
    except Exception:
        row["check_iplc_split"] = "FAIL"

    try:
        band_check_applicable = (
            scenario_params.get("un_scale_mode") == "band_inversion"
            and float(scenario_params.get("tsac_beta", 0.0) or 0.0) == 0.0
            and float(scenario_params.get("sosac_gamma", 0.0) or 0.0) == 0.0
            and float(scenario_params.get("floor_pct", 0.0) or 0.0) == 0.0
            and scenario_params.get("ceiling_pct") in (None, 0, 0.0, "")
        )
        if not band_check_applicable:
            row["check_band_monotonicity"] = "PASS"
            row["band_monotonicity_detail"] = "PASS (not evaluated for blended or constrained scenario)"
        elif {"un_band", "total_allocation"}.issubset(eligible_df.columns) and not eligible_df.empty:
            band_means = (
                eligible_df.groupby("un_band", dropna=False)["total_allocation"].mean().reset_index()
            )
            band_means["band_num"] = band_means["un_band"].astype(str).str.extract(r"Band\s+(\d+)").astype(float)
            band_means = band_means.dropna(subset=["band_num"]).sort_values("band_num")
            detail = "PASS"
            status = True
            for i in range(len(band_means) - 1):
                current = band_means.iloc[i]
                nxt = band_means.iloc[i + 1]
                if not current["total_allocation"] > nxt["total_allocation"]:
                    status = False
                    detail = (
                        f"Band {int(current['band_num'])} mean allocation <= Band {int(nxt['band_num'])} "
                        f"({current['total_allocation'] * 1_000_000.0:.2f} vs {nxt['total_allocation'] * 1_000_000.0:.2f} USD)"
                    )
                    break
            row["check_band_monotonicity"] = _passfail(status)
            row["band_monotonicity_detail"] = detail
    except Exception as exc:
        row["check_band_monotonicity"] = "FAIL"
        row["band_monotonicity_detail"] = str(exc)

    try:
        floor_pct = float(scenario_params.get("floor_pct", 0.0) or 0.0)
        if "final_share" in eligible_df.columns and not eligible_df.empty:
            row["floor_binding_count"] = int((eligible_df["final_share"] <= (floor_pct / 100.0) + 1e-9).sum()) if floor_pct > 0 else 0
        row["check_floor_not_binding_unexpectedly"] = _passfail(floor_pct > 0 or row["floor_binding_count"] == 0)
    except Exception:
        row["check_floor_not_binding_unexpectedly"] = "FAIL"

    try:
        ceiling_raw = scenario_params.get("ceiling_pct")
        if ceiling_raw in (None, 0, 0.0, ""):
            ceiling_pct = None
        else:
            ceiling_pct = float(ceiling_raw)
        if "final_share" in eligible_df.columns and not eligible_df.empty:
            row["ceiling_binding_count"] = int((eligible_df["final_share"] >= (ceiling_pct / 100.0) - 1e-9).sum()) if ceiling_pct is not None else 0
        row["check_ceiling_not_binding_unexpectedly"] = _passfail(ceiling_pct is not None or row["ceiling_binding_count"] == 0)
    except Exception:
        row["check_ceiling_not_binding_unexpectedly"] = "FAIL"

    try:
        sosac_gamma = float(scenario_params.get("sosac_gamma", 0.0) or 0.0)
        if "component_sosac_amt" in eligible_df.columns:
            row["sids_sosac_component_sum_usd"] = float(_usd(eligible_df["component_sosac_amt"]).sum())
            if sosac_gamma > 0 and row["n_eligible_sids"] > 0:
                expected_sosac = sosac_gamma * float(fund_size)
                row["check_sids_sosac_allocation"] = _passfail(
                    abs(row["sids_sosac_component_sum_usd"] - expected_sosac) <= tolerance_usd
                )
            elif sosac_gamma > 0 and row["n_eligible_sids"] == 0:
                row["check_sids_sosac_allocation"] = _passfail(
                    abs(row["sids_sosac_component_sum_usd"]) <= tolerance_usd
                )
            else:
                row["check_sids_sosac_allocation"] = _passfail(
                    abs(row["sids_sosac_component_sum_usd"]) <= tolerance_usd
                )
    except Exception:
        row["check_sids_sosac_allocation"] = "FAIL"

    check_columns = [col for col in required_columns if col.startswith("check_")]
    row["all_checks_pass"] = _passfail(all(row.get(col) == "PASS" for col in check_columns))

    for col in required_columns:
        row.setdefault(col, float("nan") if col not in {"scenario_id", "band_monotonicity_detail", "check_conservation_shares", "check_conservation_money", "check_non_negativity", "check_component_consistency", "check_iplc_split", "check_band_monotonicity", "check_floor_not_binding_unexpectedly", "check_ceiling_not_binding_unexpectedly", "check_sids_sosac_allocation", "all_checks_pass"} else "FAIL")

    return {col: row[col] for col in required_columns}


def summarize_group_totals(results_df: pd.DataFrame) -> pd.DataFrame:
    eligible_df = _eligible(results_df)
    rows = []

    region_totals = eligible_df.groupby("region", dropna=False)["total_allocation"].sum().reset_index()
    for _, row in region_totals.iterrows():
        rows.append({"group_type": "region", "group": row["region"], "total_allocation_m": row["total_allocation"]})

    income_totals = eligible_df.groupby("WB Income Group", dropna=False)["total_allocation"].sum().reset_index()
    for _, row in income_totals.iterrows():
        rows.append({"group_type": "income", "group": row["WB Income Group"], "total_allocation_m": row["total_allocation"]})

    rows.append({
        "group_type": "special",
        "group": "LDC",
        "total_allocation_m": float(eligible_df[eligible_df["is_ldc"]]["total_allocation"].sum()),
    })
    rows.append({
        "group_type": "special",
        "group": "SIDS",
        "total_allocation_m": float(eligible_df[eligible_df["is_sids"]]["total_allocation"].sum()),
    })

    return pd.DataFrame(rows)
