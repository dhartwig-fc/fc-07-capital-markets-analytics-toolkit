"""Tests for the CM006 Front Running risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm006_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm006_exposure_score,
    score_client_order_knowledge_linkage, score_position_correlation,
    score_profit_capture, score_timing_ahead_of_client_order,
)

CANON = {
    "timing_ahead_of_client_order": score_timing_ahead_of_client_order(1),
    "position_correlation": score_position_correlation(96),
    "profit_capture": score_profit_capture(2184000, 2400000),
    "client_order_knowledge_linkage": score_client_order_knowledge_linkage(13),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"timing_ahead_of_client_order": 0.35, "position_correlation": 0.25,
                                  "profit_capture": 0.20, "client_order_knowledge_linkage": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm006_exposure_score({"timing_ahead_of_client_order": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm006_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_timing_ahead_of_client_order_bands():
    assert score_timing_ahead_of_client_order(200) == "Low"
    assert score_timing_ahead_of_client_order(80) == "Medium"
    assert score_timing_ahead_of_client_order(20) == "High"
    assert score_timing_ahead_of_client_order(3) == "Critical"


def test_timing_ahead_of_client_order_is_required():
    with pytest.raises(RiskModelError):
        score_timing_ahead_of_client_order(None)


def test_position_correlation_bands():
    assert score_position_correlation(20) == "Low"
    assert score_position_correlation(55) == "Medium"
    assert score_position_correlation(75) == "High"
    assert score_position_correlation(92) == "Critical"


def test_position_correlation_is_required():
    with pytest.raises(RiskModelError):
        score_position_correlation(None)


def test_profit_capture_bands():
    assert score_profit_capture(1000, 10000) == "Low"      # r=0.10
    assert score_profit_capture(3500, 10000) == "Medium"   # r=0.35
    assert score_profit_capture(6500, 10000) == "High"     # r=0.65
    assert score_profit_capture(9000, 10000) == "Critical"  # r=0.90


def test_profit_capture_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_profit_capture(None, 10000)
    with pytest.raises(RiskModelError):
        score_profit_capture(1000, None)


def test_profit_capture_rejects_zero_position_value():
    with pytest.raises(RiskModelError):
        score_profit_capture(1000, 0)


def test_client_order_knowledge_linkage_bands():
    assert score_client_order_knowledge_linkage(1) == "Low"
    assert score_client_order_knowledge_linkage(4) == "Medium"
    assert score_client_order_knowledge_linkage(7) == "High"
    assert score_client_order_knowledge_linkage(11) == "Critical"


def test_client_order_knowledge_linkage_is_required():
    with pytest.raises(RiskModelError):
        score_client_order_knowledge_linkage(None)


def test_rounding_is_half_up():
    bands = {"timing_ahead_of_client_order": "Critical", "position_correlation": "High",
             "profit_capture": "Medium", "client_order_knowledge_linkage": "Low"}
    score, _b, w = cm006_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
