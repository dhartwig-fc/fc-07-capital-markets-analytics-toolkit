"""CM008 Cross Market Abuse — capital-markets exposure risk model.

Cross market abuse is manipulation that exploits the link between an account's cash
position and a correlated derivative (or a position that spans multiple trading
venues): a trade on one leg is used to move the price of the other. The signature is
the CONVERGENCE of four independent signals: how tightly the account's positions
correlate across venues or products, how many distinct venues/instruments the
correlated activity spans, how much of the price impact on the primary instrument
transfers to the correlated instrument, and how tightly synchronised the trades across
venues are in time (tighter synchronisation is worse).

Four components, from the macro framework:

    Cross-Venue Position Correlation  0.35   correlation between the account's cash
                                              and derivative (or cross-venue) positions
    Venue Count                       0.25   count of distinct venues/instruments the
                                              correlated activity spans
    Price Impact Transfer             0.20   how much of the price impact on the
                                              primary instrument transfers to the
                                              correlated instrument
    Timing Synchronization            0.20   time between the correlated trades across
                                              venues (fewer seconds is worse)

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_cross_venue_position_correlation", "score_venue_count",
    "score_price_impact_transfer", "score_timing_synchronization", "cm008_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "cross_venue_position_correlation": 0.35, "venue_count": 0.25,
    "price_impact_transfer": 0.20, "timing_synchronization": 0.20,
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


def score_cross_venue_position_correlation(correlation_pct: Any) -> str:
    """The core cross-market-abuse signal: correlation between the account's cash
    and derivative (or cross-venue) positions. REQUIRED."""
    n = int(float(_require(correlation_pct, "correlation_pct")))
    if n <= 40:
        return "Low"
    if n <= 65:
        return "Medium"
    if n <= 85:
        return "High"
    return "Critical"


def score_venue_count(distinct_venues: Any) -> str:
    """Count of distinct venues/instruments the correlated activity spans. REQUIRED."""
    n = int(float(_require(distinct_venues, "distinct_venues")))
    if n <= 1:
        return "Low"
    if n == 2:
        return "Medium"
    if n <= 4:
        return "High"
    return "Critical"


def score_price_impact_transfer(impact_transfer_ratio: Any) -> str:
    """How much of the price impact on the primary instrument transfers to the
    correlated instrument. REQUIRED."""
    r = float(_require(impact_transfer_ratio, "impact_transfer_ratio"))
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_timing_synchronization(seconds_between_venue_trades: Any) -> str:
    """Time between the correlated trades across venues. REQUIRED -- not measured is
    not "far apart in time". Fewer seconds between the trades is worse."""
    n = float(_require(seconds_between_venue_trades, "seconds_between_venue_trades"))
    if n <= 5:
        return "Critical"
    if n <= 30:
        return "High"
    if n <= 120:
        return "Medium"
    return "Low"


def cm008_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM008_Cross_Market_Abuse.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
