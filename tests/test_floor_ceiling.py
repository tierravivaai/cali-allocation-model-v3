import pytest
import pandas as pd
import duckdb
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations, _apply_floor_ceiling_shares

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

def test_floor_ceiling_helper_basic():
    # Test weights sum to 1.0 without constraints
    weights = pd.Series([0.1, 0.4, 0.5])
    shares = _apply_floor_ceiling_shares(weights, 0.0, 1.0)
    assert pytest.approx(shares.sum(), 1e-12) == 1.0
    pd.testing.assert_series_equal(shares, weights)

def test_floor_ceiling_helper_floor():
    # Test floor constraint (0.2)
    # Weights [0.1, 0.4, 0.5] -> 0.1 is below floor
    # Result should be [0.2, 0.355..., 0.444...]
    weights = pd.Series([0.1, 0.4, 0.5])
    shares = _apply_floor_ceiling_shares(weights, 0.2, 1.0)
    assert (shares >= 0.2 - 1e-12).all()
    assert pytest.approx(shares.sum(), 1e-12) == 1.0
    assert shares[0] == 0.2

def test_floor_ceiling_helper_ceiling():
    # Test ceiling constraint (0.4)
    # Weights [0.1, 0.4, 0.5] -> 0.5 is above ceiling
    # Result should be [0.12, 0.4, 0.4] (Wait, 0.4 is fine, 0.5 capped to 0.4)
    # Actually [0.1, 0.4, 0.5] -> cap 0.4 -> [0.15, 0.4, 0.4] approx
    weights = pd.Series([0.1, 0.4, 0.5])
    shares = _apply_floor_ceiling_shares(weights, 0.0, 0.4)
    assert (shares <= 0.4 + 1e-12).all()
    assert pytest.approx(shares.sum(), 1e-12) == 1.0
    assert shares[2] == 0.4

def test_floor_ceiling_helper_both():
    # Test both: Weights [0.05, 0.15, 0.8] with Floor 0.1 and Ceiling 0.5
    # Capped: 0.8 -> 0.5
    # Floored: 0.05 -> 0.1
    # Remaining for 0.15: 1.0 - 0.5 - 0.1 = 0.4
    weights = pd.Series([0.05, 0.15, 0.8])
    shares = _apply_floor_ceiling_shares(weights, 0.1, 0.5)
    assert pytest.approx(shares[0], 1e-12) == 0.1
    assert pytest.approx(shares[2], 1e-12) == 0.5
    assert pytest.approx(shares[1], 1e-12) == 0.4
    assert pytest.approx(shares.sum(), 1e-12) == 1.0

def test_integration_floor_ceiling(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000 # 1bn
    
    # Apply reasonable constraints
    # Total eligible parties ~190
    # 0.1% floor * 190 = 19%
    # 2% ceiling * 190 = 380% (so ceiling won't block sum)
    results = calculate_allocations(
        base_df, 
        fund_size, 
        50, 
        floor_pct=0.1, 
        ceiling_pct=2.0,
        tsac_beta=0,
        sosac_gamma=0
    )
    
    # Filter for eligible parties that have a positive allocation
    eligible_results = results[results['inverted_share'] > 0]
    
    # Check that shares (in percentage terms) are within bounds
    # inverted_share in results is a fraction (0-1)
    shares = eligible_results['inverted_share']
    
    assert (shares >= 0.001 - 1e-12).all(), f"Min share {shares.min()} below floor 0.001"
    assert (shares <= 0.02 + 1e-12).all(), f"Max share {shares.max()} above ceiling 0.02"
    assert pytest.approx(results['total_allocation'].sum(), 0.001) == 1000

def test_allocation_stability_with_no_constraints(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    
    # Default parameters should match old logic (None means no ceiling)
    # Use 0/0 weights to match old logic for this regression test
    results_new = calculate_allocations(base_df, fund_size, 50, floor_pct=0.0, ceiling_pct=None, tsac_beta=0, sosac_gamma=0)
    
    # Explicitly calculate old way (simple normalization)
    mask = (base_df['is_cbd_party']) & (base_df['un_share'] > 0)
    weights = 1.0 / (base_df.loc[mask, 'un_share'] / 100.0)
    expected_shares = weights / weights.sum()
    
    pd.testing.assert_series_equal(
        results_new.loc[mask, 'inverted_share'], 
        expected_shares, 
        check_names=False,
        check_index_type=False
    )

def test_ceiling_none_behavior(mock_con):
    base_df = get_base_data(mock_con)
    fund_size = 1_000_000_000
    # None should behave same as 100% or effectively no cap
    res_none = calculate_allocations(base_df, fund_size, 50, floor_pct=0.0, ceiling_pct=None, tsac_beta=0, sosac_gamma=0)
    res_100 = calculate_allocations(base_df, fund_size, 50, floor_pct=0.0, ceiling_pct=100.0, tsac_beta=0, sosac_gamma=0)
    
    pd.testing.assert_frame_equal(res_none, res_100)
