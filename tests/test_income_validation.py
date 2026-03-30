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

def test_income_group_country_counts(mock_con):
    base_df = get_base_data(mock_con)
    # 1. Total fund allocation with NO exclusions
    fund_size = 1_000_000_000
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    # 2. Get aggregated counts
    income_agg = aggregate_by_income(results_df)
    total_countries_in_agg = income_agg['Countries (number)'].sum()
    
    # 3. There should be exactly 196 CBD Parties/Entities
    assert total_countries_in_agg == 196
    
    # 4. Check specific income groups sum up correctly
    for group in results_df['WB Income Group'].unique():
        if group == "Not Available": continue
        
        expected_count = ((results_df['WB Income Group'] == group) & (results_df['is_cbd_party'])).sum()
        if expected_count > 0:
            actual_count = income_agg[income_agg['WB Income Group'] == group]['Countries (number)'].values[0]
            assert actual_count == expected_count

def test_income_group_counts_with_hi_exclusion(mock_con):
    base_df = get_base_data(mock_con)
    # 1. Total fund allocation WITH High Income exclusion
    fund_size = 1_000_000_000
    # Use "exclude_all" to match old logic for this regression test
    results_df = calculate_allocations(base_df, fund_size, 50, exclude_high_income=True, high_income_mode="exclude_all")
    
    # 2. Get aggregated counts
    income_agg = aggregate_by_income(results_df)
    
    # 3. High Income group should NOT be in the aggregation
    assert "High income" not in income_agg['WB Income Group'].values
    
    # 4. Total count in aggregation should match total eligible CBD parties (non-High Income)
    total_countries_in_agg = income_agg['Countries (number)'].sum()
    assert total_countries_in_agg == 130 # 196 - 66 (excluding European Union which is marked HI) or similar
