"""CM010 Suspicious Order Patterns — capital-markets exposure risk model.

Suspicious order patterns are the family's purely order-flow-behavioural typology:
quote stuffing, momentum ignition, and abnormal cancel/amend rates. There is no single
rule that condemns a trading account -- the finding is the CONVERGENCE of four
independent order-flow signals: an abnormal cancel/amend rate (orders entered with no
intent to execute), a burst of order-submission intensity consistent with quote
stuffing, a price move after an order burst well beyond the instrument's normal move
(momentum ignition), and an average order size well beyond the account's normal size.

Four components, from the macro framework:

    Cancel/Amend Rate           0.35   cancelled orders as a share of total orders --
                                        the core quote-stuffing / spoofing-adjacent
                                        signature: orders entered with no intent to
                                        execute
    Quote Stuffing Intensity    0.25   peak order-submission rate observed
                                        (orders per second)
    Momentum Ignition Signal    0.20   price move after an order burst, relative to
                                        the instrument's normal move
    Order Size Anomaly          0.20   average order size relative to the account's
                                        normal order size

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_cancel_amend_rate", "score_quote_stuffing_intensity",
    "score_momentum_ignition_signal", "score_order_size_anomaly", "cm010_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "cancel_amend_rate": 0.35, "quote_stuffing_intensity": 0.25,
    "momentum_ignition_signal": 0.20, "order_size_anomaly": 0.20,
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


def score_cancel_amend_rate(cancelled_orders: Any, total_orders: Any) -> str:
    """The core cancel/amend signature: cancelled orders as a share of total orders
    submitted -- orders entered with no intent to execute. Both counts REQUIRED."""
    cancelled = float(_require(cancelled_orders, "cancelled_orders"))
    total = float(_require(total_orders, "total_orders"))
    if total <= 0:
        raise RiskModelError("total_orders must be > 0 to compute a ratio")
    r = cancelled / total
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_quote_stuffing_intensity(orders_per_second: Any) -> str:
    """Peak order-submission rate observed. REQUIRED -- not measured is not "a quiet
    order book". Higher rates are worse."""
    n = int(float(_require(orders_per_second, "orders_per_second")))
    if n <= 5:
        return "Low"
    if n <= 15:
        return "Medium"
    if n <= 40:
        return "High"
    return "Critical"


def score_momentum_ignition_signal(price_move_after_burst_pct: Any, normal_move_pct: Any) -> str:
    """How far the price moved after an order burst, relative to the instrument's
    normal move. Both amounts REQUIRED, unbounded, larger is worse."""
    burst = float(_require(price_move_after_burst_pct, "price_move_after_burst_pct"))
    normal = float(_require(normal_move_pct, "normal_move_pct"))
    if normal <= 0:
        raise RiskModelError("normal_move_pct must be > 0 to compute a ratio")
    r = burst / normal
    if r < 1.5:
        return "Low"
    if r < 3.0:
        return "Medium"
    if r < 6.0:
        return "High"
    return "Critical"


def score_order_size_anomaly(avg_order_size: Any, normal_order_size: Any) -> str:
    """Average order size relative to the account's normal order size. Both amounts
    REQUIRED, unbounded, larger is worse."""
    avg = float(_require(avg_order_size, "avg_order_size"))
    normal = float(_require(normal_order_size, "normal_order_size"))
    if normal <= 0:
        raise RiskModelError("normal_order_size must be > 0 to compute a ratio")
    r = avg / normal
    if r < 1.3:
        return "Low"
    if r < 1.8:
        return "Medium"
    if r < 3.0:
        return "High"
    return "Critical"


def cm010_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM010_Suspicious_Order_Patterns.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
