"""CM002 Market Manipulation — capital-markets exposure risk model.

Market manipulation is the artificial distortion of a security's price or volume to
create a false or misleading impression of supply, demand or price, so a position can
be exited (or a benchmark can be gamed) at an advantage. The signature is the
CONVERGENCE of four independent signals: an abnormal price move relative to the
instrument's normal volatility, a trading footprint that is an outsized share of total
market volume, coordination across linked accounts trading in concert, and a reversal
of the price move once the manipulative window closes -- proof the move was not
information-driven.

Four components, from the macro framework:

    Price Impact Ratio          0.35   how large the price move is, relative to the
                                        instrument's normal volatility, in the
                                        surveillance window
    Volume Concentration        0.25   the account's share of total market volume in
                                        the surveillance window
    Coordinated Accounts        0.20   count of accounts trading in concert with this
                                        account
    Reversal After Close        0.20   how much of the price move reverses once the
                                        manipulative window closes

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites operations/common/Risk_Scoring_Governance.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_price_impact_ratio", "score_volume_concentration",
    "score_coordinated_accounts", "score_reversal_after_close", "cm002_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "price_impact_ratio": 0.35, "volume_concentration": 0.25,
    "coordinated_accounts": 0.20, "reversal_after_close": 0.20,
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


def score_price_impact_ratio(price_move_pct: Any, normal_volatility_pct: Any) -> str:
    """The core market-manipulation signal: how large the price move is, relative to
    the instrument's normal volatility, in the surveillance window. Both amounts are
    REQUIRED."""
    move = float(_require(price_move_pct, "price_move_pct"))
    normal = float(_require(normal_volatility_pct, "normal_volatility_pct"))
    if normal <= 0:
        raise RiskModelError("normal_volatility_pct must be > 0 to compute a ratio")
    r = move / normal
    if r < 1.5:
        return "Low"
    if r < 3.0:
        return "Medium"
    if r < 6.0:
        return "High"
    return "Critical"


def score_volume_concentration(pct_of_market_volume: Any) -> str:
    """The account's share of total market volume in the surveillance window.
    REQUIRED -- not measured is not "a negligible share of the market"."""
    n = int(float(_require(pct_of_market_volume, "pct_of_market_volume")))
    if n <= 10:
        return "Low"
    if n <= 25:
        return "Medium"
    if n <= 45:
        return "High"
    return "Critical"


def score_coordinated_accounts(linked_accounts_count: Any) -> str:
    """Count of accounts trading in concert with this account. REQUIRED."""
    n = int(float(_require(linked_accounts_count, "linked_accounts_count")))
    if n <= 1:
        return "Low"
    if n == 2:
        return "Medium"
    if n <= 4:
        return "High"
    return "Critical"


def score_reversal_after_close(post_period_reversal_pct: Any, price_move_pct: Any) -> str:
    """How much of the price move reverses once the manipulative window closes --
    the step that turns an abnormal price move into a completed manipulation leg,
    since a genuine information-driven move does not unwind."""
    reversal = float(_require(post_period_reversal_pct, "post_period_reversal_pct"))
    move = float(_require(price_move_pct, "price_move_pct"))
    if move <= 0:
        raise RiskModelError("price_move_pct must be > 0 to compute a ratio")
    r = reversal / move
    if r < 0.25:
        return "Low"
    if r < 0.50:
        return "Medium"
    if r < 0.80:
        return "High"
    return "Critical"


def cm002_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "typologies/CM002_Market_Manipulation.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
