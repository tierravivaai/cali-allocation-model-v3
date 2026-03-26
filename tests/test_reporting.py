import pandas as pd

from logic.reporting import generate_sweep_summary


def test_sweep_summary_trigger_attribution():
    sweep_df = pd.DataFrame([
        {
            "scenario_id": "test_sweep_0.0",
            "sweep_value": 0.0,
            "spearman_vs_pure_iusaf": 0.977,
            "top20_turnover_vs_pure_iusaf": 0.80,
            "departure_from_pure_iusaf_flag": True,
            "gini_coefficient": 0.101,
        }
    ])
    md = generate_sweep_summary("test sweep", sweep_df, "spearman_vs_pure_iusaf")
    assert "top20_turnover_vs_pure_iusaf=0.8000" in md
    assert "spearman_vs_pure_iusaf=0.9770` (threshold: < 0.95)" not in md


def test_sweep_summary_spearman_trigger():
    sweep_df = pd.DataFrame([
        {
            "scenario_id": "test_sweep_0.1",
            "sweep_value": 0.1,
            "spearman_vs_pure_iusaf": 0.85,
            "top20_turnover_vs_pure_iusaf": 0.10,
            "departure_from_pure_iusaf_flag": True,
            "gini_coefficient": 0.090,
        }
    ])
    md = generate_sweep_summary("test sweep", sweep_df, "spearman_vs_pure_iusaf")
    assert "spearman_vs_pure_iusaf=0.8500" in md
    assert "top20_turnover_vs_pure_iusaf=0.1000` (threshold: > 0.20)" not in md
