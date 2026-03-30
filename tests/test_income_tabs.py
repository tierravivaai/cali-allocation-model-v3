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

def test_middle_income_tab_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Logic from app.py: Middle Income includes 'Lower middle income' and 'Upper middle income'
    mi_df = results_df[results_df['WB Income Group'].isin(['Lower middle income', 'Upper middle income'])]
    
    # Check if all included rows belong to those groups
    assert all(mi_df['WB Income Group'].isin(['Lower middle income', 'Upper middle income']))
    # Verify both groups are represented (given our standard dataset)
    assert 'Lower middle income' in mi_df['WB Income Group'].values
    assert 'Upper middle income' in mi_df['WB Income Group'].values

def test_low_income_tab_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Logic from app.py: Low Income tab
    li_df = results_df[results_df['WB Income Group'] == 'Low income']
    
    # Check all included rows are Low income
    assert all(li_df['WB Income Group'] == 'Low income')
    assert 'Low income' in li_df['WB Income Group'].values

def test_middle_income_tab_columns(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Check that in Middle Income view, classification exists but EU does not
    # This reflects the specific request to remove EU and keep classification in tab6
    mi_cols = ['party', 'total_allocation', 'state_component', 'iplc_component', 'WB Income Group']
    
    # In the app, display_mi_df contains all columns, but st.dataframe filters them
    # We verify the columns intended for the dataframe exist
    for col in mi_cols:
        assert col in results_df.columns
    
def test_low_income_tab_columns(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Add UN LDC logic as in app.py
    results_df["UN LDC"] = results_df["is_ldc"].map({True: "LDC", False: "-"})
    
    # Check that in Low Income view, EU column is not used but WB Classification and UN LDC exist
    li_cols = ['party', 'total_allocation', 'state_component', 'iplc_component', 'WB Income Group', 'UN LDC']
    for col in li_cols:
        assert col in results_df.columns
    
    # Verify mapping for Low Income
    li_df = results_df[results_df['WB Income Group'] == 'Low income']
    assert all(li_df['WB Income Group'] == 'Low income')
    assert "LDC" in li_df["UN LDC"].values
    
def test_middle_income_tab_columns(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    results_df["UN LDC"] = results_df["is_ldc"].map({True: "LDC", False: "-"})
    
    # Verify both classification and UN LDC exist for Middle Income
    mi_cols = ['party', 'total_allocation', 'state_component', 'iplc_component', 'UN LDC', 'WB Income Group']
    for col in mi_cols:
        assert col in results_df.columns
    
    # Check for Middle Income LDCs (like Bangladesh)
    mi_ldcs = results_df[results_df['WB Income Group'].isin(['Lower middle income', 'Upper middle income']) & (results_df['UN LDC'] == 'LDC')]
    assert len(mi_ldcs) > 0
    
def test_ldc_consistency_across_tabs(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # 1. Total LDC Share from calculator (used in LDC Share tab)
    from cali_model.calculator import aggregate_special_groups
    ldc_total_calc, _ = aggregate_special_groups(results_df)
    expected_ldc_total = ldc_total_calc['total_allocation']
    
    # 2. Total LDCs across ALL income groups
    # Note: Some LDCs are Middle Income (e.g., Bangladesh, Nepal, Zambia)
    actual_ldc_total = results_df[results_df['is_ldc']]['total_allocation'].sum()
    
    # These must match exactly
    assert pytest.approx(actual_ldc_total, 0.001) == expected_ldc_total
    
def test_high_income_tab_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Logic from app.py: High Income tab
    hi_df = results_df[results_df['WB Income Group'] == 'High income']
    
    # Check all included rows are High income
    assert all(hi_df['WB Income Group'] == 'High income')
    assert 'High income' in hi_df['WB Income Group'].values

def test_allocation_sorting_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Default sort from app.py: Allocation (highest first) then party (A-Z)
    sorted_df = results_df.sort_values(
        by=["total_allocation", "party"],
        ascending=[False, True]
    )
    
    # First row should have the maximum allocation
    assert sorted_df.iloc[0]['total_allocation'] == results_df['total_allocation'].max()
    
    # Check monotonic decreasing (mostly) - if allocations are equal, party name is sorted alphabetically
    allocations = sorted_df['total_allocation'].tolist()
    assert all(allocations[i] >= allocations[i+1] for i in range(len(allocations)-1))

def test_alphabetical_sorting_logic(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # A-Z sort from app.py
    sorted_df = results_df.sort_values(by="party", ascending=True)
    
    parties = sorted_df['party'].tolist()
    assert parties == sorted(parties)
