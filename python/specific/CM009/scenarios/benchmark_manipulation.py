"""CM009 Benchmark Manipulation scenario — the governed callable.

Pure `evaluate_benchmark_manipulation`. Per trading account it reads the fixing window
concentration (how much of the account's total daily volume is concentrated inside the
fixing window itself), the price distortion (the fixing's price deviation relative to
the instrument's normal deviation for that window), the order timing precision (how
close to the fixing window's close the order was placed), and the repeat pattern
(count of prior fixing windows showing the same pattern), then scores the four
component bands.
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

from cm009_risk_model import (  # noqa: E402
    cm009_exposure_score, score_fixing_window_concentration, score_order_timing_precision,
    score_price_distortion, score_repeat_pattern,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("fixing_orders", "benchmarks")

OUTPUT_COLUMNS = (
    "account_ref", "trader_name", "benchmark_name", "issuer_name",
    "subject_entity_id", "subject_name",
    "fixing_window_volume", "total_daily_volume", "fixing_price_deviation_pct",
    "normal_deviation_pct", "seconds_before_fixing_close", "repeat_occurrences",
    "fixing_window_concentration_band", "price_distortion_band",
    "order_timing_precision_band", "repeat_pattern_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "fixing_window_concentration": "fixing window concentration",
    "price_distortion": "price distortion",
    "order_timing_precision": "order timing precision",
    "repeat_pattern": "repeat pattern",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(order, benchmarks) -> Dict[str, Any]:
    account_ref = str(order["account_ref"])
    benchmark_name = str(order["benchmark_name"])

    bmk = benchmarks[benchmarks["account_ref"] == account_ref]
    if bmk.empty:
        raise ValueError("CM009 cannot score %s: benchmark record for account %s is missing." % (account_ref, account_ref))

    concentration_band = score_fixing_window_concentration(order["fixing_window_volume"], order["total_daily_volume"])
    distortion_band = score_price_distortion(order["fixing_price_deviation_pct"], order["normal_deviation_pct"])
    timing_band = score_order_timing_precision(order["seconds_before_fixing_close"])
    repeat_band = score_repeat_pattern(order["repeat_occurrences"])

    bands = {
        "fixing_window_concentration": concentration_band, "price_distortion": distortion_band,
        "order_timing_precision": timing_band, "repeat_pattern": repeat_band,
    }
    score, band, working = cm009_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "trader_name": str(order["trader_name"]),
        "benchmark_name": benchmark_name, "issuer_name": str(order["issuer_name"]),
        "subject_entity_id": account_ref, "subject_name": str(order["trader_name"]),
        "fixing_window_volume": int(float(order["fixing_window_volume"])),
        "total_daily_volume": int(float(order["total_daily_volume"])),
        "fixing_price_deviation_pct": float(order["fixing_price_deviation_pct"]),
        "normal_deviation_pct": float(order["normal_deviation_pct"]),
        "seconds_before_fixing_close": int(float(order["seconds_before_fixing_close"])),
        "repeat_occurrences": int(float(order["repeat_occurrences"])),
        "fixing_window_concentration_band": concentration_band, "price_distortion_band": distortion_band,
        "order_timing_precision_band": timing_band, "repeat_pattern_band": repeat_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "CM009_BENCHMARK_MANIPULATION",
        "risk_reason": "Volume concentrated into the fixing window's closing seconds, distorting the price "
                       "far beyond the instrument's normal deviation; dominant driver: %s." % dominant,
    }


def score_all(fixing_orders, benchmarks) -> pd.DataFrame:
    rows = [_score(o, benchmarks) for _, o in fixing_orders.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_benchmark_manipulation(fixing_orders, benchmarks) -> pd.DataFrame:
    frames = {"fixing_orders": fixing_orders, "benchmarks": benchmarks}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("CM009 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"fixing_orders": read("fixing_orders.csv"), "benchmarks": read("benchmarks.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_benchmark_manipulation(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "cm009_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "cm009_benchmark_manipulation_alerts.csv", index=False)
    print("CM009 benchmark manipulation scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
