"""CM003 Spoofing scenario — the governed callable.

Pure `evaluate_spoofing`. Per trading account it reads the non-bona-fide order ratio
(share of order value placed with no intention to execute), the cancellation speed
(average time from placement to cancellation), the order book imbalance created (share
of visible depth on one side the spoof orders manufacture), and the opposite-side
execution (genuine execution on the opposite side while the spoof orders are working),
then scores the four component bands.
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

from cm003_risk_model import (  # noqa: E402
    cm003_exposure_score, score_cancellation_speed, score_non_bona_fide_order_ratio,
    score_opposite_side_execution, score_order_book_imbalance_created,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("orders", "brokers")

OUTPUT_COLUMNS = (
    "account_ref", "trader_name", "instrument", "broker_name",
    "subject_entity_id", "subject_name",
    "total_order_value", "spoof_order_value", "avg_cancel_seconds",
    "spoof_side_depth", "genuine_side_depth", "opposite_side_filled_value",
    "non_bona_fide_order_ratio_band", "cancellation_speed_band",
    "order_book_imbalance_created_band", "opposite_side_execution_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "non_bona_fide_order_ratio": "non-bona-fide order ratio",
    "cancellation_speed": "cancellation speed",
    "order_book_imbalance_created": "order book imbalance created",
    "opposite_side_execution": "opposite-side execution",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(order, brokers) -> Dict[str, Any]:
    account_ref = str(order["account_ref"])
    broker_name = str(order["broker_name"])

    src = brokers[brokers["account_ref"] == account_ref]
    if src.empty:
        raise ValueError("CM003 cannot score %s: broker record for account %s is missing." % (account_ref, account_ref))

    ratio_band = score_non_bona_fide_order_ratio(order["spoof_order_value"], order["total_order_value"])
    speed_band = score_cancellation_speed(order["avg_cancel_seconds"])
    imbalance_band = score_order_book_imbalance_created(order["spoof_side_depth"], order["genuine_side_depth"])
    execution_band = score_opposite_side_execution(order["opposite_side_filled_value"], order["spoof_order_value"])

    bands = {
        "non_bona_fide_order_ratio": ratio_band, "cancellation_speed": speed_band,
        "order_book_imbalance_created": imbalance_band, "opposite_side_execution": execution_band,
    }
    score, band, working = cm003_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "trader_name": str(order["trader_name"]),
        "instrument": str(order["instrument"]), "broker_name": broker_name,
        "subject_entity_id": account_ref, "subject_name": str(order["trader_name"]),
        "total_order_value": int(float(order["total_order_value"])),
        "spoof_order_value": int(float(order["spoof_order_value"])),
        "avg_cancel_seconds": float(order["avg_cancel_seconds"]),
        "spoof_side_depth": int(float(order["spoof_side_depth"])),
        "genuine_side_depth": int(float(order["genuine_side_depth"])),
        "opposite_side_filled_value": int(float(order["opposite_side_filled_value"])),
        "non_bona_fide_order_ratio_band": ratio_band, "cancellation_speed_band": speed_band,
        "order_book_imbalance_created_band": imbalance_band, "opposite_side_execution_band": execution_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "CM003_SPOOFING",
        "risk_reason": "Orders placed with no intention to execute, cancelled before the market could react, "
                       "and genuine execution taken on the opposite side; dominant driver: %s." % dominant,
    }


def score_all(orders, brokers) -> pd.DataFrame:
    rows = [_score(o, brokers) for _, o in orders.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_spoofing(orders, brokers) -> pd.DataFrame:
    frames = {"orders": orders, "brokers": brokers}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("CM003 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"orders": read("orders.csv"), "brokers": read("brokers.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_spoofing(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "cm003_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "cm003_spoofing_alerts.csv", index=False)
    print("CM003 spoofing scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
