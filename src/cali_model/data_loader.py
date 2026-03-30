import duckdb
import pandas as pd
import os


LAND_AREA_NAME_MAP = {
    "Egypt": "Egypt, Arab Rep.",
    "Somalia": "Somalia, Fed. Rep.",
    "Kyrgyzstan": "Kyrgyz Republic",
    "Yemen": "Yemen, Rep.",
    "Democratic Republic of the Congo": "Congo, Dem. Rep.",
    "Côte d'Ivoire": "Cote d'Ivoire",
    "Côte d’Ivoire": "Cote d'Ivoire",
    "Iran (Islamic Republic of)": "Iran, Islamic Rep.",
    "Türkiye": "Turkiye",
    "Republic of Moldova": "Moldova",
    "Micronesia (Federated States of)": "Micronesia, Fed. Sts.",
    "United Republic of Tanzania": "Tanzania",
    "Bolivia (Plurinational State of)": "Bolivia",
    "Venezuela (Bolivarian Republic of)": "Venezuela, RB",
    "Democratic People's Republic of Korea": "Korea, Dem. People's Rep.",
    "Lao People's Democratic Republic": "Lao PDR",
    "Congo": "Congo, Rep.",
    "Bahamas": "Bahamas, The",
    "Gambia": "Gambia, The",
    "Saint Kitts and Nevis": "St. Kitts and Nevis",
    "Saint Lucia": "St. Lucia",
    "Saint Vincent and the Grenadines": "St. Vincent and the Grenadines",
}

def load_data(con):
    # Base paths
    base_path = "data-raw"
    
    # 1. Load UN Scale of Assessment
    con.execute(f"CREATE TABLE un_scale AS SELECT * FROM read_csv_auto('{base_path}/UNGA_scale_of_assessment.csv')")
    
    # 2. Load UNSD Regions
    con.execute(f"CREATE TABLE unsd_regions AS SELECT * FROM read_csv_auto('{base_path}/unsd_region_useme.csv')")
    
    # 3. Load World Bank Income Classes
    con.execute(f"CREATE TABLE wb_income AS SELECT * FROM read_csv_auto('{base_path}/world_bank_income_class.csv')")
    
    # 4. Load EU27 Member States
    con.execute(f"CREATE TABLE eu27 AS SELECT * FROM read_csv_auto('{base_path}/eu27.csv')")
    
    # 5. Load Manual Name Map
    con.execute(f"CREATE TABLE name_map AS SELECT * FROM read_csv_auto('{base_path}/manual_name_map.csv')")

    # 5b. Load Land Area (World Bank)
    # The CSV has 4 header lines to skip.
    land_area_path = f"{base_path}/API_AG.LND.TOTL.K2_DS2_en_csv_v2_749/API_AG.LND.TOTL.K2_DS2_en_csv_v2_749.csv"
    land_df = pd.read_csv(land_area_path, skiprows=4)
    year_cols = [c for c in land_df.columns if str(c).strip().isdigit()]
    numeric_land = land_df[year_cols].apply(pd.to_numeric, errors="coerce")
    land_df["land_area_km2"] = numeric_land.ffill(axis=1).iloc[:, -1]
    land_df["land_area_year"] = numeric_land.apply(
        lambda row: next((int(col) for col in reversed(year_cols) if pd.notna(row[col])), None),
        axis=1,
    )
    land_df["Country Name"] = land_df["Country Name"].replace({v: k for k, v in LAND_AREA_NAME_MAP.items()})
    land_area_latest_df = land_df[["Country Name", "Country Code", "land_area_km2", "land_area_year"]].copy()
    con.register("land_area_latest_df", land_area_latest_df)
    con.execute("CREATE TABLE land_area_latest AS SELECT * FROM land_area_latest_df")

    # 6. Load CBD Parties List (using the budget table as source of truth for Parties)
    con.execute(f"""
        CREATE TABLE cbd_parties_raw AS 
        SELECT 
            TRIM(Party) as party_raw 
        FROM read_csv_auto('{base_path}/cbd_cop16_budget_table.csv')
        WHERE Party IS NOT NULL AND Party != 'Total'
    """)
    
    con.execute("""
        CREATE TABLE cbd_parties AS
        SELECT DISTINCT
            COALESCE(m.party_mapped, c.party_raw) as Party
        FROM cbd_parties_raw c
        LEFT JOIN name_map m ON c.party_raw = m.party_raw
    """)

def get_base_data(con):
    # Combine and clean data
    sql = r"""
    WITH raw_scale AS (
        SELECT 
            TRIM(REPLACE("Member State", '\n', ' ')) as party_name, 
            CASE 
                WHEN "2027" = '-' OR "2027" = 'NA' THEN 0.0 
                ELSE TRY_CAST("2027" AS DOUBLE) 
            END as un_share
        FROM un_scale
    ),
    scale_2027 AS (
        SELECT * FROM raw_scale
        WHERE party_name IS NOT NULL
          AND party_name != 'Total'
          AND un_share IS NOT NULL
          AND un_share > 0 -- Filter out states that have disappeared or have no share in 2027
          AND party_name NOT LIKE 'a/%'
          AND party_name NOT LIKE 'b/%'
          AND party_name NOT LIKE 'c/%'
          AND party_name NOT LIKE 'd/%'
          AND party_name NOT LIKE 'e/%'
          AND party_name NOT LIKE 'f/%'
          AND party_name NOT LIKE 'g/%'
          AND party_name NOT LIKE 'h/%'
          AND party_name NOT LIKE 'i/%'
          AND party_name NOT LIKE 'j/%'
          AND party_name NOT LIKE 'k/%'
          AND party_name NOT LIKE 'c:\%'
          AND party_name !~ '^\d{2}/\d{2}/\d{4}$'
    ),
    mapped_scale AS (
        SELECT 
            COALESCE(m.party_mapped, s.party_name) as party,
            s.un_share
        FROM scale_2027 s
        LEFT JOIN name_map m ON s.party_name = m.party_raw
    ),
    joined AS (
        SELECT 
            COALESCE(s.party, c.Party) as party,
            COALESCE(s.un_share, 0.0) as un_share,
            -- Prioritize UNSD Region mapping
            COALESCE(r_mapped."Region Name", r_raw."Region Name") as region,
            COALESCE(r_mapped."Sub-region Name", r_raw."Sub-region Name") as sub_region,
            COALESCE(r_mapped."Intermediate Region Name", r_raw."Intermediate Region Name") as intermediate_region,
            COALESCE(r_mapped."Least Developed Countries (LDC)", r_raw."Least Developed Countries (LDC)") = 'x' as is_ldc,
            COALESCE(r_mapped."Small Island Developing States (SIDS)", r_raw."Small Island Developing States (SIDS)") = 'x' as is_sids,
            -- Prioritize WB Income mapping
            w_mapped."Income group" is not null or w_raw."Income group" is not null as has_income_data,
            COALESCE(w_mapped."Income group", w_raw."Income group", 'Not Available') as "WB Income Group",
            e.is_eu27 IS NOT NULL as is_eu_ms,
            c.Party IS NOT NULL OR s.party = 'European Union' as is_cbd_party,
            COALESCE(la.land_area_km2, 0.0) as land_area_km2,
            la.land_area_km2 IS NOT NULL as has_land_area
        FROM mapped_scale s
        FULL OUTER JOIN cbd_parties c ON s.party = c.Party
        -- Map 1: Using the 'mapped' party name (from name_map)
        LEFT JOIN unsd_regions r_mapped ON COALESCE(s.party, c.Party) = r_mapped."Country or Area"
        LEFT JOIN wb_income w_mapped ON COALESCE(s.party, c.Party) = w_mapped.Economy
        -- Map 2: Using the 'raw' party name (from budget table) as a fallback
        LEFT JOIN unsd_regions r_raw ON c.Party = r_raw."Country or Area"
        LEFT JOIN wb_income w_raw ON c.Party = w_raw.Economy
        -- Map 3: EU27 check
        LEFT JOIN eu27 e ON COALESCE(s.party, c.Party) = e.party
        -- Map 4: Land Area (World Bank)
        -- Attempt join on mapped name first, then fallback to name_map check
        LEFT JOIN land_area_latest la ON COALESCE(s.party, c.Party) = la."Country Name"
    )
    SELECT * FROM joined
    """
    # Ensure EU Party entry exists if not already there
    df = con.execute(sql).df()
    
    # Clean up NA strings to "Not Available"
    df['WB Income Group'] = df['WB Income Group'].replace('NA', 'Not Available')
    
    # Manual fixes for known missing income data
    df.loc[df['party'] == 'Venezuela (Bolivarian Republic of)', 'WB Income Group'] = 'Lower middle income' 
    df.loc[df['party'] == 'Venezuela (Bolivarian Republic of)', 'region'] = 'Americas'
    df.loc[df['party'] == 'Venezuela (Bolivarian Republic of)', 'sub_region'] = 'Latin America and the Caribbean'
    df.loc[df['party'] == 'Venezuela (Bolivarian Republic of)', 'intermediate_region'] = 'South America'
    df.loc[df['party'] == 'Venezuela (Bolivarian Republic of)', 'is_ldc'] = False
    df.loc[df['party'] == 'Venezuela (Bolivarian Republic of)', 'is_sids'] = False
    
    df.loc[df['party'] == 'Democratic Republic of the Congo', 'WB Income Group'] = 'Low income'
    df.loc[df['party'] == 'Democratic Republic of the Congo', 'region'] = 'Africa'
    df.loc[df['party'] == 'Democratic Republic of the Congo', 'sub_region'] = 'Sub-Saharan Africa'
    df.loc[df['party'] == 'Democratic Republic of the Congo', 'intermediate_region'] = 'Middle Africa'
    df.loc[df['party'] == 'Democratic Republic of the Congo', 'is_ldc'] = True
    df.loc[df['party'] == 'Democratic Republic of the Congo', 'is_sids'] = False

    df.loc[df['party'] == 'European Union', 'WB Income Group'] = 'High income'
    df.loc[df['party'] == 'European Union', 'region'] = 'Europe'
    df.loc[df['party'] == 'European Union', 'sub_region'] = 'Western Europe'
    df.loc[df['party'] == 'European Union', 'intermediate_region'] = 'NA'
    df.loc[df['party'] == 'European Union', 'is_ldc'] = False
    df.loc[df['party'] == 'European Union', 'is_sids'] = False

    df.loc[df['party'] == 'Ethiopia', 'WB Income Group'] = 'Low income'
    df.loc[df['party'] == 'Sao Tome and Principe', 'WB Income Group'] = 'Lower middle income'
    df.loc[df['party'] == 'Cook Islands', 'WB Income Group'] = 'High income'
    df.loc[df['party'] == 'Niue', 'WB Income Group'] = 'High income'
    df.loc[df['party'] == "Lao People's Democratic Republic", 'WB Income Group'] = 'Lower middle income'
    df.loc[df['party'] == "Democratic People's Republic of Korea", 'WB Income Group'] = 'Low income'
    df.loc[df['party'] == "Slovakia", 'WB Income Group'] = 'High income'
    df.loc[df['party'] == "United Republic of Tanzania", 'WB Income Group'] = 'Lower middle income'
    df.loc[df['party'] == "Bahamas", 'WB Income Group'] = 'High income'
    df.loc[df['party'] == "Saint Lucia", 'WB Income Group'] = 'Upper middle income'
    df.loc[df['party'] == "Saint Vincent and the Grenadines", 'WB Income Group'] = 'Upper middle income'
    df.loc[df['party'] == "Bolivia (Plurinational State of)", 'WB Income Group'] = 'Lower middle income'
    df.loc[df['party'] == "Viet Nam", 'WB Income Group'] = 'Lower middle income'
    df.loc[df['party'] == "State of Palestine", 'WB Income Group'] = 'Lower middle income'
    df.loc[df['party'] == "Yemen", 'WB Income Group'] = 'Low income'
    df.loc[df['party'] == "United Kingdom of Great Britain and Northern Ireland", 'WB Income Group'] = 'High income'
    df.loc[df['party'] == "United States of America", 'WB Income Group'] = 'High income'
    
    # Manual fixes for missing land area
    # Note: land_area_km2 already initialized to 0.0 if COALESCE fails
    df.loc[df['party'] == 'Monaco', 'land_area_km2'] = 2.02
    df.loc[df['party'] == 'Cook Islands', 'land_area_km2'] = 236.0
    df.loc[df['party'] == 'Niue', 'land_area_km2'] = 260.0
    df.loc[df['party'] == 'State of Palestine', 'land_area_km2'] = 6020.0
    df.loc[df['party'] == 'European Union', 'land_area_km2'] = 0.0 # EU is not assigned land area in this model
    
    # Mark as having land area after manual fixes
    manual_la_list = ['Monaco', 'Cook Islands', 'Niue', 'State of Palestine']
    df.loc[df['party'].isin(manual_la_list), 'has_land_area'] = True

    return df
