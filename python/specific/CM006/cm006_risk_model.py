"""CM006 Front Running — capital-markets exposure risk model.

Front running is a trader dealing on their own account ahead of a client order they
know is coming, positioned in the same direction, then closing out once the client's
order has moved the market. The signature is the CONVERGENCE of four independent
signals: the trader's own order lands suspiciously close in time before the client's
order, the trader's pre-position direction correlates with the client order's
direction, a disproportionate share of the position's value is captured as profit once
the client order lands, and the trader has documented contact with the desk handling
the client order in the run-up.

Four components, from the macro framework:

    Timing Ahead of Client Order   0.35   how many seconds before the client's own
                                           order the trader's order was placed
                                           (fewer seconds ahead is worse)
    Position Correlation           0.25   correlation between the trader's
                                           pre-position direction and the client
                                           order's direction
    Profit Capture                 0.20   realised P&L relative to the position's
                                           value, once the client order lands
    Client Order Knowledge Linkage 0.20   documented contact events between the
                                           trader and the desk handling the client
                                           order in the 90 days before

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_timing_ahead_of_client_order", "score_position_correlation",
    "score_profit_capture", "score_client_order_knowledge_linkage", "cm006_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "timing_ahead_of_client_order": 0.35, "position_correlation": 0.25,
    "profit_capture": 0.20, "client_order_knowledge_linkage": 0.20,
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


def score_timing_ahead_of_client_order(seconds_ahead_of_client_order: Any) -> str:
    """The core front-running signal: how many seconds before the client's own
    order the trader's order was placed. REQUIRED. Fewer seconds ahead is worse
    -- dealing seconds ahead of the client is the tell."""
    n = float(_require(seconds_ahead_of_client_order, "seconds_ahead_of_client_order"))
    if n <= 5:
        return "Critical"
    if n <= 30:
        return "High"
    if n <= 120:
        return "Medium"
    return "Low"


def score_position_correlation(correlation_pct: Any) -> str:
    """Correlation between the trader's pre-position direction and the client
    order's direction, as an integer percentage 0-100. REQUIRED."""
    n = float(_require(correlation_pct, "correlation_pct"))
    if n <= 40:
        return "Low"
    if n <= 65:
        return "Medium"
    if n <= 85:
        return "High"
    return "Critical"


def score_profit_capture(realized_pnl: Any, position_value: Any) -> str:
    """How much of the position's value was captured as realised profit once the
    client order landed -- the step that turns knowledge of client flow into a
    completed front-running leg."""
    pnl = float(_require(realized_pnl, "realized_pnl"))
    value = float(_require(position_value, "position_value"))
    if value <= 0:
        raise RiskModelError("position_value must be > 0 to compute a ratio")
    r = pnl / value
    if r < 0.25:
        return "Low"
    if r < 0.50:
        return "Medium"
    if r < 0.80:
        return "High"
    return "Critical"


def score_client_order_knowledge_linkage(contact_events_90d: Any) -> str:
    """How many documented contact events occurred between the trader and the
    desk handling the client order, in the 90 days before. REQUIRED."""
    n = int(float(_require(contact_events_90d, "contact_events_90d")))
    if n <= 2:
        return "Low"
    if n <= 5:
        return "Medium"
    if n <= 9:
        return "High"
    return "Critical"


def cm006_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM006_Front_Running.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
