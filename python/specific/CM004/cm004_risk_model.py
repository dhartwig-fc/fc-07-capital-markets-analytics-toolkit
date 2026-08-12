"""CM004 Layering — capital-markets exposure risk model.

Order-book layering places multiple non-bona-fide orders at staggered price levels on
one side of the book to create a false impression of depth or intent, moving the price
or inducing other participants to trade against it, then cancels the staggered orders
before they are ever meant to execute. This is ORDER-BOOK layering (staggered price-
level orders) -- distinct from the AML "layering" typology (moving illicit funds
through successive transactions to obscure origin). The signature here is the
CONVERGENCE of four independent signals: how many distinct price levels the staggered
orders sit at, how disproportionate the order-to-trade ratio is (orders placed vs. ever
executed), how much visible book depth/imbalance the staggering creates on one side, and
how quickly the staggered orders are reversed (pulled) once the book has moved.

Four components, from the macro framework:

    Staggered Order Levels       0.35   how many distinct price levels the staggered
                                         orders sit at
    Order-to-Trade Ratio         0.25   orders placed per order actually executed;
                                         unbounded, larger is worse
    Book Imbalance Created       0.20   share of visible book depth the staggered
                                         orders create on one side
    Reversal Speed                0.20   how quickly the staggered orders are pulled
                                         once the book has moved; smaller is WORSE

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_staggered_order_levels", "score_order_to_trade_ratio",
    "score_book_imbalance_created", "score_reversal_speed", "cm004_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "staggered_order_levels": 0.35, "order_to_trade_ratio": 0.25,
    "book_imbalance_created": 0.20, "reversal_speed": 0.20,
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


def score_staggered_order_levels(distinct_price_levels: Any) -> str:
    """The core layering signal: how many distinct price levels the staggered orders
    sit at. REQUIRED -- not measured is not "one price level"."""
    n = int(float(_require(distinct_price_levels, "distinct_price_levels")))
    if n <= 2:
        return "Low"
    if n <= 4:
        return "Medium"
    if n <= 7:
        return "High"
    return "Critical"


def score_order_to_trade_ratio(orders_placed: Any, orders_executed: Any) -> str:
    """Orders placed per order actually executed -- how disproportionate the staggered
    order flow is relative to what ever traded. Both amounts are REQUIRED."""
    placed = float(_require(orders_placed, "orders_placed"))
    executed = float(_require(orders_executed, "orders_executed"))
    if executed <= 0:
        raise RiskModelError("orders_executed must be > 0 to compute a ratio")
    r = placed / executed
    if r < 5:
        return "Low"
    if r < 15:
        return "Medium"
    if r < 40:
        return "High"
    return "Critical"


def score_book_imbalance_created(imbalance_ratio: Any) -> str:
    """The share of visible book depth the staggered orders create on one side.
    REQUIRED -- not measured is not "no imbalance"."""
    r = float(_require(imbalance_ratio, "imbalance_ratio"))
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_reversal_speed(seconds_to_reversal: Any) -> str:
    """How quickly the staggered orders are pulled once the book has moved. REQUIRED
    -- not measured is not "never reversed". Smaller is WORSE."""
    n = float(_require(seconds_to_reversal, "seconds_to_reversal"))
    if n <= 5:
        return "Critical"
    if n <= 20:
        return "High"
    if n <= 60:
        return "Medium"
    return "Low"


def cm004_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM004_Layering.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
