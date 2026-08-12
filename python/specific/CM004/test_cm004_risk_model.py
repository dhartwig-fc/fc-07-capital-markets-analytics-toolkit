"""Tests for the CM004 Layering risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm004_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm004_exposure_score,
    score_book_imbalance_created, score_order_to_trade_ratio,
    score_reversal_speed, score_staggered_order_levels,
)

CANON = {
    "staggered_order_levels": score_staggered_order_levels(10),
    "order_to_trade_ratio": score_order_to_trade_ratio(300, 5),
    "book_imbalance_created": score_book_imbalance_created(0.75),
    "reversal_speed": score_reversal_speed(3),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"staggered_order_levels": 0.35, "order_to_trade_ratio": 0.25,
                                  "book_imbalance_created": 0.20, "reversal_speed": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm004_exposure_score({"staggered_order_levels": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm004_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_staggered_order_levels_bands():
    assert score_staggered_order_levels(1) == "Low"
    assert score_staggered_order_levels(4) == "Medium"
    assert score_staggered_order_levels(6) == "High"
    assert score_staggered_order_levels(11) == "Critical"


def test_staggered_order_levels_is_required():
    with pytest.raises(RiskModelError):
        score_staggered_order_levels(None)


def test_order_to_trade_ratio_bands():
    assert score_order_to_trade_ratio(6, 3) == "Low"        # r=2
    assert score_order_to_trade_ratio(80, 8) == "Medium"    # r=10
    assert score_order_to_trade_ratio(200, 10) == "High"    # r=20
    assert score_order_to_trade_ratio(300, 5) == "Critical"  # r=60


def test_order_to_trade_ratio_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_order_to_trade_ratio(None, 5)
    with pytest.raises(RiskModelError):
        score_order_to_trade_ratio(20, None)


def test_order_to_trade_ratio_rejects_zero_executed():
    with pytest.raises(RiskModelError):
        score_order_to_trade_ratio(20, 0)


def test_book_imbalance_created_bands():
    assert score_book_imbalance_created(0.05) == "Low"
    assert score_book_imbalance_created(0.20) == "Medium"
    assert score_book_imbalance_created(0.45) == "High"
    assert score_book_imbalance_created(0.80) == "Critical"


def test_book_imbalance_created_is_required():
    with pytest.raises(RiskModelError):
        score_book_imbalance_created(None)


def test_reversal_speed_bands():
    assert score_reversal_speed(100) == "Low"
    assert score_reversal_speed(40) == "Medium"
    assert score_reversal_speed(12) == "High"
    assert score_reversal_speed(3) == "Critical"


def test_reversal_speed_is_required():
    with pytest.raises(RiskModelError):
        score_reversal_speed(None)


def test_rounding_is_half_up():
    bands = {"staggered_order_levels": "Critical", "order_to_trade_ratio": "High",
             "book_imbalance_created": "Medium", "reversal_speed": "Low"}
    score, _b, w = cm004_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
