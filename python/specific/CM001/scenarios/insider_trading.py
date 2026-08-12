"""CM001 Insider Trading scenario — the governed callable.

Pure `evaluate_insider_trading`. Per trading account it reads the pre-event position
build (how large the position build is relative to the trader's normal average
position), the timing proximity to the event (how close to the event the position was
built), the information access linkage (documented contact events with an information
source in the 90 days before the event), and the profit realisation (realised P&L
relative to the position's entry value), then scores the four component bands.
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

from cm001_risk_model import (  # noqa: E402
    cm001_exposure_score, score_information_access_linkage, score_pre_event_position_build,
    score_profit_realisation, score_timing_proximity_to_event,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("trading_accounts", "information_sources")

OUTPUT_COLUMNS = (
    "account_ref", "trader_name", "desk", "issuer_name",
    "subject_entity_id", "subject_name",
    "normal_average_position", "pre_event_position_increase", "days_before_event",
    "contact_events_90d", "position_value_at_entry", "realized_pnl", "information_source_name",
    "pre_event_position_build_band", "timing_proximity_to_event_band",
    "information_access_linkage_band", "profit_realisation_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "pre_event_position_build": "pre-event position build",
    "timing_proximity_to_event": "timing proximity to the event",
    "information_access_linkage": "information access linkage",
    "profit_realisation": "profit realisation after the event",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, information_sources) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    source_name = str(account["information_source_name"])

    src = information_sources[information_sources["account_ref"] == account_ref]
    if src.empty:
        raise ValueError("CM001 cannot score %s: information-source record for account %s is missing." % (account_ref, account_ref))

    build_band = score_pre_event_position_build(account["pre_event_position_increase"], account["normal_average_position"])
    timing_band = score_timing_proximity_to_event(account["days_before_event"])
    linkage_band = score_information_access_linkage(account["contact_events_90d"])
    profit_band = score_profit_realisation(account["realized_pnl"], account["position_value_at_entry"])

    bands = {
        "pre_event_position_build": build_band, "timing_proximity_to_event": timing_band,
        "information_access_linkage": linkage_band, "profit_realisation": profit_band,
    }
    score, band, working = cm001_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "trader_name": str(account["trader_name"]),
        "desk": str(account["desk"]), "issuer_name": str(account["issuer_name"]),
        "subject_entity_id": account_ref, "subject_name": str(account["trader_name"]),
        "normal_average_position": int(float(account["normal_average_position"])),
        "pre_event_position_increase": int(float(account["pre_event_position_increase"])),
        "days_before_event": int(float(account["days_before_event"])),
        "contact_events_90d": int(float(account["contact_events_90d"])),
        "position_value_at_entry": int(float(account["position_value_at_entry"])),
        "realized_pnl": int(float(account["realized_pnl"])),
        "information_source_name": source_name,
        "pre_event_position_build_band": build_band, "timing_proximity_to_event_band": timing_band,
        "information_access_linkage_band": linkage_band, "profit_realisation_band": profit_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "CM001_INSIDER_TRADING",
        "risk_reason": "Position built ahead of a material non-public event and profit realised "
                       "once its price impact landed; dominant driver: %s." % dominant,
    }


def score_all(trading_accounts, information_sources) -> pd.DataFrame:
    rows = [_score(a, information_sources) for _, a in trading_accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_insider_trading(trading_accounts, information_sources) -> pd.DataFrame:
    frames = {"trading_accounts": trading_accounts, "information_sources": information_sources}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("CM001 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"trading_accounts": read("trading_accounts.csv"), "information_sources": read("information_sources.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_insider_trading(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "cm001_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "cm001_insider_trading_alerts.csv", index=False)
    print("CM001 insider trading scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
