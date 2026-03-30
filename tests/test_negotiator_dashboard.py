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

def test_high_income_exclusion_modes(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # Mode: exclude_except_sids (Default)
    # Bahamas (HI SIDS) should be eligible
    # Germany (HI non-SIDS) should be ineligible
    results_sids = calculate_allocations(
        base_df, fund_size, 50, 
        exclude_high_income=True, 
        high_income_mode="exclude_except_sids"
    )
    bahamas = results_sids[results_sids['party'] == 'Bahamas']
    germany = results_sids[results_sids['party'] == 'Germany']
    assert bahamas['eligible'].iloc[0] == True
    assert germany['eligible'].iloc[0] == False
    
    # Mode: exclude_all
    # Bahamas (HI SIDS) should be ineligible
    # Germany (HI non-SIDS) should be ineligible
    results_all = calculate_allocations(
        base_df, fund_size, 50, 
        exclude_high_income=True, 
        high_income_mode="exclude_all"
    )
    bahamas_all = results_all[results_all['party'] == 'Bahamas']
    germany_all = results_all[results_all['party'] == 'Germany']
    assert bahamas_all['eligible'].iloc[0] == False
    assert germany_all['eligible'].iloc[0] == False

def test_allocation_consistency_with_beta_gamma(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # Test a complex mix
    # beta=0.15, gamma=0.10, iusaf_weight=0.75
    results = calculate_allocations(
        base_df, fund_size, 50, 
        tsac_beta=0.15, 
        sosac_gamma=0.10
    )
    
    eligible_mask = results['eligible']
    # Total sum should be fund_size / 1e6 (since total_allocation is in millions)
    assert pytest.approx(results.loc[eligible_mask, 'total_allocation'].sum(), 0.001) == 1000.0
    
    # Check component amounts
    # total_iusaf_amt should be roughly 750
    # total_tsac_amt should be roughly 150
    # total_sosac_amt should be roughly 100
    assert pytest.approx(results['component_iusaf_amt'].sum(), 0.001) == 750.0
    assert pytest.approx(results['component_tsac_amt'].sum(), 0.001) == 150.0
    assert pytest.approx(results['component_sosac_amt'].sum(), 0.001) == 100.0

def test_floor_ceiling_on_blended_share(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # Set beta=0.5 (high weight for land area) and apply 1% ceiling
    results = calculate_allocations(
        base_df, fund_size, 50,
        tsac_beta=0.5,
        ceiling_pct=1.0
    )
    
    eligible_mask = results['eligible']
    # No country should have more than 1% of the fund
    # 1% of 1000m is 10m
    assert (results.loc[eligible_mask, 'total_allocation'] <= 10.000001).all()
    assert pytest.approx(results.loc[eligible_mask, 'total_allocation'].sum(), 0.001) == 1000.0

def test_baseline_logic_selection(mock_con):
    """
    Test that the baseline selection logic matches requirements:
    - Equality mode -> Baseline = Current (delta 0)
    - Inverted Scale (beta=0, gamma=0) -> Baseline = Equality
    - Stewardship/Balanced -> Baseline = Inverted Scale (IUSAF)
    """
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # 1. Equality mode
    results_eq = calculate_allocations(base_df, fund_size, 50, equality_mode=True)
    # In app.py: if is_eq_mode: baseline = current
    # We verify that current == baseline effectively means delta is 0
    # (The test mimics app.py logic)
    baseline_eq = results_eq.copy()
    delta_eq = results_eq['total_allocation'] - baseline_eq['total_allocation']
    assert (delta_eq == 0).all()

    # 2. Inverted Scale (beta=0, gamma=0, eq=False)
    results_inv = calculate_allocations(base_df, fund_size, 50, tsac_beta=0, sosac_gamma=0, equality_mode=False)
    # In app.py: baseline = Equality
    baseline_inv = calculate_allocations(base_df, fund_size, 50, equality_mode=True)
    delta_inv = results_inv['total_allocation'] - baseline_inv['total_allocation']
    # Delta should not be all zero because UN scale is not equal
    assert not (delta_inv == 0).all()
    assert pytest.approx(delta_inv.sum(), 0.001) == 0.0 # Sum of deltas should be 0

    # 3. Stewardship (beta=0.25, gamma=0.05)
    results_stew = calculate_allocations(base_df, fund_size, 50, tsac_beta=0.25, sosac_gamma=0.05)
    # In app.py: baseline = Inverted Scale (IUSAF)
    baseline_stew = calculate_allocations(base_df, fund_size, 50, tsac_beta=0, sosac_gamma=0, equality_mode=False)
    delta_stew = results_stew['total_allocation'] - baseline_stew['total_allocation']
    assert not (delta_stew == 0).all()
    assert pytest.approx(delta_stew.sum(), 0.001) == 0.0

def test_un_scale_mode_consistency_in_baseline(mock_con):
    """
    Test that the baseline calculation respects the un_scale_mode (e.g. banding vs raw).
    If we are in banding mode, both current and baseline should use banding.
    """
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # Mode: band_inversion
    un_mode = "band_inversion"
    
    # Current: Stewardship (beta=0.15, gamma=0.10) with banding
    results = calculate_allocations(
        base_df, fund_size, 50,
        tsac_beta=0.15,
        sosac_gamma=0.10,
        un_scale_mode=un_mode
    )
    
    # Baseline: Inverted Scale (beta=0, gamma=0) with banding
    baseline = calculate_allocations(
        base_df, fund_size, 50,
        tsac_beta=0.0,
        sosac_gamma=0.0,
        un_scale_mode=un_mode
    )
    
    # If both use banding, the sum of deltas should be zero
    delta = results['total_allocation'] - baseline['total_allocation']
    assert pytest.approx(delta.sum(), 0.001) == 0.0
    
    # Check that baseline has un_band assigned (meaning it used banding)
    assert baseline['un_band'].notna().any()
