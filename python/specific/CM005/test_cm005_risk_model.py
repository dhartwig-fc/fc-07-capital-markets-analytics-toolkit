"""Tests for the CM005 Wash Trading risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cm005_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, cm005_exposure_score,
    score_beneficial_ownership_overlap, score_counterparty_concentration,
    score_self_match_ratio, score_volume_inflation,
)

CANON = {
    "self_match_ratio": score_self_match_ratio(450000, 500000),
    "beneficial_ownership_overlap": score_beneficial_ownership_overlap(95),
    "volume_inflation": score_volume_inflation(480000, 150000),
    "counterparty_concentration": score_counterparty_concentration(1),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"self_match_ratio": 0.35, "beneficial_ownership_overlap": 0.25,
                                  "volume_inflation": 0.20, "counterparty_concentration": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        cm005_exposure_score({"self_match_ratio": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = cm005_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_self_match_ratio_bands():
    assert score_self_match_ratio(5000, 100000) == "Low"        # r=0.05
    assert score_self_match_ratio(20000, 100000) == "Medium"    # r=0.20
    assert score_self_match_ratio(45000, 100000) == "High"      # r=0.45
    assert score_self_match_ratio(65000, 100000) == "Critical"  # r=0.65


def test_self_match_ratio_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_self_match_ratio(None, 100000)
    with pytest.raises(RiskModelError):
        score_self_match_ratio(5000, None)


def test_self_match_ratio_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_self_match_ratio(1000, 0)


def test_beneficial_ownership_overlap_bands():
    assert score_beneficial_ownership_overlap(10) == "Low"
    assert score_beneficial_ownership_overlap(35) == "Medium"
    assert score_beneficial_ownership_overlap(65) == "High"
    assert score_beneficial_ownership_overlap(90) == "Critical"


def test_beneficial_ownership_overlap_is_required():
    with pytest.raises(RiskModelError):
        score_beneficial_ownership_overlap(None)


def test_volume_inflation_bands():
    assert score_volume_inflation(11000, 10000) == "Low"       # r=1.10
    assert score_volume_inflation(13500, 10000) == "Medium"    # r=1.35
    assert score_volume_inflation(20000, 10000) == "High"      # r=2.00
    assert score_volume_inflation(30000, 10000) == "Critical"  # r=3.00


def test_volume_inflation_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_volume_inflation(None, 10000)
    with pytest.raises(RiskModelError):
        score_volume_inflation(11000, None)


def test_volume_inflation_rejects_zero_genuine():
    with pytest.raises(RiskModelError):
        score_volume_inflation(1000, 0)


def test_counterparty_concentration_bands_are_inverted():
    assert score_counterparty_concentration(8) == "Low"        # more counterparties = safer
    assert score_counterparty_concentration(3) == "Medium"
    assert score_counterparty_concentration(2) == "High"
    assert score_counterparty_concentration(1) == "Critical"   # fewer counterparties = worse


def test_counterparty_concentration_is_required():
    with pytest.raises(RiskModelError):
        score_counterparty_concentration(None)


def test_rounding_is_half_up():
    bands = {"self_match_ratio": "Critical", "beneficial_ownership_overlap": "High",
             "volume_inflation": "Medium", "counterparty_concentration": "Low"}
    score, _b, w = cm005_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
