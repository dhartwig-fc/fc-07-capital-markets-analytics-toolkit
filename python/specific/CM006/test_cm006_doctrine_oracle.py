"""TT-CM006 (night 10, wave C): CM006 Front Running tested against its DOCTRINE.

Oracle: typologies/CM006_Front_Running.md -- "Exposure Scoring Framework" (weights
:112-117, midpoints / half-up / boundary at 80 :119), "Component Banding Rules"
(:123-140), the worked example (:144-153), "Classification" (:157), "Business Logic"
step 7 (:172, escalate at or above the threshold) -- and oracle rule R1 (owner,
2026-10-21: the band table governs over the doctrine's Python example). No signed-off
expected-outcome sheet exists for CM006. Every expected value below is hand-worked
from the doctrine, never pasted from an engine run. Inputs are CONSTRUCTED here; no
sample-data file is read and no sample entity name is asserted.

Checks 2 (boundaries at every doctrine threshold) and 4 (a positive and a near-miss
per detection rule, each near-miss scored in the SAME evaluate call as an alerting
control). The engine is loaded as fc-10 loads it: the scenario file by path.

Contributions per band (weight x midpoint): timing 35% L 5.25 M 15.75 H 24.5 C 31.5;
correlation 25% L 3.75 M 11.25 H 17.5 C 22.5; profit capture and knowledge linkage
20% each, L 3 M 9 H 14 C 18.
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

from cm006_risk_model import (  # noqa: E402
    RiskModelError, band_of, cm006_exposure_score, score_client_order_knowledge_linkage,
    score_position_correlation, score_profit_capture, score_timing_ahead_of_client_order,
)

SCENARIO = BASE_DIR / "scenarios" / "front_running.py"

# CM006_Front_Running.md:112-119
DOCTRINE_WEIGHTS = {
    "timing_ahead_of_client_order": Fraction(35, 100),
    "position_correlation": Fraction(25, 100),
    "profit_capture": Fraction(20, 100),
    "client_order_knowledge_linkage": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
BAND_COLUMNS = ("timing_ahead_of_client_order_band", "position_correlation_band",
                "profit_capture_band", "client_order_knowledge_linkage_band")


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # Classification (CM006_Front_Running.md:157): 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm006_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries

TIMING = [  # seconds ahead: <= 5 Critical, <= 30 High, <= 120 Medium, > 120 Low (:126). 0 and
    # negatives are NOT here: the doctrine is silent on them (QUESTION in the report).
    (1, "Critical"), (5, "Critical"), (5.5, "High"), (6, "High"),
    (30, "High"), (31, "Medium"), (120, "Medium"), (121, "Low"), (3600, "Low"),
]
CORRELATION = [  # integer 0-100: <= 40 Low, <= 65 Medium, <= 85 High, > 85 Critical (:131)
    (0, "Low"), (40, "Low"), (41, "Medium"), (65, "Medium"), (66, "High"),
    (85, "High"), (86, "Critical"), (100, "Critical"),
]
PROFIT = [  # r = realized_pnl / position_value: < 0.25 Low, < 0.50 Medium, < 0.80 High, else Critical (:135)
    ((24999, 100000), "Low"), ((25000, 100000), "Medium"), ((25001, 100000), "Medium"),
    ((49999, 100000), "Medium"), ((50000, 100000), "High"), ((50001, 100000), "High"),
    ((79999, 100000), "High"), ((80000, 100000), "Critical"), ((80001, 100000), "Critical"),
]
LINKAGE = [  # contact events: <= 2 Low, <= 5 Medium, <= 9 High, >= 10 Critical (:140)
    (0, "Low"), (2, "Low"), (3, "Medium"), (5, "Medium"), (6, "High"),
    (9, "High"), (10, "Critical"), (13, "Critical"),
]


@pytest.mark.parametrize("seconds,band", TIMING)
def test_timing_ahead_of_client_order_boundaries(seconds, band):
    assert score_timing_ahead_of_client_order(seconds) == band


def test_fewer_seconds_ahead_is_worse_not_better():
    """Doctrine :124: 'fewer seconds ahead of the client order is worse'. 2 s is
    Critical and 600 s Low; an inverted scale would swap them."""
    assert (score_timing_ahead_of_client_order(2), score_timing_ahead_of_client_order(600)) == ("Critical", "Low")


@pytest.mark.parametrize("pct,band", CORRELATION)
def test_position_correlation_boundaries(pct, band):
    assert score_position_correlation(pct) == band


@pytest.mark.parametrize("args,band", PROFIT)
def test_profit_capture_boundaries(args, band):
    assert score_profit_capture(*args) == band


def test_profit_capture_is_pnl_over_value_not_the_inverse():
    """Doctrine :134: r = realized_pnl / position_value. 30,000 on 100,000 is r = 0.3
    (Medium); inverted it would be 3.33 (Critical)."""
    assert score_profit_capture(30000, 100000) == "Medium"


@pytest.mark.parametrize("args", [(25000, 100000), (50000, 100000), (80000, 100000)],
                         ids=["0.25", "0.50", "0.80"])
def test_profit_capture_cut_lines_are_inclusive_of_the_upper_band(args):
    """Doctrine :135 uses strict '<', so a ratio exactly ON a cut-line belongs to the
    band above. Integer amounts: a single correctly-rounded division lands exactly."""
    expected = {(25000, 100000): "Medium", (50000, 100000): "High", (80000, 100000): "Critical"}[args]
    assert score_profit_capture(*args) == expected


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN N10-FLOATCUT, cited (now seen in fc-07): doctrine 'r < 0.80 -> High, otherwise "
    "Critical' (CM006_Front_Running.md:135). 1,920,000.40 / 2,400,000.50 is exactly 0.80, but "
    "the binary-float ratio is 0.7999999999999999, so cm006_risk_model.py:104-113 bands it "
    "High -- measured: AssertionError, 'High' != 'Critical'"))
def test_a_cents_ratio_exactly_on_the_critical_cut_line_is_critical():
    assert Fraction("1920000.40") / Fraction("2400000.50") == Fraction(4, 5)   # exactly on the line
    assert score_profit_capture(1920000.40, 2400000.50) == "Critical"


@pytest.mark.parametrize("n,band", LINKAGE)
def test_client_order_knowledge_linkage_boundaries(n, band):
    assert score_client_order_knowledge_linkage(n) == band


def test_boundary_tables_are_non_vacuous():
    for table in (TIMING, CORRELATION, PROFIT, LINKAGE):
        assert len(table) >= 7 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against the doctrine's weighted midpoint sum in EXACT
    arithmetic, half-up -- including the combinations whose exact total ends in .5."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, _ = cm006_exposure_score(bands)
        assert (score, band) == (_doctrine_score(bands), _doctrine_band(_doctrine_score(bands))), combo
    assert halves > 0                                               # non-vacuity: the .5 cases were examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_all_low_scores_fifteen():
    assert cm006_exposure_score(dict.fromkeys(DOCTRINE_WEIGHTS, "Low"))[:2] == (15, "Low")


# ---------------------------------------------------------------- check 4: through the callable

def _row(ref, seconds, corr, pnl, value, contacts, client=None):
    return {"trader_name": "Trader " + ref, "account_ref": ref, "desk": "Desk " + ref,
            "instrument": "Instrument " + ref, "seconds_ahead_of_client_order": seconds,
            "correlation_pct": corr, "realized_pnl": pnl, "position_value": value,
            "contact_events_90d": contacts, "client_firm_name": client or "Client " + ref}


def _frames(rows):
    """Constructed trading accounts + the matching client-order record per account."""
    orders = pd.DataFrame([{"client_firm_name": r["client_firm_name"], "account_ref": r["account_ref"],
                            "jurisdiction": "UNKNOWN", "relationship": "Constructed client", "prior_alerts": 0}
                           for r in rows])
    return {"trading_accounts": pd.DataFrame(rows), "client_orders": orders}


# The doctrine's worked example (:144-153): 1 s ahead (Critical), 96% correlation
# (Critical), 2,184,000 captured on 2,400,000 (r 0.910, Critical), 13 contact events
# (Critical) -> 31.5+22.5+18+18 = 90 Critical.
WORKED = _row("T-WORKED", 1, 96, 2184000, 2400000, 13)

# Per component: the three OTHER components held Critical (2 s, 96%, r 0.9, 12 contacts),
# and the component's own input at the cut-line that keeps the total >= 80 (positive)
# and one unit across it (near-miss). Hand-worked:
#   timing       High 24.5 + 58.5 (=22.5+18+18) = 83 alert;    Medium 15.75+58.5 = 74.25 -> 74
#   correlation  High 17.5 + 67.5 (=31.5+18+18) = 85 alert;    Medium 11.25+67.5 = 78.75 -> 79
#   profit       Medium 9 + 72 (=31.5+22.5+18) = 81 alert;     Low 3+72 = 75
#   linkage      Medium 9 + 72 = 81 alert;                     Low 3+72 = 75
PER_RULE = {
    "timing_ahead_of_client_order": (
        _row("T-TA-POS", 30, 96, 90000, 100000, 12), 83, "Critical",
        _row("T-TA-NM", 31, 96, 90000, 100000, 12), 74, "High"),
    "position_correlation": (
        _row("T-PC-POS", 2, 66, 90000, 100000, 12), 85, "Critical",
        _row("T-PC-NM", 2, 65, 90000, 100000, 12), 79, "High"),
    "profit_capture": (
        _row("T-PR-POS", 2, 96, 25000, 100000, 12), 81, "Critical",
        _row("T-PR-NM", 2, 96, 24999, 100000, 12), 75, "High"),
    "client_order_knowledge_linkage": (
        _row("T-KL-POS", 2, 96, 90000, 100000, 3), 81, "Critical",
        _row("T-KL-NM", 2, 96, 90000, 100000, 2), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_front_running(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")
    assert [row[c] for c in BAND_COLUMNS] == ["Critical"] * 4


def test_the_subject_is_the_trading_account(governed):
    """Doctrine :212: the subject is the trading account (ACC019), the trader its name."""
    out = governed.score_all(**_frames([WORKED]))
    assert list(out["subject_entity_id"]) == ["T-WORKED"]
    assert list(out["subject_name"]) == ["Trader T-WORKED"]


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
    alerted = list(governed.evaluate_front_running(**frames)["subject_entity_id"])
    assert alerted == [pos["account_ref"]]                          # the positive, and only it


def test_band_table_governs_over_the_python_example(governed):
    """R1 (owner, 2026-10-21): the band table governs over the doctrine's Python example
    (:199-204), which also demands correlation >= 68 and >= 6 contact events.
    Correlation 66 (High) with the rest Critical is 85, and 3 contacts (Medium) with the
    rest Critical is 81: both MUST alert, although the example would drop each."""
    corr_pos = PER_RULE["position_correlation"][0]
    contact_pos = PER_RULE["client_order_knowledge_linkage"][0]
    assert corr_pos["correlation_pct"] < 68 and contact_pos["contact_events_90d"] < 6
    got = set(governed.evaluate_front_running(**_frames([corr_pos, contact_pos]))["subject_entity_id"])
    assert got == {corr_pos["account_ref"], contact_pos["account_ref"]}


def test_an_ordinary_directional_bet_does_not_alert(governed):
    """Doctrine :252-253 -- what front running must be told apart from: 'an ordinary
    directional bet'. Placed 10 minutes ahead (Low), 30% correlation (Low), r 0.05 (Low),
    one contact (Low): 5.25+3.75+3+3 = 15 Low."""
    frames = _frames([_row("T-BET", 600, 30, 5000, 100000, 1), WORKED])      # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-BET", "exposure_score"], scored.loc["T-BET", "exposure_band"]) == (15, "Low")
    assert list(governed.evaluate_front_running(**frames)["subject_entity_id"]) == ["T-WORKED"]


@pytest.mark.parametrize("pnl,contacts,score", [(10000, 0, 60), (30000, 1, 66), (10000, 4, 66), (30000, 4, 72)])
def test_timing_and_correlation_without_profit_or_linkage_does_not_alert(governed, pnl, contacts, score):
    """Convergence (:7): 2 s ahead (Critical) and 96% correlated (Critical) alone are not
    the finding. With profit capture and linkage at Low/Medium the total stays under 80:
    L/L 54+3+3 = 60, M/L 54+9+3 = 66, L/M 54+3+9 = 66, M/M 54+9+9 = 72."""
    frames = _frames([_row("T-PART", 2, 96, pnl, 100000, contacts), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert scored.loc["T-PART", "exposure_score"] == score
    assert list(governed.evaluate_front_running(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_front_running(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """Doctrine: 'boundary at 80' (:119), 'escalate at or above the threshold' (:172). No
    band combination scores exactly 80 (see below), so the cut-line is constructed by
    fixing the model's score; the callable's own filter decides."""
    real = governed.cm006_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm006_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                   # non-vacuity: one row scored
    assert (len(governed.evaluate_front_running(**frames)) == 1) is alerts


def test_no_band_combination_scores_exactly_eighty():
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

@pytest.mark.parametrize("column", ["correlation_pct", "realized_pnl", "position_value", "contact_events_90d"])
def test_the_callable_refuses_a_row_with_a_missing_required_input(governed, column):
    """Doctrine: every component input is REQUIRED (:124, 129, 134, 138). A NaN must stop
    scoring, never be banded. (Measured: these four ARE refused, but only by accident, at
    an int() cast -- see the D043 xfails below for the risk model itself.)"""
    row = dict(WORKED, **{column: float("nan")})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: doctrine 'seconds_ahead_of_client_order REQUIRED' "
    "(CM006_Front_Running.md:124). A NaN is banded Low, not refused (cm006_risk_model.py:58-63, "
    "77-84: _require checks only `is None`; NaN fails every `<=`), and front_running.py:85 "
    "float() passes it through, so the worked example scores 64 High and its alert is LOST "
    "silently -- measured: Failed: DID NOT RAISE"))
def test_a_nan_timing_input_is_refused_by_the_callable(governed):
    row = dict(WORKED, seconds_ahead_of_client_order=float("nan"))
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


@pytest.mark.parametrize("call", [
    lambda: score_position_correlation(float("nan")),
    lambda: score_profit_capture(float("nan"), 100000),
    lambda: score_profit_capture(90000, float("nan")),
], ids=["nan-correlation", "nan-pnl", "nan-position-value"])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: doctrine 'REQUIRED' (CM006_Front_Running.md:129, 134) -- a NaN "
    "correlation or profit input is banded Critical, not refused (cm006_risk_model.py:58-63, "
    "87-115: _require checks only `is None`; `value <= 0` is False for NaN) -- measured: "
    "Failed: DID NOT RAISE"))
def test_a_nan_component_input_is_refused_by_the_risk_model(call):
    with pytest.raises(RiskModelError):
        call()
