# Table Validation Report: IUSAF Paper

**Date:** 2026-05-04
**Paper:** `docs/working_papers/iusaf_paper-28042026.docx`
**Validator:** Automated comparison against latest application output (`src/app.py` + `src/cali_model/`)
**Scenario:** IUSAF Equity Base (TSAC=0%, SOSAC=0%, exclude high-income except SIDS, fund=USD 1,000M, IPLC split=50/50)

---

## Summary

All tables in the paper were compared against the live application output. Two categories of issues were found:

1. **Tables 4 and 5 had incorrect country counts and allocation values** (now fixed in `model-tables/`)
2. **A data concordance bug** caused Sierra Leone and Lao PDR to be misclassified as non-LDC (now fixed in `config/party_master.csv` and `src/cali_model/data_loader.py`)

---

## Table-by-Table Results

### Tables that MATCH (no changes needed)

| Table | Description | Status |
|-------|-------------|--------|
| Table 1 | IUSAF Allocation by UN Region | **MATCH** |
| Table 2 | IUSAF Allocation by UN Subregion | **MATCH** |
| Table 3 | IUSAF Allocation by UN Intermediate Region | **MATCH** |
| Table 5 (top 20) | Band 1 countries (31 parties, 8.53M each) | **MATCH** |
| Table 6 (middle) | Band 2-3 countries (7.39M / 6.25M) | **MATCH** |
| Table 5 (bottom) | Band 4-6 countries (5.40M / 4.26M / 2.27M) | **MATCH** |
| Table 7 | SIDS Distribution Across IUSAF Bands (22/11/4/2) | **MATCH** |
| Table 8 | SOSAC Integer Comparison | **MATCH** |
| Balance points | Strict/Gini-min/Band-order (Band 5 mean=5.70, Band 6 mean=5.74) | **MATCH** |

### Tables with DISCREPANCIES (now fixed in model-tables/)

**Table 4: IUSAF Allocation for LDC**

| Row | Paper (old) | Correct values |
|-----|-------------|-----------------|
| LDC countries | 44 | 44 |
| LDC total | 247.81 M | **339.87 M** |
| LDC state | 123.90 M | **169.93 M** |
| LDC IPLC | 123.90 M | **169.93 M** |
| Other Countries count | 152 | **98** |
| Other Countries total | 752.19 M | **660.13 M** |
| Total count | 196 | **142** |

**Root cause:** The original `model-tables/iusaf-ldc-panel-16042026.csv` was generated with `exclude_high_income=False` (all 196 UN member states), producing LDC total of 247.81M. The paper's IUSAF equity base scenario uses `exclude_high_income=True` (142 eligible Parties), giving LDC total of 339.87M.

**Table 5: IUSAF Allocation for SIDS**

| Row | Paper (old) | Correct values |
|-----|-------------|-----------------|
| SIDS countries | 39 | 39 |
| SIDS total | 304.63 M | 304.63 M (unchanged) |
| SIDS state | 152.32 M | 152.32 M |
| SIDS IPLC | 152.32 M | 152.32 M |
| Other Countries count | 157 | **103** |
| Other Countries total | 695.37 M | 695.37 M (unchanged) |
| Total count | 196 | **142** |

**Root cause:** Same issue — "Other Countries" counted all non-SIDS UN members (157) instead of eligible non-SIDS Parties (103). SIDS values are unchanged because SIDS are eligible regardless of high-income exclusion.

---

## Data Concordance Bug (fixed)

**Issue:** Sierra Leone (CBD budget table entry "SierraLeone" without space) and Lao People's Democratic Republic were missing `is_ldc=True` flags because name joins with the UNSD regions file failed.

**Fix applied:**
- `config/party_master.csv`: Added `is_ldc_override=True` for Sierra Leone (with region/income overrides) and Lao PDR
- `src/cali_model/data_loader.py`: Fixed pandas `StringDtype` to `object` dtype conversion for DuckDB compatibility

**Result:** LDC count now correctly shows 44 (was 42 before fix).

---

## Files Modified

| File | Change |
|------|--------|
| `config/party_master.csv` | Added Sierra Leone row with LDC override; added `is_ldc_override=True` to Lao PDR |
| `src/cali_model/data_loader.py` | Added `astype("object")` conversion after `dtype=str` read for party_master |
| `model-tables/iusaf-ldc-panel-16042026.csv` | Regenerated with correct values (44 LDC, 142 total) |
| `model-tables/iusaf-sids-panel-16042026.csv` | Regenerated with correct values (39 SIDS, 142 total) |
| `model-tables/iusaf-ldc-panel-16042026.docx` | Regenerated from updated CSV |
| `model-tables/iusaf-sids-panel-16042026.docx` | Regenerated from updated CSV |

---

## Verification: Current App Output vs Paper (post-fix)

### Table 1: IUSAF Allocation by UN Region

| UN Region | Countries | Total (USD M) | State (USD M) | IPLC (USD M) |
|-----------|-----------|---------------|---------------|---------------|
| Africa | 54 | 394.15 | 197.07 | 197.07 |
| Asia | 37 | 239.84 | 119.92 | 119.92 |
| Americas | 29 | 194.37 | 97.19 | 97.19 |
| Oceania | 14 | 117.08 | 58.54 | 58.54 |
| Europe | 8 | 54.56 | 27.28 | 27.28 |
| **Total** | **142** | **1,000.00** | **500.00** | **500.00** |

### Table 4: IUSAF Allocation for LDC (CORRECTED)

| Group | Countries | Total (USD M) | State (USD M) | IPLC (USD M) |
|-------|-----------|---------------|---------------|---------------|
| LDC | 44 | 339.87 | 169.93 | 169.93 |
| Other Countries | 98 | 660.13 | 330.07 | 330.07 |
| **Total** | **142** | **1,000.00** | **500.00** | **500.00** |

### Table 5: IUSAF Allocation for SIDS (CORRECTED)

| Group | Countries | Total (USD M) | State (USD M) | IPLC (USD M) |
|-------|-----------|---------------|---------------|---------------|
| SIDS | 39 | 304.63 | 152.32 | 152.32 |
| Other Countries | 103 | 695.37 | 347.68 | 347.68 |
| **Total** | **142** | **1,000.00** | **500.00** | **500.00** |

---

## Data Flow Clarification

- **`data-raw/`** — Source data (UN scale, WB income, regions, EU, land area). Input to the app.
- **`data/`** — Old equality-based exports from March 27. **Stale. Do not use.**
- **`model-tables/`** — Static exported tables generated by scripts. Now regenerated with correct values.
- **`src/app.py`** — Live Streamlit application using `cali_model/` module. Source of truth.
- **`config/party_master.csv`** — Name concordance and data overrides for edge cases.
