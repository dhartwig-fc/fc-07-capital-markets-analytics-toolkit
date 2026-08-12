"""Tests for the CM003 Spoofing risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm003_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm003_exposure_score,
    score_cancellation_speed, score_non_bona_fide_order_ratio,
    score_opposite_side_execution, score_order_book_imbalance_created,
)

CANON = {
    "non_bona_fide_order_ratio": score_non_bona_fide_order_ratio(2181600, 2400000),
    "cancellation_speed": score_cancellation_speed(0.6),
    "order_book_imbalance_created": score_order_book_imbalance_created(7200, 1755),
    "opposite_side_execution": score_opposite_side_execution(1917630, 2181600),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"non_bona_fide_order_ratio": 0.35, "cancellation_speed": 0.25,
                                  "order_book_imbalance_created": 0.20, "opposite_side_execution": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm003_exposure_score({"non_bona_fide_order_ratio": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm003_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_non_bona_fide_order_ratio_bands():
    assert score_non_bona_fide_order_ratio(5000, 100000) == "Low"       # r=0.05
    assert score_non_bona_fide_order_ratio(20000, 100000) == "Medium"   # r=0.20
    assert score_non_bona_fide_order_ratio(45000, 100000) == "High"     # r=0.45
    assert score_non_bona_fide_order_ratio(65000, 100000) == "Critical"  # r=0.65


def test_non_bona_fide_order_ratio_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_non_bona_fide_order_ratio(None, 100000)
    with pytest.raises(RiskModelError):
        score_non_bona_fide_order_ratio(5000, None)


def test_non_bona_fide_order_ratio_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_non_bona_fide_order_ratio(1000, 0)


def test_cancellation_speed_bands():
    assert score_cancellation_speed(30) == "Low"
    assert score_cancellation_speed(10) == "Medium"
    assert score_cancellation_speed(4) == "High"
    assert score_cancellation_speed(1) == "Critical"


def test_cancellation_speed_is_required():
    with pytest.raises(RiskModelError):
        score_cancellation_speed(None)


def test_order_book_imbalance_created_bands():
    assert score_order_book_imbalance_created(500, 9500) == "Low"       # r=0.05
    assert score_order_book_imbalance_created(2000, 8000) == "Medium"   # r=0.20
    assert score_order_book_imbalance_created(4500, 5500) == "High"     # r=0.45
    assert score_order_book_imbalance_created(6500, 3500) == "Critical"  # r=0.65


def test_order_book_imbalance_created_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_order_book_imbalance_created(None, 8000)
    with pytest.raises(RiskModelError):
        score_order_book_imbalance_created(2000, None)


def test_order_book_imbalance_created_rejects_zero_total_depth():
    with pytest.raises(RiskModelError):
        score_order_book_imbalance_created(0, 0)


def test_opposite_side_execution_bands():
    assert score_opposite_side_execution(1000, 10000) == "Low"      # r=0.10
    assert score_opposite_side_execution(3500, 10000) == "Medium"   # r=0.35
    assert score_opposite_side_execution(6500, 10000) == "High"     # r=0.65
    assert score_opposite_side_execution(9000, 10000) == "Critical"  # r=0.90


def test_opposite_side_execution_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_opposite_side_execution(None, 10000)
    with pytest.raises(RiskModelError):
        score_opposite_side_execution(1000, None)


def test_opposite_side_execution_rejects_zero_spoof_order_value():
    with pytest.raises(RiskModelError):
        score_opposite_side_execution(1000, 0)


def test_rounding_is_half_up():
    bands = {"non_bona_fide_order_ratio": "Critical", "cancellation_speed": "High",
             "order_book_imbalance_created": "Medium", "opposite_side_execution": "Low"}
    score, _b, w = cm003_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
