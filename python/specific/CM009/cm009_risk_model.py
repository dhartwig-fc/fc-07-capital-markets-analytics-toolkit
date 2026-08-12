"""CM009 Benchmark Manipulation — capital-markets exposure risk model.

Benchmark manipulation is skewing a regulated fixing (a reference rate, an FX fix, a
commodity settlement price) through concentrated order flow placed in the closing
seconds of the fixing window. The signature is the CONVERGENCE of four independent
signals: an abnormal concentration of volume inside the fixing window itself, a price
deviation far beyond the instrument's normal fixing-window volatility, orders placed in
the final seconds before the window closes (leaving no time for the market to absorb
them), and a repeat pattern of the same behaviour across prior fixing windows.

Four components, from the macro framework:

    Fixing Window Concentration  0.35   fixing-window volume relative to total daily
                                         volume in the same instrument
    Price Distortion             0.25   the fixing's price deviation relative to the
                                         instrument's normal deviation for that window
    Order Timing Precision       0.20   how close to the fixing window's close the
                                         order was placed (fewer seconds is worse)
    Repeat Pattern                0.20   count of prior fixing windows showing the same
                                         pattern for the same account

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_fixing_window_concentration", "score_price_distortion",
    "score_order_timing_precision", "score_repeat_pattern", "cm009_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "fixing_window_concentration": 0.35, "price_distortion": 0.25,
    "order_timing_precision": 0.20, "repeat_pattern": 0.20,
}
RISK_BANDS = ((0, 29, "Low"), (30, 59, "Medium"), (60, 79, "High"), (80, 100, "Critical"))


def _round_half_up(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _require(value: Any, field: str) -> Any:
    if value is None:
        raise RiskModelError(
            "%s is missing. Refusing to score it as absent -- not measured and "
            "measured-as-zero are different findings." % field)
    return value


def band_of(score: float) -> str:
    for low, high, name in RISK_BANDS:
        if low <= score <= high:
            return name
    raise RiskModelError("score out of range: %r" % score)


def score_fixing_window_concentration(fixing_window_volume: Any, total_daily_volume: Any) -> str:
    """The core benchmark-manipulation signal: how concentrated the account's volume
    is inside the fixing window itself, relative to its total daily volume in the same
    instrument. Both amounts are REQUIRED."""
    window = float(_require(fixing_window_volume, "fixing_window_volume"))
    total = float(_require(total_daily_volume, "total_daily_volume"))
    if total <= 0:
        raise RiskModelError("total_daily_volume must be > 0 to compute a ratio")
    r = window / total
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_price_distortion(fixing_price_deviation_pct: Any, normal_deviation_pct: Any) -> str:
    """How far the fixing's price deviation runs beyond the instrument's normal
    deviation for that window. Both amounts are REQUIRED. Unbounded -- larger is
    worse."""
    deviation = float(_require(fixing_price_deviation_pct, "fixing_price_deviation_pct"))
    normal = float(_require(normal_deviation_pct, "normal_deviation_pct"))
    if normal <= 0:
        raise RiskModelError("normal_deviation_pct must be > 0 to compute a ratio")
    r = deviation / normal
    if r < 1.5:
        return "Low"
    if r < 3.0:
        return "Medium"
    if r < 6.0:
        return "High"
    return "Critical"


def score_order_timing_precision(seconds_before_fixing_close: Any) -> str:
    """How close to the fixing window's close the order was placed. REQUIRED -- not
    measured is not "far from the close". Fewer seconds before the close is worse."""
    n = int(float(_require(seconds_before_fixing_close, "seconds_before_fixing_close")))
    if n <= 5:
        return "Critical"
    if n <= 20:
        return "High"
    if n <= 60:
        return "Medium"
    return "Low"


def score_repeat_pattern(repeat_occurrences: Any) -> str:
    """Count of prior fixing windows showing the same pattern for the same account.
    REQUIRED."""
    n = int(float(_require(repeat_occurrences, "repeat_occurrences")))
    if n <= 1:
        return "Low"
    if n == 2:
        return "Medium"
    if n <= 4:
        return "High"
    return "Critical"


def cm009_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
    missing = sorted(set(COMPONENT_WEIGHTS) - set(bands))
    if missing:
        raise RiskModelError(
            "the model has four components and %d were supplied; missing: %s. "
            "Scoring a subset silently re-weights the model." % (len(bands), missing))
    working: Dict[str, Any] = {}
    total = 0.0
    for name, weight in COMPONENT_WEIGHTS.items():
        band = bands[name]
        if band not in BAND_SCORE:
            raise RiskModelError("%s: unknown band %r" % (name, band))
        contribution = BAND_SCORE[band] * weight
        total += contribution
        working[name] = {"band": band, "component_score": BAND_SCORE[band], "weight": weight, "contribution": round(contribution, 4)}
    score = _round_half_up(total)
    return score, band_of(score), {
        "components": working, "total": round(total, 4), "score": score, "band": band_of(score),
        "rounding": "half-up", "basis": "typologies/CM009_Benchmark_Manipulation.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
