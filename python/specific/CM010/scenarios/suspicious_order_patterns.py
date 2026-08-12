"""CM010 Suspicious Order Patterns scenario — the governed callable.

Pure `evaluate_suspicious_order_patterns`. Per trading account it reads the
cancel/amend rate (cancelled orders as a share of total orders), the quote stuffing
intensity (peak order-submission rate observed), the momentum ignition signal (price
move after an order burst relative to the instrument's normal move), and the order
size anomaly (average order size relative to the account's normal order size), then
scores the four component bands.
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

from cm010_risk_model import (  # noqa: E402
    cm010_exposure_score, score_cancel_amend_rate, score_momentum_ignition_signal,
    score_order_size_anomaly, score_quote_stuffing_intensity,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("order_flow", "venues")

OUTPUT_COLUMNS = (
    "account_ref", "trader_name", "instrument", "venue_operator_name",
    "subject_entity_id", "subject_name",
    "cancelled_orders", "total_orders", "orders_per_second",
    "price_move_after_burst_pct", "normal_move_pct", "avg_order_size", "normal_order_size",
    "cancel_amend_rate_band", "quote_stuffing_intensity_band",
    "momentum_ignition_signal_band", "order_size_anomaly_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "cancel_amend_rate": "cancel/amend rate",
    "quote_stuffing_intensity": "quote stuffing intensity",
    "momentum_ignition_signal": "momentum ignition signal",
    "order_size_anomaly": "order size anomaly",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, venues) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    venue_name = str(account["venue_operator_name"])

    venue = venues[venues["account_ref"] == account_ref]
    if venue.empty:
        raise ValueError("CM010 cannot score %s: venue record for account %s is missing." % (account_ref, account_ref))

    cancel_band = score_cancel_amend_rate(account["cancelled_orders"], account["total_orders"])
    quote_band = score_quote_stuffing_intensity(account["orders_per_second"])
    momentum_band = score_momentum_ignition_signal(account["price_move_after_burst_pct"], account["normal_move_pct"])
    size_band = score_order_size_anomaly(account["avg_order_size"], account["normal_order_size"])

    bands = {
        "cancel_amend_rate": cancel_band, "quote_stuffing_intensity": quote_band,
        "momentum_ignition_signal": momentum_band, "order_size_anomaly": size_band,
    }
    score, band, working = cm010_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "trader_name": str(account["trader_name"]),
        "instrument": str(account["instrument"]), "venue_operator_name": venue_name,
        "subject_entity_id": account_ref, "subject_name": str(account["trader_name"]),
        "cancelled_orders": int(float(account["cancelled_orders"])),
        "total_orders": int(float(account["total_orders"])),
        "orders_per_second": int(float(account["orders_per_second"])),
        "price_move_after_burst_pct": float(account["price_move_after_burst_pct"]),
        "normal_move_pct": float(account["normal_move_pct"]),
        "avg_order_size": int(float(account["avg_order_size"])),
        "normal_order_size": int(float(account["normal_order_size"])),
        "cancel_amend_rate_band": cancel_band, "quote_stuffing_intensity_band": quote_band,
        "momentum_ignition_signal_band": momentum_band, "order_size_anomaly_band": size_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "CM010_SUSPICIOUS_ORDER_PATTERNS",
        "risk_reason": "Order flow shows a cancel/amend and order-submission burst pattern consistent with "
                       "quote stuffing and momentum ignition; dominant driver: %s." % dominant,
    }


def score_all(order_flow, venues) -> pd.DataFrame:
    rows = [_score(a, venues) for _, a in order_flow.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_suspicious_order_patterns(order_flow, venues) -> pd.DataFrame:
    frames = {"order_flow": order_flow, "venues": venues}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("CM010 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"order_flow": read("order_flow.csv"), "venues": read("venues.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_suspicious_order_patterns(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "cm010_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "cm010_suspicious_order_patterns_alerts.csv", index=False)
    print("CM010 suspicious order patterns scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
