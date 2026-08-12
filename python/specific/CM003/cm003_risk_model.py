"""CM003 Spoofing — capital-markets exposure risk model.

Spoofing is placing orders on one side of the book with no intention of letting them
execute, to move the visible order book and induce other participants to trade, then
cancelling the spoof orders and executing genuine trades on the opposite side. The
signature is the CONVERGENCE of four independent signals: a large share of order value
that is never genuinely intended to execute, orders cancelled unusually fast (before
the market can react to them being real), a material share of visible depth on one side
manufactured by the spoof orders, and genuine execution on the opposite side while the
spoof orders are working.

Four components, from the macro framework:

    Non-Bona-Fide Order Ratio    0.35   share of order value placed with no intention
                                         to execute, relative to total order value
    Cancellation Speed           0.25   average time from placement to cancellation --
                                         faster cancellation before execution is worse
    Order Book Imbalance Created 0.20   share of visible depth on one side the spoof
                                         orders manufacture, relative to genuine depth
    Opposite-Side Execution      0.20   genuine execution on the opposite side while
                                         the spoof orders are working, relative to the
                                         spoof order value

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_non_bona_fide_order_ratio", "score_cancellation_speed",
    "score_order_book_imbalance_created", "score_opposite_side_execution", "cm003_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "non_bona_fide_order_ratio": 0.35, "cancellation_speed": 0.25,
    "order_book_imbalance_created": 0.20, "opposite_side_execution": 0.20,
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


def score_non_bona_fide_order_ratio(spoof_order_value: Any, total_order_value: Any) -> str:
    """The core spoofing signal: share of order value placed with no intention to
    execute, relative to total order value. Both amounts are REQUIRED."""
    spoof = float(_require(spoof_order_value, "spoof_order_value"))
    total = float(_require(total_order_value, "total_order_value"))
    if total <= 0:
        raise RiskModelError("total_order_value must be > 0 to compute a ratio")
    r = spoof / total
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_cancellation_speed(avg_cancel_seconds: Any) -> str:
    """Average time from placement to cancellation. REQUIRED -- not measured is not
    "slow to cancel". Faster cancellation before execution is worse (the spoofing
    tell)."""
    n = float(_require(avg_cancel_seconds, "avg_cancel_seconds"))
    if n <= 2:
        return "Critical"
    if n <= 5:
        return "High"
    if n <= 15:
        return "Medium"
    return "Low"


def score_order_book_imbalance_created(spoof_side_depth: Any, genuine_side_depth: Any) -> str:
    """Share of visible depth on one side the spoof orders manufacture, relative to
    genuine depth on that side. Both amounts REQUIRED."""
    spoof = float(_require(spoof_side_depth, "spoof_side_depth"))
    genuine = float(_require(genuine_side_depth, "genuine_side_depth"))
    total = spoof + genuine
    if total <= 0:
        raise RiskModelError("spoof_side_depth + genuine_side_depth must be > 0 to compute a ratio")
    r = spoof / total
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_opposite_side_execution(opposite_side_filled_value: Any, spoof_order_value: Any) -> str:
    """How much genuine execution happens on the opposite side while the spoof orders
    are working -- the step that turns a manufactured order book into a completed
    spoofing leg."""
    filled = float(_require(opposite_side_filled_value, "opposite_side_filled_value"))
    spoof = float(_require(spoof_order_value, "spoof_order_value"))
    if spoof <= 0:
        raise RiskModelError("spoof_order_value must be > 0 to compute a ratio")
    r = filled / spoof
    if r < 0.25:
        return "Low"
    if r < 0.50:
        return "Medium"
    if r < 0.80:
        return "High"
    return "Critical"


def cm003_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM003_Spoofing.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
