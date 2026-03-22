# Cali Fund Model v3 — Implementation Instructions

**Repo:** `tierravivaai/cali-allocation-model-v3`  
**Branch:** `main`  
**Status going in:** 6-band configuration implemented and tests updated.  
**Task:** Add balance-point diagnostics, Gini coefficient, fine-grained sweep, and related UI — then rename the stewardship-forward baseline throughout.

Run `python3 -m pytest` after each workstream. All existing tests must stay green.

---

## Context the agent must understand before writing any code

### What this model does

The Cali Fund allocation model distributes biodiversity finance among CBD Parties using:

```
Final_share_i = (1 - beta - gamma) * IUSAF_share_i
              + beta  * TSAC_share_i
              + gamma * SOSAC_share_i
```

- **IUSAF** = band-based inversion of UN Scale of Assessments. Each Party gets its band weight / sum(all band weights). Bands 1–6 from `config/un_scale_bands.yaml`. Band 1 (≤0.001%, n≈31) highest weight 1.50; Band 6 (>10%, China only) lowest weight 0.40.
- **TSAC** = proportional to land area (terrestrial stewardship recognition).
- **SOSAC** = equal share among eligible SIDS (ocean stewardship recognition).
- `beta` = TSAC weight, `gamma` = SOSAC weight. Both must stay < 1.0 combined.

### The balance-point concept — read carefully

TSAC is intended as a **correction** to the IUSAF equity base, not a co-equal component. A parameter setting is **balanced** when, for each eligible Party `i`, the IUSAF component of their allocation is ≥ their TSAC component. The **per-Party TSAC/IUSAF ratio** operationalises this:

```
tsac_iusaf_ratio_i = tsac_component_i / iusaf_component_i
```

Balance condition: `max(tsac_iusaf_ratio_i) <= 1.0` across all eligible Parties.

Three candidate balance points:
- **Strict**: highest `beta` where China's ratio ≤ 1.0 (approx 2.4%)
- **Modified**: highest `beta` where Brazil's ratio ≤ 1.0 (approx 4.9%)
- **Practical**: `beta` that minimises Gini coefficient while keeping Spearman vs pure IUSAF > 0.85

The current scenario called `balanced_baseline` (TSAC=5%, SOSAC=3%) is analytically a **stewardship-forward** setting — China's TSAC/IUSAF ratio is ~2.2× at that point. The rename throughout is intentional and analytically important.

### What already exists in the logic/ layer

The following modules and their key exports are confirmed present:

| Module | Key exports |
|---|---|
| `logic/calculator.py` | `calculate_allocations()`, `aggregate_by_region()`, `aggregate_by_income()`, `get_stewardship_blend_feedback()`, `get_outcome_warning_feedback()` |
| `logic/data_loader.py` | `load_data()`, `get_base_data()` |
| `logic/sensitivity_metrics.py` | `compute_metrics()`, `compute_local_stability_metrics()`, `compute_country_deltas()`, `summarize_group_totals()`, `build_pure_iusaf_comparator()`, `run_invariant_checks()` |
| `logic/sensitivity_scenarios.py` | `get_scenario_library()`, `get_default_ranges()`, `DEFAULT_BASELINE`, `one_way_sweep()`, `two_way_grid()` |
| `logic/reporting.py` | `generate_scenario_brief()`, `generate_sweep_summary()`, `generate_comparative_report()`, `generate_local_stability_markdown()`, `generate_technical_annex()` |

Do not modify existing function signatures. All additions are new functions or new keyword arguments with safe defaults.

### What is confirmed already done in v3

- 6-band YAML configuration (`config/un_scale_bands.yaml`): Band 5 capped at 10%, Band 6 added (weight 0.40, label "Band 6: > 10.0%").
- `app.py` sidebar updated to describe 6 bands with counts and weights.
- Test suite updated for 6-band configuration.
- `component_iusaf_amt`, `component_tsac_amt`, `component_sosac_amt` columns present in `calculate_allocations()` output.
- `un_band`, `un_band_weight` columns present in output.

---

## Workstream 1 — Rename `balanced_baseline` → `stewardship_forward_baseline`

This is a targeted rename across three files. Do it first so all subsequent work uses the correct name.

### 1A — `logic/sensitivity_scenarios.py`

In `get_scenario_library()`, find the key `"balanced_baseline"` and rename it to `"stewardship_forward_baseline"`. If the scenario dict contains a `"description"` or `"label"` key, update its value to:

```
"Exploratory stewardship-forward parameterization (TSAC=5%, SOSAC=3%). "
"Not a validated balance point — see Balance Point Analysis tab for confirmed values."
```

Immediately after `stewardship_forward_baseline` in the library dict, add:

```python
"tsac_strict_balance": {
    **DEFAULT_BASELINE,
    "tsac_beta": 0.024,
    "sosac_gamma": 0.03,
    "scenario_id": "tsac_strict_balance",
},
"tsac_modified_balance": {
    **DEFAULT_BASELINE,
    "tsac_beta": 0.049,
    "sosac_gamma": 0.03,
    "scenario_id": "tsac_modified_balance",
},
```

In `get_default_ranges()`, add two new keys for the fine sweep:

```python
"tsac_beta_fine":    [round(x * 0.005, 3) for x in range(21)],  # 0.000 to 0.100
"sosac_gamma_fine":  [round(x * 0.005, 3) for x in range(21)],  # 0.000 to 0.100
```

### 1B — `sensitivity.py`

Line 71: change the default selectbox index lookup from `"balanced_baseline"` to `"stewardship_forward_baseline"`.

Line 350: change `baseline_id="balanced_baseline"` to `baseline_id="stewardship_forward_baseline"`.

### 1C — `app.py`

Find the preset button with `"5. Balanced"` (approximately line 192). Change:
- Button label: `"5. Stewardship-Forward"`
- `help=` text: `"TSAC=0.05, SOSAC=0.03 — exploratory stewardship-forward setting, not a validated balance point"`

No other changes to `app.py`.

---

## Workstream 2 — Add `compute_gini()` and `compute_component_ratios()` to `logic/sensitivity_metrics.py`

Add both functions to `logic/sensitivity_metrics.py`. Add `import numpy as np` at the top of the file if not already present.

### 2A — `compute_gini()`

```python
def compute_gini(allocations: "pd.Series") -> float:
    """
    Gini coefficient of a non-negative allocation vector.
    Returns value in [0, 1]. 0 = perfect equality, 1 = maximum concentration.
    """
    a = allocations.dropna().values.astype(float)
    a = a[a >= 0]
    n = len(a)
    if n == 0 or a.sum() == 0:
        return 0.0
    a = np.sort(a)
    idx = np.arange(1, n + 1)
    return float((2 * (idx * a).sum()) / (n * a.sum()) - (n + 1) / n)
```

### 2B — `compute_component_ratios()`

```python
def compute_component_ratios(
    results_df: "pd.DataFrame",
    beta: float,
    gamma: float,
) -> dict:
    """
    Compute per-Party TSAC/IUSAF ratio diagnostics.

    Balance condition: tsac_iusaf_ratio_i <= 1.0 for all eligible Parties.

    Requires results_df columns: party, eligible, component_iusaf_amt,
    component_tsac_amt, component_sosac_amt (produced by calculate_allocations()).

    Returns dict with:
        ratio_df                — DataFrame, eligible Parties sorted by ratio desc
        max_tsac_iusaf_ratio    — float
        n_parties_tsac_dominant — int (count where TSAC > IUSAF)
        china_tsac_iusaf_ratio  — float or None
        brazil_tsac_iusaf_ratio — float or None
        tsac_balance_exceeded   — bool (True if max ratio > 1.0)
        sosac_balance_exceeded  — bool (True if any SIDS has SOSAC > IUSAF)
    """
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

    if "component_iusaf_amt" not in eligible.columns or beta == 0:
        return _safe_default

    df = eligible[
        ["party", "component_iusaf_amt", "component_tsac_amt", "component_sosac_amt"]
    ].copy()

    def _ratio(tsac, iusaf):
        return (tsac / iusaf) if iusaf > 0 else float("inf")

    df["tsac_iusaf_ratio"] = df.apply(
        lambda r: _ratio(r["component_tsac_amt"], r["component_iusaf_amt"]), axis=1
    )
    df["sosac_iusaf_ratio"] = df.apply(
        lambda r: _ratio(r["component_sosac_amt"], r["component_iusaf_amt"]), axis=1
    )
    df["tsac_dominant"] = df["tsac_iusaf_ratio"] > 1.0

    def _named_ratio(fragment):
        mask = df["party"].str.contains(fragment, case=False, na=False)
        return float(df.loc[mask, "tsac_iusaf_ratio"].iloc[0]) if mask.any() else None

    china_ratio  = _named_ratio("China")
    brazil_ratio = _named_ratio("Brazil")

    sids_rows = eligible[eligible.get("is_sids", pd.Series(False, index=eligible.index))] \
        if "is_sids" in eligible.columns else \
        eligible[eligible["component_sosac_amt"] > 0]
    sosac_exceeded = False
    if not sids_rows.empty and "component_iusaf_amt" in sids_rows.columns:
        sids_ratios = sids_rows.apply(
            lambda r: _ratio(r["component_sosac_amt"], r["component_iusaf_amt"]), axis=1
        )
        sosac_exceeded = bool((sids_ratios > 1.0).any())

    ratio_df = df[
        ["party", "component_iusaf_amt", "component_tsac_amt",
         "component_sosac_amt", "tsac_iusaf_ratio", "sosac_iusaf_ratio", "tsac_dominant"]
    ].sort_values("tsac_iusaf_ratio", ascending=False)

    finite_ratios = df["tsac_iusaf_ratio"].replace(float("inf"), 0)

    return {
        "ratio_df":                 ratio_df,
        "max_tsac_iusaf_ratio":     float(finite_ratios.max()),
        "n_parties_tsac_dominant":  int(df["tsac_dominant"].sum()),
        "china_tsac_iusaf_ratio":   china_ratio,
        "brazil_tsac_iusaf_ratio":  brazil_ratio,
        "tsac_balance_exceeded":    bool((df["tsac_iusaf_ratio"] > 1.0).any()),
        "sosac_balance_exceeded":   sosac_exceeded,
    }
```

### 2C — Update `compute_metrics()` return dict

`compute_metrics()` already receives `results_df` and `iusaf_results_df`. Add the following to the returned dict. Do not remove or rename any existing keys.

First, add these two calls near the top of the function body (after basic validation):

```python
_ratios = compute_component_ratios(
    results_df,
    float(scenario.get("tsac_beta", 0.0)),
    float(scenario.get("sosac_gamma", 0.0)),
)
_gini = compute_gini(
    results_df.loc[results_df["eligible"], "total_allocation"]
)
_b1_change = _band1_pct_change(results_df, iusaf_results_df)
```

Then add to the returned dict:

```python
"gini_coefficient":              _gini,
"max_tsac_iusaf_ratio":          _ratios["max_tsac_iusaf_ratio"],
"n_parties_tsac_dominant":       _ratios["n_parties_tsac_dominant"],
"china_tsac_iusaf_ratio":        _ratios["china_tsac_iusaf_ratio"],
"brazil_tsac_iusaf_ratio":       _ratios["brazil_tsac_iusaf_ratio"],
"tsac_balance_exceeded":         _ratios["tsac_balance_exceeded"],
"sosac_balance_exceeded":        _ratios["sosac_balance_exceeded"],
"band1_per_party_pct_change_vs_iusaf": _b1_change,
```

### 2D — Add `_band1_pct_change()` helper

Add this private helper to `logic/sensitivity_metrics.py`:

```python
def _band1_pct_change(
    results_df: "pd.DataFrame",
    iusaf_results_df: "pd.DataFrame",
) -> "float | None":
    """
    Percentage change in mean Band 1 per-Party allocation vs pure IUSAF.
    Negative = Band 1 countries receive less under the current scenario.
    """
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
```

---

## Workstream 3 — Create `logic/balance_analysis.py`

Create this file. It has no Streamlit imports — pure Python, pandas, numpy only.

```python
"""
logic/balance_analysis.py

Fine-grained parameter sweeps and balance-point identification.

Balance condition: tsac_component_i / iusaf_component_i <= 1.0 for all eligible Parties i.

Balance points:
    strict    highest beta where China's TSAC/IUSAF ratio <= 1.0
    modified  highest beta where Brazil's TSAC/IUSAF ratio <= 1.0
    practical beta minimising Gini coefficient, subject to Spearman vs pure IUSAF > 0.85
    sosac     highest gamma where SOSAC/IUSAF ratio <= 1.0 for average SIDS Party
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Callable


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
    """
    Run a fine-grained single-parameter sweep.

    sweep_param: "tsac_beta" or "sosac_gamma"
    values: list of floats. Defaults to 0.000, 0.005, ..., 0.100 (21 values).

    Returns DataFrame with one row per sweep value.
    """
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
            base_df, {**iusaf_s, "equality_mode": True,
                      "scenario_id": f"{s['scenario_id']}_eq"}
        )

        metrics = compute_metrics_fn(s, results, iusaf_results, eq_results)
        ratios = compute_component_ratios_fn(
            results,
            float(s.get("tsac_beta", 0.0)),
            float(s.get("sosac_gamma", 0.0)),
        )

        eligible = results[results["eligible"]]

        # Band 1 stats
        band1_alloc = None
        b1_pct_change = None
        if "un_band" in eligible.columns:
            b1 = eligible[eligible["un_band"].str.startswith("Band 1", na=False)]
            b1_ref = iusaf_results[
                iusaf_results["eligible"] &
                iusaf_results["un_band"].str.startswith("Band 1", na=False)
            ]
            if not b1.empty:
                band1_alloc = float(b1["total_allocation"].mean()) / 1_000_000
                if not b1_ref.empty:
                    ref_mean = float(b1_ref["total_allocation"].mean())
                    b1_pct_change = (
                        (float(b1["total_allocation"].mean()) - ref_mean) / ref_mean * 100
                        if ref_mean > 0 else None
                    )

        # Group totals in $m
        sids_total = (
            eligible.loc[eligible["is_sids"], "total_allocation"].sum() / 1_000_000
            if "is_sids" in eligible.columns else None
        )
        ldc_total = (
            eligible.loc[eligible.get("UN LDC", pd.Series()) == "LDC", "total_allocation"].sum() / 1_000_000
            if "UN LDC" in eligible.columns else None
        )

        rows.append({
            "sweep_param":               sweep_param,
            "sweep_value":               val,
            "spearman_vs_pure_iusaf":    metrics.get("spearman_vs_pure_iusaf"),
            "gini_coefficient":          metrics.get("gini_coefficient"),
            "pct_below_equality":        metrics.get("pct_below_equality"),
            "max_tsac_iusaf_ratio":      ratios["max_tsac_iusaf_ratio"],
            "china_tsac_iusaf_ratio":    ratios["china_tsac_iusaf_ratio"],
            "brazil_tsac_iusaf_ratio":   ratios["brazil_tsac_iusaf_ratio"],
            "n_parties_tsac_dominant":   ratios["n_parties_tsac_dominant"],
            "tsac_balance_exceeded":     ratios["tsac_balance_exceeded"],
            "band1_per_party_alloc_m":   band1_alloc,
            "band1_pct_change_vs_iusaf": b1_pct_change,
            "sids_total_m":              sids_total,
            "ldc_total_m":               ldc_total,
        })

    return pd.DataFrame(rows)


def identify_balance_points(
    tsac_sweep_df: pd.DataFrame,
    sosac_sweep_df: pd.DataFrame,
    spearman_moderate_threshold: float = 0.85,
) -> dict:
    """
    Scan fine sweep outputs and identify four balance points.

    Returns dict with keys: strict, modified, practical, sosac.
    Each value is {"value": float, "metrics": dict} or None if not found.
    """

    def _last_row_where(df, col, threshold):
        """Last row where col <= threshold (scanning ascending sweep_value)."""
        mask = df[col].notna() & (df[col] <= threshold)
        return df[mask].iloc[-1] if mask.any() else None

    def _min_gini_above_spearman(df, spearman_thresh):
        mask = (
            df["spearman_vs_pure_iusaf"].notna() &
            (df["spearman_vs_pure_iusaf"] > spearman_thresh) &
            df["gini_coefficient"].notna()
        )
        if not mask.any():
            return None
        return df[mask].loc[df[mask]["gini_coefficient"].idxmin()]

    def _fmt(row):
        return {"value": float(row["sweep_value"]), "metrics": row.to_dict()} if row is not None else None

    return {
        "strict":    _fmt(_last_row_where(tsac_sweep_df, "china_tsac_iusaf_ratio", 1.0)),
        "modified":  _fmt(_last_row_where(tsac_sweep_df, "brazil_tsac_iusaf_ratio", 1.0)),
        "practical": _fmt(_min_gini_above_spearman(tsac_sweep_df, spearman_moderate_threshold)),
        "sosac":     _fmt(_last_row_where(sosac_sweep_df, "max_tsac_iusaf_ratio", 1.0)),
    }


def generate_balance_point_summary(
    balance_points: dict,
    tsac_sweep_df: pd.DataFrame,
    sosac_sweep_df: pd.DataFrame,
    stewardship_forward_beta: float = 0.05,
    stewardship_forward_gamma: float = 0.03,
) -> str:
    """Generate a Markdown report summarising identified balance points."""

    def _tbl(m: dict) -> list[str]:
        rows = []
        fields = [
            ("sweep_value",                 "Parameter value",      lambda v: f"**{v:.1%}**"),
            ("spearman_vs_pure_iusaf",      "Spearman vs pure IUSAF", lambda v: f"{v:.4f}"),
            ("gini_coefficient",            "Gini coefficient",      lambda v: f"{v:.4f}"),
            ("china_tsac_iusaf_ratio",      "China TSAC/IUSAF ratio", lambda v: f"{v:.3f}×"),
            ("brazil_tsac_iusaf_ratio",     "Brazil TSAC/IUSAF ratio", lambda v: f"{v:.3f}×"),
            ("band1_per_party_alloc_m",     "Band 1 per-Party ($m)",  lambda v: f"${v:.3f}m"),
            ("band1_pct_change_vs_iusaf",   "Band 1 change vs IUSAF", lambda v: f"{v:+.1f}%"),
            ("sids_total_m",                "SIDS total ($m)",        lambda v: f"${v:.1f}m"),
            ("ldc_total_m",                 "LDC total ($m)",         lambda v: f"${v:.1f}m"),
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
        "A parameter setting is **balanced** when, for every eligible Party, "
        "the IUSAF equity component is at least as large as the TSAC stewardship component. "
        "Formally: `tsac_component_i / iusaf_component_i ≤ 1.0` for all eligible Parties `i`.",
        "",
        f"The **stewardship-forward baseline** "
        f"(TSAC={stewardship_forward_beta:.0%}, SOSAC={stewardship_forward_gamma:.0%}) "
        f"exceeds both the strict and modified balance points and is not a balanced setting. "
        f"It is retained as a named scenario for reference purposes only.",
        "",
        "---",
        "",
        "## Results",
        "",
    ]

    bp_meta = {
        "strict": (
            "Strict balance point",
            "Highest TSAC weight where China's TSAC/IUSAF ratio ≤ 1.0. "
            "China (Band 6) is the binding constraint: largest land area, lowest IUSAF base.",
        ),
        "modified": (
            "Modified balance point",
            "Highest TSAC weight where Brazil's TSAC/IUSAF ratio ≤ 1.0. "
            "Treats China separately (addressed by Band 6 weight); requires IUSAF dominance "
            "for all Band 5 Parties (Brazil, India, Mexico).",
        ),
        "practical": (
            "Practical balance point",
            "TSAC weight that minimises the Gini coefficient while keeping "
            "Spearman rank correlation vs pure IUSAF > 0.85 "
            "(threshold for moderate rather than dominant overlay).",
        ),
        "sosac": (
            "SOSAC balance point",
            "Highest SOSAC weight (TSAC held at 0) where the SOSAC component does not "
            "exceed the IUSAF component for any SIDS Party.",
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
        else:
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
        "- The **practical point** optimises distributional equality (Gini) within the constraint that the allocation remains a moderate rather than dominant overlay on the IUSAF base.",
        "",
        "## Note on China and TSAC",
        "",
        "Band 6 was introduced to give China a lower IUSAF base allocation than Band 5 Parties, "
        "reflecting its much larger UN assessed contribution (20% vs ~1.1–1.4% for Brazil, India, Mexico). "
        "However, China also receives a full TSAC allocation proportional to its land area (~9.6M km²), "
        "which partially offsets the Band 6 adjustment. "
        "At TSAC=5%, China's combined allocation exceeds Brazil's despite the Band 6 distinction. "
        "Parties may wish to consider whether a separate, lower TSAC coefficient for Band 6 is appropriate.",
        "",
        "---",
        "*Generated by logic/balance_analysis.py. All figures are illustrative modelling outputs.*",
    ]

    return "\n".join(sections)
```

---

## Workstream 4 — Update `logic/reporting.py`

At the bottom of `logic/reporting.py`, add a re-export so callers can import `generate_balance_point_summary` from either module:

```python
from logic.balance_analysis import generate_balance_point_summary  # noqa: F401
```

If the file has an `__all__` list, append `"generate_balance_point_summary"` to it.

---

## Workstream 5 — Update `sensitivity.py`

Make the following targeted changes. The file is 389 lines. Do not remove any existing code.

### 5A — Imports (top of file)

Add after the existing imports:

```python
from logic.balance_analysis import (
    run_fine_sweep,
    identify_balance_points,
    generate_balance_point_summary,
)
from logic.sensitivity_metrics import compute_component_ratios
```

### 5B — Rename `balanced_baseline` (already in Workstream 1B — confirm done)

### 5C — Add `gini_coefficient` and `max_tsac_iusaf_ratio` to the heatmap options

Find:
```python
heat_metric = st.selectbox("Heatmap metric", options=["spearman_vs_pure_iusaf", "pct_below_equality", "sids_total", "hhi", "top20_turnover_vs_pure_iusaf"], index=0)
```

Replace with:
```python
heat_metric = st.selectbox(
    "Heatmap metric",
    options=[
        "spearman_vs_pure_iusaf",
        "pct_below_equality",
        "gini_coefficient",
        "max_tsac_iusaf_ratio",
        "sids_total",
        "hhi",
        "top20_turnover_vs_pure_iusaf",
    ],
    index=0,
)
```

### 5D — Add Tab 5

Change the tabs declaration from:

```python
tab1, tab2, tab3, tab4 = st.tabs(["Parameter Sweep", "Robustness Diagnostics", "Thresholds and Tipping Points", "Attack Surface Report"])
```

to:

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Parameter Sweep",
    "Robustness Diagnostics",
    "Thresholds and Tipping Points",
    "Attack Surface Report",
    "Balance Point Analysis",
])
```

### 5E — Add Tab 5 content

Add the following block **after** the closing of `with tab4:` and **before** `st.divider()`.

```python
with tab5:
    st.subheader("Balance Point Analysis")
    st.markdown(
        "Identifies the TSAC and SOSAC weights at which the IUSAF equity base remains "
        "the **dominant component** of each Party's allocation. "
        "The balance condition is: `tsac_component_i / iusaf_component_i ≤ 1.0` for all eligible Parties.\n\n"
        "Three candidate TSAC balance points are identified from fine-grained sweeps at 0.5 pp intervals."
    )

    # ── Current scenario ratios ───────────────────────────────────────────
    st.markdown("### Current scenario — per-Party TSAC/IUSAF ratios")
    current_ratios = compute_component_ratios(
        current_results,
        float(scenario.get("tsac_beta", 0.0)),
        float(scenario.get("sosac_gamma", 0.0)),
    )

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric(
        "Max TSAC/IUSAF ratio",
        f"{current_ratios['max_tsac_iusaf_ratio']:.2f}×",
        help="Balance condition: ≤ 1.0 for all Parties",
    )
    col_r2.metric(
        "China ratio",
        f"{current_ratios['china_tsac_iusaf_ratio']:.2f}×"
        if current_ratios["china_tsac_iusaf_ratio"] is not None else "n/a",
        help="Strict balance point binding constraint",
    )
    col_r3.metric(
        "Brazil ratio",
        f"{current_ratios['brazil_tsac_iusaf_ratio']:.2f}×"
        if current_ratios["brazil_tsac_iusaf_ratio"] is not None else "n/a",
        help="Modified balance point binding constraint",
    )
    col_r4.metric(
        "Parties where TSAC > IUSAF",
        str(current_ratios["n_parties_tsac_dominant"]),
    )

    if current_ratios["tsac_balance_exceeded"]:
        st.warning(
            f"⚠ TSAC is the dominant component for "
            f"**{current_ratios['n_parties_tsac_dominant']} Parties** at current settings. "
            "The balance condition is not satisfied. See sweep below for balance points."
        )
    else:
        st.success("✓ Balance condition satisfied: IUSAF is dominant for all Parties.")

    if not current_ratios["ratio_df"].empty:
        st.dataframe(
            current_ratios["ratio_df"].head(20),
            column_config={
                "component_iusaf_amt": st.column_config.NumberColumn("IUSAF ($m)", format="$%.3f"),
                "component_tsac_amt":  st.column_config.NumberColumn("TSAC ($m)",  format="$%.3f"),
                "tsac_iusaf_ratio":    st.column_config.NumberColumn("TSAC/IUSAF ratio", format="%.3f"),
                "tsac_dominant":       st.column_config.CheckboxColumn("TSAC dominant?"),
            },
            use_container_width=True,
        )

    st.divider()

    # ── Fine sweep ────────────────────────────────────────────────────────
    st.markdown("### Fine-grained sweep (0.5 pp intervals, 0–10%)")
    st.caption("21 TSAC scenarios + 21 SOSAC scenarios. May take 30–60 seconds.")

    if "bp_tsac_sweep" not in st.session_state:
        st.session_state["bp_tsac_sweep"] = None
    if "bp_sosac_sweep" not in st.session_state:
        st.session_state["bp_sosac_sweep"] = None
    if "bp_results" not in st.session_state:
        st.session_state["bp_results"] = None

    if st.button("▶ Run fine-grained sweep", type="primary"):
        with st.spinner("TSAC sweep…"):
            st.session_state["bp_tsac_sweep"] = run_fine_sweep(
                base_scenario=scenario,
                base_df=base_df,
                run_scenario_fn=run_scenario,
                compute_metrics_fn=compute_metrics,
                compute_component_ratios_fn=compute_component_ratios,
                build_pure_iusaf_fn=build_pure_iusaf_comparator,
                sweep_param="tsac_beta",
                values=ranges.get("tsac_beta_fine"),
            )
        with st.spinner("SOSAC sweep…"):
            sosac_base = {**scenario, "tsac_beta": 0.0}
            st.session_state["bp_sosac_sweep"] = run_fine_sweep(
                base_scenario=sosac_base,
                base_df=base_df,
                run_scenario_fn=run_scenario,
                compute_metrics_fn=compute_metrics,
                compute_component_ratios_fn=compute_component_ratios,
                build_pure_iusaf_fn=build_pure_iusaf_comparator,
                sweep_param="sosac_gamma",
                values=ranges.get("sosac_gamma_fine"),
            )
        with st.spinner("Identifying balance points…"):
            st.session_state["bp_results"] = identify_balance_points(
                tsac_sweep_df=st.session_state["bp_tsac_sweep"],
                sosac_sweep_df=st.session_state["bp_sosac_sweep"],
            )
        st.success("Sweep complete.")

    if st.session_state["bp_tsac_sweep"] is not None:
        tsac_df = st.session_state["bp_tsac_sweep"]
        sosac_df = st.session_state["bp_sosac_sweep"]
        bp = st.session_state["bp_results"]

        # Charts
        import plotly.graph_objects as _go

        fig1 = _go.Figure()
        fig1.add_trace(_go.Scatter(
            x=tsac_df["sweep_value"] * 100,
            y=tsac_df["china_tsac_iusaf_ratio"],
            name="China TSAC/IUSAF", mode="lines+markers",
            line=dict(color="crimson"),
        ))
        fig1.add_trace(_go.Scatter(
            x=tsac_df["sweep_value"] * 100,
            y=tsac_df["brazil_tsac_iusaf_ratio"],
            name="Brazil TSAC/IUSAF", mode="lines+markers",
            line=dict(color="orange"),
        ))
        fig1.add_hline(y=1.0, line_dash="dash", line_color="grey",
                       annotation_text="Balance threshold")
        fig1.update_layout(
            title="TSAC/IUSAF ratio by TSAC weight",
            xaxis_title="TSAC weight (%)",
            yaxis_title="Ratio",
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = _go.Figure()
        fig2.add_trace(_go.Scatter(
            x=tsac_df["sweep_value"] * 100,
            y=tsac_df["gini_coefficient"],
            name="Gini coefficient", mode="lines+markers",
            line=dict(color="purple"),
        ))
        fig2.add_trace(_go.Scatter(
            x=tsac_df["sweep_value"] * 100,
            y=tsac_df["spearman_vs_pure_iusaf"],
            name="Spearman vs pure IUSAF", mode="lines+markers",
            line=dict(color="steelblue", dash="dot"),
            yaxis="y2",
        ))
        fig2.add_hline(y=0.85, line_dash="dot", line_color="steelblue",
                       annotation_text="Moderate overlay threshold (0.85)")
        fig2.update_layout(
            title="Gini coefficient and Spearman by TSAC weight",
            xaxis_title="TSAC weight (%)",
            yaxis_title="Gini coefficient",
            yaxis2=dict(title="Spearman", overlaying="y", side="right", range=[0, 1]),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Balance point table
        st.markdown("#### Identified balance points")
        if bp:
            bp_rows = []
            labels = {
                "strict":    "Strict (China ≤ 1.0)",
                "modified":  "Modified (Brazil ≤ 1.0)",
                "practical": "Practical (min Gini, Spearman > 0.85)",
                "sosac":     "SOSAC balance",
            }
            for key, label in labels.items():
                point = bp.get(key)
                if point:
                    m = point["metrics"]
                    def _f(k, fmt="{:.3f}"):
                        v = m.get(k)
                        try:
                            return fmt.format(v) if v is not None and not (isinstance(v, float) and __import__("math").isnan(v)) else "n/a"
                        except Exception:
                            return "n/a"
                    bp_rows.append({
                        "Balance point":    label,
                        "Value":            f"{point['value']:.1%}",
                        "China ratio":      _f("china_tsac_iusaf_ratio", "{:.2f}×"),
                        "Brazil ratio":     _f("brazil_tsac_iusaf_ratio", "{:.2f}×"),
                        "Gini":             _f("gini_coefficient", "{:.4f}"),
                        "Spearman":         _f("spearman_vs_pure_iusaf", "{:.4f}"),
                        "Band 1 change":    _f("band1_pct_change_vs_iusaf", "{:+.1f}%"),
                        "SIDS total ($m)":  _f("sids_total_m", "${:.1f}m"),
                    })
                else:
                    bp_rows.append({"Balance point": label, "Value": "Not found in range"})
            st.dataframe(pd.DataFrame(bp_rows), hide_index=True, use_container_width=True)

        # Raw data
        with st.expander("Raw sweep data"):
            st.dataframe(tsac_df, use_container_width=True)
            st.dataframe(sosac_df, use_container_width=True)
```

### 5F — Expand the download section

Find:
```python
e1, e2, e3, e4, e5 = st.columns(5)
```

Replace with:
```python
e1, e2, e3, e4, e5, e6 = st.columns(6)
```

Add after the `with e5:` block:

```python
with e6:
    if (
        st.session_state.get("bp_results") is not None
        and st.session_state.get("bp_tsac_sweep") is not None
    ):
        bp_md = generate_balance_point_summary(
            balance_points=st.session_state["bp_results"],
            tsac_sweep_df=st.session_state["bp_tsac_sweep"],
            sosac_sweep_df=st.session_state["bp_sosac_sweep"],
        )
        st.download_button(
            "Balance Point Summary (.md)",
            bp_md.encode("utf-8"),
            file_name="balance_point_summary.md",
        )
        st.download_button(
            "TSAC Fine Sweep (.csv)",
            csv_bytes(st.session_state["bp_tsac_sweep"]),
            file_name="tsac_fine_sweep.csv",
            mime="text/csv",
        )
        st.download_button(
            "SOSAC Fine Sweep (.csv)",
            csv_bytes(st.session_state["bp_sosac_sweep"]),
            file_name="sosac_fine_sweep.csv",
            mime="text/csv",
        )
    else:
        st.caption("Run balance-point sweep to enable these exports.")
```

### 5G — Fix plotly import in tab5

`sensitivity.py` already imports `plotly.graph_objects as go` and `plotly.express as px` at the top. In the tab5 block above, replace `import plotly.graph_objects as _go` with just `go` (using the existing module-level import). The `_go.Figure()` calls become `go.Figure()`, `_go.Scatter` becomes `go.Scatter`.

---

## Workstream 6 — Tests

Create `tests/test_balance_analysis.py`:

```python
"""Tests for balance-point diagnostics."""
from __future__ import annotations

import math
import pandas as pd
import numpy as np
import pytest
import duckdb

from logic.data_loader import load_data, get_base_data
from logic.calculator import calculate_allocations
from logic.sensitivity_metrics import compute_gini, compute_component_ratios
from logic.balance_analysis import (
    run_fine_sweep,
    identify_balance_points,
    generate_balance_point_summary,
)
from logic.sensitivity_scenarios import get_default_ranges, DEFAULT_BASELINE
from logic.sensitivity_metrics import build_pure_iusaf_comparator, compute_metrics


@pytest.fixture(scope="module")
def base_df():
    con = duckdb.connect(database=":memory:")
    load_data(con)
    return get_base_data(con)


def _run(base_df, **overrides):
    params = dict(
        fund_size=1_000_000_000,
        iplc_share_pct=50,
        exclude_high_income=True,
        floor_pct=0.0,
        ceiling_pct=None,
        tsac_beta=0.0,
        sosac_gamma=0.0,
        equality_mode=False,
        un_scale_mode="band_inversion",
    )
    params.update(overrides)
    return calculate_allocations(base_df, **params)


# ── compute_gini ──────────────────────────────────────────────────────────

class TestComputeGini:
    def test_perfect_equality(self):
        assert compute_gini(pd.Series([100.0] * 10)) == pytest.approx(0.0, abs=1e-6)

    def test_maximum_inequality(self):
        s = pd.Series([0.0] * 9 + [100.0])
        assert compute_gini(s) == pytest.approx(0.9, abs=0.01)

    def test_empty_returns_zero(self):
        assert compute_gini(pd.Series([], dtype=float)) == 0.0

    def test_real_results_in_range(self, base_df):
        results = _run(base_df)
        g = compute_gini(results.loc[results["eligible"], "total_allocation"])
        assert 0.0 <= g <= 1.0

    def test_stewardship_forward_higher_gini_than_iusaf(self, base_df):
        iusaf = _run(base_df)
        sf = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        g_iusaf = compute_gini(iusaf.loc[iusaf["eligible"], "total_allocation"])
        g_sf = compute_gini(sf.loc[sf["eligible"], "total_allocation"])
        # More concentrated = higher Gini expected at stewardship-forward
        assert g_sf >= g_iusaf - 0.05  # allow small tolerance


# ── compute_component_ratios ──────────────────────────────────────────────

class TestComputeComponentRatios:
    def test_zero_tsac_returns_zero(self, base_df):
        results = _run(base_df)
        r = compute_component_ratios(results, beta=0.0, gamma=0.0)
        assert r["max_tsac_iusaf_ratio"] == pytest.approx(0.0)
        assert r["tsac_balance_exceeded"] is False
        assert r["n_parties_tsac_dominant"] == 0

    def test_high_tsac_exceeds_balance(self, base_df):
        results = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        r = compute_component_ratios(results, beta=0.05, gamma=0.03)
        assert r["tsac_balance_exceeded"] is True
        assert r["china_tsac_iusaf_ratio"] is not None
        assert r["china_tsac_iusaf_ratio"] > 1.0

    def test_china_highest_ratio(self, base_df):
        results = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        r = compute_component_ratios(results, beta=0.05, gamma=0.03)
        # China has largest land / lowest IUSAF → highest ratio
        assert r["china_tsac_iusaf_ratio"] >= (r["brazil_tsac_iusaf_ratio"] or 0)

    def test_ratio_df_sorted_descending(self, base_df):
        results = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        r = compute_component_ratios(results, beta=0.05, gamma=0.03)
        df = r["ratio_df"]
        if len(df) > 1:
            assert df["tsac_iusaf_ratio"].iloc[0] >= df["tsac_iusaf_ratio"].iloc[-1]

    def test_required_columns_present(self, base_df):
        results = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        r = compute_component_ratios(results, beta=0.05, gamma=0.03)
        for col in ["party", "tsac_iusaf_ratio", "tsac_dominant"]:
            assert col in r["ratio_df"].columns


# ── identify_balance_points ───────────────────────────────────────────────

def _sweep_row(val, china, brazil, gini, spearman):
    return {
        "sweep_value": val,
        "china_tsac_iusaf_ratio": china,
        "brazil_tsac_iusaf_ratio": brazil,
        "gini_coefficient": gini,
        "spearman_vs_pure_iusaf": spearman,
        "max_tsac_iusaf_ratio": max(china, brazil),
    }


class TestIdentifyBalancePoints:
    def test_strict_identified(self):
        rows = [
            _sweep_row(0.020, 0.90, 0.45, 0.15, 0.93),
            _sweep_row(0.025, 1.05, 0.52, 0.16, 0.90),
        ]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df)
        assert bp["strict"] is not None
        assert bp["strict"]["value"] == pytest.approx(0.020, abs=0.001)

    def test_modified_identified(self):
        rows = [
            _sweep_row(0.045, 2.1, 0.98, 0.19, 0.87),
            _sweep_row(0.050, 2.3, 1.05, 0.20, 0.82),
        ]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df)
        assert bp["modified"] is not None
        assert bp["modified"]["value"] == pytest.approx(0.045, abs=0.001)

    def test_practical_is_min_gini_above_spearman(self):
        rows = [
            _sweep_row(0.010, 0.40, 0.20, 0.20, 0.95),
            _sweep_row(0.020, 0.80, 0.40, 0.13, 0.92),  # min Gini, Spearman > 0.85
            _sweep_row(0.090, 3.00, 1.50, 0.26, 0.79),  # excluded: Spearman < 0.85
        ]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df, spearman_moderate_threshold=0.85)
        assert bp["practical"] is not None
        assert bp["practical"]["value"] == pytest.approx(0.020, abs=0.001)

    def test_returns_none_when_never_satisfied(self):
        rows = [_sweep_row(0.01, 1.5, 1.2, 0.20, 0.92)]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df)
        assert bp["strict"] is None
        assert bp["modified"] is None


# ── generate_balance_point_summary ───────────────────────────────────────

class TestGenerateBalancePointSummary:
    def _bp(self):
        return {
            "strict": {
                "value": 0.024,
                "metrics": {
                    "sweep_value": 0.024,
                    "gini_coefficient": 0.148,
                    "spearman_vs_pure_iusaf": 0.931,
                    "china_tsac_iusaf_ratio": 1.00,
                    "brazil_tsac_iusaf_ratio": 0.49,
                    "band1_pct_change_vs_iusaf": -2.4,
                    "band1_per_party_alloc_m": 8.31,
                    "sids_total_m": 305.0,
                    "ldc_total_m": 328.0,
                },
            },
            "modified": None,
            "practical": None,
            "sosac": None,
        }

    def test_returns_string(self):
        md = generate_balance_point_summary(self._bp(), pd.DataFrame(), pd.DataFrame())
        assert isinstance(md, str)

    def test_contains_all_four_sections(self):
        md = generate_balance_point_summary(
            {"strict": None, "modified": None, "practical": None, "sosac": None},
            pd.DataFrame(), pd.DataFrame(),
        )
        for section in ["Strict balance point", "Modified balance point",
                        "Practical balance point", "SOSAC balance point"]:
            assert section in md

    def test_strict_value_present(self):
        md = generate_balance_point_summary(self._bp(), pd.DataFrame(), pd.DataFrame())
        assert "2.4%" in md

    def test_stewardship_forward_mentioned(self):
        md = generate_balance_point_summary(self._bp(), pd.DataFrame(), pd.DataFrame())
        assert "stewardship-forward" in md.lower()
```

---

## Acceptance criteria

Run `python3 -m pytest` — all existing and new tests must pass.

Verify the following manually by running `streamlit run sensitivity.py`:

1. Default scenario in the sidebar selectbox is `stewardship_forward_baseline`.
2. `tsac_strict_balance` and `tsac_modified_balance` appear in the scenario dropdown.
3. Tab 5 "Balance Point Analysis" appears and loads without error.
4. With stewardship-forward settings (TSAC=5%, SOSAC=3%), the warning "TSAC is the dominant component for N Parties" appears and the per-Party ratio table shows China at approximately 2.2× and Brazil at approximately 1.0×.
5. Clicking "▶ Run fine-grained sweep" runs successfully and populates the ratio/Gini/Spearman charts and the balance point table.
6. The strict balance point is identified at approximately 2.4% TSAC; modified at approximately 4.9%.
7. `balance_point_summary.md`, `tsac_fine_sweep.csv`, and `sosac_fine_sweep.csv` download buttons appear after the sweep.
8. The heatmap in Tab 1 includes `gini_coefficient` and `max_tsac_iusaf_ratio` as options.
9. In `app.py`, the preset button reads "5. Stewardship-Forward".
10. `compute_metrics()` output includes `gini_coefficient`, `max_tsac_iusaf_ratio`, `china_tsac_iusaf_ratio`, `brazil_tsac_iusaf_ratio`, `tsac_balance_exceeded`, `band1_per_party_pct_change_vs_iusaf`.

---

## Files summary

| Action | File | Workstream |
|---|---|---|
| MODIFY | `logic/sensitivity_scenarios.py` | 1A |
| MODIFY | `sensitivity.py` | 1B, 5A–5G |
| MODIFY | `app.py` | 1C |
| MODIFY | `logic/sensitivity_metrics.py` | 2A–2D |
| CREATE | `logic/balance_analysis.py` | 3 |
| MODIFY | `logic/reporting.py` | 4 |
| CREATE | `tests/test_balance_analysis.py` | 6 |

**Do not modify:** `logic/calculator.py`, `logic/data_loader.py`, `config/un_scale_bands.yaml`, `requirements.txt`, any existing test files.
