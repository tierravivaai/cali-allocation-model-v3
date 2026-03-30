import pytest
import pandas as pd
import duckdb
from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations, aggregate_by_region

@pytest.fixture
def mock_con():
    con = duckdb.connect(database=':memory:')
    load_data(con)
    return con

def test_region_selector_options(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    # Logic from app.py
    region_list = (
        aggregate_by_region(results_df, "region")["region"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    region_list = sorted(region_list)
    
    assert len(region_list) > 0
    assert "Africa" in region_list
    assert "Americas" in region_list

def test_sub_region_selector_options(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    sub_region_list = (
        aggregate_by_region(results_df, "sub_region")["sub_region"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    sub_region_list = sorted(sub_region_list)
    
    assert len(sub_region_list) > 0
    assert "Northern Africa" in sub_region_list or "Sub-Saharan Africa" in sub_region_list

def test_intermediate_region_selector_options(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    int_region_list = (
        aggregate_by_region(results_df[results_df['intermediate_region'] != 'NA'], "intermediate_region")["intermediate_region"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    int_region_list = sorted(int_region_list)
    
    assert len(int_region_list) > 0
    assert "South America" in int_region_list

def test_filtering_by_selected_region(mock_con):
    base_df = get_base_data(mock_con)
    results_df = calculate_allocations(base_df, 1_000_000_000, 50)
    
    selected_region = "Africa"
    region_countries = results_df[results_df["region"] == selected_region]
    
    assert len(region_countries) > 0
    assert (region_countries["region"] == selected_region).all()
