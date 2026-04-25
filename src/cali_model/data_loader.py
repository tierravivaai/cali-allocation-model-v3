import duckdb
import pandas as pd
from pathlib import Path


def load_data(con):
    # Base paths
    base_path = "data-raw"
    config_path = Path(__file__).resolve().parent.parent.parent / "config"
    
    # 1. Load UN Scale of Assessment
    con.execute(f"CREATE TABLE un_scale AS SELECT * FROM read_csv_auto('{base_path}/UNGA_scale_of_assessment.csv')")
    
    # 2. Load UNSD Regions
    con.execute(f"CREATE TABLE unsd_regions AS SELECT * FROM read_csv_auto('{base_path}/unsd_region_useme.csv')")
    
    # 3. Load World Bank Income Classes
    con.execute(f"CREATE TABLE wb_income AS SELECT * FROM read_csv_auto('{base_path}/world_bank_income_class.csv')")
    
    # 4. Load EU27 Member States
    con.execute(f"CREATE TABLE eu27 AS SELECT * FROM read_csv_auto('{base_path}/eu27.csv')")
    
    # 5. Load Party Master (consolidated name concordance + overrides)
    # Read via pandas to control types — DuckDB read_csv_auto infers BOOLEAN which breaks NULLIF
    pm_df = pd.read_csv(config_path / "party_master.csv", dtype=str)
    pm_df = pm_df.fillna("")
    con.register("party_master_df", pm_df)
    con.execute("CREATE TABLE party_master AS SELECT * FROM party_master_df")
    
    # 6. Load Manual Name Map (legacy, for UN scale + CBD party name resolution)
    con.execute(f"CREATE TABLE name_map AS SELECT * FROM read_csv_auto('{base_path}/manual_name_map.csv')")

    # 7. Load Land Area (World Bank)
    # Name concordance handled via party_master: we keep raw WB Country Names as-is
    # and SQL JOINs use party_master.wb_land_area_name as the bridge.
    land_area_path = f"{base_path}/API_AG.LND.TOTL.K2_DS2_en_csv_v2_749/API_AG.LND.TOTL.K2_DS2_en_csv_v2_749.csv"
    land_df = pd.read_csv(land_area_path, skiprows=4)
    year_cols = [c for c in land_df.columns if str(c).strip().isdigit()]
    numeric_land = land_df[year_cols].apply(pd.to_numeric, errors="coerce")
    land_df["land_area_km2"] = numeric_land.ffill(axis=1).iloc[:, -1]
    land_df["land_area_year"] = numeric_land.apply(
        lambda row: next((int(col) for col in reversed(year_cols) if pd.notna(row[col])), None),
        axis=1,
    )
    land_area_latest_df = land_df[["Country Name", "Country Code", "land_area_km2", "land_area_year"]].copy()
    # Ensure string columns use object dtype (DuckDB doesn't recognise pandas StringDtype)
    for col in land_area_latest_df.select_dtypes(include=["object"]).columns:
        land_area_latest_df[col] = land_area_latest_df[col].astype("object")
    con.register("land_area_latest_df", land_area_latest_df)
    con.execute("CREATE TABLE land_area_latest AS SELECT * FROM land_area_latest_df")

    # 8. Load CBD Parties List (using the budget table as source of truth for Parties)
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
    # Key change: land area and income joins now route through party_master
    # name concordance, eliminating manual df.loc patches and LAND_AREA_NAME_MAP.
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
          AND un_share > 0
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
            -- Region: prefer party_master override, then mapped name, then raw name
            COALESCE(NULLIF(pm.region_override, ''), r_mapped."Region Name", r_raw."Region Name") as region,
            COALESCE(NULLIF(pm.sub_region_override, ''), r_mapped."Sub-region Name", r_raw."Sub-region Name") as sub_region,
            COALESCE(NULLIF(pm.intermediate_region_override, ''), r_mapped."Intermediate Region Name", r_raw."Intermediate Region Name") as intermediate_region,
            -- LDC/SIDS: prefer party_master override, then CSV value
            CASE
                WHEN NULLIF(pm.is_ldc_override, '') IS NOT NULL THEN pm.is_ldc_override = 'True'
                ELSE COALESCE(r_mapped."Least Developed Countries (LDC)", r_raw."Least Developed Countries (LDC)") = 'x'
            END as is_ldc,
            CASE
                WHEN NULLIF(pm.is_sids_override, '') IS NOT NULL THEN pm.is_sids_override = 'True'
                ELSE COALESCE(r_mapped."Small Island Developing States (SIDS)", r_raw."Small Island Developing States (SIDS)") = 'x'
            END as is_sids,
            -- Income: prefer party_master override, then mapped/raw name JOIN
            w_mapped."Income group" is not null or w_raw."Income group" is not null or NULLIF(pm.income_group_override, '') IS NOT NULL as has_income_data,
            COALESCE(NULLIF(pm.income_group_override, ''), w_mapped."Income group", w_raw."Income group", 'Not Available') as "WB Income Group",
            -- EU membership: party_master override or eu27 table
            CASE
                WHEN NULLIF(pm.is_eu_ms_override, '') IS NOT NULL THEN pm.is_eu_ms_override = 'True'
                ELSE e.is_eu27 IS NOT NULL
            END as is_eu_ms,
            c.Party IS NOT NULL OR s.party = 'European Union' as is_cbd_party,
            -- Land area: join via party_master name concordance, then direct name fallback
            COALESCE(pm_la.land_area_km2, la_direct.land_area_km2, 0.0) as land_area_km2,
            CASE
                WHEN pm.land_area_km2_override IS NOT NULL THEN True
                WHEN pm_la.land_area_km2 IS NOT NULL THEN True
                WHEN la_direct.land_area_km2 IS NOT NULL THEN True
                ELSE False
            END as has_land_area
        FROM mapped_scale s
        FULL OUTER JOIN cbd_parties c ON s.party = c.Party
        -- Party master override table
        LEFT JOIN party_master pm ON COALESCE(s.party, c.Party) = pm.party
        -- Region via mapped name
        LEFT JOIN unsd_regions r_mapped ON COALESCE(s.party, c.Party) = r_mapped."Country or Area"
        LEFT JOIN unsd_regions r_raw ON c.Party = r_raw."Country or Area"
        -- Income via mapped name
        LEFT JOIN wb_income w_mapped ON COALESCE(s.party, c.Party) = w_mapped.Economy
        LEFT JOIN wb_income w_raw ON c.Party = w_raw.Economy
        -- EU27 check
        LEFT JOIN eu27 e ON COALESCE(s.party, c.Party) = e.party
        -- Land area via party_master name concordance (primary)
        LEFT JOIN party_master pm2 ON COALESCE(s.party, c.Party) = pm2.party
        LEFT JOIN land_area_latest pm_la ON pm2.wb_land_area_name = pm_la."Country Name"
        -- Land area via direct canonical name (fallback for ~137 parties where names match)
        LEFT JOIN land_area_latest la_direct ON COALESCE(s.party, c.Party) = la_direct."Country Name"
    )
    SELECT * FROM joined
    """
    df = con.execute(sql).df()
    
    # Apply land_area_km2 overrides from party_master (Monaco, Cook Islands, Niue, Palestine, EU)
    pm = con.execute("SELECT party, land_area_km2_override FROM party_master WHERE land_area_km2_override IS NOT NULL AND land_area_km2_override != ''").df()
    for _, row in pm.iterrows():
        mask = df['party'] == row['party']
        if mask.any():
            val = float(row['land_area_km2_override'])
            df.loc[mask, 'land_area_km2'] = val
            df.loc[mask, 'has_land_area'] = True

    # Clean up NA strings to "Not Available"
    df['WB Income Group'] = df['WB Income Group'].replace('NA', 'Not Available')

    return df
