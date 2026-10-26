"""TT-CM008 (night 10, wave C): CM008 Cross Market Abuse tested against its DOCTRINE.

Oracle: typologies/CM008_Cross_Market_Abuse.md (T) -- "Exposure Scoring Framework" T:106-115,
"Component Banding Rules" T:117-137, the worked example T:141-151, the classification T:153-154,
"Business Logic" T:158-169 -- reached through fc-10 indexes/doctrine_library.json, and the owner's
general oracle rules (2026-10-21): R1 -- the band table governs over the doctrine's Python
example (T:195-202). No signed-off expected-outcome sheet exists for CM008. Every expected
value below is hand-worked from T, never pasted from an engine run. Inputs are CONSTRUCTED
here; no sample-data file is read and no sample entity name is asserted.

Checks 2 (boundaries at every doctrine threshold) and 4 (a positive and a near-miss per
detection rule). The engine is loaded as fc-10 loads it: the scenario file by path.
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

from cm008_risk_model import (  # noqa: E402
    band_of, cm008_exposure_score, score_cross_venue_position_correlation,
    score_price_impact_transfer, score_timing_synchronization, score_venue_count,
)

SCENARIO = BASE_DIR / "scenarios" / "cross_market_abuse.py"

# The doctrine's own numbers (T:108-115): weights 35/25/20/20 %, band midpoints 15/45/70/90,
# weighted sum, half-up, boundary at 80.
DOCTRINE_WEIGHTS = {
    "cross_venue_position_correlation": Fraction(35, 100),
    "venue_count": Fraction(25, 100),
    "price_impact_transfer": Fraction(20, 100),
    "timing_synchronization": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
BAND_COLS = ("cross_venue_position_correlation_band", "venue_count_band",
             "price_impact_transfer_band", "timing_synchronization_band")


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # Classification (T:154): 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm008_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries
# At / just below / just above each cut-line (T:122, :127, :132, :137).

CORRELATION = [  # correlation_pct: <= 40 Low, <= 65 Medium, <= 85 High, > 85 Critical (T:122)
    (0, "Low"), (39, "Low"), (40, "Low"), (41, "Medium"),
    (64, "Medium"), (65, "Medium"), (66, "High"),
    (84, "High"), (85, "High"), (86, "Critical"), (100, "Critical"),
]
VENUES = [  # distinct_venues: <= 1 Low, = 2 Medium, <= 4 High, >= 5 Critical (T:127)
    (0, "Low"), (1, "Low"), (2, "Medium"), (3, "High"),
    (4, "High"), (5, "Critical"), (6, "Critical"),
]
IMPACT = [  # r = impact_transfer_ratio: < 0.10 Low, < 0.30 Medium, < 0.60 High, else Critical (T:132)
    (0.0, "Low"), (0.0999, "Low"), (0.10, "Medium"), (0.1001, "Medium"),
    (0.2999, "Medium"), (0.30, "High"), (0.3001, "High"),
    (0.5999, "High"), (0.60, "Critical"), (0.6001, "Critical"), (1.0, "Critical"),
]
TIMING = [  # seconds: <= 5 Critical, <= 30 High, <= 120 Medium, > 120 Low (T:137) -- INCLUSIVE windows
    (0, "Critical"), (4.9, "Critical"), (5, "Critical"), (5.1, "High"),
    (29.9, "High"), (30, "High"), (30.1, "Medium"),
    (119.9, "Medium"), (120, "Medium"), (120.1, "Low"), (600, "Low"),
]


@pytest.mark.parametrize("pct,band", CORRELATION)
def test_correlation_boundaries(pct, band):
    assert score_cross_venue_position_correlation(pct) == band


@pytest.mark.parametrize("count,band", VENUES)
def test_venue_count_boundaries(count, band):
    assert score_venue_count(count) == band


@pytest.mark.parametrize("ratio,band", IMPACT)
def test_price_impact_transfer_boundaries(ratio, band):
    assert score_price_impact_transfer(ratio) == band


@pytest.mark.parametrize("seconds,band", TIMING)
def test_timing_synchronization_boundaries(seconds, band):
    assert score_timing_synchronization(seconds) == band


def test_boundary_tables_are_non_vacuous():
    for table in (CORRELATION, VENUES, IMPACT, TIMING):
        assert len(table) >= 7 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


# KNOWN N10-FLOATCUT check: the CSV is read as strings (cross_market_abuse.py:118), so the
# ratio arrives as a decimal string ON the line. The ratio is supplied, not computed, so the
# cut-lines hold; pinned here so a computed ratio cannot slip in unnoticed.
@pytest.mark.parametrize("ratio,band", [("0.10", "Medium"), ("0.1", "Medium"), ("0.30", "High"),
                                        ("0.3", "High"), ("0.60", "Critical"), ("0.6", "Critical")])
def test_price_impact_decimal_strings_on_the_cut_lines(ratio, band):
    assert Fraction(ratio) in (Fraction(1, 10), Fraction(3, 10), Fraction(6, 10))   # non-vacuity: ON the line
    assert score_price_impact_transfer(ratio) == band


@pytest.mark.parametrize("seconds,band", [("5", "Critical"), ("5.0", "Critical"), ("30.0", "High"),
                                          ("120.00", "Medium")])
def test_timing_window_is_inclusive_for_decimal_strings(seconds, band):
    assert score_timing_synchronization(seconds) == band


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against T's weighted midpoint sum in EXACT arithmetic,
    half-up -- including the combinations whose exact total ends in .5."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, _ = cm008_exposure_score(bands)
        assert (score, band) == (_doctrine_score(bands), _doctrine_band(_doctrine_score(bands))), combo
    assert halves > 0                                               # non-vacuity: the .5 cases were examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_every_classification_band_is_reachable():
    reached = {_doctrine_band(_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c))))
               for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert reached == {"Low", "Medium", "High", "Critical"}


def test_no_band_combination_scores_exactly_eighty():
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- check 4: through the callable

def _row(ref, corr, venues, impact, seconds):
    return {"trader_name": "Trader " + ref, "account_ref": ref,
            "primary_instrument": "Primary " + ref, "correlated_instrument": "Correlated " + ref,
            "correlation_pct": corr, "distinct_venues": venues, "impact_transfer_ratio": impact,
            "seconds_between_venue_trades": seconds, "issuer_name": "Issuer " + ref}


def _frames(rows):
    """Constructed trading accounts + a matching instrument record per account."""
    inst = pd.DataFrame([{"issuer_name": r["issuer_name"], "account_ref": r["account_ref"],
                          "venue": "Venue " + r["account_ref"], "jurisdiction": "UNKNOWN",
                          "relationship": "constructed", "prior_alerts": 0} for r in rows])
    return {"trading_accounts": pd.DataFrame(rows), "instruments": inst}


# The doctrine's worked example (T:141-151): 97% correlation (C), 6 venues (C), 0.85 of the
# impact transferred (C), trades 2 seconds apart (C) -> 90 Critical.
WORKED = _row("T-WORKED", 97, 6, 0.85, 2)

# Per detection rule: the other three components held Critical (97%, 6 venues, 0.85, 2 s),
# the rule's own input at the cut-line that keeps the total >= 80 (positive) and across it
# (near-miss). Hand-worked from T:110-113, :115:
#   correlation High 70*.35=24.5 + 58.5 (=22.5+18+18) = 83 alert; Medium 15.75+58.5 = 74.25 -> 74
#   venues      High 70*.25=17.5 + 67.5 (=31.5+18+18) = 85 alert; Medium 11.25+67.5 = 78.75 -> 79
#   impact      Medium 45*.2=9 + 72 (=31.5+22.5+18) = 81 alert;   Low 3+72 = 75
#   timing      Medium 9 + 72 = 81 alert;                         Low 3+72 = 75
PER_RULE = {
    "cross_venue_position_correlation": (
        _row("T-COR-POS", 66, 6, 0.85, 2), 83, "Critical",
        _row("T-COR-NM", 65, 6, 0.85, 2), 74, "High"),
    "venue_count": (
        _row("T-VEN-POS", 97, 3, 0.85, 2), 85, "Critical",
        _row("T-VEN-NM", 97, 2, 0.85, 2), 79, "High"),
    "price_impact_transfer": (
        _row("T-IMP-POS", 97, 6, "0.10", 2), 81, "Critical",
        _row("T-IMP-NM", 97, 6, "0.0999", 2), 75, "High"),
    "timing_synchronization": (
        _row("T-TIM-POS", 97, 6, 0.85, 120), 81, "Critical",
        _row("T-TIM-NM", 97, 6, 0.85, 120.5), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_cross_market_abuse(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")
    assert [row[c] for c in BAND_COLS] == ["Critical"] * 4


def test_the_subject_is_the_trading_account(governed):
    """T:59, :160: the subject is the trading account; its name is the trader's."""
    out = governed.score_all(**_frames([WORKED]))
    assert list(out["subject_entity_id"]) == ["T-WORKED"]
    assert list(out["subject_name"]) == ["Trader T-WORKED"]


@pytest.mark.parametrize("rule", sorted(PER_RULE))
def test_per_rule_positive_alerts_and_near_miss_does_not(governed, rule):
    pos, pos_score, pos_band, nm, nm_score, nm_band = PER_RULE[rule]
    frames = _frames([pos, nm])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert (scored.loc[pos["account_ref"], "exposure_score"], scored.loc[pos["account_ref"], "exposure_band"]) \
        == (pos_score, pos_band)
    assert (scored.loc[nm["account_ref"], "exposure_score"], scored.loc[nm["account_ref"], "exposure_band"]) \
        == (nm_score, nm_band)
    alerted = list(governed.evaluate_cross_market_abuse(**frames)["subject_entity_id"])
    assert alerted == [pos["account_ref"]]                          # the positive, and only it


def test_band_table_governs_over_the_python_example(governed):
    """R1 (owner 2026-10-21): T's Python example (T:196-201) also demands distinct_venues >= 4
    and seconds <= 30. The band table (T:127, :137) alerts 3 venues (High, 85) and a
    120-second window (Medium, 81) with the rest Critical: both MUST alert."""
    ven = PER_RULE["venue_count"][0]
    tim = PER_RULE["timing_synchronization"][0]
    assert ven["distinct_venues"] < 4 and tim["seconds_between_venue_trades"] > 30
    got = sorted(governed.evaluate_cross_market_abuse(**_frames([ven, tim]))["subject_entity_id"])
    assert got == sorted([ven["account_ref"], tim["account_ref"]])


def _assert_only_worked_alerts(governed, row, score, band):
    frames = _frames([row, WORKED])                                 # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc[row["account_ref"], "exposure_score"], scored.loc[row["account_ref"], "exposure_band"]) \
        == (score, band)
    assert list(governed.evaluate_cross_market_abuse(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_a_tightly_correlated_single_venue_hedge_does_not_alert(governed):
    """A cash/derivative hedge correlates tightly (97, C) but on one venue (1, L), with little
    impact transferred (0.05, L) and trades far apart in time (600 s, L):
    31.5+3.75+3+3 = 41.25 -> 41 Medium."""
    _assert_only_worked_alerts(governed, _row("T-HEDGE", 97, 1, 0.05, 600), 41, "Medium")


def test_synchronised_trades_without_correlation_do_not_alert(governed):
    """Tight timing (2 s, C) across many venues (6, C) with no position correlation (20, L) and
    no impact transfer (0.05, L): 5.25+22.5+3+18 = 48.75 -> 49 Medium."""
    _assert_only_worked_alerts(governed, _row("T-ALGO", 20, 6, 0.05, 2), 49, "Medium")


def test_background_trading_scores_fifteen(governed):
    _assert_only_worked_alerts(governed, _row("T-BG", 10, 1, 0.02, 900), 15, "Low")


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_cross_market_abuse(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """T:115, :169: 'boundary at 80', 'escalate at or above the threshold'. No band
    combination scores exactly 80, so the cut-line is constructed by fixing the model's
    score; the callable's own filter decides."""
    real = governed.cm008_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm008_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                   # non-vacuity: one row scored
    assert (len(governed.evaluate_cross_market_abuse(**frames)) == 1) is alerts


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

@pytest.mark.parametrize("column", ["correlation_pct", "distinct_venues", "impact_transfer_ratio",
                                    "seconds_between_venue_trades"])
def test_the_callable_refuses_a_blank_required_input(governed, column):
    """T:120, :125, :130, :135: every component input is REQUIRED. The engine reads its CSVs
    as strings (cross_market_abuse.py:118), so a missing cell is ''; it must stop scoring,
    never be banded."""
    row = dict(WORKED, **{column: ""})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


@pytest.mark.parametrize("scorer", [score_cross_venue_position_correlation, score_venue_count,
                                    score_price_impact_transfer, score_timing_synchronization])
def test_each_component_scorer_refuses_a_blank_input(scorer):
    """The same REQUIRED rule at the scorer itself, not only at the callable's output cast
    (cross_market_abuse.py:87-90 re-casts each input and would mask a scorer that banded '')."""
    with pytest.raises(ValueError):
        scorer("")


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: T:130 'impact_transfer_ratio REQUIRED' -- a NaN ratio is banded "
    "Critical instead of refused (cm008_risk_model.py:56-61 checks `is None` only; NaN fails "
    "every `r <` test at :99-106). Effect measured in CM008: an ALERT -- a row with no measured "
    "impact transfer, 97%, 6 venues and 2 s is scored 90 Critical and alerted. A NaN "
    "seconds_between_venue_trades is scored as CLEAN (Low, :112-119: 'not measured is not far "
    "apart in time' is violated); a NaN correlation_pct or distinct_venues is refused only by "
    "accident at int() (:74, :86), which raises ValueError and loses the whole frame "
    "(cross_market_abuse.py:103). Measured: Failed: DID NOT RAISE <class 'ValueError'>"))
def test_a_nan_impact_transfer_is_refused_not_alerted(governed):
    row = _row("T-NAN", 97, 6, float("nan"), 2)
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


# ---------------------------------------------------------------- DEFECT: percentage truncated before the cut

@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "QUESTION (doctrine T:122 vs fc-07 schema.json integer typing, rule 9): "
    "Measured: AssertionError: assert ('High', 'Medium', 'Low') == ('Critical', 'High', "
    "'Medium'). T:122 bands correlation_pct '<= 85 -> High, otherwise (> 85) -> Critical' (and "
    "'<= 40', '<= 65'); cm008_risk_model.py:74 truncates the percentage with int(float(...)) "
    "before comparing, so 85.5% is High, 65.5% Medium and 40.5% Low. Measured through the "
    "callable: 85.5% with 3 venues (H), 0.85 transferred (C) and 10 s (H) scores 74 High and "
    "is NOT alerted; the doctrine's 31.5+17.5+18+14 = 81 alerts. The published correlation_pct "
    "is truncated too (cross_market_abuse.py:87). (schema.json types the field 'integer'; T "
    "does not.) Measured: AssertionError ('High', 'Medium', 'Low') == ('Critical', 'High', "
    "'Medium'); T-CORR scores 74 High"))
def test_a_fractional_correlation_is_banded_on_its_exact_value(governed):
    pos = _row("T-CORR", 85.5, 3, 0.85, 10)
    frames = _frames([pos, WORKED])                     # alerting control
    assert len(governed.score_all(**frames)) == 2
    assert tuple(score_cross_venue_position_correlation(x) for x in (85.5, 65.5, 40.5)) == \
        ("Critical", "High", "Medium")
    assert sorted(governed.evaluate_cross_market_abuse(**frames)["subject_entity_id"]) == ["T-CORR", "T-WORKED"]
