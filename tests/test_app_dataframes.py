"""
Test case to prevent regression of CSV download/server connection issues.

This test verifies that:
1. The Streamlit app initializes correctly
2. Dataframes are properly rendered with data
3. The app state is valid for CSV export functionality
"""
import pytest
from streamlit.testing.v1 import AppTest


def test_app_initializes_with_valid_dataframes():
    """
    Test that the app initializes correctly and dataframes contain data.
    This serves as a regression test for server/download connection issues.
    """
    at = AppTest.from_file("src/app.py", default_timeout=30)
    at.run()
    
    # Verify app initialized successfully
    assert at.session_state is not None
    assert "base_df" in at.session_state
    
    # Verify base dataframe exists and has data
    base_df = at.session_state["base_df"]
    assert len(base_df) > 0
    assert len(base_df.columns) > 0
    
    # Verify key columns exist for CSV export (base_df contains country identifiers)
    required_columns = ["party", "un_share"]
    for col in required_columns:
        assert col in base_df.columns or any(col in str(c) for c in base_df.columns)


def test_streamlit_renders_data_elements():
    """
    Test that Streamlit renders dataframe elements which are needed for CSV download.
    """
    at = AppTest.from_file("src/app.py", default_timeout=30)
    at.run()
    
    # Check that dataframe elements are rendered
    # Streamlit's AppTest tracks elements, dataframes appear in .dataframe
    assert len(at.dataframe) > 0, "App should render at least one dataframe for CSV export"
    
    # Verify dataframe has structure (not empty)
    first_dataframe = at.dataframe[0]
    assert hasattr(first_dataframe, 'value'), "Dataframe should have value attribute"
    assert first_dataframe.value is not None, "Dataframe value should not be None"


def test_app_state_remains_consistent_after_parameter_changes():
    """
    Test that app state remains valid after parameter changes,
    ensuring CSV download continues to work throughout user interaction.
    """
    at = AppTest.from_file("src/app.py", default_timeout=30)
    at.run()
    
    # Record initial state
    initial_df_count = len(at.dataframe)
    
    # Change parameters that affect dataframe rendering
    at.slider(key="tsac_beta_pct").set_value(5).run()
    assert len(at.dataframe) > 0, "Dataframes should still render after TSAC change"
    
    at.slider(key="fund_size_bn").set_value(2.0).run()
    assert len(at.dataframe) == initial_df_count, "Dataframe count should remain consistent"
    
    # Verify dataframes are still valid
    first_dataframe = at.dataframe[0]
    assert hasattr(first_dataframe, 'value')
    assert first_dataframe.value is not None
