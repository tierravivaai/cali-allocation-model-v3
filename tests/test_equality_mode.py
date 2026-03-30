import pandas as pd
import pytest
from cali_model.calculator import calculate_allocations

def test_equality_mode_even_split():
    # Setup a mock dataframe
    data = {
        'party': ['Country A', 'Country B', 'Country C', 'Country D'],
        'is_cbd_party': [True, True, True, True],
        'WB Income Group': ['Low income', 'Low income', 'High income', 'Low income'],
        'un_share': [0.1, 0.2, 0.3, 0.4],
        'land_area_km2': [1000, 2000, 3000, 4000],
        'is_sids': [False, False, False, False],
        'is_eu_ms': [False, False, False, False]
    }
    df = pd.DataFrame(data)
    
    # Run calculation in equality mode with HI excluded (default for Equality preset)
    # The Equality preset in app.py uses exclude_all (which excludes HI except SIDS)
    # In this test, Country C is HI and not SIDS, so it should be excluded.
    fund_size = 100_000_000
    result = calculate_allocations(
        df, 
        fund_size=fund_size,
        iplc_share_pct=20.0,
        exclude_high_income=True,
        high_income_mode="exclude_except_sids",
        equality_mode=True
    )
    
    # Country C (High income) should be ineligible
    assert result.loc[result['party'] == 'Country C', 'eligible'].iloc[0] == False
    assert result.loc[result['party'] == 'Country C', 'total_allocation'].iloc[0] == 0
    
    # Others should be eligible and have equal shares
    eligible_mask = result['eligible']
    n_eligible = eligible_mask.sum()
    assert n_eligible == 3
    
    expected_allocation = (fund_size / n_eligible) / 1_000_000.0 # in millions
    
    for party in ['Country A', 'Country B', 'Country D']:
        alloc = result.loc[result['party'] == party, 'total_allocation'].iloc[0]
        assert pytest.approx(alloc) == expected_allocation
        # Components should be 0 except IUSAF which represents the base share here
        assert result.loc[result['party'] == party, 'component_tsac_amt'].iloc[0] == 0
        assert result.loc[result['party'] == party, 'component_sosac_amt'].iloc[0] == 0

def test_equality_mode_includes_sids_even_if_hi():
    data = {
        'party': ['SIDS HI', 'Regular HI', 'LDC'],
        'is_cbd_party': [True, True, True],
        'WB Income Group': ['High income', 'High income', 'Low income'],
        'un_share': [0.1, 0.2, 0.3],
        'land_area_km2': [100, 200, 300],
        'is_sids': [True, False, False],
        'is_eu_ms': [False, False, False]
    }
    df = pd.DataFrame(data)
    
    result = calculate_allocations(
        df, 
        fund_size=100_000_000,
        iplc_share_pct=20.0,
        exclude_high_income=True,
        high_income_mode="exclude_except_sids",
        equality_mode=True
    )
    
    # SIDS HI should be eligible, Regular HI should not
    assert result.loc[result['party'] == 'SIDS HI', 'eligible'].iloc[0] == True
    assert result.loc[result['party'] == 'Regular HI', 'eligible'].iloc[0] == False
    assert result.loc[result['party'] == 'LDC', 'eligible'].iloc[0] == True
    
    assert result['eligible'].sum() == 2
