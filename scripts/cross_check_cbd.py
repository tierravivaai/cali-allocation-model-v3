import duckdb
import pandas as pd
from cali_model.data_loader import load_data, get_base_data

def cross_check_cbd_parties():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    df = get_base_data(con)
    
    # Load the raw CBD budget table to get the intended list of Parties
    base_path = "data-raw"
    cbd_raw = pd.read_csv(f"{base_path}/cbd_cop16_budget_table.csv")
    cbd_raw_parties = cbd_raw[cbd_raw['Party'] != 'Total']['Party'].dropna().unique()
    
    print(f"Total Parties in Budget Table: {len(cbd_raw_parties)}")
    
    # Check each Party from the budget table exists in our final base_df and has metadata
    missing_in_df = []
    missing_metadata = []
    
    # Debug party names in df
    # print("\nDEBUG: First 5 parties in base_df:")
    # print(df['party'].head().tolist())
    
    # We need to map the budget table name using our name_map BEFORE checking the dataframe
    name_map_df = con.execute("SELECT * FROM name_map").df()
    mapping_dict = dict(zip(name_map_df['party_raw'], name_map_df['party_mapped']))

    for party in cbd_raw_parties:
        # Check if the party name from budget table needs mapping
        mapped_party = mapping_dict.get(party, party)
        
        party_data = df[df['party'] == mapped_party]
        if len(party_data) == 0:
            missing_in_df.append(f"{party} (Mapped as: {mapped_party})")
        else:
            row = party_data.iloc[0]
            if pd.isna(row['region']) or row['WB Income Group'] == 'Not Available':
                missing_metadata.append(mapped_party)
                
    print(f"\nParties from Budget Table NOT found in base_df: {len(missing_in_df)}")
    for p in missing_in_df:
        print(f"- {p}")
        
    print(f"\nParties with missing metadata (Region or Income): {len(missing_metadata)}")
    for p in missing_metadata:
        row = df[df['party'] == p].iloc[0]
        print(f"- {p} (Region: {row['region']}, Income: {row['WB Income Group']})")

if __name__ == "__main__":
    cross_check_cbd_parties()
