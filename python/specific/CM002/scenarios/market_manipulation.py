"""CM002 Market Manipulation scenario — the governed callable.

Pure `evaluate_market_manipulation`. Per trading account it reads the price impact
ratio (how large the price move is relative to the instrument's normal volatility), the
volume concentration (the account's share of total market volume in the surveillance
window), the coordinated accounts (count of accounts trading in concert), and the
reversal after close (how much of the price move reverses once the manipulative window
closes), then scores the four component bands.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "sample-data"
OUTPUT_DIR = BASE_DIR / "expected_outputs"

if str(BASE_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(BASE_DIR))

from cm002_risk_model import (  # noqa: E402
    cm002_exposure_score, score_coordinated_accounts, score_price_impact_ratio,
    score_reversal_after_close, score_volume_concentration,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("trading_accounts", "counterparties")

OUTPUT_COLUMNS = (
    "account_ref", "account_holder_name", "desk", "instrument",
    "subject_entity_id", "subject_name",
    "normal_volatility_pct", "price_move_pct", "pct_of_market_volume",
    "linked_accounts_count", "post_period_reversal_pct", "ultimate_owner_name",
    "price_impact_ratio_band", "volume_concentration_band",
    "coordinated_accounts_band", "reversal_after_close_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "price_impact_ratio": "price impact ratio",
    "volume_concentration": "volume concentration",
    "coordinated_accounts": "coordinated accounts",
    "reversal_after_close": "reversal after close",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, counterparties) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    owner_name = str(account["ultimate_owner_name"])

    cpty = counterparties[counterparties["account_ref"] == account_ref]
    if cpty.empty:
        raise ValueError("CM002 cannot score %s: counterparty record for account %s is missing." % (account_ref, account_ref))

    impact_band = score_price_impact_ratio(account["price_move_pct"], account["normal_volatility_pct"])
    volume_band = score_volume_concentration(account["pct_of_market_volume"])
    coord_band = score_coordinated_accounts(account["linked_accounts_count"])
    reversal_band = score_reversal_after_close(account["post_period_reversal_pct"], account["price_move_pct"])

    bands = {
        "price_impact_ratio": impact_band, "volume_concentration": volume_band,
        "coordinated_accounts": coord_band, "reversal_after_close": reversal_band,
    }
    score, band, working = cm002_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "account_holder_name": str(account["account_holder_name"]),
        "desk": str(account["desk"]), "instrument": str(account["instrument"]),
        "subject_entity_id": account_ref, "subject_name": str(account["account_holder_name"]),
        "normal_volatility_pct": float(account["normal_volatility_pct"]),
        "price_move_pct": float(account["price_move_pct"]),
        "pct_of_market_volume": int(float(account["pct_of_market_volume"])),
        "linked_accounts_count": int(float(account["linked_accounts_count"])),
        "post_period_reversal_pct": float(account["post_period_reversal_pct"]),
        "ultimate_owner_name": owner_name,
        "price_impact_ratio_band": impact_band, "volume_concentration_band": volume_band,
        "coordinated_accounts_band": coord_band, "reversal_after_close_band": reversal_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "CM002_MARKET_MANIPULATION",
        "risk_reason": "Price moved well beyond normal volatility on an outsized share of market volume, "
                       "coordinated across linked accounts, and largely reversed once the window closed; "
                       "dominant driver: %s." % dominant,
    }


def score_all(trading_accounts, counterparties) -> pd.DataFrame:
    rows = [_score(a, counterparties) for _, a in trading_accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_market_manipulation(trading_accounts, counterparties) -> pd.DataFrame:
    frames = {"trading_accounts": trading_accounts, "counterparties": counterparties}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("CM002 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"trading_accounts": read("trading_accounts.csv"), "counterparties": read("counterparties.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_market_manipulation(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "cm002_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "cm002_market_manipulation_alerts.csv", index=False)
    print("CM002 market manipulation scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
