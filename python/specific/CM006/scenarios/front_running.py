"""CM006 Front Running scenario — the governed callable.

Pure `evaluate_front_running`. Per trading account it reads the timing ahead of the
client order (how many seconds before the client's own order the trader's order was
placed), the position correlation (correlation between the trader's pre-position
direction and the client order's direction), the profit capture (realised P&L relative
to the position's value, once the client order landed), and the client order knowledge
linkage (documented contact events between the trader and the desk handling the client
order in the 90 days before), then scores the four component bands.
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

from cm006_risk_model import (  # noqa: E402
    cm006_exposure_score, score_client_order_knowledge_linkage, score_position_correlation,
    score_profit_capture, score_timing_ahead_of_client_order,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("trading_accounts", "client_orders")

OUTPUT_COLUMNS = (
    "account_ref", "trader_name", "desk", "instrument",
    "subject_entity_id", "subject_name",
    "seconds_ahead_of_client_order", "correlation_pct", "realized_pnl",
    "position_value", "contact_events_90d", "client_firm_name",
    "timing_ahead_of_client_order_band", "position_correlation_band",
    "profit_capture_band", "client_order_knowledge_linkage_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "timing_ahead_of_client_order": "timing ahead of the client order",
    "position_correlation": "position correlation",
    "profit_capture": "profit capture",
    "client_order_knowledge_linkage": "client order knowledge linkage",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, client_orders) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    client_name = str(account["client_firm_name"])

    ord_ = client_orders[client_orders["account_ref"] == account_ref]
    if ord_.empty:
        raise ValueError("CM006 cannot score %s: client-order record for account %s is missing." % (account_ref, account_ref))

    timing_band = score_timing_ahead_of_client_order(account["seconds_ahead_of_client_order"])
    correlation_band = score_position_correlation(account["correlation_pct"])
    profit_band = score_profit_capture(account["realized_pnl"], account["position_value"])
    linkage_band = score_client_order_knowledge_linkage(account["contact_events_90d"])

    bands = {
        "timing_ahead_of_client_order": timing_band, "position_correlation": correlation_band,
        "profit_capture": profit_band, "client_order_knowledge_linkage": linkage_band,
    }
    score, band, working = cm006_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "trader_name": str(account["trader_name"]),
        "desk": str(account["desk"]), "instrument": str(account["instrument"]),
        "subject_entity_id": account_ref, "subject_name": str(account["trader_name"]),
        "seconds_ahead_of_client_order": float(account["seconds_ahead_of_client_order"]),
        "correlation_pct": int(float(account["correlation_pct"])),
        "realized_pnl": int(float(account["realized_pnl"])),
        "position_value": int(float(account["position_value"])),
        "contact_events_90d": int(float(account["contact_events_90d"])),
        "client_firm_name": client_name,
        "timing_ahead_of_client_order_band": timing_band, "position_correlation_band": correlation_band,
        "profit_capture_band": profit_band, "client_order_knowledge_linkage_band": linkage_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "CM006_FRONT_RUNNING",
        "risk_reason": "Trader dealt ahead of the client order in the same direction and captured "
                       "disproportionate profit once it landed; dominant driver: %s." % dominant,
    }


def score_all(trading_accounts, client_orders) -> pd.DataFrame:
    rows = [_score(a, client_orders) for _, a in trading_accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_front_running(trading_accounts, client_orders) -> pd.DataFrame:
    frames = {"trading_accounts": trading_accounts, "client_orders": client_orders}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("CM006 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"trading_accounts": read("trading_accounts.csv"), "client_orders": read("client_orders.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_front_running(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "cm006_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "cm006_front_running_alerts.csv", index=False)
    print("CM006 front running scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
