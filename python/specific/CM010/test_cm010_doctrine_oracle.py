"""TT-CM010 (night 10, wave C): CM010 Suspicious Order Patterns tested against its DOCTRINE.

Oracle: typologies/CM010_Suspicious_Order_Patterns.md -- "Exposure Scoring Framework"
(weights :108-113, midpoints / weighted sum / half-up / boundary at 80 :115), "Component
Banding Rules" (:117-133), the worked example (:137-147), "Classification" (:150),
"Business Logic" step 7 (:162, escalate at or above the threshold) -- and oracle rule R1
(owner, 2026-10-21: the band table governs over the doctrine's Python example, :188-195).
No signed-off expected-outcome sheet exists for CM010. Every expected value below is
hand-worked from the doctrine, never pasted from an engine run. Inputs are CONSTRUCTED
here; no sample-data file is read and no sample entity name is asserted.

Checks 2 (boundaries at every doctrine threshold) and 4 (a positive and a near-miss per
detection rule, each near-miss scored in the SAME evaluate call as an alerting control).
The engine is loaded as fc-10 loads it: the scenario file by path.

Contributions per band (weight x midpoint): cancel/amend rate 35% L 5.25 M 15.75 H 24.5
C 31.5; quote stuffing intensity 25% L 3.75 M 11.25 H 17.5 C 22.5; momentum ignition and
order size anomaly 20% each, L 3 M 9 H 14 C 18.
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

from cm010_risk_model import (  # noqa: E402
    RiskModelError, band_of, cm010_exposure_score, score_cancel_amend_rate,
    score_momentum_ignition_signal, score_order_size_anomaly, score_quote_stuffing_intensity,
)

SCENARIO = BASE_DIR / "scenarios" / "suspicious_order_patterns.py"

# CM010_Suspicious_Order_Patterns.md:108-115
DOCTRINE_WEIGHTS = {
    "cancel_amend_rate": Fraction(35, 100),
    "quote_stuffing_intensity": Fraction(25, 100),
    "momentum_ignition_signal": Fraction(20, 100),
    "order_size_anomaly": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
BAND_COLUMNS = ("cancel_amend_rate_band", "quote_stuffing_intensity_band",
                "momentum_ignition_signal_band", "order_size_anomaly_band")


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # Classification (:150): 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm010_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries

CANCEL = [  # r = cancelled / total: < 0.10 Low, < 0.30 Medium, < 0.60 High, otherwise Critical (:120-121).
    # Integer counts: a correctly-rounded division lands exactly on each line.
    ((0, 1000), "Low"), ((99, 1000), "Low"), ((100, 1000), "Medium"), ((101, 1000), "Medium"),
    ((299, 1000), "Medium"), ((300, 1000), "High"), ((301, 1000), "High"),
    ((599, 1000), "High"), ((600, 1000), "Critical"), ((601, 1000), "Critical"), ((1000, 1000), "Critical"),
]
QUOTE = [  # orders per second: <= 5 Low, <= 15 Medium, <= 40 High, otherwise (> 40) Critical (:124-125).
    # Whole rates only: schema.json types the field "integer"; a fractional rate is a QUESTION.
    (1, "Low"), (5, "Low"), (6, "Medium"), (15, "Medium"), (16, "High"),
    (40, "High"), (41, "Critical"), (70, "Critical"),
]
MOMENTUM = [  # r = burst move / normal move: < 1.5 Low, < 3.0 Medium, < 6.0 High, otherwise Critical (:128-129).
    # Normal move 1.0 (or 0.25/0.5): the on-line ratios are exact in binary.
    ((0.5, 1.0), "Low"), ((1.49, 1.0), "Low"), ((1.5, 1.0), "Medium"), ((1.51, 1.0), "Medium"),
    ((2.99, 1.0), "Medium"), ((3.0, 1.0), "High"), ((0.75, 0.25), "High"), ((3.01, 1.0), "High"),
    ((5.99, 1.0), "High"), ((6.0, 1.0), "Critical"), ((3.0, 0.5), "Critical"), ((6.01, 1.0), "Critical"),
]
SIZE = [  # r = avg size / normal size: < 1.3 Low, < 1.8 Medium, < 3.0 High, otherwise Critical (:132-133)
    ((1000, 1000), "Low"), ((1299, 1000), "Low"), ((1300, 1000), "Medium"), ((1301, 1000), "Medium"),
    ((1799, 1000), "Medium"), ((1800, 1000), "High"), ((1801, 1000), "High"),
    ((2999, 1000), "High"), ((3000, 1000), "Critical"), ((3001, 1000), "Critical"),
]


@pytest.mark.parametrize("args,band", CANCEL)
def test_cancel_amend_rate_boundaries(args, band):
    assert score_cancel_amend_rate(*args) == band


def test_cancel_amend_rate_is_cancelled_over_total_not_the_inverse():
    """Doctrine :120: r = cancelled_orders / total_orders. 300 of 1,000 is 0.30 (High);
    inverted it would be 3.33 (Critical)."""
    assert score_cancel_amend_rate(300, 1000) == "High"


@pytest.mark.parametrize("n,band", QUOTE)
def test_quote_stuffing_intensity_boundaries(n, band):
    assert score_quote_stuffing_intensity(n) == band


@pytest.mark.parametrize("args,band", MOMENTUM)
def test_momentum_ignition_signal_boundaries(args, band):
    assert score_momentum_ignition_signal(*args) == band


def test_momentum_is_burst_over_normal_not_the_inverse():
    """Doctrine :128: r = price_move_after_burst_pct / normal_move_pct. 0.40 after the burst
    on a 0.80 normal move is 0.5 (Low); inverted it would be 2.0 (Medium)."""
    assert score_momentum_ignition_signal(0.40, 0.80) == "Low"


@pytest.mark.parametrize("args,band", SIZE)
def test_order_size_anomaly_boundaries(args, band):
    assert score_order_size_anomaly(*args) == band


def test_order_size_is_average_over_normal_not_the_inverse():
    """Doctrine :132: r = avg_order_size / normal_order_size. 1,000 against a 2,000 normal
    is 0.5 (Low); inverted it would be 2.0 (High)."""
    assert score_order_size_anomaly(1000, 2000) == "Low"


def test_boundary_tables_are_non_vacuous():
    for table in (CANCEL, QUOTE, MOMENTUM, SIZE):
        assert len(table) >= 8 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against the doctrine's weighted midpoint sum in EXACT
    arithmetic, half-up -- including the combinations whose exact total ends in .5."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, _ = cm010_exposure_score(bands)
        assert (score, band) == (_doctrine_score(bands), _doctrine_band(_doctrine_score(bands))), combo
    assert halves > 0                                               # non-vacuity: the .5 cases were examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_all_low_scores_fifteen():
    assert cm010_exposure_score(dict.fromkeys(DOCTRINE_WEIGHTS, "Low"))[:2] == (15, "Low")


# ---------------------------------------------------------------- check 4: through the callable

def _row(ref, cancelled, total, ops, burst, normal_move, avg, normal_size, venue=None):
    return {"trader_name": "Trader " + ref, "account_ref": ref, "instrument": "Instrument " + ref,
            "cancelled_orders": cancelled, "total_orders": total, "orders_per_second": ops,
            "price_move_after_burst_pct": burst, "normal_move_pct": normal_move,
            "avg_order_size": avg, "normal_order_size": normal_size,
            "venue_operator_name": venue or "Venue " + ref}


def _frames(rows):
    """Constructed order flow + the matching venue record per account."""
    venues = pd.DataFrame([{"venue_operator_name": r["venue_operator_name"], "account_ref": r["account_ref"],
                            "jurisdiction": "UNKNOWN", "relationship": "Constructed venue", "prior_alerts": 0}
                           for r in rows])
    return {"order_flow": pd.DataFrame(rows), "venues": venues}


# The doctrine's worked example (:137-147): 2,720 of 3,200 cancelled (r 0.85, Critical),
# 70 orders/s (Critical), 2.40% vs 0.30% (r 8, Critical), 4,000 vs 1,000 (r 4, Critical)
# -> 31.5 + 22.5 + 18 + 18 = 90 Critical.
WORKED = _row("A-WORKED", 2720, 3200, 70, 2.40, 0.30, 4000, 1000)

# Per component: the three OTHER components held Critical (900/1,000, 70/s, 8.0/1.0,
# 4,000/1,000), and the component's own input at the cut-line that keeps the total >= 80
# (positive) and one unit across it (near-miss). Hand-worked:
#   cancel    High 24.5 + 58.5 (=22.5+18+18) = 83 alert;   Medium 15.75 + 58.5 = 74.25 -> 74
#   quote     High 17.5 + 67.5 (=31.5+18+18) = 85 alert;   Medium 11.25 + 67.5 = 78.75 -> 79
#   momentum  Medium 9 + 72 (=31.5+22.5+18) = 81 alert;    Low 3 + 72 = 75
#   size      Medium 9 + 72 = 81 alert;                    Low 3 + 72 = 75
PER_RULE = {
    "cancel_amend_rate": (
        _row("A-CA-POS", 300, 1000, 70, 8.0, 1.0, 4000, 1000), 83, "Critical",
        _row("A-CA-NM", 299, 1000, 70, 8.0, 1.0, 4000, 1000), 74, "High"),
    "quote_stuffing_intensity": (
        _row("A-QS-POS", 900, 1000, 16, 8.0, 1.0, 4000, 1000), 85, "Critical",
        _row("A-QS-NM", 900, 1000, 15, 8.0, 1.0, 4000, 1000), 79, "High"),
    "momentum_ignition_signal": (
        _row("A-MI-POS", 900, 1000, 70, 1.5, 1.0, 4000, 1000), 81, "Critical",
        _row("A-MI-NM", 900, 1000, 70, 1.49, 1.0, 4000, 1000), 75, "High"),
    "order_size_anomaly": (
        _row("A-OS-POS", 900, 1000, 70, 8.0, 1.0, 1300, 1000), 81, "Critical",
        _row("A-OS-NM", 900, 1000, 70, 8.0, 1.0, 1299, 1000), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_suspicious_order_patterns(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("A-WORKED", 90, "Critical")
    assert [row[c] for c in BAND_COLUMNS] == ["Critical"] * 4


def test_the_subject_is_the_trading_account(governed):
    """Doctrine :202-203: the subject is the trading account (ACC019), the trader its name."""
    out = governed.score_all(**_frames([WORKED]))
    assert list(out["subject_entity_id"]) == ["A-WORKED"]
    assert list(out["subject_name"]) == ["Trader A-WORKED"]


@pytest.mark.parametrize("rule", sorted(PER_RULE))
def test_per_rule_positive_alerts_and_near_miss_does_not(governed, rule):
    pos, pos_score, pos_band, nm, nm_score, nm_band = PER_RULE[rule]
    frames = _frames([pos, nm])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc[pos["account_ref"], "exposure_score"], scored.loc[pos["account_ref"], "exposure_band"]) \
        == (pos_score, pos_band)
    assert (scored.loc[nm["account_ref"], "exposure_score"], scored.loc[nm["account_ref"], "exposure_band"]) \
        == (nm_score, nm_band)
    alerted = list(governed.evaluate_suspicious_order_patterns(**frames)["subject_entity_id"])
    assert alerted == [pos["account_ref"]]                          # the positive, and only it


def test_each_band_column_carries_its_own_components_band(governed):
    """Four different bands on one account, so no column can borrow another's: 450 of
    1,000 cancelled (r 0.45, High), 3/s (Low), 8.0 on 1.0 (Critical), 1,500 on 1,000
    (r 1.5, Medium) -> 24.5 + 3.75 + 18 + 9 = 55.25 -> 55 Medium."""
    mix = _row("A-MIX", 450, 1000, 3, 8.0, 1.0, 1500, 1000)
    scored = governed.score_all(**_frames([mix, WORKED])).set_index("subject_entity_id")
    assert len(scored) == 2
    assert [scored.loc["A-MIX", c] for c in BAND_COLUMNS] == ["High", "Low", "Critical", "Medium"]
    assert (scored.loc["A-MIX", "exposure_score"], scored.loc["A-MIX", "exposure_band"]) == (55, "Medium")


def test_band_table_governs_over_the_python_example(governed):
    """R1 (owner, 2026-10-21): the band table governs over the doctrine's Python example
    (:188-195), which also demands orders_per_second >= 18 and a High/Critical momentum
    band. 16 orders/s (High) with the rest Critical is 85, and a Medium momentum (r 1.5)
    with the rest Critical is 81: both MUST alert, although the example would drop each."""
    quote_pos = PER_RULE["quote_stuffing_intensity"][0]
    momentum_pos = PER_RULE["momentum_ignition_signal"][0]
    assert quote_pos["orders_per_second"] < 18
    got = governed.evaluate_suspicious_order_patterns(**_frames([quote_pos, momentum_pos]))
    assert set(got["subject_entity_id"]) == {quote_pos["account_ref"], momentum_pos["account_ref"]}
    assert set(got.loc[got["subject_entity_id"] == momentum_pos["account_ref"],
                       "momentum_ignition_signal_band"]) == {"Medium"}


def test_ordinary_order_flow_does_not_alert(governed):
    """Doctrine :238-239 -- what CM010 must be told apart from: 'noisy but ordinary
    high-frequency activity'. 50 of 1,000 cancelled (Low), 3/s (Low), 0.40 on 0.40 (Low),
    1,100 on 1,000 (Low): 5.25 + 3.75 + 3 + 3 = 15 Low."""
    frames = _frames([_row("A-ORD", 50, 1000, 3, 0.40, 0.40, 1100, 1000), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["A-ORD", "exposure_score"], scored.loc["A-ORD", "exposure_band"]) == (15, "Low")
    assert list(governed.evaluate_suspicious_order_patterns(**frames)["subject_entity_id"]) == ["A-WORKED"]


@pytest.mark.parametrize("burst,avg,score", [(0.5, 1000, 60), (2.0, 1000, 66), (0.5, 1500, 66), (2.0, 1500, 72)])
def test_the_burst_alone_without_impact_or_size_does_not_alert(governed, burst, avg, score):
    """Convergence (:7, :238): a Critical cancel/amend rate (900/1,000) and a Critical
    burst (70/s) alone are not the finding. With momentum and size at Low/Medium the total
    stays under 80: L/L 54+3+3 = 60, M/L 54+9+3 = 66, L/M 54+3+9 = 66, M/M 54+9+9 = 72."""
    frames = _frames([_row("A-PART", 900, 1000, 70, burst, 1.0, avg, 1000), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert scored.loc["A-PART", "exposure_score"] == score
    assert list(governed.evaluate_suspicious_order_patterns(**frames)["subject_entity_id"]) == ["A-WORKED"]


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"A-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_suspicious_order_patterns(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """Doctrine: 'boundary at 80' (:115), 'escalate at or above the threshold' (:162). No
    band combination scores exactly 80 (see below), so the cut-line is constructed by
    fixing the model's score; the callable's own filter decides."""
    real = governed.cm010_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm010_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                   # non-vacuity: one row scored
    assert (len(governed.evaluate_suspicious_order_patterns(**frames)) == 1) is alerts


def test_no_band_combination_scores_exactly_eighty():
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- KNOWN N10-FLOATCUT (one witness)

@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN N10-FLOATCUT, cited (fc-07 CM010): doctrine 'r < 1.5 -> Low, r < 3.0 -> Medium' "
    "(CM010_Suspicious_Order_Patterns.md:129). A 0.30% move after the burst on a 0.20% normal move "
    "is exactly r = 1.5 (Medium), but the binary-float ratio is 1.4999999999999998, so "
    "cm010_risk_model.py:104-110 bands it Low and the account's alert is LOST (75, not 81) -- "
    "measured: AssertionError, assert {'A-WORKED'} == {'A-FLOAT', 'A-WORKED'}"))
def test_a_decimal_momentum_ratio_exactly_on_the_medium_cut_line_keeps_its_alert(governed):
    assert Fraction("0.30") / Fraction("0.20") == Fraction(3, 2)  # exactly on the line
    float_row = _row("A-FLOAT", 900, 1000, 70, 0.30, 0.20, 4000, 1000)  # 31.5+22.5+9+18 = 81
    alerted = set(governed.evaluate_suspicious_order_patterns(**_frames([float_row, WORKED]))["subject_entity_id"])
    assert "A-WORKED" in alerted                                    # non-vacuity: the control alerted
    assert alerted == {"A-WORKED", "A-FLOAT"}


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

@pytest.mark.parametrize("column", ["cancelled_orders", "total_orders", "orders_per_second",
                                    "avg_order_size", "normal_order_size"])
def test_the_callable_refuses_a_row_with_a_missing_required_input(governed, column):
    """Doctrine: every component input is REQUIRED (:120, 124, 128, 132). A NaN must stop
    scoring, never be banded. (Measured: these five ARE refused, but only by accident, at
    an int() cast -- see the D043 xfails below.)"""
    row = dict(WORKED, **{column: float("nan")})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


@pytest.mark.parametrize("column", ["price_move_after_burst_pct", "normal_move_pct"])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: doctrine 'Both amounts REQUIRED' (CM010_Suspicious_Order_Patterns.md:128). "
    "A NaN momentum input is banded Critical, not refused (cm010_risk_model.py:56-61, 104-115: "
    "_require checks only `is None`; `normal <= 0` and every `r <` are False for NaN), and "
    "suspicious_order_patterns.py:87-88 float() passes it through, so an account at 71 High "
    "scores 86 Critical and GAINS an alert -- measured: Failed: DID NOT RAISE"))
def test_a_nan_momentum_input_is_refused_by_the_callable(governed, column):
    row = dict(_row("A-NAN", 900, 1000, 70, 0.10, 1.0, 2200, 1000), **{column: float("nan")})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row, WORKED]))


@pytest.mark.parametrize("call", [
    lambda: score_cancel_amend_rate(float("nan"), 1000),
    lambda: score_cancel_amend_rate(900, float("nan")),
    lambda: score_momentum_ignition_signal(float("nan"), 1.0),
    lambda: score_momentum_ignition_signal(2.0, float("nan")),
    lambda: score_order_size_anomaly(float("nan"), 1000),
    lambda: score_order_size_anomaly(1300, float("nan")),
], ids=["nan-cancelled", "nan-total", "nan-burst", "nan-normal-move", "nan-avg-size", "nan-normal-size"])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: doctrine 'Both counts/amounts REQUIRED' (CM010_Suspicious_Order_Patterns.md:"
    "120, 128, 132) -- a NaN ratio input is banded Critical, not refused (cm010_risk_model.py:56-61, "
    "71-132: _require checks only `is None`; `<= 0` and every `r <` are False for NaN) -- measured: "
    "Failed: DID NOT RAISE"))
def test_a_nan_ratio_input_is_refused_by_the_risk_model(call):
    with pytest.raises(RiskModelError):
        call()
