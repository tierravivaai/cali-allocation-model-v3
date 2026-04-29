# Data Sources and Pipeline

## Data Sources

| Source | File | Purpose |
|--------|------|---------|
| UN Scale of Assessments (2025–2027) | `data-raw/UNGA_scale_of_assessment.csv` | Assessed budget shares per Party |
| CBD COP16 Budget Table | `data-raw/cbd_cop16_budget_table.csv` | Source of truth for CBD Party list (196 Parties) |
| UNSD M49 Regions | `data-raw/un_classifications.csv` | UN region, sub-region, intermediate region |
| World Bank Income Classification | `data-raw/CLASS_2025_10_07.xlsx` | Income group labels (Low, Lower-middle, Upper-middle, High) |
| Land Area | `data-raw/API_AG.LND.TOTL.K2_DS2_en_csv_v2_749.zip` | FAOSTAT/World Bank land area in km² |
| EU Member States | `data-raw/eu27.csv` | EU membership flags |
| Name Concordance | `data-raw/manual_name_map.csv` | Cross-references UN, World Bank, and CBD Party names |

## Data Pipeline

```
data-raw/  (CSV/XLSX raw files)
    │
    ▼
src/cali_model/data_loader.py   (DuckDB SQL-based ETL)
    │  ├── load_data(con)         — creates tables in DuckDB
    │  └── get_base_data(con)     — returns merged base_df (197 rows × 27 cols)
    │
    ▼
src/cali_model/calculator.py    (allocation computation)
    │  └── calculate_allocations(base_df, fund_size, ...)  →  results_df
    │
    ▼
app.py / sensitivity.py        (Streamlit presentation)
```

### `base_df` columns

Key columns in the merged dataframe used by `calculate_allocations`:

| Column | Source | Description |
|--------|--------|-------------|
| `party` | Budget table | CBD Party name |
| `un_share` | UN Scale | Assessed share (%) |
| `region`, `sub_region`, `intermediate_region` | UNSD M49 | Geographic classification |
| `is_cbd_party` | Budget table | CBD membership flag |
| `WB Income Group` | World Bank | Income classification (labels only — not used in calculation) |
| `is_ldc`, `is_sids` | UN classifications | Development group flags |
| `is_eu_ms` | EU list | EU membership flag |
| `land_area_km2` | World Bank | Land area with latest available year auto-selected |

### Name mapping

Party names differ across UN, World Bank, and CBD datasets. The `manual_name_map.csv` provides a reconciliation layer applied during `load_data()`. unmapped names are flagged for manual review.
