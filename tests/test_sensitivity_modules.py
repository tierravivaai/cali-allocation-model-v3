import duckdb
import pandas as pd

from cali_model.calculator import calculate_allocations
from cali_model.data_loader import get_base_data, load_data
from cali_model.reporting import classify_local_stability, classify_overlay_strength, generate_sweep_summary
from cali_model.sensitivity_metrics import _spearman_by_party, compute_local_stability_metrics, compute_metrics, run_invariant_checks
from cali_model.sensitivity_scenarios import get_scenario_library


def _base_df():
    con = duckdb.connect(database=":memory:")
    load_data(con)
    return get_base_data(con)


def test_scenario_library_contains_required_entries():
    library = get_scenario_library()
    required = {
        "pure_equality",
        "pure_iusaf_raw",
        "pure_iusaf_band",
        "gini_optimal_point",
        "tsac_strict_balance",
        "tsac_modified_balance",
        "terrestrial_max",
        "ocean_max",
        "gini_optimal_floor_005",
        "gini_optimal_ceiling_1",
        "gini_optimal_floor_005_ceiling_1",
        "exclude_hi_off_compare",
        "exclude_hi_on_compare",
        "raw_vs_band_compare",
    }
    assert required.issubset(set(library.keys()))


def test_metrics_and_invariants_run_for_gini_optimal_point():
    df = _base_df()
    scenario = get_scenario_library()["gini_optimal_point"]
    current = calculate_allocations(df, scenario["fund_size"], scenario["iplc_share_pct"], exclude_high_income=scenario["exclude_high_income"], floor_pct=scenario["floor_pct"], ceiling_pct=scenario["ceiling_pct"], tsac_beta=scenario["tsac_beta"], sosac_gamma=scenario["sosac_gamma"], equality_mode=scenario["equality_mode"], un_scale_mode=scenario["un_scale_mode"])
    iusaf = calculate_allocations(df, scenario["fund_size"], scenario["iplc_share_pct"], exclude_high_income=scenario["exclude_high_income"], tsac_beta=0.0, sosac_gamma=0.0, equality_mode=False, un_scale_mode=scenario["un_scale_mode"])
    equality = calculate_allocations(df, scenario["fund_size"], scenario["iplc_share_pct"], exclude_high_income=scenario["exclude_high_income"], tsac_beta=0.0, sosac_gamma=0.0, equality_mode=True, un_scale_mode=scenario["un_scale_mode"])

    local, _ = compute_local_stability_metrics(
        base_scenario=scenario,
        base_results_df=current,
        base_df=df,
        run_scenario_fn=lambda _df, s: calculate_allocations(
            _df,
            s["fund_size"],
            s["iplc_share_pct"],
            exclude_high_income=s["exclude_high_income"],
            floor_pct=s["floor_pct"],
            ceiling_pct=s["ceiling_pct"],
            tsac_beta=s["tsac_beta"],
            sosac_gamma=s["sosac_gamma"],
            equality_mode=s["equality_mode"],
            un_scale_mode=s["un_scale_mode"],
        ),
    )

    metrics = compute_metrics(scenario, current, iusaf, equality, local_stability=local)
    assert metrics["n_eligible"] > 0
    assert abs(metrics["sum_final_share"] - 1.0) < 1e-6
    assert "overlay_strength_label" in metrics
    assert "local_stability_label" in metrics
    assert "departure_from_pure_iusaf_flag" in metrics
    assert "local_blended_instability_flag" in metrics

    checks = run_invariant_checks(scenario, current)
    assert checks["pass"].all()


def test_overlay_and_local_stability_are_distinct_concepts():
    assert classify_overlay_strength(0.92, 0.15) == "strong overlay"
    assert classify_local_stability(0.995, 0.03) == "stable"


def test_spearman_by_party_handles_constant_distributions_without_warning():
    current = pd.DataFrame({"party": ["A", "B"], "final_share": [0.5, 0.5]})
    baseline = pd.DataFrame({"party": ["A", "B"], "final_share": [0.5, 0.5]})

    assert _spearman_by_party(current, baseline) == 1.0


def test_spearman_by_party_returns_zero_when_only_one_distribution_is_constant():
    current = pd.DataFrame({"party": ["A", "B", "C"], "final_share": [0.4, 0.35, 0.25]})
    baseline = pd.DataFrame({"party": ["A", "B", "C"], "final_share": [1 / 3, 1 / 3, 1 / 3]})

    assert _spearman_by_party(current, baseline) == 0.0


def test_retired_baseline_keys_absent():
    library = get_scenario_library()
    retired_stewardship_key = "stewardship" + "_forward_baseline"
    retired_balanced_key = "balanced" + "_baseline"
    retired_practical_key = "practical" + "_balance_point"
    assert retired_stewardship_key not in library
    assert retired_balanced_key not in library
    assert retired_practical_key not in library
    assert "gini_optimal_point" in library


def test_gini_optimal_scenario_key():
    library = get_scenario_library()
    assert "gini_optimal_point" in library
    assert "practical_balance_point" not in library


def test_gini_optimal_point_parameters():
    scenario = get_scenario_library()["gini_optimal_point"]
    assert abs(scenario["tsac_beta"] - 0.05) < 0.001
    assert abs(scenario["sosac_gamma"] - 0.03) < 0.001


def test_floor_ceiling_variants_renamed():
    library = get_scenario_library()
    for old_key in [
        "balanced" + "_floor_005",
        "balanced" + "_ceiling_1",
        "balanced" + "_floor_005_ceiling_1",
        "practical" + "_floor_005",
        "practical" + "_ceiling_1",
        "practical" + "_floor_005_ceiling_1",
    ]:
        assert old_key not in library
    for new_key in ["gini_optimal_floor_005", "gini_optimal_ceiling_1", "gini_optimal_floor_005_ceiling_1"]:
        assert new_key in library


def test_sweep_summary_attributes_spearman_and_turnover_thresholds_separately():
    sweep_df = pd.DataFrame(
        [
            {
                "scenario_id": "turnover_first",
                "departure_from_pure_iusaf_flag": True,
                "spearman_vs_pure_iusaf": 0.9700,
                "top20_turnover_vs_pure_iusaf": 0.25,
                "pct_below_equality": 10.0,
                "local_min_spearman_vs_baseline": 0.98,
                "local_max_top20_turnover_vs_baseline": 0.05,
                "local_max_abs_share_delta": 0.001,
                "tsac_beta": 0.05,
                "sosac_gamma": 0.03,
            },
            {
                "scenario_id": "spearman_first",
                "departure_from_pure_iusaf_flag": True,
                "spearman_vs_pure_iusaf": 0.9400,
                "top20_turnover_vs_pure_iusaf": 0.10,
                "pct_below_equality": 10.0,
                "local_min_spearman_vs_baseline": 0.93,
                "local_max_top20_turnover_vs_baseline": 0.25,
                "local_max_abs_share_delta": 0.006,
                "tsac_beta": 0.06,
                "sosac_gamma": 0.03,
            },
        ]
    )

    summary = generate_sweep_summary("test sweep", sweep_df, "spearman_vs_pure_iusaf")

    assert "departure-from-pure-IUSAF threshold: first triggered at `turnover_first`. Trigger: `top20_turnover_vs_pure_iusaf=0.2500` (threshold: > 0.20)." in summary
    assert "Local min Spearman vs baseline threshold: first triggered at `spearman_first` (`local_min_spearman_vs_baseline=0.9300`)." in summary
