# IPLC Developed-Country Allocation Tables — Specification

## Original Instructions

> On the IPLC branch I want to plan out how to calculate the IPLC component for a set of developing countries under two scenarios. This is a paper exercise and model code should not be changed. Any functions should be additional to existing code.
>
> **Option 1:** The IPLC allocation under raw equality for all Parties and then filtered to the following — Australia, Canada, Denmark, Finland, Japan, New Zealand, Norway, Russian Federation, Sweden.
>
> The allocation should display the nominal total allocation for the country with the IPLC split. Show the split for all fund volumes in the applications.
>
> **Option 2:** Banded approach. In this option the developed country Parties are added into the 6 bands of the Inverted UN Scale as a basis for the calculation of their hypothetical share. It is expected that the developed countries will mainly appear in band 4–6. The calculation is then repeated as above. The values for TSAC and SOSAC will be zero.
>
> The expected output is CSV files and tables for use in Word containing the information in the model-tables dir.

## Discussion & Clarifications

1. **IPLC split percentage:** 50% (default). State/IPLC split is 50/50.
2. **Fund volumes:** $50M, $200M, $500M, $1B (the 4 presets in the Streamlit application).
3. **Scope of HI inclusion (Option 2):** Only the 9 specified developed countries are added back in. All other high-income CBD parties remain excluded.

## Specification

### New Directory

All working files, notes, and auxiliary outputs go in `iplc-developed/`.

### New Script

**`scripts/generate_iplc_developed_tables.py`** — a standalone script that:
- Imports `load_data`, `get_base_data`, `calculate_allocations`, `assign_un_band`, `load_band_config` from existing `src/cali_model/`
- Uses `scripts/csv_to_word_lib.py` for Word table generation
- Outputs CSV + DOCX files to `model-tables/` (see Output Paths below)

### Option 1: Raw Equality

**Method:**
1. Run `calculate_allocations()` with `equality_mode=True`, `exclude_high_income=False`, `iplc_share=50`, for all CBD Parties.
2. Filter the result to the 9 specified countries only.

**Per-fund-volume table columns:**

| Country | UN Share (%) | Equal Share (%) | Total Allocation (USD M) | IPLC Component (USD M) | State Component (USD M) |

**Summary table (all fund volumes):**

| Country | $50M Total | $50M IPLC | $50M State | $200M Total | $200M IPLC | $200M State | $500M Total | $500M IPLC | $500M State | $1B Total | $1B IPLC | $1B State |

### Option 2: Banded Approach

**Method:**
1. Override eligibility so that ONLY the 9 specified countries are additionally made eligible (all other HI remain excluded).
2. Run `calculate_allocations()` with `equality_mode=False`, `un_scale_mode="band_inversion"`, `tsac_beta=0`, `sosac_gamma=0`, `iplc_share=50`.

**Band assignments (from 2027 UN Scale):**

- Band 4 (0.1–1.0%): Denmark (0.531%), Finland (0.386%), New Zealand (0.302%), Norway (0.653%), Sweden (0.822%)
- Band 5 (1.0–10.0%): Australia (2.040%), Canada (2.543%), Japan (6.930%), Russian Federation (2.094%)

**Per-fund-volume table columns:**

| Country | UN Share (%) | Band | Band Weight | IUSAF Share (%) | Total Allocation (USD M) | IPLC Component (USD M) | State Component (USD M) |

**Summary table (all fund volumes, with Band column added):**

| Country | Band | $50M Total | $50M IPLC | $50M State | $200M Total | ... | $1B State |

### Output Paths

All output goes to `model-tables/`:

| File | Content |
|------|---------|
| `iplc-option1-equality-50m.csv/.docx` | Option 1, $50M fund |
| `iplc-option1-equality-200m.csv/.docx` | Option 1, $200M fund |
| `iplc-option1-equality-500m.csv/.docx` | Option 1, $500M fund |
| `iplc-option1-equality-1bn.csv/.docx` | Option 1, $1B fund |
| `iplc-option1-equality-summary.csv/.docx` | Option 1, all fund volumes |
| `iplc-option1-equality.md` | Option 1, all fund volumes (markdown) |
| `iplc-option2-banded-50m.csv/.docx` | Option 2, $50M fund |
| `iplc-option2-banded-200m.csv/.docx` | Option 2, $200M fund |
| `iplc-option2-banded-500m.csv/.docx` | Option 2, $500M fund |
| `iplc-option2-banded-1bn.csv/.docx` | Option 2, $1B fund |
| `iplc-option2-banded-summary.csv/.docx` | Option 2, all fund volumes |
| `iplc-option2-banded.md` | Option 2, all fund volumes (markdown) |

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate_iplc_developed_tables.py` | Main script: generates CSV + DOCX from model data |
| `scripts/generate_iplc_md.py` | Converts CSV outputs to markdown (.md) tables |

### Implementation Notes

- No changes to `src/cali_model/calculator.py`, `data_loader.py`, or `app.py`
- The script forces `exclude_high_income=False` for Option 1 (equality needs all Parties)
- For Option 2, the script overrides `eligible` for the 9 countries to `True` (while keeping other HI excluded)
- TSAC and SOSAC are both 0 for both options
- CSV files use 2 decimal places for USD millions
- Word tables use `csv_to_word_lib.py` styling (Times New Roman, grey header, bold Total)
- Total row included in every table for verification
