"""TT-CM003 (night 9, wave A): CM003 Spoofing tested against its DOCTRINE.

Oracle: typologies/CM003_Spoofing.md ("Exposure Scoring Framework", "Component
Banding Rules", "Classification", the ACC019 worked example) and the signed-off
expected-outcome sheet SIT Expected Outcomes/CM003.md (2026-10-21). Every expected
value below is hand-worked from those, never pasted from an engine run. Inputs
are CONSTRUCTED here; no sample-data file is read and no sample entity name is
asserted.

Checks 2 (boundaries at every doctrine threshold) and 4 (a positive and a
near-miss per detection rule). The engine is loaded as fc-10 loads it: the
scenario file by path.
"""
from __future__ import annotations

import itertools
import math
import sys
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from cm003_risk_model import (  # noqa: E402
    RiskModelError, band_of, cm003_exposure_score, score_cancellation_speed,
    score_non_bona_fide_order_ratio, score_opposite_side_execution,
    score_order_book_imbalance_created,
)

SCENARIO = BASE_DIR / "scenarios" / "spoofing.py"

# The doctrine's own numbers (CM003_Spoofing.md, Exposure Scoring Framework):
# weights 35/25/20/20 %, band midpoints 15/45/70/90, half-up, boundary at 80.
DOCTRINE_WEIGHTS = {
    "non_bona_fide_order_ratio": Fraction(35, 100),
    "cancellation_speed": Fraction(25, 100),
    "order_book_imbalance_created": Fraction(20, 100),
    "opposite_side_execution": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
DOCTRINE_THRESHOLD = 80


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # Classification: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm003_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries
# Each row: (raw inputs, expected band), at / just below / just above each cut-line.

NBF = [  # r = spoof / total; r < 0.10 Low, < 0.30 Medium, < 0.60 High, else Critical
    ((999, 10000), "Low"), ((1000, 10000), "Medium"), ((1001, 10000), "Medium"),
    ((2999, 10000), "Medium"), ((3000, 10000), "High"), ((3001, 10000), "High"),
    ((5999, 10000), "High"), ((6000, 10000), "Critical"), ((6001, 10000), "Critical"),
]
SPEED = [  # <= 2 Critical, <= 5 High, <= 15 Medium, > 15 Low
    (1.99, "Critical"), (2.0, "Critical"), (2.01, "High"),
    (4.99, "High"), (5.0, "High"), (5.01, "Medium"),
    (14.99, "Medium"), (15.0, "Medium"), (15.01, "Low"),
]
IMBALANCE = [  # r = spoof / (spoof + genuine); same cut-lines as NBF
    ((999, 9001), "Low"), ((1000, 9000), "Medium"), ((1001, 8999), "Medium"),
    ((2999, 7001), "Medium"), ((3000, 7000), "High"), ((3001, 6999), "High"),
    ((5999, 4001), "High"), ((6000, 4000), "Critical"), ((6001, 3999), "Critical"),
]
EXECUTION = [  # r = filled / spoof; < 0.25 Low, < 0.50 Medium, < 0.80 High, else Critical
    ((2499, 10000), "Low"), ((2500, 10000), "Medium"), ((2501, 10000), "Medium"),
    ((4999, 10000), "Medium"), ((5000, 10000), "High"), ((5001, 10000), "High"),
    ((7999, 10000), "High"), ((8000, 10000), "Critical"), ((8001, 10000), "Critical"),
]


@pytest.mark.parametrize("args,band", NBF)
def test_non_bona_fide_order_ratio_boundaries(args, band):
    assert score_non_bona_fide_order_ratio(*args) == band


@pytest.mark.parametrize("seconds,band", SPEED)
def test_cancellation_speed_boundaries(seconds, band):
    assert score_cancellation_speed(seconds) == band


@pytest.mark.parametrize("args,band", IMBALANCE)
def test_order_book_imbalance_boundaries(args, band):
    assert score_order_book_imbalance_created(*args) == band


def test_order_book_imbalance_is_a_share_of_total_depth_not_a_ratio_to_genuine():
    """Doctrine: r = spoof / (spoof + genuine). 3,750 against 6,250 genuine is
    r = 0.375 (High); read as spoof/genuine it would be 0.6 (Critical)."""
    assert score_order_book_imbalance_created(3750, 6250) == "High"


@pytest.mark.parametrize("args,band", EXECUTION)
def test_opposite_side_execution_boundaries(args, band):
    assert score_opposite_side_execution(*args) == band


def test_opposite_side_execution_is_filled_over_spoof_value():
    """Doctrine: r = opposite_side_filled_value / spoof_order_value. 3,000 filled
    against 10,000 spoof is r = 0.30 (Medium); inverted it would be 3.33 (Critical)."""
    assert score_opposite_side_execution(3000, 10000) == "Medium"


def test_boundary_tables_are_non_vacuous():
    for table in (NBF, SPEED, IMBALANCE, EXECUTION):
        assert len(table) == 9 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against the doctrine's weighted midpoint sum in
    EXACT arithmetic, half-up -- including the 32 combinations whose exact total
    ends in .5, where half-up and half-even (or float drift) disagree."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, _ = cm003_exposure_score(bands)
        assert (score, band) == (_doctrine_score(bands), _doctrine_band(_doctrine_score(bands))), combo
    assert halves == 32                                             # non-vacuity: the .5 cases were examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_all_low_background_scores_fifteen():
    """Sheet: Background -- all-Low = 15 (derived)."""
    bands = dict.fromkeys(DOCTRINE_WEIGHTS, "Low")
    assert cm003_exposure_score(bands)[:2] == (15, "Low")


# ---------------------------------------------------------------- check 4: through the callable

def _frames(rows):
    """Constructed orders + a matching broker record per account."""
    orders = pd.DataFrame([{
        "trader_name": "Trader " + r["account_ref"], "instrument": "INSTR-T", "broker_name": "Broker T",
        **r} for r in rows])
    brokers = pd.DataFrame([{"broker_name": "Broker T", "account_ref": r["account_ref"], "venue": "Venue T",
                             "jurisdiction": "UNKNOWN", "relationship": "direct", "prior_alerts": 0}
                            for r in rows])
    return {"orders": orders, "brokers": brokers}


def _row(ref, total, spoof, cancel, spoof_depth, genuine_depth, filled):
    return {"account_ref": ref, "total_order_value": total, "spoof_order_value": spoof,
            "avg_cancel_seconds": cancel, "spoof_side_depth": spoof_depth,
            "genuine_side_depth": genuine_depth, "opposite_side_filled_value": filled}


# The doctrine's worked example (CM003_Spoofing.md, "Example Exposure Score"):
# 2,181,600 of 2,400,000; 0.6 s; 7,200 of 8,955 depth; 1,917,630 filled -> 90 Critical.
WORKED = _row("T-WORKED", 2400000, 2181600, 0.6, 7200, 1755, 1917630)

# Per detection rule: the three OTHER components held Critical, and the rule's own
# input set exactly at the cut-line that keeps the total >= 80 (positive) and one
# unit below it (near-miss). Hand-worked from the doctrine:
#   NBF       High 70*.35 + 72 (=90*.25+90*.2+90*.2) ... 24.5 + 58.5 = 83 alert; Medium 15.75 + 58.5 = 74.25 -> 74
#   speed     High 17.5 + 67.5 (=31.5+18+18) = 85 alert;  Medium 11.25 + 67.5 = 78.75 -> 79
#   imbalance Medium 9 + 72 (=31.5+22.5+18) = 81 alert;   Low 3 + 72 = 75
#   execution Medium 9 + 72 = 81 alert;                   Low 3 + 72 = 75
PER_RULE = {
    "non_bona_fide_order_ratio": (
        _row("T-NBF-POS", 10000, 3000, 1.0, 9000, 1000, 9000), 83, "Critical",
        _row("T-NBF-NM", 10000, 2999, 1.0, 9000, 1000, 9000), 74, "High"),
    "cancellation_speed": (
        _row("T-SPD-POS", 10000, 9000, 5.0, 9000, 1000, 9000), 85, "Critical",
        _row("T-SPD-NM", 10000, 9000, 5.01, 9000, 1000, 9000), 79, "High"),
    "order_book_imbalance_created": (
        _row("T-OBI-POS", 10000, 9000, 1.0, 1000, 9000, 9000), 81, "Critical",
        _row("T-OBI-NM", 10000, 9000, 1.0, 999, 9001, 9000), 75, "High"),
    "opposite_side_execution": (
        _row("T-OSE-POS", 10000, 9000, 1.0, 9000, 1000, 2250), 81, "Critical",
        _row("T-OSE-NM", 10000, 9000, 1.0, 9000, 1000, 2249), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_spoofing(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")


@pytest.mark.parametrize("rule", sorted(PER_RULE))
def test_per_rule_positive_alerts_and_near_miss_does_not(governed, rule):
    pos, pos_score, pos_band, nm, nm_score, nm_band = PER_RULE[rule]
    frames = _frames([pos, nm])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert (scored.loc[pos["account_ref"], "exposure_score"], scored.loc[pos["account_ref"], "exposure_band"]) \
        == (pos_score, pos_band)
    assert (scored.loc[nm["account_ref"], "exposure_score"], scored.loc[nm["account_ref"], "exposure_band"]) \
        == (nm_score, nm_band)
    alerted = list(governed.evaluate_spoofing(**frames)["subject_entity_id"])
    assert alerted == [pos["account_ref"]]                         # the positive, and only it


def test_market_maker_near_miss_does_not_alert(governed):
    """Sheet near-miss: genuine two-sided liquidity provision. A small non-bona-fide
    share (r=0.05 Low), slow cancels (30 s Low), balanced depth (r=0.5 High) and
    fills a fifth of the cancelled value (r=0.2 Low): 5.25+3.75+14+3 = 26 -> Low."""
    frames = _frames([_row("T-MM", 1000000, 50000, 30.0, 5000, 5000, 10000), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-MM", "exposure_score"], scored.loc["T-MM", "exposure_band"]) == (26, "Low")
    assert list(governed.evaluate_spoofing(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_partial_pattern_fast_cancels_alone_does_not_alert(governed):
    """Sheet near-miss: fast cancels without opposite-side execution or depth
    imbalance. NBF Critical (0.9), speed Critical (0.5 s), imbalance Low (0.05),
    execution Low (0.0): 31.5+22.5+3+3 = 60 -> High, below 80."""
    frames = _frames([_row("T-PART", 10000, 9000, 0.5, 500, 9500, 0), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-PART", "exposure_score"], scored.loc["T-PART", "exposure_band"]) == (60, "High")
    assert list(governed.evaluate_spoofing(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_background_slow_normal_order_management_scores_fifteen(governed):
    """Sheet background: normal order management, cancels slower than 15 s -> all Low = 15."""
    frames = _frames([_row("T-BG", 1000000, 10000, 45.0, 100, 9900, 0), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-BG", "exposure_score"], scored.loc["T-BG", "exposure_band"]) == (15, "Low")
    assert list(governed.evaluate_spoofing(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    """Every constructed row together: the alert set is exactly the doctrine's
    >= 80 rows (the 79 near-miss is the closest below the line the bands allow)."""
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_spoofing(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """Doctrine: 'escalate at or above the threshold', 'boundary at 80'. No band
    combination scores exactly 80 (the enumeration above: 79 is followed by 81),
    so the cut-line itself is constructed by fixing the model's score; the
    callable's own filter decides."""
    real = governed.cm003_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm003_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                  # non-vacuity: one row scored
    assert (len(governed.evaluate_spoofing(**frames)) == 1) is alerts


def test_no_band_combination_scores_exactly_eighty():
    """Recorded so the 80 cut-line test above is read correctly: the doctrine's
    own arithmetic cannot land on 80, so an exactly-80 case needs construction."""
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "DEFECT: doctrine 'avg_cancel_seconds REQUIRED' (CM003_Spoofing.md:124) and the model's own "
    "'not measured is not slow to cancel' -- a NaN cancel speed is banded Low, not refused "
    "(cm003_risk_model.py:92-99: _require checks only `is None`)"))
def test_a_nan_cancel_speed_is_refused_not_banded():
    with pytest.raises(RiskModelError):
        score_cancellation_speed(float("nan"))


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "DEFECT: doctrine 'Both amounts REQUIRED' (CM003_Spoofing.md:120) -- a NaN spoof_order_value "
    "is banded Critical, not refused (cm003_risk_model.py:74-85: _require checks only `is None`)"))
def test_a_nan_order_value_is_refused_not_banded():
    with pytest.raises(RiskModelError):
        score_non_bona_fide_order_ratio(float("nan"), 10000)


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "DEFECT: doctrine 'avg_cancel_seconds REQUIRED' (CM003_Spoofing.md:124) -- through the callable "
    "a row whose cancel speed is missing (NaN in the frame) is scored with cancellation_speed Low "
    "instead of refused (spoofing.py:69 -> cm003_risk_model.py:92)"))
def test_the_callable_refuses_a_row_with_no_cancel_speed(governed):
    frames = _frames([_row("T-NOSPEED", 10000, 9000, float("nan"), 9000, 1000, 9000)])
    with pytest.raises(ValueError):
        governed.score_all(**frames)
