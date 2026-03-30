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

def test_tsac_sosac_shares_sum(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    results = calculate_allocations(base_df, fund_size, 50, tsac_beta=0.15, sosac_gamma=0.10)
    
    # Final share should sum to 1.0 for eligible parties
    eligible_mask = results['eligible']
    assert pytest.approx(results.loc[eligible_mask, 'final_share'].sum(), 1e-12) == 1.0
    
    # IUSAF share should sum to 1.0 for eligible parties with un_share > 0
    iusaf_mask = results['eligible'] & (results['un_share'] > 0)
    assert pytest.approx(results.loc[iusaf_mask, 'iusaf_share'].sum(), 1e-12) == 1.0
    
    # TSAC share should sum to 1.0 for eligible parties with land area
    tsac_mask = results['eligible'] & (results['land_area_km2'] > 0)
    assert pytest.approx(results.loc[tsac_mask, 'tsac_share'].sum(), 1e-12) == 1.0
    
    # SOSAC share should sum to 1.0 for eligible SIDS
    sosac_mask = results['eligible'] & results['is_sids']
    assert pytest.approx(results.loc[sosac_mask, 'sosac_share'].sum(), 1e-12) == 1.0

def test_sosac_isolation(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    # gamma = 1.0 means everything to SOSAC
    results = calculate_allocations(base_df, fund_size, 50, tsac_beta=0.0, sosac_gamma=1.0)
    
    # Only SIDS should have non-zero allocation
    non_sids = results[~results['is_sids'] & results['eligible']]
    assert (non_sids['total_allocation'] == 0).all()
    
    sids = results[results['is_sids'] & results['eligible']]
    assert (sids['total_allocation'] > 0).all()

def test_tsac_isolation(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    # beta = 1.0 means everything to TSAC
    results = calculate_allocations(base_df, fund_size, 50, tsac_beta=1.0, sosac_gamma=0.0)
    
    # Only parties with land area should have non-zero allocation
    no_land = results[~(results['land_area_km2'] > 0) & results['eligible']]
    assert (no_land['total_allocation'] == 0).all()
    
    with_land = results[(results['land_area_km2'] > 0) & results['eligible']]
    assert (with_land['total_allocation'] > 0).all()

def test_high_income_sids_preserved(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # default mode preserves SIDS even if high income
    results = calculate_allocations(base_df, fund_size, 50, exclude_high_income=True)
    
    # Bahamas is a high income SIDS
    bahamas = results[results['party'] == 'Bahamas']
    assert bahamas['eligible'].iloc[0] == True
    assert bahamas['total_allocation'].iloc[0] > 0
    
    # Germany is a high income non-SIDS
    germany = results[results['party'] == 'Germany']
    assert germany['eligible'].iloc[0] == False
    assert germany['total_allocation'].iloc[0] == 0

def test_sosac_fallback_no_sids(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # Force no SIDS eligible by filtering them out in df before calling
    df_no_sids = base_df.copy()
    df_no_sids['is_sids'] = False
    
    results = calculate_allocations(df_no_sids, fund_size, 50, tsac_beta=0.1, sosac_gamma=0.1)
    
    # Gamma should be reallocated to IUSAF
    # effective_alpha = (1 - 0.1 - 0.1) + 0.1 = 0.9
    # effective_beta = 0.1
    # effective_gamma = 0
    
    # We can check component amounts (in millions)
    # total_allocation sum is 1000
    # iusaf component should be 900
    # tsac component should be 100
    # sosac component should be 0
    
    assert pytest.approx(results['component_iusaf_amt'].sum(), 0.001) == 900
    assert pytest.approx(results['component_tsac_amt'].sum(), 0.001) == 100
    assert pytest.approx(results['component_sosac_amt'].sum(), 0.001) == 0
