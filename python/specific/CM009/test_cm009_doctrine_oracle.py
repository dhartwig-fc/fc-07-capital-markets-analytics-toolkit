"""TT-CM009 (night 10, wave C): CM009 Benchmark Manipulation tested against its DOCTRINE.

Oracle: typologies/CM009_Benchmark_Manipulation.md (T) -- "Exposure Scoring Framework"
(weights 35/25/20/20 %, band midpoints 15/45/70/90, weighted sum, half-up, boundary at 80;
T:112-121), "Component Banding Rules" (T:123-139), the ACC019 worked example (T:143-153),
"Classification" (T:155-156) and Business Logic step 7, "escalate at or above the threshold"
(T:168). The family standard operations/common/Risk_Scoring_Governance.md:62 gives the same
80-100 Critical. Owner oracle rule R1 (2026-10-21): where the Python example (T:194-201)
disagrees with the framework, the band table governs. Every expected value below is
hand-worked from those, never pasted from an engine run. Inputs are CONSTRUCTED here; no
sample-data file is read and no sample entity name is asserted.

Checks 2 (boundaries at every doctrine threshold) and 4 (a positive and a near-miss per
detection rule). The engine is loaded as fc-10 loads it: the scenario file by path.

Not pinned here, because the doctrine is silent (QUESTIONS in the night-10 report):
non-integer repeat counts; zero or negative seconds; negative volumes or deviations; a
window volume above the daily total; one bad row refusing the whole frame; duplicate
account_ref rows; an order matched to a benchmark record naming a different benchmark; the
fixed risk_reason sentence.
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

from cm009_risk_model import (  # noqa: E402
    band_of, cm009_exposure_score, score_fixing_window_concentration,
    score_order_timing_precision, score_price_distortion, score_repeat_pattern,
)

SCENARIO = BASE_DIR / "scenarios" / "benchmark_manipulation.py"

# T:114-121: weights 35/25/20/20 %, band midpoints 15/45/70/90, half-up, boundary at 80.
DOCTRINE_WEIGHTS = {
    "fixing_window_concentration": Fraction(35, 100),
    "price_distortion": Fraction(25, 100),
    "order_timing_precision": Fraction(20, 100),
    "repeat_pattern": Fraction(20, 100),
}
DOCTRINE_MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}


def _doctrine_score(bands):
    exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
    return math.floor(exact + Fraction(1, 2))                      # half-up, exact arithmetic


def _doctrine_band(score):
    # T:156: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    return "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"


@pytest.fixture(scope="module")
def governed():
    spec = spec_from_file_location("fc07_cm009_tt_oracle", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- check 2: component boundaries
# At / just below / just above each cut-line. Strings sit beside numbers so a value is
# examined as it arrives from a CSV (dtype=str); every ON-the-line ratio below is exact in
# binary as well as in decimal. The decimal ratio that is not is the N10-FLOATCUT witness.

CONCENTRATION = [  # T:126-127: r = window / total; r < 0.10 Low, < 0.30 Medium, < 0.60 High, else Critical
    ((999, 10000), "Low"), ((10, 100), "Medium"), (("10", "100"), "Medium"), ((1001, 10000), "Medium"),
    ((2999, 10000), "Medium"), ((30, 100), "High"), (("3", "10"), "High"), ((3001, 10000), "High"),
    ((5999, 10000), "High"), ((60, 100), "Critical"), (("6", "10"), "Critical"), ((6001, 10000), "Critical"),
]
DISTORTION = [  # T:130-131: r = deviation / normal; r < 1.5 Low, < 3.0 Medium, < 6.0 High, else Critical
    ((149, 100), "Low"), ((150, 100), "Medium"), (("1.5", "1"), "Medium"), ((151, 100), "Medium"),
    ((299, 100), "Medium"), ((300, 100), "High"), (("3", "1"), "High"), ((301, 100), "High"),
    ((599, 100), "High"), ((600, 100), "Critical"), (("6", "1"), "Critical"), ((601, 100), "Critical"),
]
TIMING = [  # T:134-135: <= 5 Critical, <= 20 High, <= 60 Medium, otherwise (> 60) Low. Fewer is WORSE.
    (4, "Critical"), (5, "Critical"), ("5", "Critical"), (6, "High"),
    (19, "High"), (20, "High"), ("20", "High"), (21, "Medium"),
    (59, "Medium"), (60, "Medium"), ("60", "Medium"), (61, "Low"),
]
REPEAT = [  # T:138-139: <= 1 Low, = 2 Medium, <= 4 High, otherwise (>= 5) Critical
    (0, "Low"), (1, "Low"), ("1", "Low"), (2, "Medium"), ("2", "Medium"), (3, "High"),
    (4, "High"), ("4", "High"), (5, "Critical"), ("5", "Critical"), (6, "Critical"), (8, "Critical"),
]


@pytest.mark.parametrize("args,band", CONCENTRATION)
def test_fixing_window_concentration_boundaries(args, band):
    assert score_fixing_window_concentration(*args) == band


def test_concentration_is_window_over_total():
    """T:126: r = fixing_window_volume / total_daily_volume. 45 of 100 is r = 0.45 (High);
    inverted it would be 2.2 (Critical)."""
    assert score_fixing_window_concentration(45, 100) == "High"


@pytest.mark.parametrize("args,band", DISTORTION)
def test_price_distortion_boundaries(args, band):
    assert score_price_distortion(*args) == band


def test_distortion_is_deviation_over_normal():
    """T:130: r = fixing_price_deviation_pct / normal_deviation_pct. 0.4 against 1.0 is
    r = 0.4 (Low); inverted it would be 2.5 (Medium)."""
    assert score_price_distortion(0.4, 1.0) == "Low"


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN N10-FLOATCUT, cited: T:131 'r < 3.0 -> Medium' puts r = 3 in High -- a 0.3% "
    "fixing deviation against a 0.1% normal deviation is exactly r = 3, and the engine bands "
    "it Medium (cm009_risk_model.py:95-99: float 0.3/0.1 = 2.9999999999999996). Measured: "
    "AssertionError, 'Medium' != 'High'. Same class at 1.5 ('0.3'/'0.2') and 6.0 ('0.6'/'0.1'), "
    "and in concentration with decimal volumes ('0.01'/'0.1')"))
def test_a_distortion_ratio_exactly_on_the_high_line_bands_high():
    assert Fraction("0.3") / Fraction("0.1") == 3                  # the decimal ratio IS on the line
    assert score_price_distortion("0.3", "0.1") == "High"


@pytest.mark.parametrize("seconds,band", TIMING)
def test_order_timing_precision_boundaries(seconds, band):
    assert score_order_timing_precision(seconds) == band


@pytest.mark.parametrize("count,band", REPEAT)
def test_repeat_pattern_boundaries(count, band):
    assert score_repeat_pattern(count) == band


def test_boundary_tables_are_non_vacuous():
    for table in (CONCENTRATION, DISTORTION, TIMING, REPEAT):
        assert len(table) >= 12 and {b for _, b in table} == {"Low", "Medium", "High", "Critical"}


# ---------------------------------------------------------------- check 2: score, rounding, classification

def test_every_band_combination_scores_as_the_doctrine_computes_it():
    """All 256 band combinations against the doctrine's weighted midpoint sum in EXACT
    arithmetic, half-up -- including every combination whose exact total ends in .5."""
    halves = 0
    for combo in itertools.product(DOCTRINE_MIDPOINT, repeat=4):
        bands = dict(zip(DOCTRINE_WEIGHTS, combo))
        exact = sum(DOCTRINE_WEIGHTS[k] * DOCTRINE_MIDPOINT[v] for k, v in bands.items())
        halves += exact.denominator == 2
        score, band, working = cm009_exposure_score(bands)
        expected = _doctrine_score(bands)
        assert (score, band) == (expected, _doctrine_band(expected)), combo
        assert {k: v["band"] for k, v in working["components"].items()} == bands
        assert {k: v["weight"] for k, v in working["components"].items()} == \
            {k: float(w) for k, w in DOCTRINE_WEIGHTS.items()}
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
    """Constructed fixing orders + one benchmark record per account."""
    orders = pd.DataFrame([{"trader_name": "Trader " + r["account_ref"], "benchmark_name": "Fixing T",
                            "issuer_name": "Issuer T", **r} for r in rows])
    benchmarks = pd.DataFrame([{"benchmark_name": "Fixing T", "account_ref": r["account_ref"],
                                "administrator": "Administrator T", "jurisdiction": "UNKNOWN",
                                "prior_alerts": 0} for r in rows])
    return {"fixing_orders": orders, "benchmarks": benchmarks}


def _row(ref, window, total, deviation, normal, seconds, repeats):
    return {"account_ref": ref, "fixing_window_volume": window, "total_daily_volume": total,
            "fixing_price_deviation_pct": deviation, "normal_deviation_pct": normal,
            "seconds_before_fixing_close": seconds, "repeat_occurrences": repeats}


# T:143-153, the worked example's evidence: 22,525,000 of 26,500,000 (r 0.85) C, 1.44 vs 0.18
# (r 8) C, 2 s C, 8 prior windows C -> 90 Critical.
WORKED = _row("T-WORKED", 22525000, 26500000, 1.44, 0.18, 2, 8)

# Per detection rule: the three OTHER components held Critical (worth 58.5 when the rule is
# concentration, 67.5 for distortion, 72 for timing and repeat), the rule's own input set at
# the cut-line that keeps the total >= 80 (positive) and one step below it:
#   concentration High (r 0.30)   24.5 + 58.5 = 83 alert;  Medium (r 0.2999) 15.75 + 58.5 = 74.25 -> 74
#   distortion    High (r 3.00)   17.5 + 67.5 = 85 alert;  Medium (r 2.99)   11.25 + 67.5 = 78.75 -> 79
#   timing        Medium (60 s)    9   + 72   = 81 alert;  Low (61 s)         3    + 72   = 75
#   repeat        Medium (2)       9   + 72   = 81 alert;  Low (1)            3    + 72   = 75
# The timing and repeat positives fail T:194-201's example filter (seconds <= 20, repeats >= 3);
# owner rule R1 (2026-10-21): the band table governs, so they alert.
PER_RULE = {
    "fixing_window_concentration": (_row("T-CON-POS", 3000, 10000, 1.44, 0.18, 2, 8), 83, "Critical",
                                    _row("T-CON-NM", 2999, 10000, 1.44, 0.18, 2, 8), 74, "High"),
    "price_distortion": (_row("T-DIS-POS", 22525000, 26500000, "3", "1", 2, 8), 85, "Critical",
                         _row("T-DIS-NM", 22525000, 26500000, "2.99", "1", 2, 8), 79, "High"),
    "order_timing_precision": (_row("T-TIM-POS", 22525000, 26500000, 1.44, 0.18, 60, 8), 81, "Critical",
                               _row("T-TIM-NM", 22525000, 26500000, 1.44, 0.18, 61, 8), 75, "High"),
    "repeat_pattern": (_row("T-REP-POS", 22525000, 26500000, 1.44, 0.18, 2, 2), 81, "Critical",
                       _row("T-REP-NM", 22525000, 26500000, 1.44, 0.18, 2, 1), 75, "High"),
}


def test_the_worked_example_alerts_critical_ninety(governed):
    out = governed.evaluate_benchmark_manipulation(**_frames([WORKED]))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["subject_entity_id"], row["exposure_score"], row["exposure_band"]) == ("T-WORKED", 90, "Critical")
    assert [row[c] for c in ("fixing_window_concentration_band", "price_distortion_band",
                             "order_timing_precision_band", "repeat_pattern_band")] == ["Critical"] * 4


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
    assert list(governed.evaluate_benchmark_manipulation(**frames)["subject_entity_id"]) == [pos["account_ref"]]


def test_an_ordinary_large_fill_does_not_alert(governed):
    """T:247-248: what CM009 separates from 'an ordinary large fill'. 500k of 10m (r 0.05) L,
    0.1 vs 0.2 (r 0.5) L, placed 900 s before the close L, no prior windows L -> 15 Low;
    beside the worked example as the alerting control."""
    frames = _frames([_row("T-FILL", 500000, 10000000, 0.1, 0.2, 900, 0), WORKED])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-FILL", "exposure_score"], scored.loc["T-FILL", "exposure_band"]) == (15, "Low")
    assert list(governed.evaluate_benchmark_manipulation(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_timing_alone_does_not_alert(governed):
    """A one-off late order without concentration, distortion or repeats: r 0.05 L, r 1.0 L,
    2 s C, 0 prior L -> 5.25 + 3.75 + 18 + 3 = 30 Medium."""
    frames = _frames([_row("T-LATE", 500, 10000, 0.2, 0.2, 2, 0), WORKED])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert (scored.loc["T-LATE", "exposure_score"], scored.loc["T-LATE", "exposure_band"]) == (30, "Medium")
    assert list(governed.evaluate_benchmark_manipulation(**frames)["subject_entity_id"]) == ["T-WORKED"]


def test_the_alert_set_is_exactly_the_rows_at_or_above_eighty(governed):
    rows = [WORKED] + [r for v in PER_RULE.values() for r in (v[0], v[3])]
    expected = {"T-WORKED"} | {v[0]["account_ref"] for v in PER_RULE.values()}
    got = set(governed.evaluate_benchmark_manipulation(**_frames(rows))["subject_entity_id"])
    assert len(rows) == 9 and got == expected


def test_the_working_pairs_each_component_with_its_own_band(governed):
    """T:114-121 weight each component by ITS OWN band. Timing and repeat carry equal weights,
    so a swap between them leaves the score unchanged -- only the working shows it.
    r 0.20 M, r 4 H, 120 s L, 6 prior C -> 15.75 + 17.5 + 3 + 18 = 54.25 -> 54 Medium."""
    import json
    frames = _frames([_row("T-MIX", 2000, 10000, 4, 1, 120, 6)])
    row = governed.score_all(**frames).iloc[0]
    working = json.loads(row["risk_components"])["components"]
    assert {k: v["band"] for k, v in working.items()} == {
        "fixing_window_concentration": "Medium", "price_distortion": "High",
        "order_timing_precision": "Low", "repeat_pattern": "Critical"}
    assert {k: v["weight"] for k, v in working.items()} == {k: float(w) for k, w in DOCTRINE_WEIGHTS.items()}
    assert (row["exposure_score"], row["exposure_band"]) == (54, "Medium")


@pytest.mark.parametrize("forced,alerts", [(79, False), (80, True), (81, True)])
def test_escalation_is_at_or_above_eighty(governed, monkeypatch, forced, alerts):
    """T:121 'boundary at 80', T:168 'escalate at or above the threshold'. No band
    combination scores exactly 80, so the cut-line is constructed by fixing the model's
    score; the callable's own filter decides."""
    real = governed.cm009_exposure_score

    def fixed(bands):
        _s, _b, working = real(bands)
        return forced, _doctrine_band(forced), working
    monkeypatch.setattr(governed, "cm009_exposure_score", fixed)
    frames = _frames([WORKED])
    assert len(governed.score_all(**frames)) == 1                  # non-vacuity: one row scored
    assert (len(governed.evaluate_benchmark_manipulation(**frames)) == 1) is alerts


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "QUESTION (doctrine T:135 vs fc-07 schema.json integer typing, rule 9): "
    "Measured: AssertionError: assert 'Critical' == 'High'. Truncation produces a FALSE "
    "ALERT. (schema.json types seconds_before_fixing_close 'integer'; T does not.) "
    "T:135 'seconds_before_fixing_close <= 5 -> Critical, <= 20 -> High' -- an order "
    "5.5 s before the close is not <= 5, but cm009_risk_model.py:108 truncates with "
    "int(float(...)) before the cut-line, so it bands Critical. Measured: AssertionError, the "
    "row scores 83 Critical and ALERTS where the doctrine gives High 14 -> 79 High, no alert"))
def test_fractional_seconds_are_not_truncated_into_a_worse_band(governed):
    """Concentration High (r 0.45) 24.5, distortion C 22.5, repeat C 18, timing at 5.5 s is
    High 14 by T:135 -> 79 High, no alert; the worked example is the alerting control."""
    frames = _frames([_row("T-FRAC", 4500, 10000, 1.44, 0.18, "5.5", 8), WORKED])
    scored = governed.score_all(**frames).set_index("subject_entity_id")
    assert len(scored) == 2
    assert scored.loc["T-FRAC", "order_timing_precision_band"] == "High"
    assert (scored.loc["T-FRAC", "exposure_score"], scored.loc["T-FRAC", "exposure_band"]) == (79, "High")
    assert list(governed.evaluate_benchmark_manipulation(**frames)["subject_entity_id"]) == ["T-WORKED"]


# ---------------------------------------------------------------- REQUIRED inputs (doctrine)

INPUT_FIELDS = ("fixing_window_volume", "total_daily_volume", "fixing_price_deviation_pct",
                "normal_deviation_pct", "seconds_before_fixing_close", "repeat_occurrences")


@pytest.mark.parametrize("field", INPUT_FIELDS)
def test_a_blank_required_input_is_refused_not_scored_clean(governed, field):
    """T:126/130/134/138: every input is REQUIRED. A blank CSV cell (the engine reads with
    keep_default_na=False, so it arrives as '') must not be scored as an absent signal."""
    blank = dict(WORKED, account_ref="T-BLANK", **{field: ""})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([blank]))


@pytest.mark.parametrize("field", INPUT_FIELDS)
def test_a_none_required_input_is_refused(governed, field):
    none = dict(WORKED, account_ref="T-NONE", **{field: None})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([none]))


def test_a_missing_seconds_value_refuses_the_row(governed):
    """T:134 'seconds_before_fixing_close REQUIRED'. A NaN is refused (by the int() cast,
    not by _require -- recorded under D043)."""
    with pytest.raises(ValueError):
        governed.score_all(**_frames([_row("T-NOSEC", 22525000, 26500000, 1.44, 0.18, float("nan"), 8)]))


@pytest.mark.parametrize("field", ("fixing_window_volume", "total_daily_volume"))
def test_a_missing_volume_refuses_the_row(governed, field):
    """T:126 'Both amounts REQUIRED'. A NaN volume is refused -- but by ACCIDENT: the model
    bands it Critical (D043) and the scenario's output cast int(float(nan))
    (benchmark_manipulation.py:85-86) is what raises. Recorded under D043."""
    nan = dict(WORKED, account_ref="T-NANVOL", **{field: float("nan")})
    with pytest.raises(ValueError):
        governed.score_all(**_frames([nan]))


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: T:130 'Both amounts REQUIRED' -- a NaN fixing price deviation is banded "
    "Critical, not refused (cm009_risk_model.py:91-102: _require checks only `is None`, and "
    "every `r < x` is False for NaN; the same for normal_deviation_pct, and for both volumes "
    "until the scenario's output cast happens to raise). Effect measured: DID NOT RAISE, the row "
    "scores 90 Critical and ALERTS; with distortion Low it would score 71 and not alert"))
def test_a_missing_price_deviation_is_refused_not_banded_critical(governed):
    frames = _frames([_row("T-NODEV", 22525000, 26500000, float("nan"), 0.18, 2, 8)])
    with pytest.raises(ValueError):
        governed.evaluate_benchmark_manipulation(**frames)
