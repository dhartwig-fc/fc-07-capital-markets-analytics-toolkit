"""TT-CM007 (night 10, wave C): CM007 Pump and Dump tested against its DOCTRINE.

Oracle: typologies/CM007_Pump_and_Dump.md (T) -- "Exposure Scoring Framework" (T:104-113:
weights 35/25/20/20 %, midpoints 15/45/70/90, weighted sum, half-up, boundary at 80),
"Component Banding Rules" (T:115-132), the worked example (T:136-146), "Classification"
(T:153), "Business Logic" step 7 (T:165: escalate at or above the threshold) -- and the
owner's oracle rules of 2026-10-21: R1 (a Python example that disagrees with the band
table is illustrative; the band table governs) and R3 (a near miss must not alert). The
family standard (operations/common/Risk_Scoring_Governance.md:57-62, Data_Dictionary.md
weights 0.35/0.25/0.20/0.20) agrees with T. No signed-off expected-outcome sheet exists
for CM007 (wave C). Every expected value below is hand-worked from T, never pasted from
an engine run. Inputs are CONSTRUCTED; no sample-data file is read and no sample entity
name is asserted.

Checks 2 (boundaries at every doctrine cut-line, with inputs whose EXACT value lands on
the line) and 4 (a positive and a near-miss per component rule, each in the same call as
the alerting positive). The engine is loaded as fc-10 loads it: the scenario file by path.

Not pinned here (doctrine-silent, QUESTIONS in the TT-CM007 report): negative or >100 %
inputs, fractional post counts (int() truncation), duplicate account_ref rows, a promoter
record whose id disagrees with the account row, the fixed risk_reason sentence on
non-alert rows, the dominant-driver tie-break, and aggregation across the promoter's
connections (T:75 NS001).
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

from cm007_risk_model import (  # noqa: E402
    RiskModelError, band_of, cm007_exposure_score, score_accumulation_concentration,
    score_distribution_into_retail, score_price_inflation, score_promotional_coordination,
)

SCENARIO = BASE_DIR / "scenarios" / "pump_and_dump.py"

# T:106-113: weights 35/25/20/20 %, band midpoints 15/45/70/90, half-up, boundary at 80.
DOCTRINE_WEIGHTS = {
    "accumulation_concentration": Fraction(35, 100),
    "promotional_coordination": Fraction(25, 100),
    "price_inflation": Fraction(20, 100),
    "distribution_into_retail": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
BAND_COLUMNS = tuple(k + "_band" for k in DOCTRINE_WEIGHTS)


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                       # half-up, exact arithmetic


def _doctrine_band(score):
    # T:153: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm007_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries
# Inputs are decimal STRINGS, as the engine receives them from a CSV read with dtype=str.

ACCUMULATION = [  # T:119: <= 10 Low, <= 25 Medium, <= 45 High, otherwise (> 45) Critical
    ("0", "Low"), ("9.99", "Low"), ("10", "Low"), ("10.01", "Medium"), ("11", "Medium"),
    ("25", "Medium"), ("25.01", "High"), ("26", "High"),
    ("45", "High"), ("45.01", "Critical"), ("46", "Critical"), ("68", "Critical"),
]
COORDINATION = [  # T:124: <= 2 Low, <= 5 Medium, <= 9 High, otherwise (>= 10) Critical
    ("0", "Low"), ("2", "Low"), ("3", "Medium"), ("5", "Medium"), ("6", "High"),
    ("9", "High"), ("10", "Critical"), ("14", "Critical"),
]
PRICE = [  # T:128: r = peak / baseline; r < 1.3 Low, < 1.8 Medium, < 3.0 High, else Critical
    (("1.29", "1.00"), "Low"), (("1.30", "1.00"), "Medium"), (("0.65", "0.50"), "Medium"),
    (("1.105", "0.85"), "Medium"), (("1.31", "1.00"), "Medium"),
    (("1.79", "1.00"), "Medium"), (("1.80", "1.00"), "High"), (("1.53", "0.85"), "High"),
    (("1.81", "1.00"), "High"),
    (("2.99", "1.00"), "High"), (("3.00", "1.00"), "Critical"), (("2.55", "0.85"), "Critical"),
    (("3.01", "1.00"), "Critical"),
]
DISTRIBUTION = [  # T:132: r = retail / total; r < 0.25 Low, < 0.50 Medium, < 0.80 High, else Critical
    (("2499", "10000"), "Low"), (("2500", "10000"), "Medium"), (("2501", "10000"), "Medium"),
    (("4999", "10000"), "Medium"), (("5000", "10000"), "High"), (("5001", "10000"), "High"),
    (("7999", "10000"), "High"), (("8000", "10000"), "Critical"), (("8001", "10000"), "Critical"),
]


@pytest.mark.parametrize("pct,band", ACCUMULATION)
def test_accumulation_concentration_boundaries(pct, band):
    assert score_accumulation_concentration(pct) == band


@pytest.mark.parametrize("n,band", COORDINATION)
def test_promotional_coordination_boundaries(n, band):
    assert score_promotional_coordination(n) == band


@pytest.mark.parametrize("args,band", PRICE)
def test_price_inflation_boundaries(args, band):
    assert score_price_inflation(*args) == band


def test_price_inflation_is_peak_over_baseline_not_the_inverse():
    """T:127: r = price_peak / price_baseline. A 2.00 peak on a 1.00 baseline is r = 2.0
    (High); inverted it would be 0.5 (Low)."""
    assert score_price_inflation("2.00", "1.00") == "High"


@pytest.mark.parametrize("args,band", DISTRIBUTION)
def test_distribution_into_retail_boundaries(args, band):
    assert score_distribution_into_retail(*args) == band


def test_distribution_is_retail_over_total_not_the_inverse():
    """T:131: r = volume_sold_to_retail / total_position. 3,000 of 10,000 is r = 0.3
    (Medium); inverted it would be 3.33 (Critical)."""
    assert score_distribution_into_retail("3000", "10000") == "Medium"


def test_boundary_tables_are_non_vacuous():
    for table in (ACCUMULATION, COORDINATION, PRICE, DISTRIBUTION):
        assert len(table) >= 8 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


@pytest.mark.parametrize("call", [
    lambda: score_price_inflation("1.50", "0"), lambda: score_price_inflation("1.50", "-1.00"),
    lambda: score_distribution_into_retail("100", "0"), lambda: score_distribution_into_retail("100", "-5"),
], ids=["baseline-0", "baseline-negative", "total-0", "total-negative"])
def test_a_ratio_denominator_must_be_positive(call):
    """T:127 'price_baseline > 0', T:131 'total_position > 0'."""
    with pytest.raises(RiskModelError):
        call()


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against T:113's weighted midpoint sum in EXACT
    arithmetic, half-up -- including the combinations whose exact total ends in .5."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, _ = cm007_exposure_score(bands)
        assert (score, band) == (_doctrine_score(bands), _doctrine_band(_doctrine_score(bands))), combo
    assert halves > 0                                                # non-vacuity: .5 totals examined


@pytest.mark.parametrize("score,band", [(0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
                                        (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical")])
def test_classification_boundaries(score, band):
    assert band_of(score) == band


def test_every_classification_band_is_reachable_and_eighty_is_not_a_score():
    scores = {_doctrine_score(dict(zip(DOCTRINE_WEIGHTS, c)))
              for c in itertools.product(DOCTRINE_MIDPOINT, repeat=4)}
    assert {_doctrine_band(s) for s in scores} == {"Low", "Medium", "High", "Critical"}
    assert 79 in scores and 81 in scores and 80 not in scores


# ---------------------------------------------------------------- check 4: through the callable

def _row(ref, pct, posts, peak, baseline, retail, total, promoter=None):
    return {"trader_name": "Trader " + ref, "account_ref": ref, "instrument": "Instrument " + ref,
            "pct_of_float_accumulated": pct, "coordinated_posts_count": posts,
            "price_peak": peak, "price_baseline": baseline,
            "volume_sold_to_retail": retail, "total_position": total,
            "promoter_name": promoter or "Promoter " + ref, "promoter_id": "PR-" + ref}


def _frames(rows):
    """Constructed accounts + the matching promoter record per account (the engine
    refuses an account with none, pump_and_dump.py:64-66), all as CSV strings."""
    accounts = pd.DataFrame([{k: str(v) for k, v in r.items()} for r in rows])
    promoters = pd.DataFrame([{"promoter_name": r["promoter_name"], "promoter_id": r["promoter_id"],
                               "account_ref": r["account_ref"], "channel": "Constructed channel",
                               "jurisdiction": "UNKNOWN", "prior_alerts": "0"} for r in rows])
    return {"trading_accounts": accounts, "promoters": promoters}


# T:136-146: 68 % of float (Crit), 14 posts (Crit), $3.57 on $0.85 (r 4.2, Crit),
# 315,000 of 350,000 to retail (r 0.9, Crit) -> 90 Critical.
WORKED = _row("T-WORKED", "68", "14", "3.57", "0.85", "315000", "350000")

# Per component rule: the three OTHER components held Critical (68 %, 14 posts, r 4.2,
# r 0.9), the rule's own input at the lowest value that keeps the total >= 80 (positive)
# and one step below it (near-miss). Hand-worked from T:106-113 contributions
# (acc L5.25 M15.75 H24.5 C31.5; coord L3.75 M11.25 H17.5 C22.5; price/dist L3 M9 H14 C18):
#   accumulation  26 % High: 24.5+22.5+18+18 = 83 alert; 25 % Medium: 15.75+58.5 = 74.25 -> 74
#   coordination  6 posts High: 31.5+17.5+36 = 85 alert; 5 Medium: 31.5+11.25+36 = 78.75 -> 79
#   price         r 1.30 Medium: 31.5+22.5+9+18 = 81 alert; r 1.29 Low: 3+72 = 75
#   distribution  r 0.25 Medium: 81 alert;                   r 0.2499 Low: 75
PER_RULE = {
    "accumulation_concentration": (
        _row("T-AC-POS", "26", "14", "3.57", "0.85", "315000", "350000"), 83, "Critical",
        _row("T-AC-NM", "25", "14", "3.57", "0.85", "315000", "350000"), 74, "High"),
    "promotional_coordination": (
        _row("T-PC-POS", "68", "6", "3.57", "0.85", "315000", "350000"), 85, "Critical",
        _row("T-PC-NM", "68", "5", "3.57", "0.85", "315000", "350000"), 79, "High"),
    "price_inflation": (
        _row("T-PI-POS", "68", "14", "1.30", "1.00", "315000", "350000"), 81, "Critical",
        _row("T-PI-NM", "68", "14", "1.29", "1.00", "315000", "350000"), 75, "High"),
    "distribution_into_retail": (
        _row("T-DR-POS", "68", "14", "3.57", "0.85", "2500", "10000"), 81, "Critical",
        _row("T-DR-NM", "68", "14", "3.57", "0.85", "2499", "10000"), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_pump_and_dump(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")
    assert [row[c] for c in BAND_COLUMNS] == ["Critical"] * 4


def test_the_subject_is_the_trading_account(governed):
    """README.md:51: the subject is the trading account (subject_entity_id = account_ref),
    not the trader's display name."""
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
    alerted = list(governed.evaluate_pump_and_dump(**frames)["subject_entity_id"])
    assert alerted == [pos["account_ref"]]                           # the positive, and only it


def test_band_table_governs_over_the_python_example(governed):
    """R1 (owner, 2026-10-21): the band table governs over T's Python example (T:191-198),
    which also demands price_peak / price_baseline >= 1.8. r 1.30 (Medium) with the rest
    Critical is 81 (T:106-113), so it MUST alert although the example would drop it."""
    pos = PER_RULE["price_inflation"][0]
    assert float(pos["price_peak"]) / float(pos["price_baseline"]) < 1.8
    control = WORKED
    got = set(governed.evaluate_pump_and_dump(**_frames([pos, control]))["subject_entity_id"])
    assert got == {pos["account_ref"], control["account_ref"]}


def test_a_passive_holder_with_organic_interest_does_not_alert(governed):
    """R3 near miss (T:83, T:91): a passive position (2 % of float, Low), no coordinated
    posts (Low), r 1.05 (Low), 10 % sold to retail (Low) -> 15 Low. Run beside the worked
    example so the alert set is exactly the control."""
    passive = _row("T-PASSIVE", "2", "0", "1.05", "1.00", "1000", "10000")
    frames = _frames([passive, WORKED])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert (scored.loc["T-PASSIVE", "exposure_score"], scored.loc["T-PASSIVE", "exposure_band"]) == (15, "Low")
    assert list(governed.evaluate_pump_and_dump(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_a_spike_and_sell_off_without_accumulation_or_promotion_does_not_alert(governed):
    """T:8-12: the finding is a CONVERGENCE. A price spike (r 4.2, Critical) and heavy
    selling into retail (r 0.9, Critical) with no accumulation (5 %, Low) and no
    coordinated promotion (1 post, Low): 5.25 + 3.75 + 18 + 18 = 45 Medium."""
    partial = _row("T-PARTIAL", "5", "1", "3.57", "0.85", "315000", "350000")
    frames = _frames([partial, WORKED])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert (scored.loc["T-PARTIAL", "exposure_score"], scored.loc["T-PARTIAL", "exposure_band"]) == (45, "Medium")
    assert list(governed.evaluate_pump_and_dump(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_pump_and_dump(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """T:113 'boundary at 80', T:165 'escalate at or above the threshold'. No band
    combination scores exactly 80, so the cut-line is constructed by fixing the model's
    score; the callable's own filter decides."""
    real = governed.cm007_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm007_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                    # non-vacuity: one row scored
    assert (len(governed.evaluate_pump_and_dump(**frames)) == 1) is alerts


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

@pytest.mark.parametrize("column", ["pct_of_float_accumulated", "coordinated_posts_count", "price_peak",
                                    "price_baseline", "volume_sold_to_retail", "total_position"])
def test_an_absent_required_input_is_refused_not_scored_clean(governed, column):
    """T:118, 122, 127, 131: every component input is REQUIRED. An empty CSV cell (how
    the estate delivers an absent value: dtype=str, keep_default_na=False) must stop
    scoring, never be banded."""
    row = dict(WORKED, **{column: ""})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([row]))


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: T:127 'Both amounts REQUIRED' -- a NaN price_peak is banded Critical, not "
    "refused (cm007_risk_model.py:56-61 _require checks only `is None`; `baseline <= 0` passes and "
    "NaN fails every `r <` at :105-112). Measured: DID NOT RAISE, and the row ALERTS at 90 Critical, "
    "where any measured peak below 1.3x baseline would leave it at 75 High. (A NaN share of float, "
    "retail volume or position is refused only by accident, at the output int() casts "
    "pump_and_dump.py:84, 87-88, which raise ValueError and lose the whole frame.)"))
def test_a_nan_price_peak_is_refused_not_banded_critical(governed):
    row = dict(WORKED, price_peak="nan")
    frames = _frames([row])
    with pytest.raises(ValueError):
        governed.score_all(**frames)


# ---------------------------------------------------------------- exact decimal cut-line (FLOATCUT)

@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN N10-FLOATCUT, cited, now seen in fc-07: T:128 'r < 1.3 -> Low' -- a $1.69 peak on a "
    "$1.30 baseline is r = 1.3 exactly (Medium), but 1.69/1.30 is 1.2999999999999998 in binary "
    "floats (cm007_risk_model.py:105-107), so it bands Low. Measured with the rest Critical: "
    "AssertionError, scored 75 High and NOT alerted, where T:106-113 gives 81 Critical"))
def test_a_price_ratio_exactly_on_the_medium_line_bands_medium(governed):
    on_line = _row("T-FLOAT", "68", "14", "1.69", "1.30", "315000", "350000")
    frames = _frames([on_line, WORKED])
    assert len(governed.score_all(**frames)) == 2                    # non-vacuity
    got = set(governed.evaluate_pump_and_dump(**frames)["subject_entity_id"])
    assert got == {"T-FLOAT", "T-WORKED"}
