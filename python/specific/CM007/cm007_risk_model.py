"""CM007 Pump and Dump — capital-markets exposure risk model.

Pump and dump is coordinated promotion of a thinly-traded, low-float instrument to
inflate its price on false or misleading enthusiasm, followed by distribution of the
promoter's (and colluding accounts') position into the retail buying the promotion
creates. The signature is the CONVERGENCE of four independent signals: a concentrated
pre-promotion accumulation of the free float, a burst of coordinated promotional
activity, a price spike well beyond the instrument's baseline, and a distribution of
volume into retail once the price is inflated.

Four components, from the macro framework:

    Accumulation Concentration   0.35   share of the free float accumulated by the
                                         account before the promotional campaign
    Promotional Coordination     0.25   count of coordinated promotional posts,
                                         messages or accounts identified around the
                                         campaign
    Price Inflation               0.20   peak price relative to the pre-campaign
                                         baseline price
    Distribution Into Retail      0.20   volume sold to retail relative to the
                                         account's total position, once the price is
                                         inflated

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_accumulation_concentration", "score_promotional_coordination",
    "score_price_inflation", "score_distribution_into_retail", "cm007_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "accumulation_concentration": 0.35, "promotional_coordination": 0.25,
    "price_inflation": 0.20, "distribution_into_retail": 0.20,
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


def score_accumulation_concentration(pct_of_float_accumulated: Any) -> str:
    """The core pump-and-dump signal: the share of the free float accumulated by the
    account before the promotional campaign began. REQUIRED -- not measured is not
    "no accumulation"."""
    pct = float(_require(pct_of_float_accumulated, "pct_of_float_accumulated"))
    if pct <= 10:
        return "Low"
    if pct <= 25:
        return "Medium"
    if pct <= 45:
        return "High"
    return "Critical"


def score_promotional_coordination(coordinated_posts_count: Any) -> str:
    """Count of coordinated promotional posts, messages or accounts identified
    around the campaign. REQUIRED."""
    n = int(float(_require(coordinated_posts_count, "coordinated_posts_count")))
    if n <= 2:
        return "Low"
    if n <= 5:
        return "Medium"
    if n <= 9:
        return "High"
    return "Critical"


def score_price_inflation(price_peak: Any, price_baseline: Any) -> str:
    """The peak price reached during the campaign relative to the pre-campaign
    baseline price -- unbounded, larger is worse."""
    peak = float(_require(price_peak, "price_peak"))
    baseline = float(_require(price_baseline, "price_baseline"))
    if baseline <= 0:
        raise RiskModelError("price_baseline must be > 0 to compute a ratio")
    r = peak / baseline
    if r < 1.3:
        return "Low"
    if r < 1.8:
        return "Medium"
    if r < 3.0:
        return "High"
    return "Critical"


def score_distribution_into_retail(volume_sold_to_retail: Any, total_position: Any) -> str:
    """How much of the account's total position was distributed into the retail
    buying the promotion creates, once the price is inflated -- the step that turns
    the pump into a completed dump."""
    volume = float(_require(volume_sold_to_retail, "volume_sold_to_retail"))
    total = float(_require(total_position, "total_position"))
    if total <= 0:
        raise RiskModelError("total_position must be > 0 to compute a ratio")
    r = volume / total
    if r < 0.25:
        return "Low"
    if r < 0.50:
        return "Medium"
    if r < 0.80:
        return "High"
    return "Critical"


def cm007_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM007_Pump_and_Dump.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
