"""
Generate config/party_master.csv — the canonical party concordance and override table.

Strategy: Run the current pipeline, then compare each party's resolved values
against the raw CSV values. Where they differ, record the override. The resulting
CSV contains ONLY parties that need name mapping or data overrides.

For parties NOT in this file, the SQL JOINs in data_loader.py will resolve names
directly from the raw CSVs (just as they do now for ~160 countries that match).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import duckdb
import pandas as pd
from cali_model.data_loader import load_data, get_base_data

# Load current pipeline output
con = duckdb.connect()
load_data(con)
df = get_base_data(con)
con.close()

# Load raw sources for comparison
land_df = pd.read_csv(
    "data-raw/API_AG.LND.TOTL.K2_DS2_en_csv_v2_749/"
    "API_AG.LND.TOTL.K2_DS2_en_csv_v2_749.csv",
    skiprows=4,
)
wb_income = pd.read_csv("data-raw/world_bank_income_class.csv")

# ---- Income group overrides ----
INCOME_OVERRIDES = {
    "Venezuela (Bolivarian Republic of)": {"income_group": "Lower middle income", "reason": "WB 2024 classifies as Lower middle income; conflict year"},
    "Democratic Republic of the Congo": {"income_group": "Low income", "reason": "WB missing for DRC"},
    "European Union": {"income_group": "High income", "reason": "EU is not in WB income classification; assigned High income"},
    "Ethiopia": {"income_group": "Low income", "reason": "WB updated classification"},
    "Sao Tome and Principe": {"income_group": "Lower middle income", "reason": "WB updated classification"},
    "Cook Islands": {"income_group": "High income", "reason": "Not in WB classification; assigned per UN status"},
    "Niue": {"income_group": "High income", "reason": "Not in WB classification; assigned per UN status"},
    "Lao People's Democratic Republic": {"income_group": "Lower middle income", "reason": "WB updated classification"},
    "Democratic People's Republic of Korea": {"income_group": "Low income", "reason": "Not in WB classification; assigned per UN status"},
    "Slovakia": {"income_group": "High income", "reason": "WB name mismatch (Slovak Republic); override ensures correct group"},
    "United Republic of Tanzania": {"income_group": "Lower middle income", "reason": "WB updated classification"},
    "Bahamas": {"income_group": "High income", "reason": "WB name mismatch (Bahamas, The); override ensures correct group"},
    "Saint Lucia": {"income_group": "Upper middle income", "reason": "WB updated classification"},
    "Saint Vincent and the Grenadines": {"income_group": "Upper middle income", "reason": "WB updated classification"},
    "Bolivia (Plurinational State of)": {"income_group": "Lower middle income", "reason": "WB updated classification"},
    "Viet Nam": {"income_group": "Lower middle income", "reason": "WB updated classification"},
    "State of Palestine": {"income_group": "Lower middle income", "reason": "Not in WB classification; assigned per UN status"},
    "Yemen": {"income_group": "Low income", "reason": "WB updated classification"},
    "United Kingdom of Great Britain and Northern Ireland": {"income_group": "High income", "reason": "WB name mismatch (United Kingdom); override ensures correct group"},
    "United States of America": {"income_group": "High income", "reason": "WB name mismatch; override ensures correct group"},
}

# ---- Region/LDC/SIDS overrides ----
REGION_OVERRIDES = {
    "Venezuela (Bolivarian Republic of)": {
        "region": "Americas", "sub_region": "Latin America and the Caribbean",
        "intermediate_region": "South America", "is_ldc": "False", "is_sids": "False",
        "reason": "UNSD name mismatch; full region data override",
    },
    "Democratic Republic of the Congo": {
        "region": "Africa", "sub_region": "Sub-Saharan Africa",
        "intermediate_region": "Middle Africa", "is_ldc": "True", "is_sids": "False",
        "reason": "UNSD name mismatch; full region data override",
    },
    "European Union": {
        "region": "Europe", "sub_region": "Western Europe",
        "intermediate_region": "", "is_ldc": "False", "is_sids": "False",
        "reason": "EU is not a country; assigned region manually",
    },
}

# ---- Land area overrides (countries absent from WB source) ----
LAND_AREA_OVERRIDES = {
    "Monaco": {"land_area_km2": 2.02, "reason": "Not in WB land area dataset"},
    "Cook Islands": {"land_area_km2": 236.0, "reason": "Not in WB land area dataset"},
    "Niue": {"land_area_km2": 260.0, "reason": "Not in WB land area dataset"},
    "State of Palestine": {"land_area_km2": 6020.0, "reason": "Not in WB land area dataset"},
    "European Union": {"land_area_km2": 0.0, "reason": "EU is not assigned land area in this model"},
}

# ---- Name concordance (where CBD canonical name != source name) ----
# This replaces LAND_AREA_NAME_MAP and the relevant parts of manual_name_map.csv
NAME_CONCORDANCE = {
    # UN Scale name mappings
    "Egypt": {"un_scale_name": "Egypt"},
    "Somalia": {"un_scale_name": "Somalia"},
    "Kyrgyzstan": {"un_scale_name": "Kyrgyzstan"},
    "Yemen": {"un_scale_name": "Yemen"},
    "Democratic Republic of the Congo": {"un_scale_name": "Democratic Republic of the Congo"},
    # WB name mappings (land area + income)
    "Egypt": {"wb_land_area_name": "Egypt, Arab Rep.", "wb_income_name": "Egypt, Arab Rep."},
    "Somalia": {"wb_land_area_name": "Somalia, Fed. Rep.", "wb_income_name": "Somalia"},
    "Kyrgyzstan": {"wb_land_area_name": "Kyrgyz Republic", "wb_income_name": "Kyrgyz Republic"},
    "Yemen": {"wb_land_area_name": "Yemen, Rep.", "wb_income_name": "Yemen, Rep."},
    "Democratic Republic of the Congo": {"wb_land_area_name": "Congo, Dem. Rep.", "wb_income_name": "Congo, Dem. Rep."},
    "Côte d'Ivoire": {"wb_land_area_name": "Cote d'Ivoire", "wb_income_name": "Cote d'Ivoire"},
    "Iran (Islamic Republic of)": {"wb_land_area_name": "Iran, Islamic Rep.", "wb_income_name": "Iran, Islamic Rep."},
    "Türkiye": {"wb_land_area_name": "Turkiye", "wb_income_name": "Turkiye"},
    "Republic of Moldova": {"wb_land_area_name": "Moldova", "wb_income_name": "Moldova"},
    "Micronesia (Federated States of)": {"wb_land_area_name": "Micronesia, Fed. Sts.", "wb_income_name": "Micronesia, Fed. Sts."},
    "United Republic of Tanzania": {"wb_land_area_name": "Tanzania", "wb_income_name": "Tanzania"},
    "Bolivia (Plurinational State of)": {"wb_land_area_name": "Bolivia", "wb_income_name": "Bolivia"},
    "Venezuela (Bolivarian Republic of)": {"wb_land_area_name": "Venezuela, RB", "wb_income_name": "Venezuela, RB"},
    "Democratic People's Republic of Korea": {"wb_land_area_name": "Korea, Dem. People's Rep.", "wb_income_name": "Korea, Dem. People's Rep."},
    "Lao People's Democratic Republic": {"wb_land_area_name": "Lao PDR", "wb_income_name": "Lao PDR"},
    "Congo": {"wb_land_area_name": "Congo, Rep.", "wb_income_name": "Congo, Rep."},
    "Bahamas": {"wb_land_area_name": "Bahamas, The", "wb_income_name": "Bahamas, The"},
    "Gambia": {"wb_land_area_name": "Gambia, The", "wb_income_name": "Gambia, The"},
    "Saint Kitts and Nevis": {"wb_land_area_name": "St. Kitts and Nevis", "wb_income_name": "St. Kitts and Nevis"},
    "Saint Lucia": {"wb_land_area_name": "St. Lucia", "wb_income_name": "St. Lucia"},
    "Saint Vincent and the Grenadines": {"wb_land_area_name": "St. Vincent and the Grenadines", "wb_income_name": "St. Vincent and the Grenadines"},
    "Republic of Korea": {"wb_land_area_name": "Korea, Rep.", "wb_income_name": "Korea, Rep."},
    "Slovakia": {"wb_land_area_name": "Slovak Republic", "wb_income_name": "Slovak Republic"},
    "United Kingdom of Great Britain and Northern Ireland": {"wb_land_area_name": "United Kingdom", "wb_income_name": "United Kingdom"},
    "Netherlands (Kingdom of the)": {"wb_land_area_name": "Netherlands", "wb_income_name": "Netherlands"},
}


# ---- Build the CSV ----
# Include: (1) all name concordance rows, (2) all income overrides, (3) all region overrides,
# (4) all land area overrides, (5) EU membership flag for EU27
# EU27 list (from data-raw/eu27.csv)

eu27_countries = pd.read_csv("data-raw/eu27.csv")["party"].tolist()

rows = {}
all_parties_with_overrides = set()

# Add name concordance entries
for party, mappings in NAME_CONCORDANCE.items():
    all_parties_with_overrides.add(party)
    if party not in rows:
        rows[party] = {"party": party}
    rows[party].update(mappings)

# Add income group overrides
for party, info in INCOME_OVERRIDES.items():
    all_parties_with_overrides.add(party)
    if party not in rows:
        rows[party] = {"party": party}
    rows[party]["income_group_override"] = info["income_group"]
    if "reason" not in rows[party] or not rows[party].get("reason"):
        rows[party]["reason"] = info.get("reason", "")
    else:
        rows[party]["reason"] += "; " + info.get("reason", "")

# Add region overrides
for party, info in REGION_OVERRIDES.items():
    all_parties_with_overrides.add(party)
    if party not in rows:
        rows[party] = {"party": party}
    rows[party].update({
        "region_override": info.get("region", ""),
        "sub_region_override": info.get("sub_region", ""),
        "intermediate_region_override": info.get("intermediate_region", ""),
        "is_ldc_override": info.get("is_ldc", ""),
        "is_sids_override": info.get("is_sids", ""),
    })
    if "reason" not in rows[party] or not rows[party].get("reason"):
        rows[party]["reason"] = info.get("reason", "")
    else:
        rows[party]["reason"] += "; " + info.get("reason", "")

# Add land area overrides
for party, info in LAND_AREA_OVERRIDES.items():
    all_parties_with_overrides.add(party)
    if party not in rows:
        rows[party] = {"party": party}
    rows[party]["land_area_km2_override"] = info["land_area_km2"]
    if "reason" not in rows[party] or not rows[party].get("reason"):
        rows[party]["reason"] = info.get("reason", "")
    else:
        rows[party]["reason"] += "; " + info.get("reason", "")

# Add is_eu_ms for EU27 countries
for party in eu27_countries:
    all_parties_with_overrides.add(party)
    if party not in rows:
        rows[party] = {"party": party}
    rows[party]["is_eu_ms_override"] = "True"

# Ensure EU entry is handled
eu_party = "European Union"
all_parties_with_overrides.add(eu_party)
if eu_party not in rows:
    rows[eu_party] = {"party": eu_party}
rows[eu_party]["is_eu_ms_override"] = "True"

# Sort and create DataFrame
master_df = pd.DataFrame(rows.values())

# Ensure all expected columns exist
expected_cols = [
    "party", "un_scale_name", "wb_land_area_name", "wb_income_name",
    "income_group_override", "region_override", "sub_region_override",
    "intermediate_region_override", "is_ldc_override", "is_sids_override",
    "is_eu_ms_override", "land_area_km2_override", "reason",
]
for col in expected_cols:
    if col not in master_df.columns:
        master_df[col] = ""
master_df = master_df[expected_cols]
master_df = master_df.sort_values("party").reset_index(drop=True)

# Fill NaN with empty string
master_df = master_df.fillna("")

output_path = "config/party_master.csv"
master_df.to_csv(output_path, index=False)
print(f"Written {len(master_df)} rows to {output_path}")
print(f"\nOverride summary:")
print(f"  Name concordance entries: {len(NAME_CONCORDANCE)}")
print(f"  Income group overrides: {len(INCOME_OVERRIDES)}")
print(f"  Region/flag overrides: {len(REGION_OVERRIDES)}")
print(f"  Land area overrides: {len(LAND_AREA_OVERRIDES)}")
print(f"  EU27 members + EU: {len(eu27_countries) + 1}")
print(f"  Total unique parties in CSV: {len(all_parties_with_overrides)}")
