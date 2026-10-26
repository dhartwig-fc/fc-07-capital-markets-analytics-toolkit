"""TT-CM002 (night 10, wave C): CM002 Market Manipulation tested against its DOCTRINE.

Oracle: typologies/CM002_Market_Manipulation.md ("Exposure Scoring Framework" :100-109,
"Component Banding Rules" :111-128, the worked example :132-145, "Business Logic" :149-157),
reached through fc-10 indexes/doctrine_library.json, and the owner's general oracle rules
(2026-10-21): R1 -- the band table governs over the doctrine's Python example (:183-190).
No signed-off expected-outcome sheet exists for CM002. Every expected value below is
hand-worked from the doctrine, never pasted from an engine run. Inputs are CONSTRUCTED
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

from cm002_risk_model import (  # noqa: E402
    band_of, cm002_exposure_score, score_coordinated_accounts, score_price_impact_ratio,
    score_reversal_after_close, score_volume_concentration,
)

SCENARIO = BASE_DIR / "scenarios" / "market_manipulation.py"

# The doctrine's own numbers (CM002_Market_Manipulation.md:102-109): weights 35/25/20/20 %,
# band midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.
DOCTRINE_WEIGHTS = {
    "price_impact_ratio": Fraction(35, 100),
    "volume_concentration": Fraction(25, 100),
    "coordinated_accounts": Fraction(20, 100),
    "reversal_after_close": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # Classification (CM002_Market_Manipulation.md:145): 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm002_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries
# At / just below / just above each cut-line. Inputs chosen so the exact ratio is also the
# binary-float ratio (x/100, x/10000); the decimal cut-line cases are tested separately below.

IMPACT = [  # r = price_move_pct / normal_volatility_pct; r < 1.5 Low, < 3.0 Medium, < 6.0 High, else Critical (:114-115)
    ((149, 100), "Low"), ((150, 100), "Medium"), ((151, 100), "Medium"),
    ((299, 100), "Medium"), ((300, 100), "High"), ((301, 100), "High"),
    ((599, 100), "High"), ((600, 100), "Critical"), ((601, 100), "Critical"),
]
VOLUME = [  # pct_of_market_volume: <= 10 Low, <= 25 Medium, <= 45 High, > 45 Critical (:118-120)
    (0, "Low"), (10, "Low"), (11, "Medium"),
    (25, "Medium"), (26, "High"),
    (45, "High"), (46, "Critical"), (100, "Critical"),
]
COORD = [  # linked_accounts_count: <= 1 Low, = 2 Medium, <= 4 High, >= 5 Critical (:123-124)
    (0, "Low"), (1, "Low"), (2, "Medium"), (3, "High"),
    (4, "High"), (5, "Critical"), (8, "Critical"),
]
REVERSAL = [  # r = post_period_reversal_pct / price_move_pct; < 0.25 Low, < 0.50 Medium, < 0.80 High, else Critical (:127-128)
    ((2499, 10000), "Low"), ((2500, 10000), "Medium"), ((2501, 10000), "Medium"),
    ((4999, 10000), "Medium"), ((5000, 10000), "High"), ((5001, 10000), "High"),
    ((7999, 10000), "High"), ((8000, 10000), "Critical"), ((8001, 10000), "Critical"),
]


@pytest.mark.parametrize("args,band", IMPACT)
def test_price_impact_ratio_boundaries(args, band):
    assert score_price_impact_ratio(*args) == band


def test_price_impact_is_move_over_volatility_not_the_inverse():
    """Doctrine :114: r = price_move_pct / normal_volatility_pct. A 2% move on 10%
    volatility is r = 0.2 (Low); inverted it would be 5.0 (High)."""
    assert score_price_impact_ratio(2, 10) == "Low"


@pytest.mark.parametrize("pct,band", VOLUME)
def test_volume_concentration_boundaries(pct, band):
    assert score_volume_concentration(pct) == band


@pytest.mark.parametrize("count,band", COORD)
def test_coordinated_accounts_boundaries(count, band):
    assert score_coordinated_accounts(count) == band


@pytest.mark.parametrize("args,band", REVERSAL)
def test_reversal_after_close_boundaries(args, band):
    assert score_reversal_after_close(*args) == band


def test_reversal_is_reversal_over_move_not_the_inverse():
    """Doctrine :127: r = post_period_reversal_pct / price_move_pct (the first argument
    over the second). 1% reversed of a 10% move is r = 0.1 (Low); inverted it is 10 (Critical)."""
    assert score_reversal_after_close(1, 10) == "Low"


def test_boundary_tables_are_non_vacuous():
    for table in (IMPACT, VOLUME, COORD, REVERSAL):
        assert len(table) >= 7 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


# Decimal inputs whose EXACT ratio lands on a cut-line (KNOWN N10-FLOATCUT check). The
# 0.25 and 0.50 reversal lines hold for every 2-dp input tried (move 1.00-49.99); they are
# pinned here. The 1.5 / 3.0 / 6.0 / 0.8 lines misfire -- one witness below.
@pytest.mark.parametrize("reversal,move,band", [
    ("0.55", "2.2", "Medium"), ("2.75", "11", "Medium"), ("0.4", "1.6", "Medium"),   # r = 0.25 exactly
    ("1.1", "2.2", "High"), ("0.35", "0.7", "High"), ("4.05", "8.1", "High"),        # r = 0.50 exactly
])
def test_reversal_decimal_inputs_on_the_quarter_and_half_lines(reversal, move, band):
    assert Fraction(reversal) / Fraction(move) in (Fraction(1, 4), Fraction(1, 2))   # non-vacuity: ON the line
    assert score_reversal_after_close(float(reversal), float(move)) == band


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN N10-FLOATCUT, cited (now seen in fc-07): doctrine :115 'r < 3.0 -> Medium' puts a "
    "3.30% move on 1.1% volatility (r = 3.0 exactly) in High; the float ratio is "
    "2.9999999999999996 and cm002_risk_model.py:79-83 bands it Medium. Through the callable, "
    "with the other three Critical, the doctrine's 83 Critical becomes 74 High: the alert is "
    "LOST. Same class measured at r=1.5 (1.65/1.1 -> Low), r=6.0 (6.60/1.1 -> High) and "
    "reversal r=0.8 (1.20/1.5 -> High, cm002_risk_model.py:122-129). Measured: AssertionError "
    "'Medium' == 'High'; T-FLOAT scores 74 High"))
def test_a_price_impact_on_the_three_line_in_decimal_inputs_bands_high(governed):
    pos = _row("T-FLOAT", 1.1, 3.30, 67, 8, 3.0)        # r 3.0 H, 67 C, 8 C, reversal 3.0/3.3 = .909 C
    frames = _frames([pos, WORKED])                     # alerting control
    assert len(governed.score_all(**frames)) == 2
    assert Fraction("3.30") / Fraction("1.1") == 3
    assert score_price_impact_ratio(3.30, 1.1) == "High"
    assert sorted(governed.evaluate_market_manipulation(**frames)["subject_entity_id"]) == ["T-FLOAT", "T-WORKED"]


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against the doctrine's weighted midpoint sum in EXACT
    arithmetic, half-up -- including the 32 combinations whose exact total ends in .5."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, _ = cm002_exposure_score(bands)
        assert (score, band) == (_doctrine_score(bands), _doctrine_band(_doctrine_score(bands))), combo
    assert halves > 0                                               # non-vacuity: the .5 cases were examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_every_classification_band_is_reachable():
    """Unreachable-band check: each of the four classification bands (:145) is the
    outcome of at least one component-band combination."""
    reached = {_doctrine_band(_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c))))
               for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert reached == {"Low", "Medium", "High", "Critical"}


def test_no_band_combination_scores_exactly_eighty():
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- check 4: through the callable

def _row(ref, normal, move, volume, linked, reversal):
    return {"account_holder_name": "Holder " + ref, "account_ref": ref, "desk": "Desk T",
            "instrument": "Instrument " + ref, "normal_volatility_pct": normal, "price_move_pct": move,
            "pct_of_market_volume": volume, "linked_accounts_count": linked,
            "post_period_reversal_pct": reversal, "ultimate_owner_name": "Owner " + ref}


def _frames(rows):
    """Constructed trading accounts + a matching counterparty record per account."""
    cps = pd.DataFrame([{"ultimate_owner_name": r["ultimate_owner_name"], "account_ref": r["account_ref"],
                         "venue": "Venue T", "jurisdiction": "UNKNOWN", "relationship": "constructed",
                         "prior_alerts": 0} for r in rows])
    return {"trading_accounts": pd.DataFrame(rows), "counterparties": cps}


# The doctrine's worked example (:132-141): 30.06% move on 4.0% volatility (r 7.515 C), 67%
# of market volume (C), 8 linked accounts (C), 28.74% reversed (r 0.956 C) -> 90 Critical.
WORKED = _row("T-WORKED", 4.0, 30.06, 67, 8, 28.74)

# Per detection rule: the other three components held Critical (r 10 on 1% volatility,
# 67%, 8 linked, reversal 9 of 10 = .9), the rule's own input at the cut-line that keeps
# the total >= 80 (positive) and one unit across it (near-miss). Hand-worked:
#   impact   High 70*.35=24.5 + 58.5 (=22.5+18+18) = 83 alert;  Medium 15.75+58.5 = 74.25 -> 74
#   volume   High 70*.25=17.5 + 67.5 (=31.5+18+18) = 85 alert;  Medium 11.25+67.5 = 78.75 -> 79
#   linked   Medium 45*.2=9 + 72 (=31.5+22.5+18) = 81 alert;    Low 3+72 = 75
#   reversal Medium 9 + 72 = 81 alert;                          Low 3+72 = 75
PER_RULE = {
    "price_impact_ratio": (
        _row("T-IMP-POS", 1, 3.0, 67, 8, 2.7), 83, "Critical",
        _row("T-IMP-NM", 1, 2.99, 67, 8, 2.7), 74, "High"),
    "volume_concentration": (
        _row("T-VOL-POS", 1, 10, 26, 8, 9), 85, "Critical",
        _row("T-VOL-NM", 1, 10, 25, 8, 9), 79, "High"),
    "coordinated_accounts": (
        _row("T-LNK-POS", 1, 10, 67, 2, 9), 81, "Critical",
        _row("T-LNK-NM", 1, 10, 67, 1, 9), 75, "High"),
    "reversal_after_close": (
        _row("T-REV-POS", 1, 10, 67, 8, 2.5), 81, "Critical",
        _row("T-REV-NM", 1, 10, 67, 8, 2.49), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_market_manipulation(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")
    assert [row[c] for c in ("price_impact_ratio_band", "volume_concentration_band",
                             "coordinated_accounts_band", "reversal_after_close_band")] == ["Critical"] * 4


def test_the_subject_is_the_trading_account(governed):
    """Doctrine :151 resolves the account holder; the subject is the account reference,
    not the holder's display name."""
    out = governed.score_all(**_frames([WORKED]))
    assert list(out["subject_entity_id"]) == ["T-WORKED"]
    assert list(out["subject_name"]) == ["Holder T-WORKED"]


@pytest.mark.parametrize("rule", sorted(PER_RULE))
def test_per_rule_positive_alerts_and_near_miss_does_not(governed, rule):
    pos, pos_score, pos_band, nm, nm_score, nm_band = PER_RULE[rule]
    frames = _frames([pos, nm])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert (scored.loc[pos["account_ref"], "exposure_score"], scored.loc[pos["account_ref"], "exposure_band"]) \
        == (pos_score, pos_band)
    assert (scored.loc[nm["account_ref"], "exposure_score"], scored.loc[nm["account_ref"], "exposure_band"]) \
        == (nm_score, nm_band)
    alerted = list(governed.evaluate_market_manipulation(**frames)["subject_entity_id"])
    assert alerted == [pos["account_ref"]]                          # the positive, and only it


def test_band_table_governs_over_the_python_example(governed):
    """R1 (owner 2026-10-21): the band table governs over the doctrine's Python example
    (:184-189, which also demands linked_accounts_count >= 3). Two linked accounts
    (Medium) with the rest Critical is 31.5+22.5+9+18 = 81: it MUST alert."""
    pos = PER_RULE["coordinated_accounts"][0]
    assert pos["linked_accounts_count"] < 3
    assert list(governed.evaluate_market_manipulation(**_frames([pos]))["subject_entity_id"]) == [pos["account_ref"]]


def _assert_only_worked_alerts(governed, row, score, band):
    frames = _frames([row, WORKED])                                 # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc[row["account_ref"], "exposure_score"], scored.loc[row["account_ref"], "exposure_band"]) \
        == (score, band)
    assert list(governed.evaluate_market_manipulation(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_an_information_driven_directional_trade_does_not_alert(governed):
    """Doctrine :238 near-miss: 'an ordinary large directional trade' -- a large move (r 10,
    C) on a big share of volume (67, C), but no coordination (1, L) and no reversal (r .1, L):
    31.5+22.5+3+3 = 60 -> High, below 80."""
    _assert_only_worked_alerts(governed, _row("T-DIRECT", 1, 10, 67, 1, 1), 60, "High")


def test_a_thin_instrument_footprint_alone_does_not_alert(governed):
    """A large share of a thin instrument's volume (60, C) with a move inside normal
    volatility (r 1, L), no coordination (0, L) and no reversal (r .1, L):
    5.25+22.5+3+3 = 33.75 -> 34 Medium."""
    _assert_only_worked_alerts(governed, _row("T-THIN", 2, 2, 60, 0, 0.2), 34, "Medium")


def test_background_trading_scores_fifteen(governed):
    """All four components Low: 15 (midpoint 15 x weights summing to 100%)."""
    _assert_only_worked_alerts(governed, _row("T-BG", 2, 1, 2, 0, 0.1), 15, "Low")


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_market_manipulation(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """Doctrine :109, :157: 'boundary at 80', 'escalate at or above the threshold'. No band
    combination scores exactly 80, so the cut-line is constructed by fixing the model's
    score; the callable's own filter decides."""
    real = governed.cm002_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm002_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                   # non-vacuity: one row scored
    assert (len(governed.evaluate_market_manipulation(**frames)) == 1) is alerts


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

@pytest.mark.parametrize("column", ["price_move_pct", "normal_volatility_pct", "pct_of_market_volume",
                                    "linked_accounts_count", "post_period_reversal_pct"])
def test_the_callable_refuses_a_blank_required_input(governed, column):
    """Doctrine :114, :118, :123, :127: every component input is REQUIRED. The engine reads
    its CSVs as strings (market_manipulation.py:116), so a missing cell is ''; it must stop
    scoring, never be banded."""
    row = dict(WORKED, **{column: ""})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: doctrine :114/:127 'Both amounts REQUIRED' -- a NaN price_move_pct is "
    "banded Critical twice (price impact and reversal) instead of refused "
    "(cm002_risk_model.py:56-61 checks `is None` only; NaN fails every `r <` test and the "
    "`move <= 0` guard). Effect measured in CM002: an alert FLIP -- a row with no measured move, "
    "67% and 8 linked, is published 90 Critical. A NaN pct_of_market_volume or "
    "linked_accounts_count is refused only by accident at int() (cm002_risk_model.py:92, 104), "
    "which raises ValueError and loses the whole frame (market_manipulation.py:101). Measured: Failed: DID NOT RAISE <class 'ValueError'>"))
def test_a_nan_price_move_is_refused_not_alerted(governed):
    row = _row("T-NAN", 4.0, float("nan"), 67, 8, 28.74)
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


# ---------------------------------------------------------------- DEFECT: share truncated before the cut

@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "QUESTION (doctrine T:120 vs fc-07 schema.json integer typing, rule 9): "
    "Measured: AssertionError: assert ('High', 'Low') == ('Critical', 'Medium'). "
    "Doctrine :120 bands pct_of_market_volume '<= 45 -> High, otherwise (> 45) -> "
    "Critical' (and '<= 10 -> Low'); cm002_risk_model.py:92 truncates the share with "
    "int(float(...)) before comparing, so 45.5% is High and 10.5% is Low. Measured through the "
    "callable: a 45.5% share with price impact High (r 4) and the rest Critical scores 78 High "
    "and is NOT alerted; the doctrine's 24.5+22.5+18+18 = 83 alerts. (schema.json types the "
    "field 'integer'; the doctrine does not.) Measured: AssertionError ('High', 'Low') == "
    "('Critical', 'Medium'); T-SHARE scores 78 High"))
def test_a_fractional_market_share_is_banded_on_its_exact_value(governed):
    pos = _row("T-SHARE", 1, 4, 45.5, 8, 3.6)          # r 4 H, 45.5 C (> 45), 8 C, .9 C
    frames = _frames([pos, WORKED])                     # alerting control
    assert len(governed.score_all(**frames)) == 2
    assert (score_volume_concentration(45.5), score_volume_concentration(10.5)) == ("Critical", "Medium")
    assert sorted(governed.evaluate_market_manipulation(**frames)["subject_entity_id"]) == ["T-SHARE", "T-WORKED"]
