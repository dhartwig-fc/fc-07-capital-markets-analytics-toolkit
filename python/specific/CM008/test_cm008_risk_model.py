"""Tests for the CM008 Cross Market Abuse risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm008_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm008_exposure_score,
    score_cross_venue_position_correlation, score_price_impact_transfer,
    score_timing_synchronization, score_venue_count,
)

CANON = {
    "cross_venue_position_correlation": score_cross_venue_position_correlation(97),
    "venue_count": score_venue_count(6),
    "price_impact_transfer": score_price_impact_transfer(0.85),
    "timing_synchronization": score_timing_synchronization(2),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"cross_venue_position_correlation": 0.35, "venue_count": 0.25,
                                  "price_impact_transfer": 0.20, "timing_synchronization": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm008_exposure_score({"cross_venue_position_correlation": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm008_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_cross_venue_position_correlation_bands():
    assert score_cross_venue_position_correlation(20) == "Low"
    assert score_cross_venue_position_correlation(55) == "Medium"
    assert score_cross_venue_position_correlation(78) == "High"
    assert score_cross_venue_position_correlation(93) == "Critical"


def test_cross_venue_position_correlation_is_required():
    with pytest.raises(RiskModelError):
        score_cross_venue_position_correlation(None)


def test_venue_count_bands():
    assert score_venue_count(1) == "Low"
    assert score_venue_count(2) == "Medium"
    assert score_venue_count(3) == "High"
    assert score_venue_count(4) == "High"
    assert score_venue_count(5) == "Critical"


def test_venue_count_is_required():
    with pytest.raises(RiskModelError):
        score_venue_count(None)


def test_price_impact_transfer_bands():
    assert score_price_impact_transfer(0.05) == "Low"
    assert score_price_impact_transfer(0.20) == "Medium"
    assert score_price_impact_transfer(0.45) == "High"
    assert score_price_impact_transfer(0.75) == "Critical"


def test_price_impact_transfer_is_required():
    with pytest.raises(RiskModelError):
        score_price_impact_transfer(None)


def test_timing_synchronization_bands():
    assert score_timing_synchronization(300) == "Low"
    assert score_timing_synchronization(60) == "Medium"
    assert score_timing_synchronization(20) == "High"
    assert score_timing_synchronization(3) == "Critical"


def test_timing_synchronization_is_required():
    with pytest.raises(RiskModelError):
        score_timing_synchronization(None)


def test_rounding_is_half_up():
    bands = {"cross_venue_position_correlation": "Critical", "venue_count": "High",
             "price_impact_transfer": "Medium", "timing_synchronization": "Low"}
    score, _b, w = cm008_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
