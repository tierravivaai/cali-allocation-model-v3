# Retire Stewardship-Forward Baseline — Implementation Instructions

**Repo:** `tierravivaai/cali-allocation-model-v3`  
**Branch:** `main`  
**Scope:** Rename `stewardship_forward_baseline` to `practical_balance_point` throughout the codebase and update all dependent labels, documentation, and tests.  
**Run `python3 -m pytest` after each workstream. All existing tests must stay green.**

---

## Background the agent must understand

The stewardship-forward baseline (TSAC=5%, SOSAC=3%) was created before sensitivity testing as a provisional reference scenario — a rough estimate of where a balance point might lie. The fine-grained TSAC sweep has now confirmed that TSAC=5% is precisely where the **practical balance point** sits: the setting that minimises the Gini coefficient while keeping Spearman rank correlation vs pure IUSAF above 0.85.

The two scenarios are identical in every parameter and produce identical outputs. The stewardship-forward baseline no longer serves any purpose that is not already served by the practical balance point. Retaining it creates confusion because it is described as "not balanced" while producing results identical to the practical balance point.

**What changes:** The scenario key and all labels are renamed. Parameter values (TSAC=5%, SOSAC=3%) do not change. All numerical outputs remain identical.

**What does not change:** `logic/calculator.py`, `logic/balance_analysis.py`, `logic/sensitivity_metrics.py`, `config/un_scale_bands.yaml`, any data files.

---

## Workstream 1 — `logic/sensitivity_scenarios.py`

### 1A — Rename `stewardship_forward_baseline`

Find the scenario entry with key `"stewardship_forward_baseline"`. Rename the key to `"practical_balance_point"`. Update its `description` field to:

```
"Practical balance point: minimises Gini coefficient while keeping Spearman vs pure IUSAF > 0.85. TSAC=5%, SOSAC=3%."
```

### 1B — Rename the three `balanced_` floor/ceiling variants

These scenarios test floor and ceiling constraints at the practical balance point parameterisation. Rename their keys to reflect this:

| Old key | New key |
|---|---|
| `balanced_floor_005` | `practical_floor_005` |
| `balanced_ceiling_1` | `practical_ceiling_1` |
| `balanced_floor_005_ceiling_1` | `practical_floor_005_ceiling_1` |

Update each description field to reference "the practical balance point" rather than "the balanced baseline".

### 1C — Verify the default scenario index

The scenario library is loaded as an ordered dict. The `practical_balance_point` entry should remain in the same position as `stewardship_forward_baseline` was — third entry after the two pure IUSAF scenarios. Do not reorder other scenarios.

### 1D — Verify no remaining references to old keys

Search `logic/sensitivity_scenarios.py` for any remaining occurrences of `stewardship_forward_baseline`, `balanced_floor_005`, `balanced_ceiling_1`, `balanced_floor_005_ceiling_1`. There should be none after this workstream.

---

## Workstream 2 — `sensitivity.py`

Two lines reference the old key directly.

### 2A — Line 71: default scenario selector

```python
# BEFORE
library_choice = st.sidebar.selectbox(
    "Named scenario",
    options=list(scenario_library.keys()),
    index=list(scenario_library.keys()).index("balanced_baseline")
)

# AFTER
library_choice = st.sidebar.selectbox(
    "Named scenario",
    options=list(scenario_library.keys()),
    index=list(scenario_library.keys()).index("practical_balance_point")
)
```

Note: the old value was `"balanced_baseline"` — a legacy key that no longer exists in the library. This line was already broken (would raise `ValueError` at runtime). The correct target is `"practical_balance_point"`.

### 2B — Line 350: comparative report baseline ID

```python
# BEFORE
comparative_md = generate_comparative_report(library_metrics_df, baseline_id="balanced_baseline")

# AFTER
comparative_md = generate_comparative_report(library_metrics_df, baseline_id="practical_balance_point")
```

### 2C — No other changes to sensitivity.py

The `stewardship_total` variable name (lines 278–288) refers to the sum of TSAC and SOSAC weights as a generic measure — it is not a reference to the scenario and should not be renamed.

---

## Workstream 3 — `app.py`

### 3A — Rename preset button 5

```python
# BEFORE (line 192)
if st.button("5. Balanced", help="TSAC=0.05, SOSAC=0.03 (Default)", use_container_width=True):

# AFTER
if st.button("5. Practical Balance Point",
             help="TSAC=5%, SOSAC=3% — practical balance point (minimises Gini, Spearman > 0.85)",
             use_container_width=True):
```

Parameter assignments on lines 193–198 do not change (TSAC=0.05, SOSAC=0.03 remain correct).

### 3B — Update inline comments

```python
# BEFORE (line 418)
# 2. If we are in any other preset (Stewardship, Balanced, etc.),

# AFTER
# 2. If we are in any other preset (Balance Points, Stewardship extremes, etc.),
```

```python
# BEFORE (line 446)
# Stewardship/Balanced selected: Compare against Inverted UN Scale (IUSAF)

# AFTER
# Balance point or stewardship extreme selected: Compare against Inverted UN Scale (IUSAF)
```

These are comments only — no logic changes.

### 3C — No other changes to app.py

The introductory caption (line 39) and sidebar header (line 211) use the word "stewardship" in a generic descriptive sense — they correctly describe the TSAC and SOSAC components and do not reference the retired scenario. Leave them unchanged.

---

## Workstream 4 — Tests

### 4A — Update `tests/test_sensitivity_scenarios.py` (or equivalent)

Find any test that references `"stewardship_forward_baseline"`, `"balanced_baseline"`, `"balanced_floor_005"`, `"balanced_ceiling_1"`, or `"balanced_floor_005_ceiling_1"` by name. Update each to the new key.

Common patterns to search for and replace:

```python
# Old → New
"stewardship_forward_baseline"    →  "practical_balance_point"
"balanced_baseline"               →  "practical_balance_point"
"balanced_floor_005"              →  "practical_floor_005"
"balanced_ceiling_1"              →  "practical_ceiling_1"
"balanced_floor_005_ceiling_1"    →  "practical_floor_005_ceiling_1"
```

### 4B — Update `tests/test_balance_analysis.py`

This file tests balance point identification. Find any assertion that uses `"stewardship_forward_baseline"` as an input scenario or expected output label. Update to `"practical_balance_point"`.

If the file contains a test such as:

```python
assert metrics["scenario_id"] == "stewardship_forward_baseline"
```

Replace with:

```python
assert metrics["scenario_id"] == "practical_balance_point"
```

### 4C — Update `tests/test_concordance.py`

If this file references `stewardship_forward_baseline` in any integration test fixture, update to `practical_balance_point`.

### 4D — Add one new test

In the most appropriate existing test file (e.g. `tests/test_sensitivity_scenarios.py`), add:

```python
def test_stewardship_forward_baseline_retired():
    """Confirm the retired scenario key no longer exists in the scenario library."""
    from logic.sensitivity_scenarios import get_scenario_library
    library = get_scenario_library()
    assert "stewardship_forward_baseline" not in library, \
        "stewardship_forward_baseline has been retired — use practical_balance_point"
    assert "balanced_baseline" not in library, \
        "balanced_baseline has been retired — use practical_balance_point"
    assert "practical_balance_point" in library, \
        "practical_balance_point must exist in the scenario library"

def test_practical_balance_point_parameters():
    """Confirm practical_balance_point has the correct parameter values."""
    from logic.sensitivity_scenarios import get_scenario_library
    scenario = get_scenario_library()["practical_balance_point"]
    assert abs(scenario["tsac_beta"] - 0.05) < 0.001, \
        "practical_balance_point must have TSAC=5%"
    assert abs(scenario["sosac_gamma"] - 0.03) < 0.001, \
        "practical_balance_point must have SOSAC=3%"

def test_floor_ceiling_variants_renamed():
    """Confirm floor/ceiling variant keys use the practical_ prefix."""
    from logic.sensitivity_scenarios import get_scenario_library
    library = get_scenario_library()
    for old_key in ["balanced_floor_005", "balanced_ceiling_1",
                    "balanced_floor_005_ceiling_1"]:
        assert old_key not in library, \
            f"'{old_key}' has been renamed — use 'practical_' prefix instead"
    for new_key in ["practical_floor_005", "practical_ceiling_1",
                    "practical_floor_005_ceiling_1"]:
        assert new_key in library, \
            f"'{new_key}' must exist in the scenario library"
```

---

## Workstream 5 — Generated markdown reports

The sensitivity application generates six markdown reports. Three contain references to the old scenario name and need template updates in `logic/reporting.py` (or wherever the report generation functions live).

### 5A — `generate_scenario_brief()`

Find the function that generates the scenario brief. It currently uses `"stewardship_forward_baseline"` as a display name or ID in its output text. Update to `"practical_balance_point"`.

The scenario brief header currently reads:
```
# Scenario Brief: stewardship_forward_baseline
```
It should read:
```
# Scenario Brief: practical_balance_point
```

All other content in the brief is generated from metrics, not from the hardcoded scenario name, so no other changes are needed in this function.

### 5B — `generate_comparative_report()`

The function signature receives `baseline_id`. It uses this to generate the line:
```
Baseline is `stewardship_forward_baseline` with fund size...
```
After the Workstream 2B change (`baseline_id="practical_balance_point"`), this line will automatically update. No change needed to the function body.

### 5C — `balance_point_summary.md` template or generator

The balance point summary currently contains:

```
The **stewardship-forward baseline** (TSAC=5%, SOSAC=3%) exceeds both the strict and 
modified balance points and is not a balanced setting. It is retained as a named scenario 
for reference purposes only.
```

Replace with:

```
The **practical balance point** (TSAC=5%, SOSAC=3%) is the setting that minimises the 
Gini coefficient while keeping Spearman rank correlation vs pure IUSAF above 0.85. It 
coincides with what was previously called the stewardship-forward baseline, which has 
now been retired. The practical balance point is the default reference scenario.
```

Also update the "Choosing among balance points" section. The current bullet:

```
- The **practical point** optimises distributional equality (Gini) within the constraint 
  that the allocation remains a moderate rather than dominant overlay on the IUSAF base.
```

Update to:

```
- The **practical point** (TSAC=5%, SOSAC=3%) minimises the Gini coefficient within 
  the constraint that the allocation remains a moderate overlay on the IUSAF base 
  (Spearman > 0.85). This is also the default scenario in the application.
```

---

## Workstream 6 — Word documents

### 6A — `CBD_AHEGF_IUSAF_technical_note.docx`

Search for all occurrences of "stewardship-forward baseline" and "stewardship-forward". The term appears in Section V (balance point discussion). Make the following replacements:

1. Every occurrence of "stewardship-forward baseline" → "practical balance point"

2. The sentence that currently reads (approximately):
   > *The stewardship-forward baseline (TSAC=5%, SOSAC=3%) exceeds both the strict and modified balance points and is not a balanced setting.*
   
   Replace with:
   > *The practical balance point (TSAC=5%, SOSAC=3%) is the setting that minimises the Gini coefficient subject to the allocation remaining a moderate overlay on the IUSAF base (Spearman rank correlation above 0.85). It supersedes the earlier stewardship-forward baseline, which was a provisional reference used during development and has now been retired.*

3. The Table 6 row labelled "Stewardship-forward" → "Practical balance point (default)"

4. In the recommendation section (paragraph 58/59), replace any reference to the stewardship-forward baseline as a reference with the practical balance point.

### 6B — `v3_sensitivity_assessment.docx`

The assessment document uses "stewardship-forward baseline" extensively — in Section 3 heading, Table 2, throughout the text. Make the following replacements throughout:

1. "stewardship-forward baseline" → "practical balance point" everywhere it refers to the TSAC=5%, SOSAC=3% scenario.

2. Section 3 heading: "The stewardship-forward baseline" → "The practical balance point"

3. Table 2 caption: update accordingly.

4. The sentence in Section 2 that reads:
   > *The stewardship-forward baseline (TSAC=5%, SOSAC=3%) is further from any defensible balance point than previously understood.*
   
   This statement is now obsolete — the practical balance point IS at 5%. Replace the sentence or remove it.

5. Table 6 in Section 8 currently has a row "Stewardship-forward | 5.0% | 3.0% | Reference only — not a balanced setting." Remove this row. The practical balance point row already covers TSAC=5%, SOSAC=3%.

6. Section 9 integrity summary: update the row "Brazil > China in final allocation" note and any row referencing the SF baseline.

---

## Workstream 7 — Historical audit trail note

### 7A — Add to `technical_annex.md`

At the end of the **Formula Specification** section, add:

```
## Historical note: stewardship-forward baseline

Prior to the completion of the fine-grained TSAC sweep, sensitivity analysis used a 
provisional reference scenario called the stewardship-forward baseline (TSAC=5%, 
SOSAC=3%). This was a development placeholder used before balance points had been 
formally identified. The sweep confirmed that TSAC=5% is precisely the practical balance 
point — the setting that minimises the Gini coefficient while keeping Spearman rank 
correlation above 0.85. The stewardship-forward baseline was accordingly retired and 
replaced by the practical balance point, which has identical parameter values. Any 
outputs generated before this change that reference the stewardship-forward baseline 
are equivalent to outputs referencing the practical balance point.
```

This note preserves the audit trail for any CBD submissions or external documents that referenced the stewardship-forward baseline by name.

---

## Acceptance criteria

Run `python3 -m pytest` — all tests must pass.

Verify manually:

1. `get_scenario_library()` contains `"practical_balance_point"` and does not contain `"stewardship_forward_baseline"` or `"balanced_baseline"`.
2. `get_scenario_library()` contains `"practical_floor_005"`, `"practical_ceiling_1"`, `"practical_floor_005_ceiling_1"` and does not contain the old `"balanced_"` variants.
3. `practical_balance_point` has `tsac_beta=0.05` and `sosac_gamma=0.03`.
4. The sensitivity app loads without error and defaults to `practical_balance_point` in the scenario selector.
5. The app.py preset button 5 is labelled "5. Practical Balance Point".
6. Running the sensitivity app and exporting the scenario brief produces a document headed "Scenario Brief: practical_balance_point".
7. Running the sensitivity app and exporting the comparative report shows baseline as `practical_balance_point`.
8. The word "stewardship_forward_baseline" does not appear in any `.py` file in the repo.
9. The word "balanced_baseline" does not appear in any `.py` file in the repo.
10. `technical_annex.md` contains the historical note.

---

## Files to create or modify — summary

| Action | File | Workstream |
|---|---|---|
| MODIFY | `logic/sensitivity_scenarios.py` | 1 |
| MODIFY | `sensitivity.py` | 2 |
| MODIFY | `app.py` | 3 |
| MODIFY | `tests/test_sensitivity_scenarios.py` | 4A, 4D |
| MODIFY | `tests/test_balance_analysis.py` | 4B |
| MODIFY | `tests/test_concordance.py` | 4C (if needed) |
| MODIFY | `logic/reporting.py` | 5A |
| MODIFY | `CBD_AHEGF_IUSAF_technical_note.docx` | 6A |
| MODIFY | `v3_sensitivity_assessment.docx` | 6B |
| MODIFY | `data-raw/balance_point_summary.md` | 5C |
| MODIFY | `data-raw/technical_annex.md` | 7A |

**Do not modify:** `logic/calculator.py`, `logic/balance_analysis.py`, `logic/sensitivity_metrics.py`, `config/un_scale_bands.yaml`, any data files, any CSV exports.

---

## Parameter values — unchanged

For absolute clarity: **no parameter values change**. The practical balance point uses exactly the same values as the stewardship-forward baseline:

```
tsac_beta:          0.05   (5%)
sosac_gamma:        0.03   (3%)
exclude_hi:         True
un_scale_mode:      band_inversion
iplc_share_pct:     50
floor_pct:          0.0    (off)
ceiling_pct:        None   (off)
```

All scenario metrics, Gini values, Spearman figures, LDC totals, SIDS totals, and country-level allocations are identical before and after this change. This is a renaming exercise, not a recalculation.
