"""CM001 Insider Trading — capital-markets exposure risk model.

Insider trading is dealing ahead of a material non-public event (an earnings release,
an M&A announcement, a regulatory decision) using information the trader should not
have had. The signature is the CONVERGENCE of four independent signals: an abnormal
build-up of position sized well beyond the trader's normal activity, timed close to the
event, corroborated by a documented information-access linkage to a source with early
knowledge, and followed by profit realised once the event's price impact lands.

Four components, from the macro framework:

    Pre-Event Position Build    0.35   how large the trader's position build is,
                                        relative to their normal average position,
                                        in the run-up to the event
    Timing Proximity to Event   0.25   how close to the event the position was built
                                        (fewer days before the event is worse)
    Information Access Linkage  0.20   documented contact events between the trader
                                        and an information source in the 90 days
                                        before the event
    Profit Realisation          0.20   realised P&L relative to the position's value
                                        at entry, once the event's price impact lands

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_pre_event_position_build", "score_timing_proximity_to_event",
    "score_information_access_linkage", "score_profit_realisation", "cm001_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "pre_event_position_build": 0.35, "timing_proximity_to_event": 0.25,
    "information_access_linkage": 0.20, "profit_realisation": 0.20,
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


def score_pre_event_position_build(pre_event_position_increase: Any, normal_average_position: Any) -> str:
    """The core insider-trading signal: how large the pre-event position build is,
    relative to the trader's normal average position. Both amounts are REQUIRED."""
    increase = float(_require(pre_event_position_increase, "pre_event_position_increase"))
    normal = float(_require(normal_average_position, "normal_average_position"))
    if normal <= 0:
        raise RiskModelError("normal_average_position must be > 0 to compute a ratio")
    r = increase / normal
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_timing_proximity_to_event(days_before_event: Any) -> str:
    """How close to the material event the position was built. REQUIRED -- not
    measured is not "far from the event". Fewer days before the event is worse."""
    n = int(float(_require(days_before_event, "days_before_event")))
    if n <= 1:
        return "Critical"
    if n <= 3:
        return "High"
    if n <= 7:
        return "Medium"
    return "Low"


def score_information_access_linkage(contact_events_90d: Any) -> str:
    """How many documented contact events occurred between the trader and an
    information source in the 90 days before the event. REQUIRED."""
    n = int(float(_require(contact_events_90d, "contact_events_90d")))
    if n <= 2:
        return "Low"
    if n <= 5:
        return "Medium"
    if n <= 9:
        return "High"
    return "Critical"


def score_profit_realisation(realized_pnl: Any, position_value_at_entry: Any) -> str:
    """How much of the position's entry value was realised as profit once the
    event's price impact landed -- the step that turns information access into
    a completed insider-trading leg."""
    pnl = float(_require(realized_pnl, "realized_pnl"))
    value = float(_require(position_value_at_entry, "position_value_at_entry"))
    if value <= 0:
        raise RiskModelError("position_value_at_entry must be > 0 to compute a ratio")
    r = pnl / value
    if r < 0.25:
        return "Low"
    if r < 0.50:
        return "Medium"
    if r < 0.80:
        return "High"
    return "Critical"


def cm001_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM001_Insider_Trading.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
