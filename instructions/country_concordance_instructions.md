# Concordance Refactor — Implementation Instructions

**Repo:** `tierravivaai/cali-allocation-model-v3`  
**Branch:** `main`  
**Scope:** Replace fragile name-based joins with a three-file ISO3-keyed concordance.  
**Run `python3 -m pytest` after each workstream. All existing tests must stay green.**

---

## Background the agent must understand

The model joins data from five sources — UN Scale of Assessments (UNGA 2025–2027), CBD budget table (COP16), World Bank land area (WDI), World Bank income groups, and UN M49 regional classifications — using free-text country name matching. The UN and World Bank use different name conventions for roughly 30 countries, causing 21 CBD Parties to receive zero TSAC allocation due to silent join failures. The fix is a three-file concordance keyed on ISO3 codes, eliminating all string matching from `data_loader.py`.

### The three files

| File | Rows | Source | Owner | Changes when |
|---|---|---|---|---|
| `data-raw/countrycode.csv` | 263 | R countrycode package | Package maintainers | New package version released |
| `data-raw/un_classifications.csv` | 197 | UN OHRLLS / UN DESA | Us | LDC/SIDS/LLDC list changes |
| `data-raw/country_overlay.csv` | 197 | CBD Secretariat / WB | Us | Party status or income group changes |
| `data-raw/cbd_cop16_budget_table.csv` | 197 | CBD Secretariat | External — do not edit | New COP budget decision |

All joins use `iso3c` as the key. The `cbd_party_name` column in `country_overlay.csv` is the authoritative display value for the `party` column throughout all model outputs.

**On row counts:** The CBD has 196 Parties. The model country universe has 197 rows — 196 CBD Parties plus one non-Party row for the United States of America (present in UN Scale and WB data sources; `is_cbd_party = FALSE`, `eligible = FALSE`, receives no allocation). File row counts in these instructions refer to the 197-row universe. Party counts in any document facing Parties are always 196.

---

## Workstream 1 — Modify `data-raw/countrycode.csv`

### 1A — Drop four columns

Remove the following columns from `data-raw/countrycode.csv` entirely. They are replaced by `un_classifications.csv` which is under our control and will not silently drift.

```
country_lower
un_least_developed_countries_ldc
un_land_locked_developing_countries_lldc
un_small_island_developing_states_sids
```

The 12 columns that remain:

```
iso3c, iso2c, country_code, country_name,
eu27,
un_region_name, un_sub_region_name, un_intermediate_region_name,
un_region_clean, un_sub_region_clean, un_intermediate_region_clean,
un_developed_or_developing_countries
```

### 1B — Fix one typo

Row with `country_name = "European Commission"` has `un_developed_or_developing_countries = "Developedl"`. Correct to `"Developed"`. This row is never used by the model (iso3c = "unknown") but the typo should not persist.

### 1C — No other changes

Do not add rows, do not change iso3c values, do not alter any other column. The file remains 263 rows.

---

## Workstream 2 — Create `data-raw/un_classifications.csv`

Create this file from scratch. It is the authoritative source for LDC, SIDS, and LLDC status for all 197 countries in the model universe. It replaces the dropped columns from countrycode.

### Schema

```
iso3c               — ISO3 join key (matches iso3c in countrycode.csv)
is_ldc              — TRUE/FALSE  UN Least Developed Country
is_sids             — TRUE/FALSE  UN Small Island Developing State
is_lldc             — TRUE/FALSE  UN Land-Locked Developing Country
ldc_source_date     — date        last verified against UN OHRLLS LDC list
sids_source_date    — date        last verified against UN DESA SIDS list
lldc_source_date    — date        last verified against UN OHRLLS LLDC list
notes               — text        graduation dates, pending reviews, exceptions
```

### Source URLs (record in file header comment or README)

```
LDC:  https://www.un.org/development/desa/dpad/least-developed-country-category.html
SIDS: https://www.un.org/ohrlls/content/list-sids
LLDC: https://www.un.org/ohrlls/content/list-lldcs
```

### Population rules

**is_ldc:** Copy from the model's current `country_results.csv` `is_ldc` column (via iso3 mapping). Do NOT copy from countrycode — it has four stale entries. The model's current values are correct. Set `ldc_source_date = 2025-01-01`.

**Critical LDC overrides vs countrycode** — these four countries have graduated. The model correctly has `is_ldc = FALSE` for all four. Countrycode incorrectly has `is_ldc = TRUE`. Record in the notes column:

| iso3c | Country | Graduated | Notes |
|---|---|---|---|
| BTN | Bhutan | 2023-12-13 | CDP 2021 recommendation, effective Dec 2023 |
| VUT | Vanuatu | 2020-12-04 | CDP 2012 recommendation, effective Dec 2020 |
| GNQ | Equatorial Guinea | 2017-06-12 | CDP 2012 recommendation, effective Jun 2017 |
| STP | Sao Tome and Principe | 2024-11-27 | CDP 2021 recommendation, effective Nov 2024 |

**is_sids:** 39 sovereign SIDS. Copy from model's `country_results.csv` `is_sids` column. Do NOT use countrycode — it includes 14 non-sovereign territories (Aruba, Puerto Rico, Guam etc.) that are not CBD Parties. Set `sids_source_date = 2025-01-01`.

**is_lldc:** 32 countries. Copy from countrycode `un_land_locked_developing_countries_lldc` (non-null = TRUE). This column is current and matches the official OHRLLS list. Two name updates exist in countrycode that are already correct in iso3c terms: North Macedonia (MKD, listed as "Macedonia, the former Yugoslav Republic of") and Eswatini (SWZ, listed as "Swaziland") — the iso3 codes are correct regardless of the displayed name. Set `lldc_source_date = 2025-01-01`.

**is_lldc for EU row:** `iso3c = EUU`, all flags FALSE.

### Counts to verify after creation

```
is_ldc  = TRUE:   44 rows
is_sids = TRUE:   39 rows
is_lldc = TRUE:   32 rows
Total rows:      197
```

---

## Workstream 3 — Create `data-raw/country_overlay.csv`

Create this file from scratch. It provides the CBD-specific and model-specific data that neither countrycode nor un_classifications holds.

### Schema

```
iso3c                   — ISO3 join key
cbd_party_name          — exact string used as 'party' throughout model outputs
                          This is the UN formal name from CBD instruments.
                          MUST match exactly what data_loader.py currently produces.
wb_name                 — World Bank country name for joining WDI land area and
                          income group files. Blank for Cook Islands and Niue.
is_cbd_party            — TRUE/FALSE  Party to the Convention on Biological Diversity
wb_income_group         — World Bank income classification:
                          "Low income" / "Lower middle income" /
                          "Upper middle income" / "High income"
land_area_km2_override  — Non-null only for Cook Islands and Niue.
                          All other rows: blank/null.
cbd_budget_name         — The exact Party name string as it appears in
                          data-raw/cbd_cop16_budget_table.csv. Non-null only
                          where this differs from cbd_party_name (3 rows).
                          Null/blank means names are identical.
notes                   — Special handling flags
```

### Special cases to record in notes

| iso3c | cbd_party_name | Notes |
|---|---|---|
| CIV | Côte d\u2019Ivoire | Party name uses RIGHT SINGLE QUOTATION MARK (U+2019), not ASCII apostrophe. wb_name is "Cote d'Ivoire" (ASCII). Join on iso3c not name. |
| EUU | European Union | CBD Party but not a sovereign state. Not in countrycode. No land area. WB code EUU. |
| PSE | State of Palestine | WB name is "West Bank and Gaza". Sensitive designation — retain cbd_party_name as official UN name. |
| NLD | Netherlands (Kingdom of the) | WB name is "Netherlands". |
| GBR | United Kingdom of Great Britain and Northern Ireland | WB name is "United Kingdom". |
| USA | United States of America | Not a CBD Party (is_cbd_party = FALSE). Present in model universe for completeness. |
| PRK | Democratic People's Republic of Korea | CBD budget uses RIGHT SINGLE QUOTATION MARK (U+2019) in Party name. cbd_budget_name = 'Democratic People\u2019s Republic of Korea'. cbd_party_name uses ASCII apostrophe. |
| LAO | Lao People's Democratic Republic | Same U+2019 issue as PRK. cbd_budget_name = 'Lao People\u2019s Democratic Republic'. |
| SLE | Sierra Leone | CBD budget has data entry error: 'SierraLeone' (no space). cbd_budget_name = 'SierraLeone'. |
| COK | Cook Islands | Not in WB WDI land area file. land_area_km2_override = 236.0 (UN Statistics). wb_name blank. |
| NIU | Niue | Not in WB WDI land area file. land_area_km2_override = 260.0 (UN Statistics). wb_name blank. |

### The `cbd_budget_name` column — 3 entries only

Only populate `cbd_budget_name` where it differs from `cbd_party_name`. All other rows leave it blank (blank = same as `cbd_party_name`).

| iso3c | cbd_party_name | cbd_budget_name | Reason |
|---|---|---|---|
| PRK | Democratic People's Republic of Korea (ASCII apostrophe U+0027) | Democratic People’s Republic of Korea (U+2019) | CBD budget uses smart quote |
| LAO | Lao People's Democratic Republic (ASCII apostrophe U+0027) | Lao People’s Democratic Republic (U+2019) | CBD budget uses smart quote |
| SLE | Sierra Leone | SierraLeone | Data entry error in CBD budget — do not correct the source file |

### The 21 wb_name mappings (CBD name → World Bank name)

These are the entries where `cbd_party_name != wb_name`. All others have identical names in both systems.

```
Egypt                                         → Egypt, Arab Rep.
Somalia                                       → Somalia, Fed. Rep.
Kyrgyzstan                                    → Kyrgyz Republic
Yemen                                         → Yemen, Rep.
Democratic Republic of the Congo              → Congo, Dem. Rep.
Côte d'Ivoire  [U+2019 apostrophe]           → Cote d'Ivoire  [ASCII apostrophe]
Iran (Islamic Republic of)                    → Iran, Islamic Rep.
Türkiye                                       → Turkiye
Republic of Moldova                           → Moldova
Micronesia (Federated States of)              → Micronesia, Fed. Sts.
United Republic of Tanzania                   → Tanzania
Bolivia (Plurinational State of)              → Bolivia
Venezuela (Bolivarian Republic of)            → Venezuela, RB
Democratic People's Republic of Korea         → Korea, Dem. People's Rep.
Lao People's Democratic Republic              → Lao PDR
Congo                                         → Congo, Rep.
Bahamas                                       → Bahamas, The
Gambia                                        → Gambia, The
Saint Kitts and Nevis                         → St. Kitts and Nevis
Saint Lucia                                   → St. Lucia
Saint Vincent and the Grenadines              → St. Vincent and the Grenadines
Republic of Korea                             → Korea, Rep.
Slovakia                                      → Slovak Republic
State of Palestine                            → West Bank and Gaza
United Kingdom of Great Britain and Nor... → United Kingdom
United States of America                      → United States
Netherlands (Kingdom of the)                  → Netherlands
```

### Counts to verify after creation

```
Total rows:                      197
is_cbd_party = TRUE:             196
wb_name blank:                     2  (Cook Islands, Niue)
land_area_km2_override non-null:   2  (Cook Islands=236, Niue=260)
cbd_budget_name non-null:          3  (PRK, LAO, SLE only)
```

---

## Workstream 4 — Rewrite `logic/data_loader.py`

This is the core change. Replace all name-based join logic with ISO3-keyed joins through the concordance.

### 4A — Add concordance loader function

Add a new function `load_concordance(con: duckdb.DuckDBPyConnection) -> None` that loads all three files into DuckDB tables at startup. Call it once at the beginning of `load_data()`.

```python
def load_concordance(con):
    """
    Load the three-file concordance into DuckDB.
    Creates tables: countrycode, un_classifications, country_overlay.
    All subsequent joins use iso3c as the key — no string matching.
    """
    con.execute("""
        CREATE OR REPLACE TABLE countrycode AS
        SELECT * FROM read_csv_auto('data-raw/countrycode.csv')
    """)
    con.execute("""
        CREATE OR REPLACE TABLE un_classifications AS
        SELECT * FROM read_csv_auto('data-raw/un_classifications.csv')
    """)
    con.execute("""
        CREATE OR REPLACE TABLE country_overlay AS
        SELECT * FROM read_csv_auto('data-raw/country_overlay.csv')
    """)
    # Build unified reference — one row per country
    con.execute("""
        CREATE OR REPLACE TABLE country_reference AS
        SELECT
            o.iso3c,
            o.cbd_party_name          AS party,
            o.wb_name,
            o.is_cbd_party,
            o.wb_income_group,
            o.land_area_km2_override,
            c.country_name            AS cc_name,
            c.eu27,
            c.un_region_name          AS region,
            c.un_sub_region_name      AS sub_region,
            c.un_intermediate_region_name AS intermediate_region,
            c.un_developed_or_developing_countries,
            u.is_ldc,
            u.is_sids,
            u.is_lldc,
            u.ldc_source_date,
            u.sids_source_date,
            u.lldc_source_date
        FROM country_overlay o
        LEFT JOIN countrycode c     ON o.iso3c = c.iso3c
        LEFT JOIN un_classifications u ON o.iso3c = u.iso3c
    """)
```

### 4B — Rewrite land area join

Find the existing land area loading code. Replace it with the following pattern.

**Before (current — fragile name join):**
```python
# Something like: join on country name with ad hoc matching
```

**After:**
```python
# Load WB land area file — use most recent non-null year value
con.execute("""
    CREATE OR REPLACE TABLE wb_land_raw AS
    SELECT * FROM read_csv_auto('data-raw/API_AG_LND_TOTL_K2_DS2_en_csv_v2_749.csv',
                                 skip=4)
""")

# Unpivot years and take most recent non-null value per country
# Then join to country_reference via wb_name → Country Name
con.execute("""
    CREATE OR REPLACE TABLE wb_land AS
    WITH years AS (
        -- Select all year columns and unpivot to get latest non-null
        -- DuckDB: use UNPIVOT or a lateral approach
        SELECT
            "Country Code" AS iso3c_wb,
            "Country Name" AS wb_name_raw,
            -- Take last non-null year column value
            -- Year columns run 1961–2025; filter to numeric column names
            COALESCE("2025","2024","2023","2022","2021","2020") AS land_area_km2
        FROM wb_land_raw
        WHERE "Country Code" IS NOT NULL
    )
    SELECT
        r.iso3c,
        COALESCE(y.land_area_km2, r.land_area_km2_override) AS land_area_km2,
        (y.land_area_km2 IS NOT NULL OR r.land_area_km2_override IS NOT NULL) AS has_land_area
    FROM country_reference r
    LEFT JOIN years y ON r.wb_name = y.wb_name_raw
""")
```

**Note on the COALESCE year chain:** Extend the COALESCE to cover all years back to at least 2018 so that any country whose most recent data is older than 2020 still resolves correctly. The full chain should be `COALESCE("2025","2024","2023","2022","2021","2020","2019","2018")`.

**Note on Cook Islands and Niue:** The `land_area_km2_override` column in `country_overlay.csv` handles these automatically — the COALESCE above picks them up when the WB join returns NULL.

### 4C — Rewrite income group join

Find the existing WB income group join. Replace with a direct read from `country_reference`:

```python
# Income group now comes directly from country_overlay — no external join needed
# wb_income_group is already in country_reference
```

If there is a separate WB income group file being joined, it can be retired once `country_overlay.csv` is the source. If the income group data needs to be kept fresh from the WB file, follow the same pattern as land area — join on `iso3c_wb` via `wb_name`.

### 4D — Rewrite LDC / SIDS / LLDC flag joins

These now come directly from `country_reference` (sourced from `un_classifications.csv`). Remove any existing logic that derives these flags from countrycode or other sources. The flags in `country_reference` are the authoritative values.

### 4E — Rewrite region joins

Regions now come from `country_reference` (sourced from `countrycode.csv`). Remove any existing separate region join logic.

### 4F — Remove all name-matching code

Search `data_loader.py` for any of the following patterns and remove them entirely — they are replaced by the concordance:

- `LAND_AREA_NAME_MAP` or any equivalent dict
- Any `.replace()`, `.map()`, or string-comparison logic applied to country names before a join
- Any hardcoded lists of LDC, SIDS, or LLDC country names
- Any `if country_name in [...]` logic for classification flags

### 4H — Add CBD budget join

The CBD budget table is the authoritative source for the `is_cbd_party` flag. Load it and join to `country_reference` via `iso3c`.

```python
con.execute("""
    CREATE OR REPLACE TABLE cbd_budget AS
    SELECT *
    FROM read_csv_auto('data-raw/cbd_cop16_budget_table.csv')
    WHERE Party != 'Total'  -- remove footer row
""")

-- Normalise apostrophe variants and typo before joining
-- Use REPLACE to handle U+2019 → ASCII and 'SierraLeone' → 'Sierra Leone'
con.execute("""
    CREATE OR REPLACE TABLE cbd_parties AS
    SELECT
        -- Normalise to match cbd_budget_name in country_overlay
        REPLACE(REPLACE(Party, '’', ''''), 'SierraLeone', 'Sierra Leone') AS cbd_budget_name_norm,
        TRUE AS is_cbd_party_budget
    FROM cbd_budget
""")

-- Join via country_overlay's cbd_budget_name / cbd_party_name
con.execute("""
    UPDATE country_reference
    SET is_cbd_party = (
        SELECT TRUE
        FROM cbd_parties
        WHERE cbd_budget_name_norm = country_reference.party
           OR cbd_budget_name_norm = country_reference.cbd_budget_name_norm
        LIMIT 1
    )
""")
```

**Alternative approach (simpler):** Since `is_cbd_party` is already stored in `country_overlay.csv` and has been manually verified against the CBD budget table, the join above is only needed if you want to validate the overlay against the source file at load time. If `country_overlay.csv` is trusted, `is_cbd_party` can be read directly from it without loading the CBD budget table at all. Either approach is acceptable — the key requirement is that the concordance, not ad hoc name matching, governs the flag.

**Critical — do not use the CBD budget UN scale for IUSAF.** The `UN_scale_percentage` column in the CBD budget table must not be used for band assignment or IUSAF calculation. This is a policy requirement, not merely a data precision issue.

The reason is structural. Under band-based inversion, a lower UN assessed share places a Party in a higher band and produces a larger Cali Fund allocation. If the CBD budget scale were used, a Party that successfully negotiated a lower CBD assessed contribution would consequently receive a larger Cali Fund allocation. This creates a direct financial incentive to minimise CBD budget contributions in order to maximise Cali Fund receipts — a perverse outcome that would formally link the two instruments in a way that undermines both.

Using the UNGA Scale of Assessments (UNGA resolution 79/225, 2025–2027) severs this link entirely. The UNGA scale is negotiated through a separate process (ACABQ and the Fifth Committee of the General Assembly) in which no Party can influence their Cali Fund allocation by adjusting their CBD contribution. The two instruments remain independent.

Concretely: the two scales differ for 136 of 196 Parties, and 11 Parties would move bands if the CBD budget scale were substituted — including Algeria and Venezuela moving to higher bands (more Cali), and Viet Nam, Cuba and Guyana moving to lower bands (less Cali). The band assignments under the UNGA scale are the correct and intended values.

The `UN_scale_percentage` column in `cbd_cop16_budget_table.csv` is not loaded or used by `data_loader.py` for any purpose. The `is_cbd_party` flag is the only value extracted from that file.

### 4G — Add parameter naming comment

Add the following comment block immediately after the module docstring:

```python
# Parameter naming convention
# ----------------------------
# The allocation formula weights are stored internally as:
#   tsac_beta   — the TSAC (Terrestrial Stewardship Allocation Component) weight
#   sosac_gamma — the SOSAC (SIDS Ocean Stewardship Allocation Component) weight
# These names follow the convention used in the original formula specification
# (Final_share = (1 - beta - gamma) * IUSAF + beta * TSAC + gamma * SOSAC).
# Display labels in the UI use "TSAC weight" and "SOSAC weight" for clarity.
# See also: logic/sensitivity_scenarios.py, logic/sensitivity_metrics.py,
#           logic/balance_analysis.py — same convention applies.
```

---

## Workstream 5 — Tests

### 5A — Add `tests/test_concordance.py`

```python
"""Tests for the three-file concordance and data_loader concordance integration."""
import pandas as pd
import pytest
import duckdb

from logic.data_loader import load_data, get_base_data

COUNTRYCODE      = 'data-raw/countrycode.csv'
UN_CLASS         = 'data-raw/un_classifications.csv'
COUNTRY_OVERLAY  = 'data-raw/country_overlay.csv'


# ── File structure tests ──────────────────────────────────────────────────

class TestCountrycode:
    def test_row_count(self):
        df = pd.read_csv(COUNTRYCODE)
        assert len(df) == 263

    def test_dropped_columns_absent(self):
        df = pd.read_csv(COUNTRYCODE)
        for col in ['country_lower',
                    'un_least_developed_countries_ldc',
                    'un_land_locked_developing_countries_lldc',
                    'un_small_island_developing_states_sids']:
            assert col not in df.columns, f"Column '{col}' should have been dropped"

    def test_required_columns_present(self):
        df = pd.read_csv(COUNTRYCODE)
        for col in ['iso3c', 'iso2c', 'eu27', 'un_region_name',
                    'un_sub_region_name', 'un_intermediate_region_name']:
            assert col in df.columns

    def test_no_typo_in_developed_column(self):
        df = pd.read_csv(COUNTRYCODE)
        col = 'un_developed_or_developing_countries'
        vals = df[col].dropna().unique()
        assert 'Developedl' not in vals, "Typo 'Developedl' still present"


class TestUnClassifications:
    def test_row_count(self):
        df = pd.read_csv(UN_CLASS)
        assert len(df) == 197

    def test_ldc_count(self):
        df = pd.read_csv(UN_CLASS)
        assert df['is_ldc'].sum() == 44

    def test_sids_count(self):
        df = pd.read_csv(UN_CLASS)
        assert df['is_sids'].sum() == 39

    def test_lldc_count(self):
        df = pd.read_csv(UN_CLASS)
        assert df['is_lldc'].sum() == 32

    def test_graduated_ldcs_are_false(self):
        df = pd.read_csv(UN_CLASS).set_index('iso3c')
        for iso3 in ['BTN', 'VUT', 'GNQ', 'STP']:
            assert not df.loc[iso3, 'is_ldc'], \
                f"{iso3} graduated from LDC but is_ldc=True"

    def test_no_duplicate_iso3(self):
        df = pd.read_csv(UN_CLASS)
        assert df['iso3c'].nunique() == len(df)

    def test_source_dates_present(self):
        df = pd.read_csv(UN_CLASS)
        for col in ['ldc_source_date', 'sids_source_date', 'lldc_source_date']:
            assert df[col].notna().all(), f"{col} has null values"


class TestCountryOverlay:
    def test_row_count(self):
        df = pd.read_csv(COUNTRY_OVERLAY)
        assert len(df) == 197

    def test_cbd_party_count(self):
        df = pd.read_csv(COUNTRY_OVERLAY)
        assert df['is_cbd_party'].sum() == 196

    def test_no_duplicate_iso3(self):
        df = pd.read_csv(COUNTRY_OVERLAY)
        assert df['iso3c'].nunique() == len(df)

    def test_cook_islands_niue_overrides(self):
        df = pd.read_csv(COUNTRY_OVERLAY).set_index('iso3c')
        assert df.loc['COK', 'land_area_km2_override'] == pytest.approx(236.0)
        assert df.loc['NIU', 'land_area_km2_override'] == pytest.approx(260.0)

    def test_wb_name_blank_only_for_missing_wb_data(self):
        df = pd.read_csv(COUNTRY_OVERLAY)
        blank_wb = df[df['wb_name'].isna() | (df['wb_name'] == '')]
        # Only Cook Islands and Niue should have blank wb_name
        assert set(blank_wb['iso3c']) == {'COK', 'NIU'}

    def test_usa_not_cbd_party(self):
        df = pd.read_csv(COUNTRY_OVERLAY).set_index('iso3c')
        assert not df.loc['USA', 'is_cbd_party']

    def test_eu_is_cbd_party(self):
        df = pd.read_csv(COUNTRY_OVERLAY).set_index('iso3c')
        assert df.loc['EUU', 'is_cbd_party']

    def test_all_iso3_consistent_with_countrycode(self):
        overlay = pd.read_csv(COUNTRY_OVERLAY)
        cc = pd.read_csv(COUNTRYCODE)
        cc_iso3 = set(cc['iso3c'])
        # All overlay iso3 codes except EUU should be in countrycode
        overlay_iso3 = set(overlay['iso3c']) - {'EUU'}
        missing = overlay_iso3 - cc_iso3
        assert not missing, f"iso3 codes in overlay but not countrycode: {missing}"


class TestCbdBudgetTable:
    CBD_BUDGET = 'data-raw/cbd_cop16_budget_table.csv'

    def test_total_row_filtered(self):
        df = pd.read_csv(self.CBD_BUDGET)
        # 'Total' row should not be treated as a Party
        assert 'Total' in df['Party'].values, "Total row absent — test expectations wrong"

    def test_sierra_leone_typo_documented(self):
        df = pd.read_csv(self.CBD_BUDGET)
        # Confirm the known typo is still present in the source file
        # (it should be corrected via cbd_budget_name in overlay, not in the source)
        assert 'SierraLeone' in df['Party'].values,             "SierraLeone typo corrected in source — remove cbd_budget_name entry for SLE"

    def test_196_parties_excluding_total(self):
        df = pd.read_csv(self.CBD_BUDGET)
        parties = df[df['Party'] != 'Total']
        assert len(parties) == 196

    def test_usa_absent(self):
        df = pd.read_csv(self.CBD_BUDGET)
        assert 'United States of America' not in df['Party'].values
        assert 'United States' not in df['Party'].values


# ── Integration tests ─────────────────────────────────────────────────────

@pytest.fixture(scope='module')
def base_df():
    con = duckdb.connect(':memory:')
    load_data(con)
    return get_base_data(con)


class TestDataLoaderIntegration:
    def test_all_197_rows_present(self, base_df):
        assert len(base_df) == 197

    def test_no_missing_land_area_for_eligible(self, base_df):
        # All eligible parties should now have land area data
        eligible = base_df[base_df['eligible']]
        missing = eligible[~eligible['has_land_area']]
        assert len(missing) == 0, \
            f"Eligible parties missing land area: {missing['party'].tolist()}"

    def test_21_previously_missing_now_have_land_area(self, base_df):
        previously_missing = [
            'Egypt', 'Somalia', 'Kyrgyzstan', 'Yemen',
            'Democratic Republic of the Congo', 'Iran (Islamic Republic of)',
            'Türkiye', 'Republic of Moldova',
            'Micronesia (Federated States of)',
            'United Republic of Tanzania',
            'Bolivia (Plurinational State of)',
            'Venezuela (Bolivarian Republic of)',
            "Democratic People's Republic of Korea",
            "Lao People's Democratic Republic",
            'Congo', 'Bahamas', 'Gambia',
            'Saint Kitts and Nevis', 'Saint Lucia',
            'Saint Vincent and the Grenadines',
        ]
        # Côte d'Ivoire excluded from list — test by iso3 instead
        for party in previously_missing:
            row = base_df[base_df['party'] == party]
            assert not row.empty, f"{party} not found"
            assert row['has_land_area'].values[0], \
                f"{party} still missing land area after concordance fix"

    def test_cote_divoire_has_land_area(self, base_df):
        cdi = base_df[base_df['party'].str.contains('voire', na=False)]
        assert len(cdi) == 1
        assert cdi['has_land_area'].values[0]

    def test_graduated_ldcs_not_flagged(self, base_df):
        graduated_names = ['Bhutan', 'Vanuatu', 'Equatorial Guinea',
                           'Sao Tome and Principe']
        for name in graduated_names:
            row = base_df[base_df['party'] == name]
            if not row.empty:
                assert not row['is_ldc'].values[0], \
                    f"{name} incorrectly flagged as LDC"

    def test_ldc_count(self, base_df):
        assert base_df['is_ldc'].sum() == 44

    def test_sids_count(self, base_df):
        assert base_df['is_sids'].sum() == 39

    def test_eligible_land_total_approx(self, base_df):
        # After fix: ~78M km² (was ~67M km² before concordance)
        total = base_df[base_df['eligible']]['land_area_km2'].sum()
        assert total > 75_000_000, \
            f"Total eligible land area too low: {total:,.0f} km² (expect ~78M)"
        assert total < 85_000_000, \
            f"Total eligible land area too high: {total:,.0f} km²"

    def test_cbd_party_count(self, base_df):
        assert base_df['is_cbd_party'].sum() == 196

    def test_usa_not_cbd_party(self, base_df):
        usa = base_df[base_df['party'].str.contains('United States', na=False)]
        assert not usa.empty
        assert not usa['is_cbd_party'].values[0]

    def test_sierra_leone_is_cbd_party(self, base_df):
        sl = base_df[base_df['party'] == 'Sierra Leone']
        assert not sl.empty
        assert sl['is_cbd_party'].values[0], \
            "Sierra Leone is_cbd_party=False — SierraLeone typo not resolved"

    def test_dprk_is_cbd_party(self, base_df):
        dprk = base_df[base_df['party'].str.contains('Democratic People', na=False)]
        assert not dprk.empty
        assert dprk['is_cbd_party'].values[0], \
            "DPRK is_cbd_party=False — U+2019 apostrophe not resolved"

    def test_lao_is_cbd_party(self, base_df):
        lao = base_df[base_df['party'].str.contains('Lao People', na=False)]
        assert not lao.empty
        assert lao['is_cbd_party'].values[0], \
            "Lao PDR is_cbd_party=False — U+2019 apostrophe not resolved"

    def test_un_share_uses_2025_2027_scale_not_cbd_budget(self, base_df):
        # China's 2025-2027 UN scale is 20.004% — CBD budget has 15.254%
        # If the model accidentally joined from CBD budget, China would show ~15.25
        china = base_df[base_df['party'] == 'China']
        assert not china.empty
        assert abs(china['un_share'].values[0] - 20.004) < 0.01, \
            f"China un_share={china['un_share'].values[0]} — model may be using CBD budget scale instead of UNGA 2025-2027"

    def test_conservation(self, base_df):
        # Allocations sum to fund size (checked via calculate_allocations separately)
        # Here just check no negative land areas
        assert (base_df['land_area_km2'].fillna(0) >= 0).all()
```

### 5B — Update `tests/test_band_inversion.py` if needed

If this test file includes hardcoded counts of parties with land area (e.g. `assert n_with_land == 121`), update to `142` (all eligible parties) or remove the hardcoded count and replace with `assert base_df[base_df['eligible']]['has_land_area'].all()`.

---

## Workstream 6 — Rerun sensitivity tests and update outputs

Once data_loader.py is updated and all tests pass, the sensitivity outputs will change because 21 previously-missing parties now contribute to the TSAC land area pool. The eligible land total increases from ~67M km² to ~78M km² (+16.3%), which reduces China's and Brazil's TSAC shares and shifts the balance points upward.

### 6A — Regenerate all sensitivity outputs

Run the sensitivity application and export fresh versions of all standard outputs:
- `scenario_metrics.csv`
- `tsac_fine_sweep.csv` and `sosac_fine_sweep.csv`
- `balance_points.csv`
- `current_component_ratios.csv`
- All markdown reports

### 6B — Expected changes to balance points

The confirmed balance points will shift. Approximate expected new values based on analytical calculation with the corrected 78M km² land total:

| Balance point | Current | Expected after fix |
|---|---|---|
| Strict (China crossover) | 1.5% | ~1.9% |
| Modified (Brazil crossover) | 3.0% | ~3.8% |
| Practical (min Gini, Spearman > 0.85) | 4.0% | TBD from sweep |

Verify the actual values from the sweep rather than using these analytical estimates — they are indicative only.

### 6C — Update named scenarios

After the sweep confirms the new balance points, update `logic/sensitivity_scenarios.py`:
- `tsac_strict_balance`: set `tsac_beta` to confirmed strict balance point (~1.9%)
- `tsac_modified_balance`: set `tsac_beta` to confirmed modified balance point (~3.8%)

### 6D — Update documentation

Update the following documents with confirmed figures from the new sweep:
- `balance_point_summary.md`: replace 1.5% / 3.0% / 4.0% with new values
- `CBD_AHEGF_IUSAF_technical_note.docx` Section V: replace balance point figures
- `v3_sensitivity_assessment.docx`: update Section 2.2 table and Section 9 integrity summary

---

## Acceptance criteria

Run `python3 -m pytest` — all tests including `tests/test_concordance.py` must pass.

Verify manually:

1. `data-raw/countrycode.csv` does not contain `country_lower`, `un_least_developed_countries_ldc`, `un_land_locked_developing_countries_lldc`, or `un_small_island_developing_states_sids` columns.
2. `data-raw/un_classifications.csv` exists with 197 rows: 44 LDC, 39 SIDS, 32 LLDC.
3. `data-raw/country_overlay.csv` exists with 197 rows: 196 CBD Parties, wb_name blank only for COK and NIU.
4. `get_base_data()` returns 197 rows with `has_land_area = True` for all 142 eligible parties.
5. `base_df[base_df['eligible']]['land_area_km2'].sum()` is approximately 78 million km² (previously ~67 million).
6. Bhutan, Vanuatu, Equatorial Guinea and Sao Tome and Principe all have `is_ldc = False`.
7. `data_loader.py` contains no string-matching logic, no name-mapping dicts, no hardcoded country name lists.
8. The sensitivity application runs without error.
9. `base_df['is_cbd_party'].sum() == 196`.
10. Sierra Leone, DPRK, and Lao PDR all have `is_cbd_party = True`.
11. China's `un_share` is approximately 20.004 (UNGA 2025-2027 scale), not 15.254 (CBD budget scale). The TSAC fine sweep produces updated balance points consistent with the larger land area total.

---

## Files to create or modify — summary

| Action | File | Workstream |
|---|---|---|
| MODIFY | `data-raw/countrycode.csv` | 1 |
| CREATE | `data-raw/un_classifications.csv` | 2 |
| CREATE | `data-raw/country_overlay.csv` | 3 |
| MODIFY | `logic/data_loader.py` | 4 |
| CREATE | `tests/test_concordance.py` | 5 |
| MODIFY | `tests/test_band_inversion.py` | 5B (if needed) |
| MODIFY | `logic/sensitivity_scenarios.py` | 6C |
| MODIFY | `data-raw/balance_point_summary.md` | 6D |

| VERIFY (do not modify) | `data-raw/cbd_cop16_budget_table.csv` | 3, 4H |

**Do not modify:** `logic/calculator.py`, `logic/balance_analysis.py`, `logic/sensitivity_metrics.py`, `app.py`, `sensitivity.py`, `config/un_scale_bands.yaml`.
