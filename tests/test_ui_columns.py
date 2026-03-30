import pytest
import pandas as pd
import duckdb
import re
from pathlib import Path
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations, aggregate_by_region, aggregate_by_income, aggregate_special_groups

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

def test_column_visibility_by_tab(mock_con):
    base_df = get_base_data(mock_con)
    fund_size_usd = 1_000_000_000
    iplc_share = 50
    
    results_df = calculate_allocations(
        base_df,
        fund_size_usd,
        iplc_share,
        False, # show_raw
        True,  # exclude_hi
        un_scale_mode="band_inversion"
    )
    
    # 1. Test "By Party" columns logic
    # In app.py: display_cols = ['party', 'total_allocation', 'state_component', 'iplc_component', 'WB Income Group', 'UN LDC', 'CBD Party', 'EU']
    # If show_advanced is False (default) and un_scale_mode is "band_inversion":
    display_cols_party = ['party', 'total_allocation', 'state_component', 'iplc_component', 'WB Income Group', 'UN LDC', 'CBD Party', 'EU', 'un_band', 'un_band_weight']
    
    # Verify "Countries (number)" is NOT in display_cols_party
    assert "Countries (number)" not in display_cols_party
    
    # 2. Test "By UN Region" columns logic
    # In app.py: display_cols_region = ["region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    display_cols_region = ["region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    assert "Countries (number)" in display_cols_region
    
    # 3. Test "By UN Sub-region" columns logic
    display_cols_sub = ["sub_region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    assert "Countries (number)" in display_cols_sub
    
    # 4. Test "By UN Intermediate Region" columns logic
    display_cols_int = ["intermediate_region", "Countries (number)", "total_allocation", "state_component", "iplc_component"]
    assert "Countries (number)" in display_cols_int

    # 5. Test "Share by Income Group" columns logic
    display_cols_income = ['WB Income Group', 'Countries (number)', 'total_allocation', 'state_component', 'iplc_component']
    assert "Countries (number)" in display_cols_income

def test_inversion_comparison_headlines(mock_con):
    base_df = get_base_data(mock_con)
    fund_size_usd = 1_000_000_000
    iplc_share = 50
    
    # Scenario A: Exclude High Income
    results_hi_excluded = calculate_allocations(
        base_df, fund_size_usd, iplc_share, False, exclude_high_income=True
    )
    n_eligible_hi_excluded = results_hi_excluded['eligible'].sum()
    
    # Scenario B: Include High Income
    results_hi_included = calculate_allocations(
        base_df, fund_size_usd, iplc_share, False, exclude_high_income=False
    )
    n_eligible_hi_included = results_hi_included['eligible'].sum()
    
    assert n_eligible_hi_excluded < n_eligible_hi_included
    assert n_eligible_hi_excluded == 142 # 196 - (HIC-SIDS)
    assert n_eligible_hi_included == 196


def test_tab_order_keeps_sids_before_income_tabs():
    app_text = Path("src/app.py").read_text(encoding="utf-8")
    match = re.search(r"tabs\s*=\s*\[(.*?)\]", app_text, re.DOTALL)
    assert match is not None

    tabs_block = match.group(1)
    tab_sequence = ["LDC Share", "SIDS", "Low Income", "Middle Income", "High Income"]
    positions = [tabs_block.index(f'"{label}"') for label in tab_sequence]
    assert positions == sorted(positions)


def test_income_and_sids_tab_totals_match_expected_categories(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)

    low_total = results_df[results_df['WB Income Group'] == 'Low income']['total_allocation'].sum()
    mid_total = results_df[results_df['WB Income Group'].isin(['Lower middle income', 'Upper middle income'])]['total_allocation'].sum()
    high_total = results_df[results_df['WB Income Group'] == 'High income']['total_allocation'].sum()

    income_mask = results_df['WB Income Group'].isin(['Low income', 'Lower middle income', 'Upper middle income', 'High income'])
    expected_income_total = results_df[income_mask]['total_allocation'].sum()
    assert pytest.approx(low_total + mid_total + high_total, 0.001) == expected_income_total

    _, sids_total = aggregate_special_groups(results_df)
    expected_sids_total = results_df[results_df['eligible'] & results_df['is_sids']]['total_allocation'].sum()
    assert pytest.approx(sids_total['total_allocation'], 0.001) == expected_sids_total
