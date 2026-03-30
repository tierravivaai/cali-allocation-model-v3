import pytest
import pandas as pd
import duckdb
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations, aggregate_by_region, aggregate_special_groups, aggregate_by_income

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

@pytest.mark.parametrize("fund_size_usd", [2_000_000, 5_000_000, 50_000_000, 100_000_000, 1_000_000_000])
@pytest.mark.parametrize("exclude_high_income", [True, False])
def test_fund_sums_consistency(mock_con, fund_size_usd, exclude_high_income):
    base_df = get_base_data(mock_con)
    iplc_share = 50
    results = calculate_allocations(base_df, fund_size_usd, iplc_share, exclude_high_income=exclude_high_income)
    
    expected_total_m = fund_size_usd / 1_000_000
    
    # 1. Total allocation sums to fund size (approximately, due to tiny rounding in normalisation)
    # The calculator returns values in Millions.
    expected_total_m = fund_size_usd / 1_000_000
    actual_total_m = results['total_allocation'].sum()
    assert pytest.approx(actual_total_m, abs=0.001) == expected_total_m
    
    # 2. IPLC + State = Total for every row
    check = results['iplc_component'] + results['state_component']
    pd.testing.assert_series_equal(check, results['total_allocation'], check_names=False)
    
    # 3. Regional totals sum to the actual total allocation
    region_df = aggregate_by_region(results)
    assert pytest.approx(region_df['total_allocation'].sum(), abs=0.001) == actual_total_m
    
    # 4. Income group totals sum to the actual total allocation
    income_df = aggregate_by_income(results)
    assert pytest.approx(income_df['total_allocation'].sum(), abs=0.001) == actual_total_m
    
    # 5. LDC + non-LDC totals sum to the actual total allocation
    ldc_total, _ = aggregate_special_groups(results)
    # Use fillna(False) to ensure NaNs are treated as non-LDC for the sum consistency check
    non_ldc_total = results[results['is_ldc'].fillna(False) == False]['total_allocation'].sum()
    assert pytest.approx(ldc_total['total_allocation'] + non_ldc_total, abs=0.001) == actual_total_m

def test_extreme_tiny_fund(mock_con):
    # Testing with $1 (basically checking for division by zero or extreme rounding issues)
    fund_size_usd = 1
    base_df = get_base_data(mock_con)
    results = calculate_allocations(base_df, fund_size_usd, 50)
    
    expected_total_m = 1 / 1_000_000
    assert pytest.approx(results['total_allocation'].sum(), 0.0001) == expected_total_m
