from __future__ import annotations

import duckdb
import pandas as pd

from cali_model.calculator import calculate_allocations
from cali_model.data_loader import get_base_data, load_data
from cali_model.sensitivity_metrics import generate_integrity_checks
from cali_model.sensitivity_scenarios import get_scenario_library


def _base_df():
    con = duckdb.connect(database=":memory:")
    load_data(con)
    return get_base_data(con)


def _run_scenario(df, scenario):
    return calculate_allocations(
        df,
        fund_size=float(scenario["fund_size"]),
        iplc_share_pct=float(scenario["iplc_share_pct"]),
        exclude_high_income=bool(scenario["exclude_high_income"]),
        floor_pct=float(scenario.get("floor_pct", 0.0) or 0.0),
        ceiling_pct=scenario.get("ceiling_pct"),
        tsac_beta=float(scenario.get("tsac_beta", 0.0)),
        sosac_gamma=float(scenario.get("sosac_gamma", 0.0)),
        equality_mode=bool(scenario.get("equality_mode", False)),
        un_scale_mode=scenario.get("un_scale_mode", "band_inversion"),
    )


def test_integrity_checks_all_pass_for_valid_scenario():
    df = _base_df()
    scenario = get_scenario_library()["gini_minimum_point"]
    results_df = _run_scenario(df, scenario)

    row = generate_integrity_checks(
        scenario_id="gini_minimum_point",
        scenario_params=scenario,
        results_df=results_df,
        fund_size=1_000_000_000,
    )

    assert row["all_checks_pass"] == "PASS"


def test_integrity_checks_detects_non_conservation():
    bad_df = pd.DataFrame(
        {
            "eligible": [True, True],
            "final_share": [0.6, 0.6],
            "total_allocation": [600, 600],
            "component_iusaf_amt": [600, 600],
            "component_tsac_amt": [0, 0],
            "component_sosac_amt": [0, 0],
            "state_component": [300, 300],
            "iplc_component": [300, 300],
            "un_band": ["Band 1: <= 0.001%", "Band 2: 0.001% - 0.01%"],
            "is_sids": [False, False],
        }
    )
    row = generate_integrity_checks(
        scenario_id="test_broken",
        scenario_params={"tsac_beta": 0.0, "sosac_gamma": 0.0, "floor_pct": 0.0, "ceiling_pct": None},
        results_df=bad_df,
        fund_size=1_000_000_000,
    )
    assert row["check_conservation_shares"] == "FAIL"
    assert row["all_checks_pass"] == "FAIL"


def test_integrity_checks_columns_complete():
    required_columns = [
        "scenario_id", "fund_size_usd", "tsac_beta", "sosac_gamma",
        "check_conservation_shares", "sum_final_share",
        "check_conservation_money", "sum_total_allocation_usd",
        "check_non_negativity", "min_allocation_usd",
        "check_component_consistency", "max_component_abs_diff_usd",
        "check_iplc_split", "max_iplc_abs_diff_usd",
        "check_band_monotonicity", "band_monotonicity_detail",
        "check_floor_not_binding_unexpectedly", "floor_binding_count",
        "check_ceiling_not_binding_unexpectedly", "ceiling_binding_count",
        "check_sids_sosac_allocation", "sids_sosac_component_sum_usd",
        "n_eligible_parties", "n_eligible_sids", "all_checks_pass",
    ]
    row = generate_integrity_checks(
        scenario_id="test",
        scenario_params={},
        results_df=pd.DataFrame(),
        fund_size=1e9,
    )
    for col in required_columns:
        assert col in row
