"""Tests for the CM009 Benchmark Manipulation risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm009_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm009_exposure_score,
    score_fixing_window_concentration, score_order_timing_precision,
    score_price_distortion, score_repeat_pattern,
)

CANON = {
    "fixing_window_concentration": score_fixing_window_concentration(22525000, 26500000),
    "price_distortion": score_price_distortion(1.44, 0.18),
    "order_timing_precision": score_order_timing_precision(2),
    "repeat_pattern": score_repeat_pattern(8),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"fixing_window_concentration": 0.35, "price_distortion": 0.25,
                                  "order_timing_precision": 0.20, "repeat_pattern": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm009_exposure_score({"fixing_window_concentration": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm009_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_fixing_window_concentration_bands():
    assert score_fixing_window_concentration(5000, 100000) == "Low"       # r=0.05
    assert score_fixing_window_concentration(20000, 100000) == "Medium"   # r=0.20
    assert score_fixing_window_concentration(45000, 100000) == "High"     # r=0.45
    assert score_fixing_window_concentration(65000, 100000) == "Critical"  # r=0.65


def test_fixing_window_concentration_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_fixing_window_concentration(None, 100000)
    with pytest.raises(RiskModelError):
        score_fixing_window_concentration(5000, None)


def test_fixing_window_concentration_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_fixing_window_concentration(1000, 0)


def test_price_distortion_bands():
    assert score_price_distortion(1.0, 1.0) == "Low"      # r=1.0
    assert score_price_distortion(2.0, 1.0) == "Medium"   # r=2.0
    assert score_price_distortion(5.0, 1.0) == "High"     # r=5.0
    assert score_price_distortion(8.0, 1.0) == "Critical"  # r=8.0


def test_price_distortion_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_price_distortion(None, 1.0)
    with pytest.raises(RiskModelError):
        score_price_distortion(1.0, None)


def test_price_distortion_rejects_zero_normal():
    with pytest.raises(RiskModelError):
        score_price_distortion(1.0, 0)


def test_order_timing_precision_bands():
    assert score_order_timing_precision(90) == "Low"
    assert score_order_timing_precision(40) == "Medium"
    assert score_order_timing_precision(15) == "High"
    assert score_order_timing_precision(3) == "Critical"


def test_order_timing_precision_is_required():
    with pytest.raises(RiskModelError):
        score_order_timing_precision(None)


def test_repeat_pattern_bands():
    assert score_repeat_pattern(1) == "Low"
    assert score_repeat_pattern(2) == "Medium"
    assert score_repeat_pattern(4) == "High"
    assert score_repeat_pattern(7) == "Critical"


def test_repeat_pattern_is_required():
    with pytest.raises(RiskModelError):
        score_repeat_pattern(None)


def test_rounding_is_half_up():
    bands = {"fixing_window_concentration": "Critical", "price_distortion": "High",
             "order_timing_precision": "Medium", "repeat_pattern": "Low"}
    score, _b, w = cm009_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
