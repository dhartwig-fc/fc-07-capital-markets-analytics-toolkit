"""Tests for the CM010 Suspicious Order Patterns risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm010_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm010_exposure_score,
    score_cancel_amend_rate, score_momentum_ignition_signal, score_order_size_anomaly,
    score_quote_stuffing_intensity,
)

CANON = {
    "cancel_amend_rate": score_cancel_amend_rate(2720, 3200),
    "quote_stuffing_intensity": score_quote_stuffing_intensity(70),
    "momentum_ignition_signal": score_momentum_ignition_signal(2.40, 0.30),
    "order_size_anomaly": score_order_size_anomaly(4000, 1000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"cancel_amend_rate": 0.35, "quote_stuffing_intensity": 0.25,
                                  "momentum_ignition_signal": 0.20, "order_size_anomaly": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm010_exposure_score({"cancel_amend_rate": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm010_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_cancel_amend_rate_bands():
    assert score_cancel_amend_rate(50, 1000) == "Low"        # r=0.05
    assert score_cancel_amend_rate(200, 1000) == "Medium"    # r=0.20
    assert score_cancel_amend_rate(450, 1000) == "High"      # r=0.45
    assert score_cancel_amend_rate(650, 1000) == "Critical"  # r=0.65


def test_cancel_amend_rate_requires_both_counts():
    with pytest.raises(RiskModelError):
        score_cancel_amend_rate(None, 1000)
    with pytest.raises(RiskModelError):
        score_cancel_amend_rate(50, None)


def test_cancel_amend_rate_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_cancel_amend_rate(50, 0)


def test_quote_stuffing_intensity_bands():
    assert score_quote_stuffing_intensity(3) == "Low"
    assert score_quote_stuffing_intensity(10) == "Medium"
    assert score_quote_stuffing_intensity(25) == "High"
    assert score_quote_stuffing_intensity(55) == "Critical"


def test_quote_stuffing_intensity_is_required():
    with pytest.raises(RiskModelError):
        score_quote_stuffing_intensity(None)


def test_momentum_ignition_signal_bands():
    assert score_momentum_ignition_signal(0.40, 0.40) == "Low"      # r=1.0
    assert score_momentum_ignition_signal(0.80, 0.40) == "Medium"   # r=2.0
    assert score_momentum_ignition_signal(1.60, 0.40) == "High"     # r=4.0
    assert score_momentum_ignition_signal(3.20, 0.40) == "Critical"  # r=8.0


def test_momentum_ignition_signal_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_momentum_ignition_signal(None, 0.40)
    with pytest.raises(RiskModelError):
        score_momentum_ignition_signal(0.80, None)


def test_momentum_ignition_signal_rejects_zero_normal():
    with pytest.raises(RiskModelError):
        score_momentum_ignition_signal(0.80, 0)


def test_order_size_anomaly_bands():
    assert score_order_size_anomaly(1100, 1000) == "Low"       # r=1.10
    assert score_order_size_anomaly(1500, 1000) == "Medium"    # r=1.50
    assert score_order_size_anomaly(2200, 1000) == "High"      # r=2.20
    assert score_order_size_anomaly(4000, 1000) == "Critical"  # r=4.00


def test_order_size_anomaly_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_order_size_anomaly(None, 1000)
    with pytest.raises(RiskModelError):
        score_order_size_anomaly(1100, None)


def test_order_size_anomaly_rejects_zero_normal():
    with pytest.raises(RiskModelError):
        score_order_size_anomaly(1100, 0)


def test_rounding_is_half_up():
    bands = {"cancel_amend_rate": "Critical", "quote_stuffing_intensity": "High",
             "momentum_ignition_signal": "Medium", "order_size_anomaly": "Low"}
    score, _b, w = cm010_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
