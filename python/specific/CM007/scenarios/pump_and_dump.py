"""CM007 Pump and Dump scenario — the governed callable.

Pure `evaluate_pump_and_dump`. Per trading account it reads the accumulation
concentration (share of the free float accumulated pre-promotion), the promotional
coordination (count of coordinated promotional posts/messages/accounts identified),
the price inflation (peak price relative to the pre-campaign baseline), and the
distribution into retail (volume sold to retail relative to the account's total
position), then scores the four component bands.
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

from cm007_risk_model import (  # noqa: E402
    cm007_exposure_score, score_accumulation_concentration, score_distribution_into_retail,
    score_price_inflation, score_promotional_coordination,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("trading_accounts", "promoters")

OUTPUT_COLUMNS = (
    "account_ref", "trader_name", "instrument", "promoter_name",
    "subject_entity_id", "subject_name",
    "pct_of_float_accumulated", "coordinated_posts_count", "price_peak", "price_baseline",
    "volume_sold_to_retail", "total_position", "promoter_id",
    "accumulation_concentration_band", "promotional_coordination_band",
    "price_inflation_band", "distribution_into_retail_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "accumulation_concentration": "accumulation concentration",
    "promotional_coordination": "promotional coordination",
    "price_inflation": "price inflation",
    "distribution_into_retail": "distribution into retail",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, promoters) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    promoter_id = str(account["promoter_id"])

    src = promoters[promoters["account_ref"] == account_ref]
    if src.empty:
        raise ValueError("CM007 cannot score %s: promoter record for account %s is missing." % (account_ref, account_ref))

    accumulation_band = score_accumulation_concentration(account["pct_of_float_accumulated"])
    coordination_band = score_promotional_coordination(account["coordinated_posts_count"])
    inflation_band = score_price_inflation(account["price_peak"], account["price_baseline"])
    distribution_band = score_distribution_into_retail(account["volume_sold_to_retail"], account["total_position"])

    bands = {
        "accumulation_concentration": accumulation_band, "promotional_coordination": coordination_band,
        "price_inflation": inflation_band, "distribution_into_retail": distribution_band,
    }
    score, band, working = cm007_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "trader_name": str(account["trader_name"]),
        "instrument": str(account["instrument"]), "promoter_name": str(account["promoter_name"]),
        "subject_entity_id": account_ref, "subject_name": str(account["trader_name"]),
        "pct_of_float_accumulated": int(float(account["pct_of_float_accumulated"])),
        "coordinated_posts_count": int(float(account["coordinated_posts_count"])),
        "price_peak": float(account["price_peak"]), "price_baseline": float(account["price_baseline"]),
        "volume_sold_to_retail": int(float(account["volume_sold_to_retail"])),
        "total_position": int(float(account["total_position"])),
        "promoter_id": promoter_id,
        "accumulation_concentration_band": accumulation_band, "promotional_coordination_band": coordination_band,
        "price_inflation_band": inflation_band, "distribution_into_retail_band": distribution_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "CM007_PUMP_AND_DUMP",
        "risk_reason": "Free float accumulated ahead of a coordinated promotional campaign and the "
                       "position distributed into the retail buying it created; dominant driver: %s." % dominant,
    }


def score_all(trading_accounts, promoters) -> pd.DataFrame:
    rows = [_score(a, promoters) for _, a in trading_accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_pump_and_dump(trading_accounts, promoters) -> pd.DataFrame:
    frames = {"trading_accounts": trading_accounts, "promoters": promoters}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("CM007 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"trading_accounts": read("trading_accounts.csv"), "promoters": read("promoters.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_pump_and_dump(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "cm007_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "cm007_pump_and_dump_alerts.csv", index=False)
    print("CM007 pump and dump scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
