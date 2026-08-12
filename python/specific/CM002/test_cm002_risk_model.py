"""Tests for the CM002 Market Manipulation risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm002_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm002_exposure_score,
    score_coordinated_accounts, score_price_impact_ratio,
    score_reversal_after_close, score_volume_concentration,
)

CANON = {
    "price_impact_ratio": score_price_impact_ratio(30.06, 4.0),
    "volume_concentration": score_volume_concentration(67),
    "coordinated_accounts": score_coordinated_accounts(8),
    "reversal_after_close": score_reversal_after_close(28.74, 30.06),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"price_impact_ratio": 0.35, "volume_concentration": 0.25,
                                  "coordinated_accounts": 0.20, "reversal_after_close": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm002_exposure_score({"price_impact_ratio": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm002_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_price_impact_ratio_bands():
    assert score_price_impact_ratio(1.0, 2.0) == "Low"        # r=0.50
    assert score_price_impact_ratio(4.0, 2.0) == "Medium"      # r=2.00
    assert score_price_impact_ratio(9.0, 2.0) == "High"        # r=4.50
    assert score_price_impact_ratio(16.0, 2.0) == "Critical"   # r=8.00


def test_price_impact_ratio_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_price_impact_ratio(None, 2.0)
    with pytest.raises(RiskModelError):
        score_price_impact_ratio(1.0, None)


def test_price_impact_ratio_rejects_zero_normal_volatility():
    with pytest.raises(RiskModelError):
        score_price_impact_ratio(1.0, 0)


def test_volume_concentration_bands():
    assert score_volume_concentration(5) == "Low"
    assert score_volume_concentration(20) == "Medium"
    assert score_volume_concentration(40) == "High"
    assert score_volume_concentration(60) == "Critical"


def test_volume_concentration_is_required():
    with pytest.raises(RiskModelError):
        score_volume_concentration(None)


def test_coordinated_accounts_bands():
    assert score_coordinated_accounts(1) == "Low"
    assert score_coordinated_accounts(2) == "Medium"
    assert score_coordinated_accounts(4) == "High"
    assert score_coordinated_accounts(6) == "Critical"


def test_coordinated_accounts_is_required():
    with pytest.raises(RiskModelError):
        score_coordinated_accounts(None)


def test_reversal_after_close_bands():
    assert score_reversal_after_close(1.0, 10.0) == "Low"       # r=0.10
    assert score_reversal_after_close(3.5, 10.0) == "Medium"    # r=0.35
    assert score_reversal_after_close(6.5, 10.0) == "High"      # r=0.65
    assert score_reversal_after_close(9.0, 10.0) == "Critical"  # r=0.90


def test_reversal_after_close_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_reversal_after_close(None, 10.0)
    with pytest.raises(RiskModelError):
        score_reversal_after_close(1.0, None)


def test_reversal_after_close_rejects_zero_price_move():
    with pytest.raises(RiskModelError):
        score_reversal_after_close(1.0, 0)


def test_rounding_is_half_up():
    bands = {"price_impact_ratio": "Critical", "volume_concentration": "High",
             "coordinated_accounts": "Medium", "reversal_after_close": "Low"}
    score, _b, w = cm002_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
