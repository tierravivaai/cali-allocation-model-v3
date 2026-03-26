import pytest
from streamlit.testing.v1 import AppTest


def test_initial_load_defaults_to_true_equality():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    assert at.checkbox(key="exclude_hi").value is False
    assert at.slider(key="tsac_beta_pct").value == 0
    assert at.slider(key="sosac_gamma_pct").value == 0
    assert at.session_state["equality_mode"] is True

def test_reset_button_functionality():
    """
    Test that the 'Reset to default' button correctly resets the app state.
    """
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    
    # 1. Modify some values
    # Slider 0 is fund_size_bn, Slider 1 is iplc_share
    at.slider(key="fund_size_bn").set_value(5.0).run()
    at.toggle(key="use_thousands").set_value(True).run()
    at.checkbox(key="exclude_hi").set_value(False).run()
    at.selectbox(key="sort_option").set_value("Country name (A–Z)").run()
    
    # Verify modifications took place
    assert at.slider(key="fund_size_bn").value == 5.0
    assert at.toggle(key="use_thousands").value is True
    assert at.checkbox(key="exclude_hi").value is False
    assert at.selectbox(key="sort_option").value == "Country name (A–Z)"
    
    # 2. Click the reset button
    # at.button returns a list, we filter it by label
    reset_button = [b for b in at.button if b.label == "Reset to default"][0]
    reset_button.click().run()
    
    # 3. Verify values are back to defaults
    assert at.slider(key="fund_size_bn").value == 1.0
    assert at.toggle(key="use_thousands").value is False
    assert at.checkbox(key="exclude_hi").value is False
    assert at.slider(key="iplc_share").value == 50
    assert at.slider(key="tsac_beta_pct").value == 0
    assert at.slider(key="sosac_gamma_pct").value == 0
    assert at.session_state["equality_mode"] is True
    assert at.selectbox(key="sort_option").value == "Allocation (highest first)"


def test_inverted_un_scale_turns_on_exclude_high_income():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    at.checkbox(key="exclude_hi").set_value(False).run()
    assert at.checkbox(key="exclude_hi").value is False

    inverted_button = [b for b in at.button if b.label == "2. Inverted UN Scale"][0]
    inverted_button.click().run()

    assert at.checkbox(key="exclude_hi").value is True
    assert at.session_state["equality_mode"] is False
    assert at.slider(key="tsac_beta_pct").value == 0
    assert at.slider(key="sosac_gamma_pct").value == 0


def test_negotiation_country_caption_tracks_selected_country_across_rerun():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    target = "Honduras"
    at.selectbox(key="negotiation_target_party").set_value(target).run()

    # Trigger a rerun through a related control to ensure selection remains synchronized
    at.slider(key="tsac_beta_pct").set_value(6).run()

    assert at.selectbox(key="negotiation_target_party").value == target
    summary_caption = [c.value for c in at.caption if "Current setting allocates" in c.value][0]
    assert summary_caption.startswith(f"{target}:")


def test_fund_size_scenario_markers_update_slider():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    button_50m = [b for b in at.button if b.label == "$50m"][0]
    button_50m.click().run()
    assert at.slider(key="fund_size_bn").value == 0.05

    button_200m = [b for b in at.button if b.label == "$200m"][0]
    button_200m.click().run()
    assert at.slider(key="fund_size_bn").value == 0.2

    button_500m = [b for b in at.button if b.label == "$500m"][0]
    button_500m.click().run()
    assert at.slider(key="fund_size_bn").value == 0.5

    button_1bn = [b for b in at.button if b.label == "$1bn"][0]
    button_1bn.click().run()
    assert at.slider(key="fund_size_bn").value == 1.0


def test_terrestrial_stewardship_preset_sets_tsac_max_and_sosac_zero():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    at.checkbox(key="exclude_hi").set_value(False).run()
    terrestrial_button = [b for b in at.button if b.label == "3. Terrestrial Stewardship"][0]
    terrestrial_button.click().run()

    assert at.checkbox(key="exclude_hi").value is True
    assert at.slider(key="tsac_beta_pct").value == 15
    assert at.slider(key="sosac_gamma_pct").value == 0


def test_oceans_stewardship_preset_sets_sosac_max_and_tsac_zero():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    at.checkbox(key="exclude_hi").set_value(False).run()
    oceans_button = [b for b in at.button if b.label == "4. Oceans Stewardship"][0]
    oceans_button.click().run()

    assert at.checkbox(key="exclude_hi").value is True
    assert at.slider(key="tsac_beta_pct").value == 0
    assert at.slider(key="sosac_gamma_pct").value == 10


def test_gini_optimal_point_preset_turns_on_exclude_high_income():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()

    at.checkbox(key="exclude_hi").set_value(False).run()
    balanced_button = [b for b in at.button if b.label == "5. Gini-optimal point"][0]
    balanced_button.click().run()

    assert at.checkbox(key="exclude_hi").value is True
    assert at.slider(key="tsac_beta_pct").value == 5
    assert at.slider(key="sosac_gamma_pct").value == 3
