# UN Scale of Assessment 2027 — Distribution Figures

Generated: 2026-04-15 15:12 UTC
Project: Cali Allocation Model (Inverted UN Scale Option)

---

## Figure 1: Full Distribution (All Countries)

- **File**: `fig_1_full_distribution.svg`
- **Data**: `fig_1_full_distribution.csv`
- **Source**: `/Users/pauloldham/Documents/cali-allocation-model-unscale-v3/data-raw/UNGA_scale_of_assessment.csv` (column: 2027)
- **Filter**: All countries with non-zero 2027 UN share (N=193)
- **Chart type**: Log-scale histogram
- **Packages**: matplotlib 3.10.8, pandas 2.3.3, numpy 2.4.3

### Key statistics
- Min: 0.0010%
- Max: 22.0000%
- Median: 0.0140%
- Top 10 countries hold 72.3% of total shares

---

## Figure 2: CBD Parties (High Income Excluded, SIDS Preserved)

- **File**: `fig_2_non_high_income.svg`
- **Data**: `fig_2_non_high_income.csv`
- **Source data**:
  - UN Scale: `/Users/pauloldham/Documents/cali-allocation-model-unscale-v3/data-raw/UNGA_scale_of_assessment.csv` (column: 2027)
  - CBD Parties: `/Users/pauloldham/Documents/cali-allocation-model-unscale-v3/data-raw/cbd_cop16_budget_table.csv`
  - Income groups: `/Users/pauloldham/Documents/cali-allocation-model-unscale-v3/data-raw/world_bank_income_class.csv`
  - SIDS flag: `/Users/pauloldham/Documents/cali-allocation-model-unscale-v3/data-raw/unsd_region_useme.csv`
  - Name mapping: `/Users/pauloldham/Documents/cali-allocation-model-unscale-v3/data-raw/manual_name_map.csv`
- **Filter**: CBD Parties, exclude High income except SIDS
  (replicates calculator.py: `exclude_high_income=True, high_income_mode="exclude_except_sids"`)
- **N = 142** eligible Parties (3 with 0% UN share)
- **Chart type**: Log-scale histogram
- **Packages**: matplotlib 3.10.8, pandas 2.3.3, numpy 2.4.3

### Key statistics
- Min: 0.0000%
- Max: 20.0040%
- Median: 0.0070%
- Top 10 countries hold 26.6% of total shares

---

## Regeneration

Run from project root:
```
python figures/un_scale_distribution/generate_plots.py
```
