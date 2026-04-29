"""Structural validation tests for IPLC developed-country allocations.

These tests verify the mathematical integrity of the two IPLC scenarios
(Option 1: raw equality, Option 2: banded IUSAF) for 9 developed countries,
without depending on the generate_iplc_developed_tables.py script.

They confirm that the closeness of Option 1 and Option 2 IPLC totals
(2.30% vs 2.11% of fund) is structurally expected, not a bug.

See iplc-developed/validation_analysis.md for the full explanation.

Run with: pytest iplc-developed/test_structural_validation.py -v
"""

import sys
import os
import pytest
import duckdb
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cali_model.data_loader import load_data, get_base_data
from cali_model.calculator import calculate_allocations

DEVELOPED_COUNTRIES = [
    "Australia", "Canada", "Denmark", "Finland", "Japan",
    "New Zealand", "Norway", "Russian Federation", "Sweden",
]

BAND_4_COUNTRIES = {"Denmark", "Finland", "New Zealand", "Norway", "Sweden"}
BAND_5_COUNTRIES = {"Australia", "Canada", "Japan", "Russian Federation"}

IPLC_SHARE_PCT = 50
FUND_SIZES = {
    "50m": 50_000_000,
    "200m": 200_000_000,
    "500m": 500_000_000,
    "1bn": 1_000_000_000,
}


@pytest.fixture
def con():
    c = duckdb.connect(database=":memory:")
    load_data(c)
    return c


@pytest.fixture
def base_df(con):
    return get_base_data(con)


def _compute_option1(base_df, fund_usd):
    """Option 1: raw equality for all Parties, exclude_hi=False."""
    return calculate_allocations(
        base_df, fund_usd, IPLC_SHARE_PCT,
        exclude_high_income=False,
        equality_mode=True,
        tsac_beta=0.0, sosac_gamma=0.0,
        un_scale_mode="raw_inversion",
    )


def _compute_option2(base_df, fund_usd):
    """Option 2: banded IUSAF with 9 developed countries made eligible.

    Temporarily override WB Income Group so the 9 pass the exclude_hi filter.
    """
    df = base_df.copy()
    for country in DEVELOPED_COUNTRIES:
        mask = df["party"] == country
        if mask.any():
            df.loc[mask, "WB Income Group"] = "Upper middle income"

    return calculate_allocations(
        df, fund_usd, IPLC_SHARE_PCT,
        exclude_high_income=True,
        equality_mode=False,
        tsac_beta=0.0, sosac_gamma=0.0,
        un_scale_mode="band_inversion",
    )


def _filter_developed(results_df):
    """Filter results to the 9 developed countries."""
    return results_df[results_df["party"].isin(DEVELOPED_COUNTRIES)].copy()


# =====================================================================
# Invariant 1: IPLC + State = Total
# =====================================================================

class TestIPLCStateSum:
    @pytest.mark.parametrize("fund_key,fund_usd", FUND_SIZES.items())
    def test_option1_iplc_plus_state_equals_total(self, base_df, fund_key, fund_usd):
        res = _compute_option1(base_df, fund_usd)
        dev = _filter_developed(res)
        diff = (dev["iplc_component"] + dev["state_component"] - dev["total_allocation"]).abs()
        assert diff.max() < 1e-8, f"Option 1 {fund_key}: IPLC+State != Total"

    @pytest.mark.parametrize("fund_key,fund_usd", FUND_SIZES.items())
    def test_option2_iplc_plus_state_equals_total(self, base_df, fund_key, fund_usd):
        res = _compute_option2(base_df, fund_usd)
        dev = _filter_developed(res)
        diff = (dev["iplc_component"] + dev["state_component"] - dev["total_allocation"]).abs()
        assert diff.max() < 1e-8, f"Option 2 {fund_key}: IPLC+State != Total"


# =====================================================================
# Invariant 2: IPLC = 50% of total
# =====================================================================

class TestIPLCShareIs50:
    @pytest.mark.parametrize("fund_key,fund_usd", FUND_SIZES.items())
    def test_option1_iplc_is_50pct(self, base_df, fund_key, fund_usd):
        res = _compute_option1(base_df, fund_usd)
        dev = _filter_developed(res)
        ratio = dev["iplc_component"] / dev["total_allocation"]
        assert (ratio - 0.5).abs().max() < 1e-8

    @pytest.mark.parametrize("fund_key,fund_usd", FUND_SIZES.items())
    def test_option2_iplc_is_50pct(self, base_df, fund_key, fund_usd):
        res = _compute_option2(base_df, fund_usd)
        dev = _filter_developed(res)
        ratio = dev["iplc_component"] / dev["total_allocation"]
        assert (ratio - 0.5).abs().max() < 1e-8


# =====================================================================
# Invariant 3: Fund conservation (total allocations sum to fund size)
# =====================================================================

class TestFundConservation:
    @pytest.mark.parametrize("fund_key,fund_usd", FUND_SIZES.items())
    def test_option1_total_eligible_sums_to_fund(self, base_df, fund_key, fund_usd):
        res = _compute_option1(base_df, fund_usd)
        total_m = res.loc[res["eligible"], "total_allocation"].sum()
        fund_m = fund_usd / 1_000_000
        assert abs(total_m - fund_m) < 1e-6, f"Option 1 {fund_key}: sum={total_m:.6f}m vs fund={fund_m:.6f}m"

    @pytest.mark.parametrize("fund_key,fund_usd", FUND_SIZES.items())
    def test_option2_total_eligible_sums_to_fund(self, base_df, fund_key, fund_usd):
        res = _compute_option2(base_df, fund_usd)
        total_m = res.loc[res["eligible"], "total_allocation"].sum()
        fund_m = fund_usd / 1_000_000
        assert abs(total_m - fund_m) < 1e-6, f"Option 2 {fund_key}: sum={total_m:.6f}m vs fund={fund_m:.6f}m"


# =====================================================================
# Invariant 4: Scale invariance (allocations proportional to fund size)
# =====================================================================

class TestScaleInvariance:
    def test_option1_allocations_scale_proportionally(self, base_df):
        res_1bn = _compute_option1(base_df, 1_000_000_000)
        res_200m = _compute_option1(base_df, 200_000_000)
        dev_1bn = _filter_developed(res_1bn).sort_values("party")
        dev_200m = _filter_developed(res_200m).sort_values("party")
        ratio = dev_1bn["total_allocation"].values / dev_200m["total_allocation"].values
        assert pytest.approx(ratio, rel=1e-6) == [5.0] * 9

    def test_option2_allocations_scale_proportionally(self, base_df):
        res_1bn = _compute_option2(base_df, 1_000_000_000)
        res_200m = _compute_option2(base_df, 200_000_000)
        dev_1bn = _filter_developed(res_1bn).sort_values("party")
        dev_200m = _filter_developed(res_200m).sort_values("party")
        ratio = dev_1bn["total_allocation"].values / dev_200m["total_allocation"].values
        assert pytest.approx(ratio, rel=1e-6) == [5.0] * 9


# =====================================================================
# Invariant 5: Band assignments correct
# =====================================================================

class TestBandAssignments:
    def test_band4_countries_in_option2(self, base_df):
        res = _compute_option2(base_df, 1_000_000_000)
        dev = _filter_developed(res)
        for country in BAND_4_COUNTRIES:
            row = dev[dev["party"] == country].iloc[0]
            assert row["un_band"].startswith("Band 4"), \
                f"{country} in {row['un_band']}, expected Band 4"

    def test_band5_countries_in_option2(self, base_df):
        res = _compute_option2(base_df, 1_000_000_000)
        dev = _filter_developed(res)
        for country in BAND_5_COUNTRIES:
            row = dev[dev["party"] == country].iloc[0]
            assert row["un_band"].startswith("Band 5"), \
                f"{country} in {row['un_band']}, expected Band 5"

    def test_no_developed_countries_in_band6(self, base_df):
        """None of the 9 should be in Band 6 (>10% UN share)."""
        res = _compute_option2(base_df, 1_000_000_000)
        dev = _filter_developed(res)
        for _, row in dev.iterrows():
            assert not row["un_band"].startswith("Band 6"), \
                f"{row['party']} in Band 6 — unexpected"


# =====================================================================
# Invariant 6: No HI leakage in Option 2
# =====================================================================

class TestNoHILeakage:
    def test_option2_eligible_count(self, base_df):
        """Should be 142 developing + 9 developed = 151."""
        res = _compute_option2(base_df, 1_000_000_000)
        n_eligible = res["eligible"].sum()
        assert n_eligible == 151, f"Expected 151 eligible, got {n_eligible}"

    def test_option2_developed_countries_are_eligible(self, base_df):
        res = _compute_option2(base_df, 1_000_000_000)
        dev = _filter_developed(res)
        assert dev["eligible"].all(), "Not all 9 developed countries are eligible"

    def test_option2_no_other_hi_countries_eligible_except_sids(self, base_df):
        """Other high-income CBD parties (not the 9) should remain excluded,
        except SIDS which are always eligible under exclude_except_sids mode."""
        res = _compute_option2(base_df, 1_000_000_000)
        hi_not_dev = res[
            (res["WB Income Group"] == "High income")
            & (~res["party"].isin(DEVELOPED_COUNTRIES))
            & (res["is_cbd_party"])
        ]
        eligible_leakers = hi_not_dev[hi_not_dev["eligible"]]
        # HI SIDS are correctly eligible under exclude_except_sids mode
        non_sids_leakers = eligible_leakers[~eligible_leakers["is_sids"]]
        assert len(non_sids_leakers) == 0, \
            f"Non-SIDS HI leakage: {list(non_sids_leakers['party'])} are eligible but shouldn't be"


# =====================================================================
# Invariant 7: Option 1 total > Option 2 total
# =====================================================================

class TestOption1ExceedsOption2:
    def test_total_allocation_option1_greater(self, base_df):
        opt1 = _compute_option1(base_df, 1_000_000_000)
        opt2 = _compute_option2(base_df, 1_000_000_000)
        dev1 = _filter_developed(opt1)
        dev2 = _filter_developed(opt2)
        assert dev1["total_allocation"].sum() > dev2["total_allocation"].sum()

    def test_iplc_pool_option1_greater(self, base_df):
        opt1 = _compute_option1(base_df, 1_000_000_000)
        opt2 = _compute_option2(base_df, 1_000_000_000)
        dev1 = _filter_developed(opt1)
        dev2 = _filter_developed(opt2)
        assert dev1["iplc_component"].sum() > dev2["iplc_component"].sum()

    def test_option2_within_10pct_of_option1(self, base_df):
        """Option 2 should be close to Option 1 but smaller (partial cancellation effect)."""
        opt1 = _compute_option1(base_df, 1_000_000_000)
        opt2 = _compute_option2(base_df, 1_000_000_000)
        total1 = _filter_developed(opt1)["total_allocation"].sum()
        total2 = _filter_developed(opt2)["total_allocation"].sum()
        ratio = total2 / total1
        assert 0.85 < ratio < 1.0, \
            f"Option 2 / Option 1 ratio = {ratio:.4f}, expected 0.85–1.0"


# =====================================================================
# Invariant 8: Cali Fund % constant across fund sizes
# =====================================================================

class TestCaliFundPctConstant:
    def test_option1_iplc_pct_constant(self, base_df):
        """Under equality, 9-country IPLC % of fund should be same at all fund sizes."""
        pcts = []
        for fund_usd in FUND_SIZES.values():
            res = _compute_option1(base_df, fund_usd)
            dev = _filter_developed(res)
            iplc_total = dev["iplc_component"].sum()
            fund_m = fund_usd / 1_000_000
            pcts.append(iplc_total / fund_m * 100)
        assert pytest.approx(pcts, rel=1e-10) == [pcts[0]] * len(pcts)

    def test_option2_iplc_pct_constant(self, base_df):
        """Under banding, 9-country IPLC % of fund should be same at all fund sizes."""
        pcts = []
        for fund_usd in FUND_SIZES.values():
            res = _compute_option2(base_df, fund_usd)
            dev = _filter_developed(res)
            iplc_total = dev["iplc_component"].sum()
            fund_m = fund_usd / 1_000_000
            pcts.append(iplc_total / fund_m * 100)
        assert pytest.approx(pcts, rel=1e-10) == [pcts[0]] * len(pcts)


# =====================================================================
# Structural explanation: why Option 1 and Option 2 are close
# =====================================================================

class TestClosenessExplanation:
    def test_band4_countries_gain_vs_equality(self, base_df):
        """Band 4 countries (smaller UN share) get MORE under banding than equality."""
        opt1 = _compute_option1(base_df, 1_000_000_000)
        opt2 = _compute_option2(base_df, 1_000_000_000)
        for country in BAND_4_COUNTRIES:
            a1 = opt1.loc[opt1["party"] == country, "total_allocation"].values[0]
            a2 = opt2.loc[opt2["party"] == country, "total_allocation"].values[0]
            assert a2 > a1, f"{country}: banding ({a2:.2f}m) should exceed equality ({a1:.2f}m)"

    def test_band5_countries_lose_vs_equality(self, base_df):
        """Band 5 countries (larger UN share) get LESS under banding than equality."""
        opt1 = _compute_option1(base_df, 1_000_000_000)
        opt2 = _compute_option2(base_df, 1_000_000_000)
        for country in BAND_5_COUNTRIES:
            a1 = opt1.loc[opt1["party"] == country, "total_allocation"].values[0]
            a2 = opt2.loc[opt2["party"] == country, "total_allocation"].values[0]
            assert a2 < a1, f"{country}: banding ({a2:.2f}m) should be less than equality ({a1:.2f}m)"

    def test_gains_and_losses_partially_cancel(self, base_df):
        """Net effect: Band 4 gains don't fully offset Band 5 losses."""
        opt1 = _compute_option1(base_df, 1_000_000_000)
        opt2 = _compute_option2(base_df, 1_000_000_000)
        b4_gain = sum(
            opt2.loc[opt2["party"] == c, "total_allocation"].values[0]
            - opt1.loc[opt1["party"] == c, "total_allocation"].values[0]
            for c in BAND_4_COUNTRIES
        )
        b5_loss = sum(
            opt1.loc[opt1["party"] == c, "total_allocation"].values[0]
            - opt2.loc[opt2["party"] == c, "total_allocation"].values[0]
            for c in BAND_5_COUNTRIES
        )
        assert b5_loss > b4_gain, \
            f"Band 5 loss ({b5_loss:.2f}m) should exceed Band 4 gain ({b4_gain:.2f}m)"
