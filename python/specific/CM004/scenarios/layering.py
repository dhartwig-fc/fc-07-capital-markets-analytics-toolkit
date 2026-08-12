"""CM004 Layering scenario — the governed callable.

Pure `evaluate_layering`. Per trading account it reads the staggered order levels (how
many distinct price levels the staggered orders sit at), the order-to-trade ratio
(orders placed per order actually executed), the book imbalance created (the share of
visible book depth the staggered orders create on one side), and the reversal speed
(how quickly the staggered orders are pulled once the book has moved), then scores the
four component bands.
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

from cm004_risk_model import (  # noqa: E402
    cm004_exposure_score, score_book_imbalance_created, score_order_to_trade_ratio,
    score_reversal_speed, score_staggered_order_levels,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("orders", "venues")

OUTPUT_COLUMNS = (
    "account_ref", "trader_name", "instrument",
    "subject_entity_id", "subject_name",
    "distinct_price_levels", "orders_placed", "orders_executed",
    "imbalance_ratio", "seconds_to_reversal", "venue_operator_name",
    "staggered_order_levels_band", "order_to_trade_ratio_band",
    "book_imbalance_created_band", "reversal_speed_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "staggered_order_levels": "staggered order levels",
    "order_to_trade_ratio": "order-to-trade ratio",
    "book_imbalance_created": "book imbalance created",
    "reversal_speed": "reversal speed",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(order, venues) -> Dict[str, Any]:
    account_ref = str(order["account_ref"])
    venue_name = str(order["venue_operator_name"])

    ven = venues[venues["account_ref"] == account_ref]
    if ven.empty:
        raise ValueError("CM004 cannot score %s: venue record for account %s is missing." % (account_ref, account_ref))

    levels_band = score_staggered_order_levels(order["distinct_price_levels"])
    ratio_band = score_order_to_trade_ratio(order["orders_placed"], order["orders_executed"])
    imbalance_band = score_book_imbalance_created(order["imbalance_ratio"])
    reversal_band = score_reversal_speed(order["seconds_to_reversal"])

    bands = {
        "staggered_order_levels": levels_band, "order_to_trade_ratio": ratio_band,
        "book_imbalance_created": imbalance_band, "reversal_speed": reversal_band,
    }
    score, band, working = cm004_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "trader_name": str(order["trader_name"]),
        "instrument": str(order["instrument"]),
        "subject_entity_id": account_ref, "subject_name": str(order["trader_name"]),
        "distinct_price_levels": int(float(order["distinct_price_levels"])),
        "orders_placed": int(float(order["orders_placed"])),
        "orders_executed": int(float(order["orders_executed"])),
        "imbalance_ratio": float(order["imbalance_ratio"]),
        "seconds_to_reversal": float(order["seconds_to_reversal"]),
        "venue_operator_name": venue_name,
        "staggered_order_levels_band": levels_band, "order_to_trade_ratio_band": ratio_band,
        "book_imbalance_created_band": imbalance_band, "reversal_speed_band": reversal_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "CM004_LAYERING",
        "risk_reason": "Staggered price-level orders created a false impression of book depth and were "
                       "reversed once the book moved; dominant driver: %s." % dominant,
    }


def score_all(orders, venues) -> pd.DataFrame:
    rows = [_score(o, venues) for _, o in orders.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_layering(orders, venues) -> pd.DataFrame:
    frames = {"orders": orders, "venues": venues}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("CM004 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"orders": read("orders.csv"), "venues": read("venues.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_layering(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "cm004_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "cm004_layering_alerts.csv", index=False)
    print("CM004 layering scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
