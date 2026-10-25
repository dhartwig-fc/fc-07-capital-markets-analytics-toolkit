"""TT-CM001 (night 9, wave A): CM001 Insider Trading tested against its DOCTRINE.

Oracle: typologies/CM001_Insider_Trading.md ("Exposure Scoring Framework",
"Component Banding Rules", "Classification", the worked example) and the
signed-off expected-outcome sheet SIT Expected Outcomes/CM001.md (2026-10-21),
including its resolved point CM001.3 (R1: the scoring band table governs over
the doctrine's Python example). Every expected value below is hand-worked from
those, never pasted from an engine run. Inputs are CONSTRUCTED here; no
sample-data file is read and no sample entity name is asserted.

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

from cm001_risk_model import (  # noqa: E402
    RiskModelError, band_of, cm001_exposure_score, score_information_access_linkage,
    score_pre_event_position_build, score_profit_realisation, score_timing_proximity_to_event,
)

SCENARIO = BASE_DIR / "scenarios" / "insider_trading.py"

# The doctrine's own numbers (CM001_Insider_Trading.md:100-109): weights
# 35/25/20/20 %, band midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.
DOCTRINE_WEIGHTS = {
    "pre_event_position_build": Fraction(35, 100),
    "timing_proximity_to_event": Fraction(25, 100),
    "information_access_linkage": Fraction(20, 100),
    "profit_realisation": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
DOCTRINE_THRESHOLD = 80


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # Classification (CM001_Insider_Trading.md:145): 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm001_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries
# Each row: (raw inputs, expected band), at / just below / just above each cut-line.

BUILD = [  # r = increase / normal; r < 0.10 Low, < 0.30 Medium, < 0.60 High, else Critical (doctrine :115)
    ((999, 10000), "Low"), ((1000, 10000), "Medium"), ((1001, 10000), "Medium"),
    ((2999, 10000), "Medium"), ((3000, 10000), "High"), ((3001, 10000), "High"),
    ((5999, 10000), "High"), ((6000, 10000), "Critical"), ((6001, 10000), "Critical"),
]
TIMING = [  # days_before_event: <= 1 Critical, <= 3 High, <= 7 Medium, > 7 Low (doctrine :119)
    (0, "Critical"), (1, "Critical"), (2, "High"),
    (3, "High"), (4, "Medium"),
    (7, "Medium"), (8, "Low"), (30, "Low"),
]
LINKAGE = [  # contact_events_90d: <= 2 Low, <= 5 Medium, <= 9 High, >= 10 Critical (doctrine :124)
    (0, "Low"), (2, "Low"), (3, "Medium"),
    (5, "Medium"), (6, "High"),
    (9, "High"), (10, "Critical"), (11, "Critical"),
]
PROFIT = [  # r = pnl / entry value; < 0.25 Low, < 0.50 Medium, < 0.80 High, else Critical (doctrine :128)
    ((2499, 10000), "Low"), ((2500, 10000), "Medium"), ((2501, 10000), "Medium"),
    ((4999, 10000), "Medium"), ((5000, 10000), "High"), ((5001, 10000), "High"),
    ((7999, 10000), "High"), ((8000, 10000), "Critical"), ((8001, 10000), "Critical"),
]


@pytest.mark.parametrize("args,band", BUILD)
def test_pre_event_position_build_boundaries(args, band):
    assert score_pre_event_position_build(*args) == band


def test_position_build_is_increase_over_normal_not_the_inverse():
    """Doctrine: r = pre_event_position_increase / normal_average_position.
    2,000 built on a 10,000 normal is r = 0.2 (Medium); inverted it would be 5.0 (Critical)."""
    assert score_pre_event_position_build(2000, 10000) == "Medium"


@pytest.mark.parametrize("days,band", TIMING)
def test_timing_proximity_boundaries(days, band):
    assert score_timing_proximity_to_event(days) == band


@pytest.mark.parametrize("contacts,band", LINKAGE)
def test_information_access_linkage_boundaries(contacts, band):
    assert score_information_access_linkage(contacts) == band


@pytest.mark.parametrize("args,band", PROFIT)
def test_profit_realisation_boundaries(args, band):
    assert score_profit_realisation(*args) == band


def test_profit_realisation_is_pnl_over_entry_value_not_the_inverse():
    """Doctrine: r = realized_pnl / position_value_at_entry. 3,000 realised on a
    10,000 entry is r = 0.30 (Medium); inverted it would be 3.33 (Critical)."""
    assert score_profit_realisation(3000, 10000) == "Medium"


def test_boundary_tables_are_non_vacuous():
    for table in (BUILD, TIMING, LINKAGE, PROFIT):
        assert len(table) >= 8 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against the doctrine's weighted midpoint sum in
    EXACT arithmetic, half-up -- including the combinations whose exact total
    ends in .5, where half-up and half-even (or float drift) disagree."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, _ = cm001_exposure_score(bands)
        assert (score, band) == (_doctrine_score(bands), _doctrine_band(_doctrine_score(bands))), combo
    assert halves > 0                                               # non-vacuity: the .5 cases were examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_all_low_background_scores_fifteen():
    """Sheet: Background -- all-Low = 15 (midpoint 15 x weights summing to 100%)."""
    bands = dict.fromkeys(DOCTRINE_WEIGHTS, "Low")
    assert cm001_exposure_score(bands)[:2] == (15, "Low")


# ---------------------------------------------------------------- check 4: through the callable

def _row(ref, normal, increase, days, contacts, entry, pnl):
    return {"trader_name": "Trader " + ref, "account_ref": ref, "desk": "Desk T", "issuer_name": "Issuer T",
            "normal_average_position": normal, "pre_event_position_increase": increase,
            "days_before_event": days, "contact_events_90d": contacts,
            "position_value_at_entry": entry, "realized_pnl": pnl, "information_source_name": "Source " + ref}


def _frames(rows):
    """Constructed trading accounts + a matching information-source record per account."""
    sources = pd.DataFrame([{"information_source_name": r["information_source_name"],
                             "account_ref": r["account_ref"], "role": "Constructed role",
                             "employer": "Issuer T", "jurisdiction": "UNKNOWN",
                             "relationship": "constructed", "prior_alerts": 0} for r in rows])
    return {"trading_accounts": pd.DataFrame(rows), "information_sources": sources}


# The doctrine's worked example (CM001_Insider_Trading.md:132-141): 39,600 of a
# 60,000 normal (0.660 Crit), 0 days (Crit), 10 contacts (Crit), 2,090,400 on a
# 2,400,000 entry (0.871 Crit) -> 90 Critical.
WORKED = _row("T-WORKED", 60000, 39600, 0, 10, 2400000, 2090400)

# Per detection rule: the three OTHER components held Critical (build 0.9, 0 days,
# 12 contacts, profit 0.9), and the rule's own input at the cut-line that keeps the
# total >= 80 (positive) and one unit across it (near-miss). Hand-worked:
#   build    High 70*.35=24.5 + 58.5 (=90*.25+90*.2+90*.2) = 83 alert; Medium 15.75+58.5 = 74.25 -> 74
#   timing   High 70*.25=17.5 + 67.5 (=31.5+18+18) = 85 alert;          Medium 11.25+67.5 = 78.75 -> 79
#   linkage  Medium 45*.2=9 + 72 (=31.5+22.5+18) = 81 alert;            Low 3+72 = 75
#   profit   Medium 9 + 72 = 81 alert;                                  Low 3+72 = 75
PER_RULE = {
    "pre_event_position_build": (
        _row("T-BLD-POS", 10000, 3000, 0, 12, 10000, 9000), 83, "Critical",
        _row("T-BLD-NM", 10000, 2999, 0, 12, 10000, 9000), 74, "High"),
    "timing_proximity_to_event": (
        _row("T-TIM-POS", 10000, 9000, 3, 12, 10000, 9000), 85, "Critical",
        _row("T-TIM-NM", 10000, 9000, 4, 12, 10000, 9000), 79, "High"),
    "information_access_linkage": (
        _row("T-LNK-POS", 10000, 9000, 0, 3, 10000, 9000), 81, "Critical",
        _row("T-LNK-NM", 10000, 9000, 0, 2, 10000, 9000), 75, "High"),
    "profit_realisation": (
        _row("T-PRF-POS", 10000, 9000, 0, 12, 10000, 2500), 81, "Critical",
        _row("T-PRF-NM", 10000, 9000, 0, 12, 10000, 2499), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_insider_trading(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")
    assert [row[c] for c in ("pre_event_position_build_band", "timing_proximity_to_event_band",
                             "information_access_linkage_band", "profit_realisation_band")] == ["Critical"] * 4


def test_the_subject_is_the_trading_account(governed):
    """Sheet: the subject is the account (fc-10 batch row: subject_entity_id,
    identity mapping). The account reference, not the trader's display name."""
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
    alerted = list(governed.evaluate_insider_trading(**frames)["subject_entity_id"])
    assert alerted == [pos["account_ref"]]                          # the positive, and only it


def test_band_table_governs_over_the_python_example(governed):
    """CM001.3 (R1, owner 2026-10-21): the band table governs over the doctrine's
    Python example (which also demands contacts >= 6 and days <= 3). Three
    contacts (Medium) with the rest Critical is 31.5+22.5+9+18 = 81: it MUST
    alert, although the example's `contact_events_90d >= 6` would drop it."""
    pos = PER_RULE["information_access_linkage"][0]
    assert pos["contact_events_90d"] < 6
    assert list(governed.evaluate_insider_trading(**_frames([pos]))["subject_entity_id"]) == [pos["account_ref"]]


def test_no_linkage_near_miss_does_not_alert(governed):
    """Sheet near-miss: position build and profit without an information-access
    linkage (doctrine: linkage 'corroborates'). Build 0.9 Crit, 0 days Crit,
    0 contacts Low, profit 0.9 Crit: 31.5+22.5+3+18 = 75 -> High, below 80."""
    frames = _frames([_row("T-NOLINK", 10000, 9000, 0, 0, 10000, 9000), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-NOLINK", "exposure_score"], scored.loc["T-NOLINK", "exposure_band"]) == (75, "High")
    assert list(governed.evaluate_insider_trading(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_ordinary_directional_bet_does_not_alert(governed):
    """Sheet near-miss: an ordinary directional bet at normal size, far from the
    event, that happened to pay. Build 0.05 Low, 30 days Low, 1 contact Low,
    profit 0.6 High: 5.25+3.75+3+14 = 26 -> Low."""
    frames = _frames([_row("T-BET", 10000, 500, 30, 1, 10000, 6000), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-BET", "exposure_score"], scored.loc["T-BET", "exposure_band"]) == (26, "Low")
    assert list(governed.evaluate_insider_trading(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_normal_coverage_contacts_alone_do_not_alert(governed):
    """Sheet near-miss: frequent contacts consistent with normal coverage
    relationships must not alert on that basis. Build 0.05 Low, 30 days Low,
    12 contacts Critical, profit 0.1 Low: 5.25+3.75+18+3 = 30 -> Medium."""
    frames = _frames([_row("T-COVER", 10000, 500, 30, 12, 10000, 1000), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-COVER", "exposure_score"], scored.loc["T-COVER", "exposure_band"]) == (30, "Medium")
    assert list(governed.evaluate_insider_trading(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_background_normal_positions_far_from_any_event_score_fifteen(governed):
    """Sheet background: normal-size positions, no event proximity -> all Low = 15."""
    frames = _frames([_row("T-BG", 10000, 100, 60, 0, 10000, 100), WORKED])  # alerting control
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-BG", "exposure_score"], scored.loc["T-BG", "exposure_band"]) == (15, "Low")
    assert list(governed.evaluate_insider_trading(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_insider_trading(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """Doctrine: 'escalate at or above the threshold', 'boundary at 80'. No band
    combination scores exactly 80 (see below), so the cut-line itself is
    constructed by fixing the model's score; the callable's own filter decides."""
    real = governed.cm001_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm001_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                   # non-vacuity: one row scored
    assert (len(governed.evaluate_insider_trading(**frames)) == 1) is alerts


def test_no_band_combination_scores_exactly_eighty():
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

@pytest.mark.parametrize("column", ["pre_event_position_increase", "normal_average_position",
                                    "days_before_event", "contact_events_90d",
                                    "position_value_at_entry", "realized_pnl"])
def test_the_callable_refuses_a_row_with_a_missing_required_input(governed, column):
    """Doctrine: every component input is REQUIRED (CM001_Insider_Trading.md:114,
    118, 122, 127); sheet FN: 'a case missed because one required input was
    absent'. A NaN in the frame must stop scoring, never be banded."""
    row = dict(WORKED, **{column: float("nan")})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "DEFECT: doctrine 'Both amounts REQUIRED' (CM001_Insider_Trading.md:114) -- a NaN "
    "pre_event_position_increase is banded Critical, not refused (cm001_risk_model.py:55-61, 73-84: "
    "_require checks only `is None`; NaN fails every `r <` test). Sibling: CM003 D1"))
def test_a_nan_position_increase_is_refused_not_banded():
    with pytest.raises(RiskModelError):
        score_pre_event_position_build(float("nan"), 10000)


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "DEFECT: doctrine 'Both amounts REQUIRED' (CM001_Insider_Trading.md:114) -- a NaN "
    "normal_average_position is banded Critical, not refused (cm001_risk_model.py:55-61, 74-84: "
    "the `normal <= 0` guard is False for NaN). Sibling: CM003 D1"))
def test_a_nan_normal_position_is_refused_not_banded():
    with pytest.raises(RiskModelError):
        score_pre_event_position_build(1000, float("nan"))


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "DEFECT: doctrine 'Both amounts REQUIRED' (CM001_Insider_Trading.md:127) -- a NaN realized_pnl "
    "is banded Critical, not refused (cm001_risk_model.py:55-61, 117-128). Sibling: CM003 D1"))
def test_a_nan_realised_pnl_is_refused_not_banded():
    with pytest.raises(RiskModelError):
        score_profit_realisation(float("nan"), 10000)


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "DEFECT: doctrine 'Both amounts REQUIRED' (CM001_Insider_Trading.md:127) -- a NaN "
    "position_value_at_entry is banded Critical, not refused (cm001_risk_model.py:55-61, 118-128: "
    "the `value <= 0` guard is False for NaN). Sibling: CM003 D1"))
def test_a_nan_entry_value_is_refused_not_banded():
    with pytest.raises(RiskModelError):
        score_profit_realisation(1000, float("nan"))
