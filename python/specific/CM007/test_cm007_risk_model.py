"""Tests for the CM007 Pump and Dump risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm007_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm007_exposure_score,
    score_accumulation_concentration, score_distribution_into_retail,
    score_price_inflation, score_promotional_coordination,
)

CANON = {
    "accumulation_concentration": score_accumulation_concentration(68),
    "promotional_coordination": score_promotional_coordination(14),
    "price_inflation": score_price_inflation(3.57, 0.85),
    "distribution_into_retail": score_distribution_into_retail(315000, 350000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"accumulation_concentration": 0.35, "promotional_coordination": 0.25,
                                  "price_inflation": 0.20, "distribution_into_retail": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm007_exposure_score({"accumulation_concentration": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm007_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_accumulation_concentration_bands():
    assert score_accumulation_concentration(5) == "Low"        # 5
    assert score_accumulation_concentration(20) == "Medium"    # 20
    assert score_accumulation_concentration(40) == "High"      # 40
    assert score_accumulation_concentration(60) == "Critical"  # 60


def test_accumulation_concentration_is_required():
    with pytest.raises(RiskModelError):
        score_accumulation_concentration(None)


def test_promotional_coordination_bands():
    assert score_promotional_coordination(1) == "Low"
    assert score_promotional_coordination(4) == "Medium"
    assert score_promotional_coordination(7) == "High"
    assert score_promotional_coordination(11) == "Critical"


def test_promotional_coordination_is_required():
    with pytest.raises(RiskModelError):
        score_promotional_coordination(None)


def test_price_inflation_bands():
    assert score_price_inflation(1.15, 1.00) == "Low"       # r=1.15
    assert score_price_inflation(1.60, 1.00) == "Medium"    # r=1.60
    assert score_price_inflation(2.40, 1.00) == "High"      # r=2.40
    assert score_price_inflation(4.00, 1.00) == "Critical"  # r=4.00


def test_price_inflation_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_price_inflation(None, 1.00)
    with pytest.raises(RiskModelError):
        score_price_inflation(1.50, None)


def test_price_inflation_rejects_zero_baseline():
    with pytest.raises(RiskModelError):
        score_price_inflation(1.50, 0)


def test_distribution_into_retail_bands():
    assert score_distribution_into_retail(1000, 10000) == "Low"       # r=0.10
    assert score_distribution_into_retail(3500, 10000) == "Medium"    # r=0.35
    assert score_distribution_into_retail(6500, 10000) == "High"      # r=0.65
    assert score_distribution_into_retail(9000, 10000) == "Critical"  # r=0.90


def test_distribution_into_retail_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_distribution_into_retail(None, 10000)
    with pytest.raises(RiskModelError):
        score_distribution_into_retail(1000, None)


def test_distribution_into_retail_rejects_zero_total_position():
    with pytest.raises(RiskModelError):
        score_distribution_into_retail(1000, 0)


def test_rounding_is_half_up():
    bands = {"accumulation_concentration": "Critical", "promotional_coordination": "High",
             "price_inflation": "Medium", "distribution_into_retail": "Low"}
    score, _b, w = cm007_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
