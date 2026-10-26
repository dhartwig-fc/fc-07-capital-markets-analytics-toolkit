"""TT-CM004 (night 10, wave C): CM004 Layering tested against its DOCTRINE.

Oracle: typologies/CM004_Layering.md -- "Exposure Scoring Framework" (weights 35/25/20/20 %,
band midpoints 15/45/70/90, weighted sum, half-up, boundary at 80; T:106-115), "Component
Banding Rules" (T:117-136), "Classification" (T:152-153), the ACC019 worked example
(T:140-150) and Business Logic step 7, "escalate at or above the threshold" (T:165). The
family standard operations/common/Risk_Scoring_Governance.md:57-62 gives the same
classification. Every expected value below is hand-worked from those, never pasted from an
engine run. Inputs are CONSTRUCTED here; no sample-data file is read and no sample entity
name is asserted.

Checks 2 (boundaries at every doctrine threshold) and 4 (a positive and a near-miss per
detection rule). The engine is loaded as fc-10 loads it: the scenario file by path.

Not pinned here, because the doctrine is silent or contradicts itself (QUESTIONS in the
night-10 report): whether a reversal-Medium row that scores 81 alerts (T:192-197's example
filter requires seconds_to_reversal <= 20, the framework does not); non-integer, negative
and out-of-range inputs; duplicate account_ref rows; the fixed risk_reason sentence.
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

from cm004_risk_model import (  # noqa: E402
    band_of, cm004_exposure_score, score_book_imbalance_created, score_order_to_trade_ratio,
    score_reversal_speed, score_staggered_order_levels,
)

SCENARIO = BASE_DIR / "scenarios" / "layering.py"

# T:108-115: weights 35/25/20/20 %, band midpoints 15/45/70/90, half-up, boundary at 80.
DOCTRINE_WEIGHTS = {
    "staggered_order_levels": Fraction(35, 100),
    "order_to_trade_ratio": Fraction(25, 100),
    "book_imbalance_created": Fraction(20, 100),
    "reversal_speed": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # T:153: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm004_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries
# At / just below / just above each cut-line. Decimal STRINGS sit beside floats wherever the
# cut-line is a decimal, so a value whose exact decimal is ON the line is examined as it
# arrives from a CSV (the N10-FLOATCUT class).

LEVELS = [  # T:122: <= 2 Low, <= 4 Medium, <= 7 High, otherwise (>= 8) Critical
    (1, "Low"), (2, "Low"), ("2", "Low"), (3, "Medium"), (4, "Medium"), ("4", "Medium"),
    (5, "High"), (7, "High"), ("7", "High"), (8, "Critical"), ("8", "Critical"), (9, "Critical"),
]
OTR = [  # T:125-126: r = placed / executed; r < 5 Low, < 15 Medium, < 40 High, otherwise Critical
    ((499, 100), "Low"), ((500, 100), "Medium"), (("45", "9"), "Medium"), ((501, 100), "Medium"),
    ((1499, 100), "Medium"), ((1500, 100), "High"), (("45", "3"), "High"), ((1501, 100), "High"),
    ((3999, 100), "High"), ((4000, 100), "Critical"), (("120", "3"), "Critical"), ((4001, 100), "Critical"),
]
IMBALANCE = [  # T:131: r < 0.10 Low, < 0.30 Medium, < 0.60 High, otherwise Critical
    (0.0999, "Low"), (0.10, "Medium"), ("0.10", "Medium"), ("0.1", "Medium"), (0.1001, "Medium"),
    (0.2999, "Medium"), (0.30, "High"), ("0.30", "High"), ("0.3", "High"), (0.3001, "High"),
    (0.5999, "High"), (0.60, "Critical"), ("0.60", "Critical"), ("0.6", "Critical"), (0.6001, "Critical"),
]
REVERSAL = [  # T:136: <= 5 Critical, <= 20 High, <= 60 Medium, otherwise (> 60) Low. Smaller is WORSE.
    (4.99, "Critical"), (5, "Critical"), ("5.0", "Critical"), (5.01, "High"),
    (19.99, "High"), (20, "High"), ("20.00", "High"), (20.01, "Medium"),
    (59.99, "Medium"), (60, "Medium"), ("60.0", "Medium"), (60.01, "Low"),
]


@pytest.mark.parametrize("levels,band", LEVELS)
def test_staggered_order_levels_boundaries(levels, band):
    assert score_staggered_order_levels(levels) == band


@pytest.mark.parametrize("args,band", OTR)
def test_order_to_trade_ratio_boundaries(args, band):
    assert score_order_to_trade_ratio(*args) == band


def test_order_to_trade_ratio_is_placed_over_executed():
    """T:125: r = orders_placed / orders_executed. 300 placed against 20 executed is
    r = 15 (High); inverted it would be 0.067 (Low)."""
    assert score_order_to_trade_ratio(300, 20) == "High"


@pytest.mark.parametrize("ratio,band", IMBALANCE)
def test_book_imbalance_created_boundaries(ratio, band):
    assert score_book_imbalance_created(ratio) == band


@pytest.mark.parametrize("seconds,band", REVERSAL)
def test_reversal_speed_boundaries(seconds, band):
    assert score_reversal_speed(seconds) == band


def test_boundary_tables_are_non_vacuous():
    for table in (LEVELS, OTR, IMBALANCE, REVERSAL):
        assert len(table) >= 12 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against the doctrine's weighted midpoint sum in EXACT
    arithmetic, half-up -- including the 32 whose exact total ends in .5."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, working = cm004_exposure_score(bands)
        expected = _doctrine_score(bands)
        assert (score, band) == (expected, _doctrine_band(expected)), combo
        assert {k: v["band"] for k, v in working["components"].items()} == bands
    assert halves == 32                                             # non-vacuity: the .5 cases were examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_no_band_combination_scores_exactly_eighty():
    """Recorded so the 80 cut-line test below is read correctly: the doctrine's own
    arithmetic cannot land on 80 (79 is followed by 81)."""
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- check 4: through the callable

def _frames(rows):
    """Constructed orders + one venue record per account."""
    orders = pd.DataFrame([{"trader_name": "Trader " + r["account_ref"], "instrument": "INSTR-T",
                            "venue_operator_name": "Venue Op T", **r} for r in rows])
    venues = pd.DataFrame([{"venue_operator_name": "Venue Op T", "account_ref": r["account_ref"],
                            "jurisdiction": "UNKNOWN", "relationship": "direct", "prior_alerts": 0}
                           for r in rows])
    return {"orders": orders, "venues": venues}


def _row(ref, levels, placed, executed, imbalance, seconds):
    return {"account_ref": ref, "distinct_price_levels": levels, "orders_placed": placed,
            "orders_executed": executed, "imbalance_ratio": imbalance, "seconds_to_reversal": seconds}


# T:140-150, the worked example: 10 levels C, 300/5 (r 60) C, 0.75 C, 3 s C -> 90 Critical.
WORKED = _row("T-WORKED", 10, 300, 5, 0.75, 3)

# Per detection rule: the three OTHER components held Critical (worth 58.5 when the rule is
# staggered levels, 67.5 for order-to-trade, 72 for imbalance and reversal), the rule's own
# input set at the cut-line that keeps the total >= 80 (positive) and one step below it:
#   levels     High (5)       24.5 + 58.5 = 83 alert;   Medium (4)       15.75 + 58.5 = 74.25 -> 74
#   OTR        High (r 15)    17.5 + 67.5 = 85 alert;   Medium (r 14.99) 11.25 + 67.5 = 78.75 -> 79
#   imbalance  Medium (0.10)  9 + 72 = 81 alert;        Low (0.0999)     3 + 72 = 75
PER_RULE = {
    "staggered_order_levels": (_row("T-LVL-POS", 5, 300, 5, 0.75, 3), 83, "Critical",
                               _row("T-LVL-NM", 4, 300, 5, 0.75, 3), 74, "High"),
    "order_to_trade_ratio": (_row("T-OTR-POS", 10, 1500, 100, 0.75, 3), 85, "Critical",
                             _row("T-OTR-NM", 10, 1499, 100, 0.75, 3), 79, "High"),
    "book_imbalance_created": (_row("T-IMB-POS", 10, 300, 5, "0.10", 3), 81, "Critical",
                               _row("T-IMB-NM", 10, 300, 5, 0.0999, 3), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_layering(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")
    assert [row[c] for c in ("staggered_order_levels_band", "order_to_trade_ratio_band",
                             "book_imbalance_created_band", "reversal_speed_band")] == ["Critical"] * 4


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
    assert list(governed.evaluate_layering(**frames)["subject_entity_id"]) == [pos["account_ref"]]


def test_reversal_speed_cut_lines_score_as_the_framework_computes(governed):
    """Reversal High (20 s): 14 + 72 = 86, alerts (and also passes T:192-197's example
    filter, seconds <= 20). Reversal Medium (60 s): 9 + 72 = 81 Critical; Low (60.01 s):
    3 + 72 = 75 High. Whether the 81 row alerts is a QUESTION (the example filter excludes
    it, the framework does not), so only its score and band are pinned."""
    frames = _frames([_row("T-REV-H", 10, 300, 5, 0.75, 20), _row("T-REV-M", 10, 300, 5, 0.75, 60),
                      _row("T-REV-L", 10, 300, 5, 0.75, 60.01)])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 3
    got = {k: (scored.loc[k, "exposure_score"], scored.loc[k, "exposure_band"]) for k in scored.index}
    assert got == {"T-REV-H": (86, "Critical"), "T-REV-M": (81, "Critical"), "T-REV-L": (75, "High")}
    assert "T-REV-H" in set(governed.evaluate_layering(**frames)["subject_entity_id"])
    assert "T-REV-L" not in set(governed.evaluate_layering(**frames)["subject_entity_id"])


def test_market_maker_near_miss_does_not_alert(governed):
    """Genuine two-sided liquidity provision (T:241-242): 2 levels L, 40 placed / 10 executed
    (r 4) L, 0.05 L, 90 s L -> 15 Low; beside the worked example as the alerting control."""
    frames = _frames([_row("T-MM", 2, 40, 10, 0.05, 90), WORKED])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-MM", "exposure_score"], scored.loc["T-MM", "exposure_band"]) == (15, "Low")
    assert list(governed.evaluate_layering(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_partial_pattern_wide_levels_alone_does_not_alert(governed):
    """Many levels without disproportionate order flow, imbalance or fast reversal:
    12 levels C, r 2 L, 0.05 L, 300 s L -> 31.5 + 3.75 + 3 + 3 = 41.25 -> 41 Medium."""
    frames = _frames([_row("T-PART", 12, 20, 10, 0.05, 300), WORKED])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-PART", "exposure_score"], scored.loc["T-PART", "exposure_band"]) == (41, "Medium")
    assert list(governed.evaluate_layering(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_layering(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 7 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """T:115 'boundary at 80', T:165 'escalate at or above the threshold'. No band
    combination scores exactly 80, so the cut-line is constructed by fixing the model's
    score; the callable's own filter decides."""
    real = governed.cm004_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm004_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                  # non-vacuity: one row scored
    assert (len(governed.evaluate_layering(**frames)) == 1) is alerts


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

def test_a_missing_level_count_refuses_the_row(governed):
    """T:120 'distinct_price_levels REQUIRED'. A NaN count is refused (by the int() cast,
    not by _require -- recorded under D043)."""
    with pytest.raises(ValueError):
        governed.score_all(**_frames([_row("T-NOLVL", float("nan"), 300, 5, 0.75, 3)]))


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: T:129 'imbalance_ratio REQUIRED' -- a NaN imbalance is banded "
    "Critical, not refused (cm004_risk_model.py:105-112: _require checks only `is None`, and "
    "every `r < x` is False for NaN). Effect measured: the row scores 90 Critical and ALERTS; "
    "with the imbalance Low it would score 75 and not alert"))
def test_a_missing_imbalance_is_refused_not_banded_critical(governed):
    frames = _frames([_row("T-NOIMB", 10, 300, 5, float("nan"), 3)])
    with pytest.raises(ValueError):
        governed.evaluate_layering(**frames)
