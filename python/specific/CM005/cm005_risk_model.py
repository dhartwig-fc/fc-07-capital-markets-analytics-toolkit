"""CM005 Wash Trading — capital-markets exposure risk model.

Wash trading is trading that produces no genuine change in beneficial ownership --
matched buy and sell orders crossed against each other (directly or through a small,
concentrated ring of counterparties) to manufacture volume, mark a price, or generate
a misleading impression of liquidity. The signature is the CONVERGENCE of four
independent signals: a high self-match ratio (the trader's own buy and sell volume
matching against itself), documented overlap in beneficial ownership between the
buy-side and sell-side, reported volume materially exceeding the genuine economic
volume actually changing hands, and concentration in a small number of distinct
counterparties -- the fewer the counterparties, the more likely the trades are being
crossed within a controlled ring rather than executed in the open market.

Four components, from the macro framework:

    Self-Match Ratio               0.35   self_matched_volume / total_volume -- how
                                           much of the account's volume matches
                                           against its own opposing orders
    Beneficial Ownership Overlap   0.25   documented overlap between the buy-side and
                                           sell-side beneficial ownership
    Volume Inflation               0.20   reported_volume / genuine_economic_volume --
                                           how much reported volume exceeds the volume
                                           that reflects genuine economic activity
    Counterparty Concentration     0.20   distinct_counterparties -- FEWER is WORSE;
                                           concentration in one or two counterparties
                                           is the wash-trading tell

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_self_match_ratio", "score_beneficial_ownership_overlap",
    "score_volume_inflation", "score_counterparty_concentration", "cm005_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "self_match_ratio": 0.35, "beneficial_ownership_overlap": 0.25,
    "volume_inflation": 0.20, "counterparty_concentration": 0.20,
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


def score_self_match_ratio(self_matched_volume: Any, total_volume: Any) -> str:
    """How much of the account's volume matches against its own opposing orders,
    relative to total volume. Both amounts are REQUIRED."""
    matched = float(_require(self_matched_volume, "self_matched_volume"))
    total = float(_require(total_volume, "total_volume"))
    if total <= 0:
        raise RiskModelError("total_volume must be > 0 to compute a ratio")
    r = matched / total
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_beneficial_ownership_overlap(overlap_score: Any) -> str:
    """Documented overlap between the buy-side and sell-side beneficial ownership.
    REQUIRED -- not measured is not "no overlap"."""
    n = int(float(_require(overlap_score, "overlap_score")))
    if n <= 20:
        return "Low"
    if n <= 50:
        return "Medium"
    if n <= 80:
        return "High"
    return "Critical"


def score_volume_inflation(reported_volume: Any, genuine_economic_volume: Any) -> str:
    """How much reported volume exceeds the volume that reflects genuine economic
    activity. Both amounts are REQUIRED."""
    reported = float(_require(reported_volume, "reported_volume"))
    genuine = float(_require(genuine_economic_volume, "genuine_economic_volume"))
    if genuine <= 0:
        raise RiskModelError("genuine_economic_volume must be > 0 to compute a ratio")
    r = reported / genuine
    if r < 1.2:
        return "Low"
    if r < 1.5:
        return "Medium"
    if r < 2.5:
        return "High"
    return "Critical"


def score_counterparty_concentration(distinct_counterparties: Any) -> str:
    """How many distinct counterparties the volume trades against. REQUIRED --
    FEWER is WORSE: concentration in one or two counterparties is the wash-trading
    tell, so this component's banding is inverted relative to the other three."""
    n = int(float(_require(distinct_counterparties, "distinct_counterparties")))
    if n <= 1:
        return "Critical"
    if n <= 2:
        return "High"
    if n <= 4:
        return "Medium"
    return "Low"


def cm005_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM005_Wash_Trading.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
