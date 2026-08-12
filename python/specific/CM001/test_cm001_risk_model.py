"""Tests for the CM001 Insider Trading risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm001_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm001_exposure_score,
    score_information_access_linkage, score_pre_event_position_build,
    score_profit_realisation, score_timing_proximity_to_event,
)

CANON = {
    "pre_event_position_build": score_pre_event_position_build(39600, 60000),
    "timing_proximity_to_event": score_timing_proximity_to_event(0),
    "information_access_linkage": score_information_access_linkage(10),
    "profit_realisation": score_profit_realisation(2090400, 2400000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"pre_event_position_build": 0.35, "timing_proximity_to_event": 0.25,
                                  "information_access_linkage": 0.20, "profit_realisation": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm001_exposure_score({"pre_event_position_build": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm001_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_pre_event_position_build_bands():
    assert score_pre_event_position_build(5000, 100000) == "Low"       # r=0.05
    assert score_pre_event_position_build(20000, 100000) == "Medium"   # r=0.20
    assert score_pre_event_position_build(45000, 100000) == "High"     # r=0.45
    assert score_pre_event_position_build(65000, 100000) == "Critical"  # r=0.65


def test_pre_event_position_build_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_pre_event_position_build(None, 100000)
    with pytest.raises(RiskModelError):
        score_pre_event_position_build(5000, None)


def test_pre_event_position_build_rejects_zero_normal():
    with pytest.raises(RiskModelError):
        score_pre_event_position_build(1000, 0)


def test_timing_proximity_bands():
    assert score_timing_proximity_to_event(10) == "Low"
    assert score_timing_proximity_to_event(5) == "Medium"
    assert score_timing_proximity_to_event(3) == "High"
    assert score_timing_proximity_to_event(1) == "Critical"


def test_timing_proximity_is_required():
    with pytest.raises(RiskModelError):
        score_timing_proximity_to_event(None)


def test_information_access_linkage_bands():
    assert score_information_access_linkage(1) == "Low"
    assert score_information_access_linkage(4) == "Medium"
    assert score_information_access_linkage(7) == "High"
    assert score_information_access_linkage(11) == "Critical"


def test_information_access_linkage_is_required():
    with pytest.raises(RiskModelError):
        score_information_access_linkage(None)


def test_profit_realisation_bands():
    assert score_profit_realisation(1000, 10000) == "Low"      # r=0.10
    assert score_profit_realisation(3500, 10000) == "Medium"   # r=0.35
    assert score_profit_realisation(6500, 10000) == "High"     # r=0.65
    assert score_profit_realisation(9000, 10000) == "Critical"  # r=0.90


def test_profit_realisation_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_profit_realisation(None, 10000)
    with pytest.raises(RiskModelError):
        score_profit_realisation(1000, None)


def test_profit_realisation_rejects_zero_position_value():
    with pytest.raises(RiskModelError):
        score_profit_realisation(1000, 0)


def test_rounding_is_half_up():
    bands = {"pre_event_position_build": "Critical", "timing_proximity_to_event": "High",
             "information_access_linkage": "Medium", "profit_realisation": "Low"}
    score, _b, w = cm001_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
