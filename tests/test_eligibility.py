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

def test_eligibility_filter_high_income(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000 # 1bn
    
    # Toggle ON: Exclude High Income
    # Note: New default mode is "exclude_except_sids", so we explicitly use "exclude_all" for this test
    results_filtered = calculate_allocations(base_df, fund_size, 50, exclude_high_income=True, high_income_mode="exclude_all")
    
    # Check that High income countries have 0 allocation
    hi_countries = results_filtered[results_filtered['WB Income Group'] == 'High income']
    assert (hi_countries['total_allocation'] == 0).all()
    
    # Check that non-High income CBD Parties have > 0 allocation (if un_share > 0)
    eligible_countries = results_filtered[
        (results_filtered['WB Income Group'] != 'High income') & 
        (results_filtered['un_share'] > 0) &
        (results_filtered['is_cbd_party'])
    ]
    assert (eligible_countries['total_allocation'] > 0).all()
    
    # Check that non-CBD Parties have 0 allocation
    non_cbd = results_filtered[~results_filtered['is_cbd_party']]
    assert (non_cbd['total_allocation'] == 0).all()
    
    # Check sum consistency
    assert pytest.approx(results_filtered['total_allocation'].sum(), 0.001) == 1000

def test_eligibility_toggle_off(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # Toggle OFF: Include all CBD Parties
    results_all = calculate_allocations(base_df, fund_size, 50, exclude_high_income=False)
    
    # High income CBD Parties should have > 0 allocation
    hi_countries = results_all[
        (results_all['WB Income Group'] == 'High income') & 
        (results_all['un_share'] > 0) &
        (results_all['is_cbd_party'])
    ]
    assert (hi_countries['total_allocation'] > 0).all()
    
    # Non-CBD Parties should still have 0
    non_cbd = results_all[~results_all['is_cbd_party']]
    assert (non_cbd['total_allocation'] == 0).all()
