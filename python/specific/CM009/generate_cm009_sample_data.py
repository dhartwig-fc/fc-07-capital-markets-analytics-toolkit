"""Generate synthetic sample data for CM009 Benchmark Manipulation.

22 trading accounts (>= the 20-row sample-data standard; CM009 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Sergei Ivanov, 90/Critical, the single highest-scoring account
in the set) concentrates volume into the closing seconds of a USD reference-rate
fixing window, distorting the price far beyond the instrument's normal deviation, with
the issuer of record being **Gamma Imports Ltd** -- an entity already in the estate
network -- so canonical entity resolution joins CM009 onto the existing fused case.
Being the top-scored account matters: the FC-10 adapter builds its case/graph from the
single highest exposure_score row, so the Gamma Imports Ltd bridge has to be that row,
not merely A Critical row.

Run:  python3 generate_cm009_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, benchmark_name, fixing_window_volume, total_daily_volume,
# fixing_price_deviation_pct, normal_deviation_pct, seconds_before_fixing_close,
# repeat_occurrences, issuer_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"trader_name": "Marta Kowalski", "account_ref": "ACC001", "benchmark_name": "SONIA 3-Month Fixing",
     "fixing_window_volume": 1680000, "total_daily_volume": 42000000,
     "fixing_price_deviation_pct": 0.200, "normal_deviation_pct": 0.20,
     "seconds_before_fixing_close": 120, "repeat_occurrences": 0, "issuer_name": "Alpha Trading Ltd"},
    {"trader_name": "Dmitri Volkov", "account_ref": "ACC002", "benchmark_name": "EURIBOR 3-Month Fixing",
     "fixing_window_volume": 2310000, "total_daily_volume": 38500000,
     "fixing_price_deviation_pct": 0.225, "normal_deviation_pct": 0.25,
     "seconds_before_fixing_close": 95, "repeat_occurrences": 2, "issuer_name": "Zeta Commodities Ltd"},
    {"trader_name": "Fatima Al-Rashid", "account_ref": "ACC003", "benchmark_name": "WM/Reuters 4pm London Fix (GBP/USD)",
     "fixing_window_volume": 2550000, "total_daily_volume": 51000000,
     "fixing_price_deviation_pct": 0.198, "normal_deviation_pct": 0.18,
     "seconds_before_fixing_close": 40, "repeat_occurrences": 1, "issuer_name": "Continental Correspondent Bank"},
    {"trader_name": "Connor Doyle", "account_ref": "ACC004", "benchmark_name": "LBMA Gold Price PM Fixing",
     "fixing_window_volume": 2384000, "total_daily_volume": 29800000,
     "fixing_price_deviation_pct": 0.396, "normal_deviation_pct": 0.22,
     "seconds_before_fixing_close": 150, "repeat_occurrences": 0, "issuer_name": "Ravenwood Trading Co"},
    {"trader_name": "Ines Alves", "account_ref": "ACC005", "benchmark_name": "ICE Brent Crude Settlement Fixing",
     "fixing_window_volume": 7095000, "total_daily_volume": 47300000,
     "fixing_price_deviation_pct": 0.360, "normal_deviation_pct": 0.30,
     "seconds_before_fixing_close": 110, "repeat_occurrences": 1, "issuer_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Haruto Nakamura", "account_ref": "ACC006", "benchmark_name": "SOFR Overnight Fixing",
     "fixing_window_volume": 2352000, "total_daily_volume": 33600000,
     "fixing_price_deviation_pct": 0.150, "normal_deviation_pct": 0.15,
     "seconds_before_fixing_close": 35, "repeat_occurrences": 2, "issuer_name": "Highgate Commodities Ltd"},
    {"trader_name": "Isabela Santos", "account_ref": "ACC007", "benchmark_name": "Platts Dated Brent Assessment",
     "fixing_window_volume": 8262000, "total_daily_volume": 45900000,
     "fixing_price_deviation_pct": 0.400, "normal_deviation_pct": 0.20,
     "seconds_before_fixing_close": 130, "repeat_occurrences": 0, "issuer_name": "Northwind Freight Co"},
    {"trader_name": "Karl Fischer", "account_ref": "ACC008", "benchmark_name": "LME Copper Official Settlement",
     "fixing_window_volume": 11528000, "total_daily_volume": 52400000,
     "fixing_price_deviation_pct": 0.414, "normal_deviation_pct": 0.18,
     "seconds_before_fixing_close": 45, "repeat_occurrences": 1, "issuer_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Noor Haidari", "account_ref": "ACC009", "benchmark_name": "SONIA 3-Month Fixing",
     "fixing_window_volume": 9175000, "total_daily_volume": 36700000,
     "fixing_price_deviation_pct": 0.475, "normal_deviation_pct": 0.25,
     "seconds_before_fixing_close": 50, "repeat_occurrences": 2, "issuer_name": "Alpha Trading Ltd"},
    {"trader_name": "Liu Wei", "account_ref": "ACC010", "benchmark_name": "EURIBOR 3-Month Fixing",
     "fixing_window_volume": 8240000, "total_daily_volume": 41200000,
     "fixing_price_deviation_pct": 0.400, "normal_deviation_pct": 0.16,
     "seconds_before_fixing_close": 15, "repeat_occurrences": 1, "issuer_name": "Zeta Commodities Ltd"},
    {"trader_name": "Petra Novakova", "account_ref": "ACC011", "benchmark_name": "WM/Reuters 4pm London Fix (EUR/USD)",
     "fixing_window_volume": 10982000, "total_daily_volume": 28900000,
     "fixing_price_deviation_pct": 0.238, "normal_deviation_pct": 0.28,
     "seconds_before_fixing_close": 30, "repeat_occurrences": 2, "issuer_name": "Continental Correspondent Bank"},
    {"trader_name": "Samuel Osei", "account_ref": "ACC012", "benchmark_name": "LBMA Gold Price PM Fixing",
     "fixing_window_volume": 12015000, "total_daily_volume": 44500000,
     "fixing_price_deviation_pct": 0.760, "normal_deviation_pct": 0.20,
     "seconds_before_fixing_close": 55, "repeat_occurrences": 0, "issuer_name": "Ravenwood Trading Co"},
    {"trader_name": "Yuki Tanaka", "account_ref": "ACC013", "benchmark_name": "ICE Brent Crude Settlement Fixing",
     "fixing_window_volume": 20670000, "total_daily_volume": 31800000,
     "fixing_price_deviation_pct": 1.050, "normal_deviation_pct": 0.15,
     "seconds_before_fixing_close": 170, "repeat_occurrences": 1, "issuer_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Anton Petrov", "account_ref": "ACC014", "benchmark_name": "SOFR Overnight Fixing",
     "fixing_window_volume": 27720000, "total_daily_volume": 39600000,
     "fixing_price_deviation_pct": 0.924, "normal_deviation_pct": 0.22,
     "seconds_before_fixing_close": 42, "repeat_occurrences": 0, "issuer_name": "Highgate Commodities Ltd"},
    {"trader_name": "Chiara Romano", "account_ref": "ACC015", "benchmark_name": "Platts Dated Brent Assessment",
     "fixing_window_volume": 21690000, "total_daily_volume": 48200000,
     "fixing_price_deviation_pct": 0.864, "normal_deviation_pct": 0.18,
     "seconds_before_fixing_close": 12, "repeat_occurrences": 2, "issuer_name": "Northwind Freight Co"},
    {"trader_name": "Rajesh Kumar", "account_ref": "ACC016", "benchmark_name": "LME Copper Official Settlement",
     "fixing_window_volume": 20475000, "total_daily_volume": 27300000,
     "fixing_price_deviation_pct": 1.500, "normal_deviation_pct": 0.20,
     "seconds_before_fixing_close": 38, "repeat_occurrences": 1, "issuer_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Greta Lindqvist", "account_ref": "ACC017", "benchmark_name": "SONIA 3-Month Fixing",
     "fixing_window_volume": 22724000, "total_daily_volume": 43700000,
     "fixing_price_deviation_pct": 1.200, "normal_deviation_pct": 0.24,
     "seconds_before_fixing_close": 4, "repeat_occurrences": 2, "issuer_name": "Alpha Trading Ltd"},
    {"trader_name": "Mateus Silva", "account_ref": "ACC018", "benchmark_name": "EURIBOR 3-Month Fixing",
     "fixing_window_volume": 28720000, "total_daily_volume": 35900000,
     "fixing_price_deviation_pct": 0.832, "normal_deviation_pct": 0.16,
     "seconds_before_fixing_close": 10, "repeat_occurrences": 2, "issuer_name": "Zeta Commodities Ltd"},
    {"trader_name": "Sergei Ivanov", "account_ref": "ACC019", "benchmark_name": "ICE LIBOR-style USD Reference Rate Fixing",
     "fixing_window_volume": 22525000, "total_daily_volume": 26500000,
     "fixing_price_deviation_pct": 1.440, "normal_deviation_pct": 0.18,
     "seconds_before_fixing_close": 2, "repeat_occurrences": 8, "issuer_name": "Gamma Imports Ltd"},
    {"trader_name": "Ana Ferreira", "account_ref": "ACC020", "benchmark_name": "WM/Reuters 4pm London Fix (GBP/USD)",
     "fixing_window_volume": 35856000, "total_daily_volume": 49800000,
     "fixing_price_deviation_pct": 0.990, "normal_deviation_pct": 0.22,
     "seconds_before_fixing_close": 3, "repeat_occurrences": 4, "issuer_name": "Continental Correspondent Bank"},
    {"trader_name": "Tobias Richter", "account_ref": "ACC021", "benchmark_name": "LBMA Gold Price PM Fixing",
     "fixing_window_volume": 17820000, "total_daily_volume": 32400000,
     "fixing_price_deviation_pct": 1.170, "normal_deviation_pct": 0.15,
     "seconds_before_fixing_close": 1, "repeat_occurrences": 7, "issuer_name": "Ravenwood Trading Co"},
    {"trader_name": "Naledi Dube", "account_ref": "ACC022", "benchmark_name": "ICE Brent Crude Settlement Fixing",
     "fixing_window_volume": 32648000, "total_daily_volume": 37100000,
     "fixing_price_deviation_pct": 1.060, "normal_deviation_pct": 0.20,
     "seconds_before_fixing_close": 5, "repeat_occurrences": 6, "issuer_name": "Falcon Ridge Commodities Ltd"},
]

# benchmark_name, account_ref, administrator, jurisdiction, prior_alerts
_ADMIN = {
    "SONIA 3-Month Fixing": ("Bank of England", "United Kingdom"),
    "EURIBOR 3-Month Fixing": ("European Money Markets Institute (EMMI)", "Belgium"),
    "WM/Reuters 4pm London Fix (GBP/USD)": ("Refinitiv Benchmark Services (UK) Limited", "United Kingdom"),
    "WM/Reuters 4pm London Fix (EUR/USD)": ("Refinitiv Benchmark Services (UK) Limited", "United Kingdom"),
    "LBMA Gold Price PM Fixing": ("ICE Benchmark Administration", "United Kingdom"),
    "ICE Brent Crude Settlement Fixing": ("ICE Benchmark Administration", "United Kingdom"),
    "SOFR Overnight Fixing": ("Federal Reserve Bank of New York", "United States"),
    "Platts Dated Brent Assessment": ("S&P Global Platts", "United Kingdom"),
    "LME Copper Official Settlement": ("London Metal Exchange", "United Kingdom"),
    "ICE LIBOR-style USD Reference Rate Fixing": ("ICE Benchmark Administration", "United Kingdom"),
}

_PRIOR_ALERTS = {
    "ACC001": 0, "ACC002": 0, "ACC003": 0, "ACC004": 0, "ACC005": 0, "ACC006": 0,
    "ACC007": 1, "ACC008": 1, "ACC009": 1, "ACC010": 1, "ACC011": 1, "ACC012": 1,
    "ACC013": 2, "ACC014": 2, "ACC015": 2, "ACC016": 2, "ACC017": 2, "ACC018": 2,
    "ACC019": 3, "ACC020": 3, "ACC021": 3, "ACC022": 3,
}

BENCHMARKS: List[Dict[str, Any]] = []
for _acc in ACCOUNTS:
    _administrator, _jurisdiction = _ADMIN[_acc["benchmark_name"]]
    BENCHMARKS.append({
        "benchmark_name": _acc["benchmark_name"], "account_ref": _acc["account_ref"],
        "administrator": _administrator, "jurisdiction": _jurisdiction,
        "prior_alerts": _PRIOR_ALERTS[_acc["account_ref"]],
    })

_TABLES = {"fixing_orders.csv": ACCOUNTS, "benchmarks.csv": BENCHMARKS}


def generate(data_dir: Path = DATA_DIR) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in _TABLES.items():
        with (data_dir / name).open("w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print("wrote %s (%d rows)" % (name, len(rows)))


if __name__ == "__main__":
    generate()
