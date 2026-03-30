import pytest
import pandas as pd
import duckdb
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

def test_allocation_sums_to_fund_size(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000 # 1bn
    # Use 0/0 weights to match old logic for this regression test
    results = calculate_allocations(base_df, fund_size, 50, tsac_beta=0, sosac_gamma=0)
    
    # Sum of total_allocation should be 1000 (millions)
    assert pytest.approx(results['total_allocation'].sum(), 0.001) == 1000

def test_iplc_state_consistency(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    # Use 0/0 weights to match old logic for this regression test
    results = calculate_allocations(base_df, fund_size, 60, tsac_beta=0, sosac_gamma=0)
    
    # iplc + state should equal total
    check = results['iplc_component'] + results['state_component']
    pd.testing.assert_series_equal(check, results['total_allocation'], check_names=False)
    
    # iplc should be 60% of total
    assert pytest.approx(results['iplc_component'].sum(), 0.001) == 600

def test_eu_party_exists(mock_con):
    base_df = get_base_data(mock_con)
    assert 'European Union' in base_df['party'].values
    eu_share = base_df[base_df['party'] == 'European Union']['un_share'].values[0]
    assert eu_share == 0.0

def test_cbd_party_count(mock_con):
    base_df = get_base_data(mock_con)
    
    # 1. Count Parties in the source CSV
    # (Verified via pandas script as 196 including European Union)
    source_count = 196 
    
    # 2. Count is_cbd_party = True in our processed dataframe
    calculated_count = base_df['is_cbd_party'].sum()
    
    # These should match exactly
    assert calculated_count == source_count
    
    # 3. Ensure EU is marked as a CBD Party
    eu_cbd_status = base_df[base_df['party'] == 'European Union']['is_cbd_party'].values[0]
    assert eu_cbd_status == True

def test_column_presence_and_renaming(mock_con):
    base_df = get_base_data(mock_con)
    # Verify that the data loader now uses 'WB Income Group' and not 'World Bank Income Group'
    assert 'WB Income Group' in base_df.columns
    assert 'World Bank Income Group' not in base_df.columns
    assert 'is_cbd_party' in base_df.columns
    assert 'is_ldc' in base_df.columns

def test_metadata_completeness(mock_con):
    base_df = get_base_data(mock_con)
    # Ensure every party has a valid region (not None or NaN)
    assert base_df['region'].isna().sum() == 0
    # Ensure every party has a valid WB Income Group (not 'Not Available')
    # Note: European Union is a special case handled in data_loader.py
    missing_income = base_df[base_df['WB Income Group'] == 'Not Available']
    assert len(missing_income) == 0, f"Parties with missing income: {missing_income['party'].tolist()}"

def test_budget_table_alignment(mock_con):
    base_df = get_base_data(mock_con)
    base_path = "data-raw"
    cbd_raw = pd.read_csv(f"{base_path}/cbd_cop16_budget_table.csv")
    expected_parties = cbd_raw[cbd_raw['Party'] != 'Total']['Party'].dropna().unique()
    
    # Check that all 196 parties (after mapping) are present and marked as is_cbd_party
    # We use the mapping logic from scripts/cross_check_cbd.py
    name_map_df = mock_con.execute("SELECT * FROM name_map").df()
    mapping_dict = dict(zip(name_map_df['party_raw'], name_map_df['party_mapped']))
    
    for party in expected_parties:
        mapped_name = mapping_dict.get(party, party)
        party_row = base_df[base_df['party'] == mapped_name]
        assert len(party_row) == 1, f"Missing party: {party} (mapped as {mapped_name})"
        assert party_row.iloc[0]['is_cbd_party'] == True

def test_strict_data_integrity(mock_con):
    base_df = get_base_data(mock_con)
    # Essential columns must not contain nulls
    essential_cols = ['party', 'un_share', 'region', 'WB Income Group', 'is_ldc', 'is_sids', 'is_eu_ms', 'is_cbd_party']
    for col in essential_cols:
        assert base_df[col].isna().sum() == 0, f"Column '{col}' contains null values"
    
    # un_share must be >= 0.0
    assert (base_df['un_share'] >= 0.0).all()


def test_all_eligible_parties_have_land_area_after_matching_fix(mock_con):
    base_df = get_base_data(mock_con)
    results = calculate_allocations(base_df, 1_000_000_000, 50, exclude_high_income=True)
    eligible = results[results['eligible']]
    assert len(eligible) == 142
    assert eligible['has_land_area'].all()

def test_venezuela_consolidation(mock_con):
    base_df = get_base_data(mock_con)
    # Check that Venezuela exists only once
    venezuela_rows = base_df[base_df['party'].str.contains('Venezuela', case=False)]
    assert len(venezuela_rows) == 1, f"Found multiple Venezuela rows: {venezuela_rows['party'].tolist()}"
    
    # Check that the single row has the correct normalized name
    assert venezuela_rows.iloc[0]['party'] == 'Venezuela (Bolivarian Republic of)'
    
    # Check that it has an un_share (it was 0.069 in the UN scale)
    assert venezuela_rows.iloc[0]['un_share'] > 0


