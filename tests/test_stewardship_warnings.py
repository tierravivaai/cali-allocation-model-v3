import pandas as pd

from cali_model.calculator import get_stewardship_blend_feedback, get_outcome_warning_feedback


def test_stewardship_feedback_thresholds():
    none = get_stewardship_blend_feedback(0.0, 0.0)
    assert none["warning_level"] == "none"
    assert none["status_text"] == "Current blend: no stewardship recognition."

    low = get_stewardship_blend_feedback(0.05, 0.03)
    assert low["warning_level"] == "none"
    assert low["status_text"] == "Current blend: modest stewardship recognition."

    mild = get_stewardship_blend_feedback(0.12, 0.04)
    assert mild["warning_level"] == "mild"
    assert "becoming strong" in mild["warning_text"]

    strong = get_stewardship_blend_feedback(0.15, 0.06)
    assert strong["warning_level"] == "strong"
    assert "may be overriding the IUSAF base" in strong["warning_text"]


def test_outcome_warning_condition_a_only():
    # n=10, equal share=100m, 70% below equality but median at 95% of equality
    df = pd.DataFrame({
        "eligible": [True] * 10,
        "total_allocation": [95.0] * 7 + [111.6666666667] * 3,
    })

    feedback = get_outcome_warning_feedback(df, 1_000_000_000)
    assert feedback is not None
    assert "more than 60% of eligible countries are below the equality reference" in feedback["message"]
    assert "median eligible country is receiving less than 90%" not in feedback["message"]


def test_outcome_warning_condition_b_only():
    # n=10, equal share=100m, exactly 60% below equality (not >60), median below 90%
    df = pd.DataFrame({
        "eligible": [True] * 10,
        "total_allocation": [89.0] * 6 + [116.5] * 4,
    })

    feedback = get_outcome_warning_feedback(df, 1_000_000_000)
    assert feedback is not None
    assert "median eligible country is receiving less than 90%" in feedback["message"]
    assert "more than 60% of eligible countries are below the equality reference" not in feedback["message"]


def test_outcome_warning_combined():
    # n=10, equal share=100m, both conditions true
    df = pd.DataFrame({
        "eligible": [True] * 10,
        "total_allocation": [80.0] * 7 + [146.6666666667] * 3,
    })

    feedback = get_outcome_warning_feedback(df, 1_000_000_000)
    assert feedback is not None
    assert "more than 60% of eligible countries are below the equality reference" in feedback["message"]
    assert "median eligible country is receiving less than 90%" in feedback["message"]
