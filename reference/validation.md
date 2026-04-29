# Validation and Testing

## Test Suite

The repository contains **25+ test modules** with **178+ automated tests** covering mathematical integrity, UI behaviour, and data consistency.

Run all tests:
```bash
pytest tests/ -v
```

Run IPLC structural validation:
```bash
pytest iplc-developed/test_structural_validation.py -v
```

## Test Modules

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_logic.py` | Party count, inversion logic, allocation sums, metadata completeness |
| `test_band_inversion.py` | Band assignment, weight normalisation, mode consistency |
| `test_tsac_sosac.py` | Component blending, isolation, SIDS preservation, SOSAC fallback |
| `test_totals.py` | Aggregation correctness (region, income, LDC, SIDS tabs) |
| `test_floor_ceiling.py` | Constraint redistribution, dynamic limits |
| `test_equality_mode.py` | Equal shares, mode switching |
| `test_tiny_scenarios.py` | Fund conservation at extreme sizes ($2m–$1bn) |
| `test_negotiator_dashboard.py` | Baseline comparison, UN scale mode consistency |
| `test_ui_reset.py` | Preset buttons, reset defaults |
| `test_ui_columns.py` | Tab content, column ordering |
| `test_ui_selectors.py` | Region/sub-region filtering |
| `test_stewardship_warnings.py` | Blend threshold triggers |
| `test_sensitivity_modules.py` | Gini, Spearman, balance-point metrics |
| `test_balance_analysis.py` | Fine sweeps, Gini-minimum identification |
| `test_reporting.py` | Markdown/CSV export integrity |
| `test_formatting.py` | Currency display, thousands toggle |
| `test_aggregates.py` | EU block, special group aggregation |
| `test_dashboard_stability.py` | Negotiation dashboard rendering |
| `test_income_tabs.py` | Income group tab totals |
| `test_income_validation.py` | Income classification correctness |
| `test_eligibility.py` | Eligibility filtering, HI exclusion |
| `test_app_dataframes.py` | Streamlit dataframe export regression |

## IPLC Structural Validation

`iplc-developed/test_structural_validation.py` provides **40 tests** verifying 8 invariants for the 9-country IPLC allocation across both Option 1 (equality) and Option 2 (banded IUSAF):

1. IPLC + State = Total
2. IPLC = 50% of total
3. Fund conservation (sum of eligible allocations = fund size)
4. Scale invariance (2× fund → 2× allocation)
5. Band assignments (Band 4 / Band 5)
6. No non-SIDS HI leakage
7. Option 1 total > Option 2 total
8. Cali Fund % constant across fund sizes

## Integrity Checks

The sensitivity framework generates `integrity_checks.csv` as a reviewer-facing export with one row per scenario and `all_checks_pass=PASS` for all standard scenarios. This validates:
- Allocation sums equal the fund size
- No negative allocations
- No missing data for eligible parties
