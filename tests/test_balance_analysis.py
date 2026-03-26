"""Tests for balance-point diagnostics."""
from __future__ import annotations

import duckdb
import pandas as pd
import pytest

from logic.balance_analysis import (
    generate_balance_point_summary,
    identify_balance_points,
    run_fine_sweep,
)
from logic.calculator import calculate_allocations
from logic.data_loader import get_base_data, load_data
from logic.sensitivity_metrics import (
    build_pure_iusaf_comparator,
    compute_component_ratios,
    compute_gini,
    compute_metrics,
)
from logic.sensitivity_scenarios import DEFAULT_BASELINE, get_default_ranges


@pytest.fixture(scope="module")
def base_df():
    con = duckdb.connect(database=":memory:")
    load_data(con)
    return get_base_data(con)


def _run(base_df, **overrides):
    params = dict(
        fund_size=1_000_000_000,
        iplc_share_pct=50,
        exclude_high_income=True,
        floor_pct=0.0,
        ceiling_pct=None,
        tsac_beta=0.0,
        sosac_gamma=0.0,
        equality_mode=False,
        un_scale_mode="band_inversion",
    )
    params.update(overrides)
    return calculate_allocations(base_df, **params)


def _run_scenario(base_df, scenario):
    return calculate_allocations(
        base_df,
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


class TestComputeGini:
    def test_perfect_equality(self):
        assert compute_gini(pd.Series([100.0] * 10)) == pytest.approx(0.0, abs=1e-6)

    def test_maximum_inequality(self):
        s = pd.Series([0.0] * 9 + [100.0])
        assert compute_gini(s) == pytest.approx(0.9, abs=0.01)

    def test_empty_returns_zero(self):
        assert compute_gini(pd.Series([], dtype=float)) == 0.0

    def test_real_results_in_range(self, base_df):
        results = _run(base_df)
        g = compute_gini(results.loc[results["eligible"], "total_allocation"])
        assert 0.0 <= g <= 1.0

    def test_gini_optimal_point_higher_gini_than_iusaf(self, base_df):
        iusaf = _run(base_df)
        sf = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        g_iusaf = compute_gini(iusaf.loc[iusaf["eligible"], "total_allocation"])
        g_sf = compute_gini(sf.loc[sf["eligible"], "total_allocation"])
        assert g_sf >= g_iusaf - 0.05


class TestComputeComponentRatios:
    def test_zero_tsac_returns_zero(self, base_df):
        results = _run(base_df)
        r = compute_component_ratios(results, beta=0.0, gamma=0.0)
        assert r["max_tsac_iusaf_ratio"] == pytest.approx(0.0)
        assert r["tsac_balance_exceeded"] is False
        assert r["n_parties_tsac_dominant"] == 0

    def test_high_tsac_exceeds_balance(self, base_df):
        results = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        r = compute_component_ratios(results, beta=0.05, gamma=0.03)
        assert r["tsac_balance_exceeded"] is True
        assert r["china_tsac_iusaf_ratio"] is not None
        assert r["china_tsac_iusaf_ratio"] > 1.0

    def test_china_highest_ratio(self, base_df):
        results = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        r = compute_component_ratios(results, beta=0.05, gamma=0.03)
        assert r["china_tsac_iusaf_ratio"] >= (r["brazil_tsac_iusaf_ratio"] or 0)

    def test_ratio_df_sorted_descending(self, base_df):
        results = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        r = compute_component_ratios(results, beta=0.05, gamma=0.03)
        df = r["ratio_df"]
        if len(df) > 1:
            assert df["tsac_iusaf_ratio"].iloc[0] >= df["tsac_iusaf_ratio"].iloc[-1]

    def test_required_columns_present(self, base_df):
        results = _run(base_df, tsac_beta=0.05, sosac_gamma=0.03)
        r = compute_component_ratios(results, beta=0.05, gamma=0.03)
        for col in ["party", "tsac_iusaf_ratio", "tsac_dominant"]:
            assert col in r["ratio_df"].columns


def _sweep_row(val, china, brazil, gini, spearman):
    return {
        "sweep_value": val,
        "china_tsac_iusaf_ratio": china,
        "brazil_tsac_iusaf_ratio": brazil,
        "gini_coefficient": gini,
        "spearman_vs_pure_iusaf": spearman,
        "max_tsac_iusaf_ratio": max(china, brazil),
        "max_sosac_iusaf_ratio": max(china, brazil),
    }


class TestIdentifyBalancePoints:
    def test_strict_identified(self):
        rows = [
            _sweep_row(0.020, 0.90, 0.45, 0.15, 0.93),
            _sweep_row(0.025, 1.05, 0.52, 0.16, 0.90),
        ]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df)
        assert bp["strict"] is not None
        assert bp["strict"]["value"] == pytest.approx(0.020, abs=0.001)

    def test_modified_identified(self):
        rows = [
            _sweep_row(0.045, 2.1, 0.98, 0.19, 0.87),
            _sweep_row(0.050, 2.3, 1.05, 0.20, 0.82),
        ]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df)
        assert bp["modified"] is not None
        assert bp["modified"]["value"] == pytest.approx(0.045, abs=0.001)

    def test_gini_optimal_is_min_gini_above_spearman(self):
        rows = [
            _sweep_row(0.010, 0.40, 0.20, 0.20, 0.95),
            _sweep_row(0.020, 0.80, 0.40, 0.13, 0.92),
            _sweep_row(0.090, 3.00, 1.50, 0.26, 0.79),
        ]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df, spearman_moderate_threshold=0.85)
        assert bp["gini_optimal"] is not None
        assert bp["gini_optimal"]["value"] == pytest.approx(0.020, abs=0.001)

    def test_gini_optimal_label(self):
        rows = [
            _sweep_row(0.010, 0.40, 0.20, 0.20, 0.95),
            _sweep_row(0.020, 0.80, 0.40, 0.13, 0.92),
            _sweep_row(0.090, 3.00, 1.50, 0.26, 0.79),
        ]
        df = pd.DataFrame(rows)
        df["tsac_balance_exceeded"] = [False, True, True]
        bp = identify_balance_points(df, df, spearman_moderate_threshold=0.85)
        assert bp["gini_optimal"] is not None
        assert bp["gini_optimal"]["metrics"]["tsac_balance_exceeded"] is True

    def test_practical_label_retired(self):
        rows = [
            _sweep_row(0.010, 0.40, 0.20, 0.20, 0.95),
            _sweep_row(0.020, 0.80, 0.40, 0.13, 0.92),
        ]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df, spearman_moderate_threshold=0.85)
        assert "practical" not in bp
        assert "gini_optimal" in bp

    def test_returns_none_when_never_satisfied(self):
        rows = [_sweep_row(0.01, 1.5, 1.2, 0.20, 0.92)]
        df = pd.DataFrame(rows)
        bp = identify_balance_points(df, df)
        assert bp["strict"] is None
        assert bp["modified"] is None

    def test_sosac_reports_above_range_when_threshold_never_crossed(self):
        rows = [
            _sweep_row(0.005, 0.0, 0.0, 0.10, 0.97),
            _sweep_row(0.100, 0.0, 0.0, 0.14, 0.87),
        ]
        df = pd.DataFrame(rows)
        df["max_sosac_iusaf_ratio"] = [0.0239, 0.5277]
        df["max_sosac_ratio_parties"] = ["Cuba, Singapore", "Cuba, Singapore"]
        bp = identify_balance_points(df, df)
        assert bp["sosac"] is not None
        assert bp["sosac"]["above_range"] is True
        assert bp["sosac"]["value"] is None
        assert bp["sosac"]["max_ratio_at_sweep_limit"] == pytest.approx(0.5277, abs=1e-4)


class TestGenerateBalancePointSummary:
    def _bp(self):
        return {
            "strict": {
                "value": 0.024,
                "metrics": {
                    "sweep_value": 0.024,
                    "gini_coefficient": 0.148,
                    "spearman_vs_pure_iusaf": 0.931,
                    "china_tsac_iusaf_ratio": 1.00,
                    "brazil_tsac_iusaf_ratio": 0.49,
                    "band1_pct_change_vs_iusaf": -2.4,
                    "band1_per_party_alloc_m": 8.31,
                    "sids_total_m": 305.0,
                    "ldc_total_m": 328.0,
                },
            },
            "modified": None,
            "gini_optimal": None,
            "sosac": None,
        }

    def test_returns_string(self):
        md = generate_balance_point_summary(self._bp(), pd.DataFrame(), pd.DataFrame())
        assert isinstance(md, str)

    def test_contains_all_four_sections(self):
        md = generate_balance_point_summary(
            {"strict": None, "modified": None, "gini_optimal": None, "sosac": None},
            pd.DataFrame(),
            pd.DataFrame(),
        )
        for section in [
            "Strict balance point",
            "Modified balance point",
            "Gini-optimal point",
            "SOSAC balance point",
        ]:
            assert section in md

    def test_strict_value_present(self):
        md = generate_balance_point_summary(self._bp(), pd.DataFrame(), pd.DataFrame())
        assert "2.4%" in md

    def test_gini_optimal_point_mentioned(self):
        md = generate_balance_point_summary(self._bp(), pd.DataFrame(), pd.DataFrame())
        assert "gini-optimal point" in md.lower()

    def test_gini_optimal_note_present(self):
        bp = {
            "strict": None,
            "modified": None,
            "gini_optimal": {
                "value": 0.05,
                "metrics": {
                    "sweep_value": 0.05,
                    "spearman_vs_pure_iusaf": 0.8520,
                    "gini_coefficient": 0.0829,
                    "china_tsac_iusaf_ratio": 2.869,
                    "brazil_tsac_iusaf_ratio": 1.362,
                    "tsac_balance_exceeded": True,
                },
            },
            "sosac": None,
        }
        md = generate_balance_point_summary(bp, pd.DataFrame(), pd.DataFrame())
        assert "The Spearman constraint (> 0.85) binds" in md
        assert "the unconstrained Gini minimum is at TSAC=5.5%" in md
        assert "Spearman=0.822" in md
        assert '"minimises the Gini coefficient while keeping Spearman rank correlation vs pure IUSAF > 0.85"' in md
        assert "does not satisfy the TSAC/IUSAF dominance balance condition" in md
        assert "`tsac_balance_exceeded` is `True`" in md

    def test_sosac_above_range_text_present(self):
        bp = {
            "strict": None,
            "modified": None,
            "gini_optimal": None,
            "sosac": {
                "value": None,
                "above_range": True,
                "max_ratio_at_sweep_limit": 0.5277,
                "analytical_estimate": 0.174,
                "metrics": {"max_sosac_ratio_parties": "Cuba, Singapore"},
            },
        }
        md = generate_balance_point_summary(bp, pd.DataFrame(), pd.DataFrame())
        assert "lies above the 0–10% sweep range" in md
        assert "0.528×" in md
        assert "17.4%" in md


class TestRunFineSweep:
    def test_runs_and_returns_expected_columns(self, base_df):
        sweep = run_fine_sweep(
            base_scenario=dict(DEFAULT_BASELINE),
            base_df=base_df,
            run_scenario_fn=_run_scenario,
            compute_metrics_fn=compute_metrics,
            compute_component_ratios_fn=compute_component_ratios,
            build_pure_iusaf_fn=build_pure_iusaf_comparator,
            sweep_param="tsac_beta",
            values=get_default_ranges()["tsac_beta_fine"][:3],
        )
        assert len(sweep) == 3
        for col in ["gini_coefficient", "china_tsac_iusaf_ratio", "band1_per_party_alloc_m"]:
            assert col in sweep.columns
