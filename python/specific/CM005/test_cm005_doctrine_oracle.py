"""TT-CM005 (night 9, wave A): CM005 Wash Trading tested against its DOCTRINE.

Oracle: typologies/CM005_Wash_Trading.md ("Exposure Scoring Framework" :106-115,
"Component Banding Rules" :117-136, "Classification" :152-153, the worked example
:140-150, "Business Logic" step 7 :165) and the signed-off expected-outcome sheet
SIT Expected Outcomes/CM005.md (2026-10-21), including its resolved point CM005.2
(R1: the scoring band table governs over the doctrine's Python example). Every
expected value below is hand-worked from those, never pasted from an engine run.
Inputs are CONSTRUCTED here; no sample-data file is read and no sample entity
name is asserted.

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

from cm005_risk_model import (  # noqa: E402
    RiskModelError, band_of, cm005_exposure_score, score_beneficial_ownership_overlap,
    score_counterparty_concentration, score_self_match_ratio, score_volume_inflation,
)

SCENARIO = BASE_DIR / "scenarios" / "wash_trading.py"

# The doctrine's own numbers (CM005_Wash_Trading.md:108-115): weights 35/25/20/20 %,
# band midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.
DOCTRINE_WEIGHTS = {
    "self_match_ratio": Fraction(35, 100),
    "beneficial_ownership_overlap": Fraction(25, 100),
    "volume_inflation": Fraction(20, 100),
    "counterparty_concentration": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
BAND_COLUMNS = ("self_match_ratio_band", "beneficial_ownership_overlap_band",
                "volume_inflation_band", "counterparty_concentration_band")


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # Classification (CM005_Wash_Trading.md:153): 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm005_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries
# Each row: (raw inputs, expected band), at / just below / just above each cut-line.

SELF_MATCH = [  # r = self_matched / total; r < 0.10 Low, < 0.30 Medium, < 0.60 High, else Critical (:121)
    ((9999, 100000), "Low"), ((10000, 100000), "Medium"), ((10001, 100000), "Medium"),
    ((29999, 100000), "Medium"), ((30000, 100000), "High"), ((30001, 100000), "High"),
    ((59999, 100000), "High"), ((60000, 100000), "Critical"), ((60001, 100000), "Critical"),
]
OVERLAP = [  # overlap_score 0-100: <= 20 Low, <= 50 Medium, <= 80 High, > 80 Critical (:126)
    (0, "Low"), (20, "Low"), (21, "Medium"),
    (50, "Medium"), (51, "High"),
    (80, "High"), (81, "Critical"), (100, "Critical"),
]
INFLATION = [  # r = reported / genuine; r < 1.2 Low, < 1.5 Medium, < 2.5 High, else Critical (:130)
    ((11999, 10000), "Low"), ((12000, 10000), "Medium"), ((12001, 10000), "Medium"),
    ((14999, 10000), "Medium"), ((15000, 10000), "High"), ((15001, 10000), "High"),
    ((24999, 10000), "High"), ((25000, 10000), "Critical"), ((25001, 10000), "Critical"),
]
CONCENTRATION = [  # distinct_counterparties, inverted: <= 1 Critical, <= 2 High, <= 4 Medium, >= 5 Low (:136)
    (1, "Critical"), (2, "High"), (3, "Medium"),
    (4, "Medium"), (5, "Low"), (6, "Low"), (40, "Low"),
]


@pytest.mark.parametrize("args,band", SELF_MATCH)
def test_self_match_ratio_boundaries(args, band):
    assert score_self_match_ratio(*args) == band


def test_self_match_is_matched_over_total_not_the_inverse():
    """Doctrine: r = self_matched_volume / total_volume. 20,000 matched of
    100,000 is r = 0.2 (Medium); inverted it would be 5.0 (Critical)."""
    assert score_self_match_ratio(20000, 100000) == "Medium"


@pytest.mark.parametrize("overlap,band", OVERLAP)
def test_beneficial_ownership_overlap_boundaries(overlap, band):
    assert score_beneficial_ownership_overlap(overlap) == band


@pytest.mark.parametrize("args,band", INFLATION)
def test_volume_inflation_boundaries(args, band):
    assert score_volume_inflation(*args) == band


def test_volume_inflation_is_reported_over_genuine_not_the_inverse():
    """Doctrine: r = reported_volume / genuine_economic_volume. 13,000 reported on
    10,000 genuine is r = 1.3 (Medium); inverted it would be 0.77 (Low)."""
    assert score_volume_inflation(13000, 10000) == "Medium"


@pytest.mark.parametrize("n,band", CONCENTRATION)
def test_counterparty_concentration_boundaries(n, band):
    assert score_counterparty_concentration(n) == band


def test_boundary_tables_are_non_vacuous():
    for table in (SELF_MATCH, OVERLAP, INFLATION, CONCENTRATION):
        assert len(table) >= 7 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


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
        score, band, _ = cm005_exposure_score(bands)
        assert (score, band) == (_doctrine_score(bands), _doctrine_band(_doctrine_score(bands))), combo
    assert halves > 0                                               # non-vacuity: the .5 cases were examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_all_low_background_scores_fifteen():
    """Sheet: Background -- all-Low = 15 (midpoint 15 x weights summing to 100%)."""
    assert cm005_exposure_score(dict.fromkeys(DOCTRINE_WEIGHTS, "Low"))[:2] == (15, "Low")


# ---------------------------------------------------------------- check 4: through the callable

def _row(ref, matched, total, overlap, reported, genuine, counterparties):
    return {"trader_name": "Trader " + ref, "account_ref": ref, "instrument": "Instrument " + ref,
            "self_matched_volume": matched, "total_volume": total, "overlap_score": overlap,
            "reported_volume": reported, "genuine_economic_volume": genuine,
            "distinct_counterparties": counterparties, "clearing_broker_name": "Broker " + ref}


def _frames(rows):
    """Constructed trades + the matching counterparty record per account."""
    cps = pd.DataFrame([{"clearing_broker_name": r["clearing_broker_name"], "account_ref": r["account_ref"],
                         "jurisdiction": "UNKNOWN", "relationship": "Clearing broker", "prior_alerts": 0}
                        for r in rows])
    return {"trades": pd.DataFrame(rows), "counterparties": cps}


# The doctrine's worked example (CM005_Wash_Trading.md:140-150): 450,000 of 500,000
# self-matched (0.900 Crit), overlap 95 (Crit), 480,000 reported on 150,000 genuine
# (3.200 Crit), 1 counterparty (Crit) -> 90 Critical.
WORKED = _row("T-WORKED", 450000, 500000, 95, 480000, 150000, 1)

# Per detection rule: the three OTHER components held Critical (self-match 0.9,
# overlap 95, inflation 3.0, 1 counterparty), and the rule's own input at the
# cut-line that keeps the total >= 80 (positive) and one unit across it (near-miss).
# Hand-worked:
#   self-match  High 70*.35=24.5 + 58.5 (=90*.25+90*.2+90*.2) = 83 alert; Medium 15.75+58.5 = 74.25 -> 74
#   overlap     High 70*.25=17.5 + 67.5 (=31.5+18+18) = 85 alert;          Medium 11.25+67.5 = 78.75 -> 79
#   inflation   Medium 45*.2=9 + 72 (=31.5+22.5+18) = 81 alert;            Low 3+72 = 75
#   concentr.   Medium 9 + 72 = 81 alert;                                  Low 3+72 = 75
PER_RULE = {
    "self_match_ratio": (
        _row("T-SM-POS", 3000, 10000, 95, 30000, 10000, 1), 83, "Critical",
        _row("T-SM-NM", 2999, 10000, 95, 30000, 10000, 1), 74, "High"),
    "beneficial_ownership_overlap": (
        _row("T-BO-POS", 9000, 10000, 51, 30000, 10000, 1), 85, "Critical",
        _row("T-BO-NM", 9000, 10000, 50, 30000, 10000, 1), 79, "High"),
    "volume_inflation": (
        _row("T-VI-POS", 9000, 10000, 95, 12000, 10000, 1), 81, "Critical",
        _row("T-VI-NM", 9000, 10000, 95, 11999, 10000, 1), 75, "High"),
    "counterparty_concentration": (
        _row("T-CC-POS", 9000, 10000, 95, 30000, 10000, 4), 81, "Critical",
        _row("T-CC-NM", 9000, 10000, 95, 30000, 10000, 5), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_wash_trading(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")
    assert [row[c] for c in BAND_COLUMNS] == ["Critical"] * 4


def test_the_subject_is_the_trading_account(governed):
    """Sheet / fc-10 batch row: the subject is the account (subject_entity_id,
    identity mapping) -- the account reference, not the trader's display name."""
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
    alerted = list(governed.evaluate_wash_trading(**frames)["subject_entity_id"])
    assert alerted == [pos["account_ref"]]                          # the positive, and only it


def test_band_table_governs_over_the_python_example(governed):
    """CM005.2 (R1, owner 2026-10-21): the band table governs over the doctrine's
    Python example (:191-198), which also demands overlap >= 55 and <= 2
    counterparties. Overlap 51 (High) with the rest Critical is 85, and 4
    counterparties (Medium) with the rest Critical is 81: both MUST alert,
    although the example would drop each."""
    overlap_pos = PER_RULE["beneficial_ownership_overlap"][0]
    spread_pos = PER_RULE["counterparty_concentration"][0]
    assert overlap_pos["overlap_score"] < 55 and spread_pos["distinct_counterparties"] > 2
    got = set(governed.evaluate_wash_trading(**_frames([overlap_pos, spread_pos]))["subject_entity_id"])
    assert got == {overlap_pos["account_ref"], spread_pos["account_ref"]}


def test_ordinary_market_making_does_not_alert(governed):
    """Sheet near-miss: ordinary two-sided market making -- some self-match, a
    broad counterparty spread (>= 5), arm's-length ownership. Self-match 0.2
    Medium, overlap 10 Low, inflation 1.05 Low, 12 counterparties Low:
    15.75+3.75+3+3 = 25.5 -> 26 (half-up) Low."""
    frames = _frames([_row("T-MM", 2000, 10000, 10, 10500, 10000, 12)])
    scored = governed.score_all(**frames)
    assert (scored.iloc[0]["exposure_score"], scored.iloc[0]["exposure_band"]) == (26, "Low")
    assert governed.evaluate_wash_trading(**frames).empty


@pytest.mark.parametrize("matched,score", [(500, 30), (2000, 41), (4000, 49), (9000, 56)])
def test_concentration_without_overlap_or_inflation_does_not_alert(governed, matched, score):
    """Sheet near-miss: concentrated counterparties (1, Critical) but no documented
    overlap (0, Low) and no inflation (1.0, Low) -- partial pattern. Whatever the
    self-match band, the doctrine total stays under 80: Low 5.25+24.75 = 30,
    Medium 15.75+24.75 = 40.5 -> 41, High 24.5+24.75 = 49.25 -> 49, Critical
    31.5+24.75 = 56.25 -> 56."""
    frames = _frames([_row("T-PART", matched, 10000, 0, 10000, 10000, 1)])
    scored = governed.score_all(**frames)
    assert scored.iloc[0]["exposure_score"] == score
    assert governed.evaluate_wash_trading(**frames).empty


def test_background_diverse_counterparties_no_self_match_scores_fifteen(governed):
    """Sheet background: diverse counterparties, no self-match -> all Low = 15."""
    frames = _frames([_row("T-BG", 0, 10000, 0, 10000, 10000, 25)])
    scored = governed.score_all(**frames)
    assert (scored.iloc[0]["exposure_score"], scored.iloc[0]["exposure_band"]) == (15, "Low")
    assert governed.evaluate_wash_trading(**frames).empty


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_wash_trading(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """Doctrine: 'escalate at or above the threshold', 'boundary at 80'. No band
    combination scores exactly 80 (see below), so the cut-line itself is
    constructed by fixing the model's score; the callable's own filter decides."""
    real = governed.cm005_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm005_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                   # non-vacuity: one row scored
    assert (len(governed.evaluate_wash_trading(**frames)) == 1) is alerts


def test_no_band_combination_scores_exactly_eighty():
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

@pytest.mark.parametrize("column", ["self_matched_volume", "total_volume", "overlap_score",
                                    "reported_volume", "genuine_economic_volume", "distinct_counterparties"])
def test_the_callable_refuses_a_row_with_a_missing_required_input(governed, column):
    """Doctrine: every component input is REQUIRED (CM005_Wash_Trading.md:120, 124,
    129, 133). A NaN in the frame must stop scoring, never be banded."""
    row = dict(WORKED, **{column: float("nan")})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


@pytest.mark.parametrize("args", [(float("nan"), 100000), (90000, float("nan"))],
                         ids=["nan-self-matched", "nan-total"])
@pytest.mark.xfail(strict=True, reason=(
    "DEFECT: doctrine 'Both amounts REQUIRED' (CM005_Wash_Trading.md:120) -- a NaN self-match "
    "input is banded Critical, not refused (cm005_risk_model.py:60-65, 78-89: _require checks only "
    "`is None`; `total <= 0` is False for NaN and NaN fails every `r <` test). Siblings: CM001 D1, "
    "CM003 D1, BA001, BA004, TBML002U, SAN001"))
def test_a_nan_self_match_input_is_refused_not_banded(args):
    with pytest.raises(RiskModelError):
        score_self_match_ratio(*args)


@pytest.mark.parametrize("args", [(float("nan"), 10000), (30000, float("nan"))],
                         ids=["nan-reported", "nan-genuine"])
@pytest.mark.xfail(strict=True, reason=(
    "DEFECT: doctrine 'Both amounts REQUIRED' (CM005_Wash_Trading.md:129) -- a NaN volume-inflation "
    "input is banded Critical, not refused (cm005_risk_model.py:60-65, 108-119: _require checks only "
    "`is None`; `genuine <= 0` is False for NaN). Siblings: CM001 D1, CM003 D1, BA001, BA004, "
    "TBML002U, SAN001"))
def test_a_nan_volume_inflation_input_is_refused_not_banded(args):
    with pytest.raises(RiskModelError):
        score_volume_inflation(*args)
