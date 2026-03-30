import pytest
import pandas as pd
import duckdb
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations, aggregate_by_income

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

def test_aggregate_by_income_sums(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50)
    
    income_df = aggregate_by_income(results_df)
    
    # Check that the sum of all income groups equals the total fund size (in millions)
    assert pytest.approx(income_df['total_allocation'].sum(), 0.001) == 1000
    
    # "Not Available" group should no longer exist as all Parties have been mapped
    # (except for EU which is now handled separately or mapped to High Income)
    assert "Not Available" not in income_df['WB Income Group'].values

def test_aggregate_by_income_structure(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    income_df = aggregate_by_income(results_df)
    
    required_cols = ['WB Income Group', 'total_allocation', 'state_component', 'iplc_component', 'Countries (number)']
    for col in required_cols:
        assert col in income_df.columns

def test_aggregate_country_counts(mock_con):
    base_df = get_base_data(mock_con)
    # Exclude High Income to see if counts change
    # Note: New default mode is "exclude_except_sids", so HI SIDS will still be there
    results_df = calculate_allocations(base_df, 1_000_000_000, 50, exclude_high_income=True, high_income_mode="exclude_all")
    
    income_df = aggregate_by_income(results_df)
    assert "High income" not in income_df['WB Income Group'].values
    
    # Check that eligible CBD parties are counted
    total_countries = income_df['Countries (number)'].sum()
    actual_eligible_parties = (results_df['is_cbd_party'] & results_df['eligible']).sum()
    assert total_countries == actual_eligible_parties
