# Reporting Fixes — Implementation Instructions

**Repo:** `tierravivaai/cali-allocation-model-v3`  
**Branch:** `main`  
**Scope:** Three fixes to the reporting layer addressing findings from independent review.  
**Run `python3 -m pytest` after each workstream. All existing tests must stay green.**

---

## Background the agent must understand

An independent review of the exported report pack identified three findings, all confirmed against the CSV exports. None involve calculation errors. All are in the reporting and labelling layer.

**Finding 1 (substantive):** The `balance_points.csv` export labels TSAC=5% as `practical` — implying it is a balance point — but `tsac_balance_exceeded=True` for that row. The document defines balanced as `tsac_component_i / iusaf_component_i ≤ 1.0` for all eligible Parties. The 5% setting fails this condition for China (2.869×) and Brazil (1.362×). The label is materially misleading. Decision taken: rename to `gini_optimal` throughout, reflecting that this setting is identified by minimising the Gini coefficient subject to Spearman > 0.85 — which is a different criterion from the balance condition used to identify the strict and modified points.

**Finding 2 (minor):** The generated `sweep_summary.md` correctly identifies the first row where the departure flag fires (`tsac_beta_sweep_0.0`) but attributes the trigger to Spearman=0.9771, which does not cross the <0.95 threshold. The actual trigger is `top20_turnover_vs_pure_iusaf=0.8 (80%)`, which does exceed the >20% threshold. The report names the correct row but the wrong metric.

**Finding 3 (utility gap):** The report pack asserts mechanical validity in prose but exports no file a human reviewer can use to verify it independently. The existing `scenario_metrics.csv` contains several relevant columns (`sum_final_share`, `sum_total_allocation`, `negative_count`, `floor_binding_count`, `ceiling_binding_count`) but does not surface all invariants, and these columns are not framed for a reviewer — they are buried among 60+ columns. A dedicated `integrity_checks.csv` is needed.

---

## Workstream 1 — Rename `practical` to `gini_optimal`

### 1A — `logic/balance_analysis.py`

Find the section that identifies and records the three TSAC balance points. The third entry is currently labelled `practical` or `"practical"`. Change the label string to `"gini_optimal"` everywhere it appears in this file.

The identification logic itself does not change. The `gini_optimal` point is still the TSAC weight that minimises the Gini coefficient while keeping Spearman rank correlation vs pure IUSAF above 0.85. Only the label changes.

Also update any comment or docstring in this file that refers to the "practical balance point" by name. Change to "Gini-optimal point" in comments.

### 1B — `balance_point_summary.md` template or generator

The generated `balance_point_summary.md` currently contains a section headed `### Practical balance point`. Change to `### Gini-optimal point`.

The description of this point currently reads something like:

> TSAC weight that minimises the Gini coefficient while keeping Spearman rank correlation vs pure IUSAF > 0.85 (threshold for moderate rather than dominant overlay).

Add the following sentence immediately after this description, before the metrics table:

> *Note: this point is identified by a different criterion from the strict and modified balance points. The Spearman constraint (> 0.85) binds: the unconstrained Gini minimum is at TSAC=5.5% (Spearman=0.822, which fails the threshold), so the constrained optimum is TSAC=5.0% — the last point where Spearman remains above 0.85. The description "minimises the Gini coefficient while keeping Spearman rank correlation vs pure IUSAF > 0.85" is therefore precise and should be kept exactly as written. This point does not satisfy the TSAC/IUSAF dominance balance condition — `tsac_balance_exceeded` is `True`, meaning TSAC exceeds IUSAF for China and Brazil. It is included here as a distributional optimum, not as a balanced setting in the TSAC/IUSAF sense.*

Also update the "Choosing among balance points" section. The bullet that currently refers to "the practical point" should now read:

> - The **Gini-optimal point** (TSAC=5%, SOSAC=3%) minimises the Gini coefficient within the constraint that the allocation remains a moderate overlay on the IUSAF base (Spearman > 0.85). It does not satisfy the TSAC/IUSAF balance condition and should not be read as a "balanced" setting in that sense. It is the default scenario in the application because it produces the most equal per-Party distribution measurable by Gini.

### 1C — `logic/sensitivity_scenarios.py`

The scenario key `practical_balance_point` was renamed in a previous workstream. Verify it has already been renamed to `gini_optimal_point`. If it has not, rename it now.

Also rename the three floor/ceiling variant keys if they still carry the `practical_` prefix from the previous renaming:

| Old key | New key |
|---|---|
| `practical_balance_point` | `gini_optimal_point` |
| `practical_floor_005` | `gini_optimal_floor_005` |
| `practical_ceiling_1` | `gini_optimal_ceiling_1` |
| `practical_floor_005_ceiling_1` | `gini_optimal_floor_005_ceiling_1` |

Update the description field of each to reference "Gini-optimal point" rather than "practical balance point."

### 1D — `sensitivity.py`

Line 71 sets the default scenario in the selector. If it currently reads `"practical_balance_point"`, update to `"gini_optimal_point"`.

Line 350 passes `baseline_id` to `generate_comparative_report()`. If it currently reads `baseline_id="practical_balance_point"`, update to `baseline_id="gini_optimal_point"`.

### 1E — `app.py`

Preset button 5 was labelled "5. Practical Balance Point" in a previous workstream. Update to:

```python
if st.button("5. Gini-optimal point",
             help="TSAC=5%, SOSAC=3% — Gini-optimal point (minimises Gini, Spearman > 0.85)",
             use_container_width=True):
```

Parameter assignments (TSAC=0.05, SOSAC=0.03) do not change.

### 1F — Tests

In any test file that references `"practical_balance_point"` or `"practical"` as a scenario key or balance point label, update to `"gini_optimal_point"` or `"gini_optimal"` respectively.

Add the following tests:

```python
def test_gini_optimal_label():
    """Balance point labelled gini_optimal must have tsac_balance_exceeded=True."""
    from logic.balance_analysis import identify_balance_points
    # The gini_optimal point is NOT a balanced setting in the TSAC/IUSAF sense.
    # Confirm this is correctly reflected in the output.
    bp = identify_balance_points(...)  # use appropriate test fixture
    gini_row = [r for r in bp if r['balance_point'] == 'gini_optimal']
    assert len(gini_row) == 1, "gini_optimal row must exist"
    assert gini_row[0]['tsac_balance_exceeded'] == True, \
        "gini_optimal must have tsac_balance_exceeded=True — it is not a balance point in the TSAC/IUSAF dominance sense"

def test_practical_label_retired():
    """The label 'practical' must not appear in balance point outputs."""
    from logic.balance_analysis import identify_balance_points
    bp = identify_balance_points(...)
    labels = [r['balance_point'] for r in bp]
    assert 'practical' not in labels, \
        "'practical' has been renamed 'gini_optimal' — update the balance_analysis code"

def test_gini_optimal_scenario_key():
    """Scenario library must contain gini_optimal_point, not practical_balance_point."""
    from logic.sensitivity_scenarios import get_scenario_library
    lib = get_scenario_library()
    assert 'gini_optimal_point' in lib
    assert 'practical_balance_point' not in lib
```

### 1G — Search for residual references

After all the above changes, search the entire repository for the strings `practical_balance_point`, `practical balance point`, `Practical balance point`, and `practical` where used as a balance point label (not as an English adjective). Fix any remaining occurrences.

Do **not** rename Python variables or function names that happen to use "practical" in a generic sense. Only rename where the word refers specifically to this named balance point.

---

## Workstream 2 — Fix the sweep summary trigger attribution

### 2A — `logic/reporting.py` — `generate_sweep_summary()` function

Find the function that generates the sweep summary markdown. It currently produces a "Thresholds / Tipping Points" section that reads approximately:

```
- departure-from-pure-IUSAF threshold: first triggered at `tsac_beta_sweep_0.0`. 
  `spearman_vs_pure_iusaf=0.9771`
```

The departure flag is defined in `technical_annex.md` and the codebase as firing when **either**:
- `spearman_vs_pure_iusaf < 0.95`, **or**
- `top20_turnover_vs_pure_iusaf > 0.20`

The function must identify **which criterion actually triggered the flag** for the first flagged row, and report that criterion — not assume it was Spearman.

Rewrite the tipping-point generation logic as follows:

```python
def _explain_departure_trigger(row):
    """Return a plain-language explanation of which criterion triggered the departure flag."""
    reasons = []
    if row.get('spearman_vs_pure_iusaf', 1.0) < 0.95:
        reasons.append(
            f"`spearman_vs_pure_iusaf={row['spearman_vs_pure_iusaf']:.4f}` "
            f"(threshold: < 0.95)"
        )
    if row.get('top20_turnover_vs_pure_iusaf', 0.0) > 0.20:
        reasons.append(
            f"`top20_turnover_vs_pure_iusaf={row['top20_turnover_vs_pure_iusaf']:.4f}` "
            f"(threshold: > 0.20)"
        )
    if not reasons:
        return "trigger criterion not identified"
    return "; ".join(reasons)
```

Use this helper when building the tipping-point narrative. The generated text for the current data should read approximately:

```
- departure-from-pure-IUSAF threshold: first triggered at `tsac_beta_sweep_0.0`.  
  Trigger: `top20_turnover_vs_pure_iusaf=0.8000` (threshold: > 0.20).
```

Apply the same logic wherever `generate_sweep_summary()` or any related function currently hard-codes or assumes Spearman as the trigger metric. Both criteria must be checked.

### 2B — Tests

```python
def test_sweep_summary_trigger_attribution():
    """Sweep summary must identify the correct triggering criterion."""
    # Construct a minimal sweep dataframe where Spearman does NOT cross <0.95
    # but top20_turnover DOES cross >0.20 — confirming turnover is reported as trigger.
    import pandas as pd
    from logic.reporting import generate_sweep_summary

    sweep_df = pd.DataFrame([{
        'scenario_id': 'test_sweep_0.0',
        'sweep_value': 0.0,
        'spearman_vs_pure_iusaf': 0.977,       # does NOT cross <0.95
        'top20_turnover_vs_pure_iusaf': 0.80,  # DOES cross >0.20
        'departure_from_pure_iusaf_flag': True,
        'gini_coefficient': 0.101,
    }])
    md = generate_sweep_summary("test sweep", sweep_df, "spearman_vs_pure_iusaf")
    assert 'top20_turnover' in md, \
        "Sweep summary must name top20_turnover as the trigger when that is what fires"
    # Spearman=0.977 does not cross threshold so must NOT be named as trigger
    # (Allow it to appear in data context but not as the stated trigger reason)

def test_sweep_summary_spearman_trigger():
    """Sweep summary must also correctly attribute Spearman when that is the trigger."""
    import pandas as pd
    from logic.reporting import generate_sweep_summary

    sweep_df = pd.DataFrame([{
        'scenario_id': 'test_sweep_0.1',
        'sweep_value': 0.1,
        'spearman_vs_pure_iusaf': 0.85,        # DOES cross <0.95
        'top20_turnover_vs_pure_iusaf': 0.10,  # does NOT cross >0.20
        'departure_from_pure_iusaf_flag': True,
        'gini_coefficient': 0.090,
    }])
    md = generate_sweep_summary("test sweep", sweep_df, "spearman_vs_pure_iusaf")
    assert 'spearman' in md.lower(), \
        "Sweep summary must name Spearman as trigger when that is what fires"
```

---

## Workstream 3 — Export `integrity_checks.csv`

### 3A — Design

The goal is a file that a human reviewer — with no access to the application or codebase — can open and use to independently verify the mechanical soundness of every scenario in the library. Every row is a scenario. Every column is a named invariant check. Every cell is either `PASS`, `FAIL`, or the actual value that was checked. The file must be self-describing: column names and cell values must be unambiguous without reference to any other file.

The file is exported alongside `scenario_metrics.csv` whenever the sensitivity application runs a full scenario library comparison.

### 3B — Columns specification

The file must contain exactly the following columns, in this order:

| Column | Type | Description |
|---|---|---|
| `scenario_id` | string | Matches `scenario_id` in `scenario_metrics.csv` |
| `fund_size_usd` | float | Fund size in USD |
| `tsac_beta` | float | TSAC weight used |
| `sosac_gamma` | float | SOSAC weight used |
| `check_conservation_shares` | `PASS`/`FAIL` | `sum(final_share)` across all eligible Parties rounds to 1.0 within 1e-6 |
| `sum_final_share` | float | Actual sum of final shares (should be 1.0) |
| `check_conservation_money` | `PASS`/`FAIL` | `sum(total_allocation)` across all eligible Parties equals `fund_size_usd` within $0.01 |
| `sum_total_allocation_usd` | float | Actual sum of allocations in USD |
| `check_non_negativity` | `PASS`/`FAIL` | All `total_allocation` values ≥ 0 |
| `min_allocation_usd` | float | Minimum allocation across eligible Parties (should be ≥ 0) |
| `check_component_consistency` | `PASS`/`FAIL` | For all eligible Parties: `\|total_allocation − (iusaf_component + tsac_component + sosac_component)\|` < 1e-6 |
| `max_component_abs_diff_usd` | float | Maximum absolute difference between total and component sum |
| `check_iplc_split` | `PASS`/`FAIL` | For all eligible Parties: `\|total_allocation − (state_component + iplc_component)\|` < 1e-6 |
| `max_iplc_abs_diff_usd` | float | Maximum absolute difference between total and IPLC split sum |
| `check_band_monotonicity` | `PASS`/`FAIL` | Mean per-Party allocation strictly decreases from Band 1 to Band 6 across all bands with ≥ 1 eligible Party |
| `band_monotonicity_detail` | string | "PASS" or description of which band pair violates monotonicity |
| `check_floor_not_binding_unexpectedly` | `PASS`/`FAIL` | If `floor_pct=0`, then `floor_binding_count=0`. If `floor_pct>0`, record actual binding count. |
| `floor_binding_count` | int | Number of Parties where floor constraint is binding |
| `check_ceiling_not_binding_unexpectedly` | `PASS`/`FAIL` | If `ceiling_pct=None/0`, then `ceiling_binding_count=0`. |
| `ceiling_binding_count` | int | Number of Parties where ceiling constraint is binding |
| `check_sids_sosac_allocation` | `PASS`/`FAIL` | If `sosac_gamma > 0` and eligible SIDS exist: SOSAC component sum equals `sosac_gamma × fund_size` within $0.01. If no eligible SIDS: SOSAC component sum is 0 (reallocated to IUSAF). |
| `sids_sosac_component_sum_usd` | float | Actual sum of SOSAC components across all eligible Parties |
| `n_eligible_parties` | int | Number of eligible Parties |
| `n_eligible_sids` | int | Number of eligible SIDS Parties |
| `all_checks_pass` | `PASS`/`FAIL` | `PASS` only if every `check_*` column in this row is `PASS` |

### 3C — Implementation location

Add a function `generate_integrity_checks(scenario_id, scenario_params, results_df, fund_size)` to `logic/sensitivity_metrics.py` (or an appropriate existing module — do not create a new module unless no suitable home exists).

The function signature:
```python
def generate_integrity_checks(
    scenario_id: str,
    scenario_params: dict,      # keys: tsac_beta, sosac_gamma, floor_pct, ceiling_pct, etc.
    results_df: pd.DataFrame,   # country-level results for this scenario
    fund_size: float,           # in USD
) -> dict:
    """Return a dict with one key per column in integrity_checks.csv for this scenario."""
```

Each check is computed independently. A failure in one check does not prevent other checks from running. Where a check raises an unexpected exception, record `FAIL` and include the exception message in the detail column if one exists for that check.

### 3D — Integration in `sensitivity.py`

In the section that iterates over the scenario library and collects `library_metrics`, add a call to `generate_integrity_checks()` for each scenario. Accumulate the results into a list. After the loop, convert to a DataFrame and export as `integrity_checks.csv` alongside the other exports.

```python
# Alongside the existing library_metrics loop:
integrity_rows = []
for scenario_i in scenario_library.values():
    res = calculate_allocations(...)  # existing call
    integrity_rows.append(
        generate_integrity_checks(
            scenario_id=scenario_i['scenario_id'],
            scenario_params=scenario_i,
            results_df=res,
            fund_size=scenario_i.get('fund_size', 1_000_000_000),
        )
    )
integrity_df = pd.DataFrame(integrity_rows)
```

Add a download button for `integrity_checks.csv` in the exports section alongside the existing export buttons:

```python
st.download_button(
    "Download Integrity checks CSV",
    csv_bytes(integrity_df),
    file_name="integrity_checks.csv",
    mime="text/csv"
)
```

### 3E — Tests

```python
def test_integrity_checks_all_pass_for_valid_scenario():
    """All integrity checks must pass for a well-formed scenario."""
    from logic.sensitivity_metrics import generate_integrity_checks
    # Use the practical balance point / gini_optimal scenario as the test fixture
    # (or any valid scenario with known-good results)
    # ... set up results_df ...
    row = generate_integrity_checks(
        scenario_id='gini_optimal_point',
        scenario_params={'tsac_beta': 0.05, 'sosac_gamma': 0.03,
                         'floor_pct': 0.0, 'ceiling_pct': None},
        results_df=results_df,
        fund_size=1_000_000_000,
    )
    assert row['all_checks_pass'] == 'PASS', \
        f"All integrity checks should pass for valid scenario. Failures: " \
        f"{[k for k,v in row.items() if v == 'FAIL']}"

def test_integrity_checks_detects_non_conservation():
    """Integrity check must detect when shares do not sum to 1."""
    from logic.sensitivity_metrics import generate_integrity_checks
    import pandas as pd
    # Construct a deliberately broken results_df
    bad_df = pd.DataFrame({
        'eligible': [True, True],
        'final_share': [0.6, 0.6],           # sums to 1.2, not 1.0
        'total_allocation': [600, 600],
        'component_iusaf_amt': [600, 600],
        'component_tsac_amt': [0, 0],
        'component_sosac_amt': [0, 0],
        'state_component': [300, 300],
        'iplc_component': [300, 300],
        'un_band': ['Band 1: <= 0.001%', 'Band 2: 0.001% - 0.01%'],
        'is_sids': [False, False],
    })
    row = generate_integrity_checks(
        scenario_id='test_broken',
        scenario_params={'tsac_beta': 0.0, 'sosac_gamma': 0.0,
                         'floor_pct': 0.0, 'ceiling_pct': None},
        results_df=bad_df,
        fund_size=1_000_000_000,
    )
    assert row['check_conservation_shares'] == 'FAIL'
    assert row['all_checks_pass'] == 'FAIL'

def test_integrity_checks_columns_complete():
    """Integrity checks dict must contain all required columns."""
    from logic.sensitivity_metrics import generate_integrity_checks
    required_columns = [
        'scenario_id', 'fund_size_usd', 'tsac_beta', 'sosac_gamma',
        'check_conservation_shares', 'sum_final_share',
        'check_conservation_money', 'sum_total_allocation_usd',
        'check_non_negativity', 'min_allocation_usd',
        'check_component_consistency', 'max_component_abs_diff_usd',
        'check_iplc_split', 'max_iplc_abs_diff_usd',
        'check_band_monotonicity', 'band_monotonicity_detail',
        'check_floor_not_binding_unexpectedly', 'floor_binding_count',
        'check_ceiling_not_binding_unexpectedly', 'ceiling_binding_count',
        'check_sids_sosac_allocation', 'sids_sosac_component_sum_usd',
        'n_eligible_parties', 'n_eligible_sids', 'all_checks_pass',
    ]
    row = generate_integrity_checks(
        scenario_id='test', scenario_params={},
        results_df=pd.DataFrame(), fund_size=1e9)
    for col in required_columns:
        assert col in row, f"Missing required column: {col}"
```

---

## Acceptance criteria

Run `python3 -m pytest` — all tests must pass.

Verify manually:

1. `balance_points.csv` exported from the sensitivity app contains `gini_optimal` as the third row's `balance_point` value. The string `practical` does not appear as a balance point label.
2. `balance_point_summary.md` section heading reads `### Gini-optimal point` and the note paragraph explaining it does not satisfy the balance condition is present.
3. `scenario_metrics.csv` does not contain a row with `scenario_id = practical_balance_point`. The row exists under `gini_optimal_point`.
4. The sensitivity app scenario selector defaults to `gini_optimal_point`.
5. App preset button 5 is labelled "5. Gini-optimal point".
6. `sweep_summary.md` generated from a sweep where the first flagged row has Spearman=0.977 and top-20 turnover=0.80 names `top20_turnover_vs_pure_iusaf=0.8000` as the trigger, not Spearman.
7. `integrity_checks.csv` is available as a download in the sensitivity app exports section.
8. `integrity_checks.csv` has one row per scenario in the library and contains all columns listed in Workstream 3B.
9. Every `check_*` column value is either `PASS` or `FAIL` — no nulls, no numeric values in those columns.
10. `all_checks_pass` is `PASS` for all 14 standard library scenarios (assuming no bugs are introduced).
11. The string `practical` does not appear anywhere in the codebase as a balance point label (use `grep -r "practical" --include="*.py"` and review all hits).

---

## Files to modify — summary

| Action | File | Workstream |
|---|---|---|
| MODIFY | `logic/balance_analysis.py` | 1A |
| MODIFY | `logic/reporting.py` (balance point summary generator) | 1B |
| MODIFY | `logic/sensitivity_scenarios.py` | 1C |
| MODIFY | `sensitivity.py` | 1D |
| MODIFY | `app.py` | 1E |
| MODIFY | `tests/test_balance_analysis.py` | 1F |
| MODIFY | `tests/test_sensitivity_scenarios.py` | 1F |
| MODIFY | `logic/reporting.py` (sweep summary generator) | 2A |
| MODIFY | `tests/test_reporting.py` | 2B |
| ADD function | `logic/sensitivity_metrics.py` | 3C |
| MODIFY | `sensitivity.py` | 3D |
| MODIFY | `tests/test_sensitivity_metrics.py` | 3E |

**Do not modify:** `logic/calculator.py`, `logic/balance_analysis.py` calculation logic (only labels), `config/un_scale_bands.yaml`, any data files, any CSV exports already committed.

---

## Notes on sequencing

Complete Workstream 1 before Workstream 3, because `generate_integrity_checks()` will reference `gini_optimal_point` as the default test fixture and the scenario library must already carry that key.

Workstream 2 is independent and can be done in any order.
