"""Generate synthetic sample data for CM003 Spoofing.

22 trading accounts (>= the 20-row sample-data standard; CM003 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Viktor Sokolov, 90/Critical, the single highest-scoring account
in the set) spoofs the order book in Zeta Commodities Ltd Ordinary Shares -- placing
orders with no intention to execute, cancelling them in under a second, manufacturing
one-sided depth, and executing genuine opposite-side trades while the spoof orders are
working -- routed through **Zeta Commodities Ltd** as the account's broker, an entity
already in the estate network, so canonical entity resolution joins CM003 onto the
existing fused case. Being the top-scored account matters: the FC-10 adapter builds its
case/graph from the single highest exposure_score row, so the Zeta Commodities Ltd
bridge has to be that row, not merely A Critical row.

Run:  python3 generate_cm003_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, instrument, total_order_value, spoof_order_value,
# avg_cancel_seconds, spoof_side_depth, genuine_side_depth, opposite_side_filled_value,
# broker_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"trader_name": "Nadia Petrova", "account_ref": "ACC001", "instrument": "S&P 500 E-mini Futures",
     "total_order_value": 1250000, "spoof_order_value": 85000, "avg_cancel_seconds": 21.0,
     "spoof_side_depth": 4200, "genuine_side_depth": 85162, "opposite_side_filled_value": 7060,
     "broker_name": "Gamma Imports Ltd"},
    {"trader_name": "Julius Ferreira", "account_ref": "ACC002", "instrument": "10-Year US Treasury Futures",
     "total_order_value": 980000, "spoof_order_value": 72500, "avg_cancel_seconds": 47.1,
     "spoof_side_depth": 3600, "genuine_side_depth": 39257, "opposite_side_filled_value": 21390,
     "broker_name": "Alpha Trading Ltd"},
    {"trader_name": "Meera Krishnan", "account_ref": "ACC003", "instrument": "EUR/USD Spot FX",
     "total_order_value": 1620000, "spoof_order_value": 89100, "avg_cancel_seconds": 21.2,
     "spoof_side_depth": 5100, "genuine_side_depth": 27803, "opposite_side_filled_value": 11230,
     "broker_name": "Continental Correspondent Bank"},
    {"trader_name": "Oskar Lindqvist", "account_ref": "ACC004", "instrument": "Brent Crude Oil Futures",
     "total_order_value": 2100000, "spoof_order_value": 67200, "avg_cancel_seconds": 7.8,
     "spoof_side_depth": 6200, "genuine_side_depth": 83655, "opposite_side_filled_value": 8870,
     "broker_name": "Ravenwood Trading Co"},
    {"trader_name": "Chidi Okonkwo", "account_ref": "ACC005", "instrument": "Gold Futures (COMEX)",
     "total_order_value": 1430000, "spoof_order_value": 221600, "avg_cancel_seconds": 43.6,
     "spoof_side_depth": 4800, "genuine_side_depth": 55959, "opposite_side_filled_value": 11300,
     "broker_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Ingrid Halvorsen", "account_ref": "ACC006", "instrument": "FTSE 100 Index Futures",
     "total_order_value": 875000, "spoof_order_value": 68200, "avg_cancel_seconds": 47.9,
     "spoof_side_depth": 3900, "genuine_side_depth": 18514, "opposite_side_filled_value": 20870,
     "broker_name": "Highgate Commodities Ltd"},
    {"trader_name": "Tomasz Wojcik", "account_ref": "ACC007", "instrument": "Natural Gas Futures",
     "total_order_value": 1980000, "spoof_order_value": 540500, "avg_cancel_seconds": 9.0,
     "spoof_side_depth": 5600, "genuine_side_depth": 149956, "opposite_side_filled_value": 35130,
     "broker_name": "Northwind Freight Co"},
    {"trader_name": "Amara Diallo", "account_ref": "ACC008", "instrument": "Copper Futures (LME)",
     "total_order_value": 2450000, "spoof_order_value": 627200, "avg_cancel_seconds": 11.4,
     "spoof_side_depth": 7100, "genuine_side_depth": 21414, "opposite_side_filled_value": 99720,
     "broker_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Felix Brandt", "account_ref": "ACC009", "instrument": "Corn Futures (CBOT)",
     "total_order_value": 1340000, "spoof_order_value": 276000, "avg_cancel_seconds": 14.8,
     "spoof_side_depth": 4400, "genuine_side_depth": 19909, "opposite_side_filled_value": 103220,
     "broker_name": "Gamma Imports Ltd"},
    {"trader_name": "Yuki Tanaka", "account_ref": "ACC010", "instrument": "Bund Futures (Eurex)",
     "total_order_value": 3100000, "spoof_order_value": 784300, "avg_cancel_seconds": 11.6,
     "spoof_side_depth": 8300, "genuine_side_depth": 6957, "opposite_side_filled_value": 107450,
     "broker_name": "Alpha Trading Ltd"},
    {"trader_name": "Ruben Castellano", "account_ref": "ACC011", "instrument": "Alpha Trading Ltd Ordinary Shares",
     "total_order_value": 1760000, "spoof_order_value": 885300, "avg_cancel_seconds": 21.8,
     "spoof_side_depth": 5900, "genuine_side_depth": 31921, "opposite_side_filled_value": 291260,
     "broker_name": "Continental Correspondent Bank"},
    {"trader_name": "Freya Solheim", "account_ref": "ACC012", "instrument": "Nikkei 225 Futures",
     "total_order_value": 2280000, "spoof_order_value": 303200, "avg_cancel_seconds": 3.5,
     "spoof_side_depth": 6700, "genuine_side_depth": 42565, "opposite_side_filled_value": 27890,
     "broker_name": "Ravenwood Trading Co"},
    {"trader_name": "Dmitri Volkov", "account_ref": "ACC013", "instrument": "Silver Futures (COMEX)",
     "total_order_value": 1590000, "spoof_order_value": 1319700, "avg_cancel_seconds": 0.7,
     "spoof_side_depth": 5300, "genuine_side_depth": 96623, "opposite_side_filled_value": 106900,
     "broker_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Aisha Rahman", "account_ref": "ACC014", "instrument": "WTI Crude Oil Futures",
     "total_order_value": 2950000, "spoof_order_value": 2088600, "avg_cancel_seconds": 4.9,
     "spoof_side_depth": 8900, "genuine_side_depth": 30832, "opposite_side_filled_value": 294490,
     "broker_name": "Highgate Commodities Ltd"},
    {"trader_name": "Callum Fitzgerald", "account_ref": "ACC015", "instrument": "DAX Index Futures",
     "total_order_value": 1120000, "spoof_order_value": 407700, "avg_cancel_seconds": 4.5,
     "spoof_side_depth": 4100, "genuine_side_depth": 7226, "opposite_side_filled_value": 140660,
     "broker_name": "Northwind Freight Co"},
    {"trader_name": "Elif Demir", "account_ref": "ACC016", "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares",
     "total_order_value": 2670000, "spoof_order_value": 2528500, "avg_cancel_seconds": 1.3,
     "spoof_side_depth": 7800, "genuine_side_depth": 29521, "opposite_side_filled_value": 386860,
     "broker_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Santiago Rivas", "account_ref": "ACC017", "instrument": "Soybean Futures (CBOT)",
     "total_order_value": 3350000, "spoof_order_value": 1805600, "avg_cancel_seconds": 4.6,
     "spoof_side_depth": 9600, "genuine_side_depth": 4435, "opposite_side_filled_value": 514600,
     "broker_name": "Gamma Imports Ltd"},
    {"trader_name": "Noor Al-Sayed", "account_ref": "ACC018", "instrument": "GBP/USD Spot FX",
     "total_order_value": 1890000, "spoof_order_value": 1368400, "avg_cancel_seconds": 3.5,
     "spoof_side_depth": 5700, "genuine_side_depth": 9500, "opposite_side_filled_value": 602100,
     "broker_name": "Alpha Trading Ltd"},
    {"trader_name": "Viktor Sokolov", "account_ref": "ACC019", "instrument": "Zeta Commodities Ltd Ordinary Shares",
     "total_order_value": 2400000, "spoof_order_value": 2181600, "avg_cancel_seconds": 0.6,
     "spoof_side_depth": 7200, "genuine_side_depth": 1755, "opposite_side_filled_value": 1917630,
     "broker_name": "Zeta Commodities Ltd"},
    {"trader_name": "Beatriz Menendez", "account_ref": "ACC020", "instrument": "Wheat Futures (CBOT)",
     "total_order_value": 2820000, "spoof_order_value": 2600000, "avg_cancel_seconds": 3.9,
     "spoof_side_depth": 8600, "genuine_side_depth": 3792, "opposite_side_filled_value": 1557400,
     "broker_name": "Continental Correspondent Bank"},
    {"trader_name": "Kwame Asante", "account_ref": "ACC021", "instrument": "Highgate Commodities Ltd Ordinary Shares",
     "total_order_value": 1975000, "spoof_order_value": 920400, "avg_cancel_seconds": 0.5,
     "spoof_side_depth": 6100, "genuine_side_depth": 1681, "opposite_side_filled_value": 878980,
     "broker_name": "Ravenwood Trading Co"},
    {"trader_name": "Lena Kowalski", "account_ref": "ACC022", "instrument": "Nasdaq 100 E-mini Futures",
     "total_order_value": 3480000, "spoof_order_value": 2617000, "avg_cancel_seconds": 3.4,
     "spoof_side_depth": 9900, "genuine_side_depth": 1112, "opposite_side_filled_value": 2344830,
     "broker_name": "Falcon Ridge Commodities Ltd"},
]

# broker_name, account_ref, venue, jurisdiction, relationship, prior_alerts
BROKERS: List[Dict[str, Any]] = [
    {"broker_name": "Gamma Imports Ltd", "account_ref": "ACC001", "venue": "CME Globex",
     "jurisdiction": "United States", "relationship": "Executing Broker", "prior_alerts": 0},
    {"broker_name": "Alpha Trading Ltd", "account_ref": "ACC002", "venue": "ICE Futures Europe",
     "jurisdiction": "United Kingdom", "relationship": "Prime Broker", "prior_alerts": 0},
    {"broker_name": "Continental Correspondent Bank", "account_ref": "ACC003", "venue": "EBS Market",
     "jurisdiction": "Switzerland", "relationship": "Direct Market Access", "prior_alerts": 0},
    {"broker_name": "Ravenwood Trading Co", "account_ref": "ACC004", "venue": "ICE Futures Europe",
     "jurisdiction": "United Kingdom", "relationship": "Introducing Broker", "prior_alerts": 0},
    {"broker_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC005", "venue": "CME Globex",
     "jurisdiction": "United States", "relationship": "Executing Broker", "prior_alerts": 0},
    {"broker_name": "Highgate Commodities Ltd", "account_ref": "ACC006", "venue": "ICE Futures Europe",
     "jurisdiction": "United Kingdom", "relationship": "Prime Broker", "prior_alerts": 0},
    {"broker_name": "Northwind Freight Co", "account_ref": "ACC007", "venue": "CME Globex",
     "jurisdiction": "United States", "relationship": "Direct Market Access", "prior_alerts": 1},
    {"broker_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC008", "venue": "London Metal Exchange",
     "jurisdiction": "United Kingdom", "relationship": "Executing Broker", "prior_alerts": 1},
    {"broker_name": "Gamma Imports Ltd", "account_ref": "ACC009", "venue": "CME Globex",
     "jurisdiction": "United States", "relationship": "Prime Broker", "prior_alerts": 1},
    {"broker_name": "Alpha Trading Ltd", "account_ref": "ACC010", "venue": "Eurex",
     "jurisdiction": "Germany", "relationship": "Introducing Broker", "prior_alerts": 1},
    {"broker_name": "Continental Correspondent Bank", "account_ref": "ACC011", "venue": "London Stock Exchange",
     "jurisdiction": "United Kingdom", "relationship": "Executing Broker", "prior_alerts": 1},
    {"broker_name": "Ravenwood Trading Co", "account_ref": "ACC012", "venue": "Osaka Exchange",
     "jurisdiction": "Japan", "relationship": "Direct Market Access", "prior_alerts": 1},
    {"broker_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC013", "venue": "CME Globex",
     "jurisdiction": "United States", "relationship": "Prime Broker", "prior_alerts": 1},
    {"broker_name": "Highgate Commodities Ltd", "account_ref": "ACC014", "venue": "NYMEX",
     "jurisdiction": "United States", "relationship": "Executing Broker", "prior_alerts": 2},
    {"broker_name": "Northwind Freight Co", "account_ref": "ACC015", "venue": "Eurex",
     "jurisdiction": "Germany", "relationship": "Direct Market Access", "prior_alerts": 1},
    {"broker_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC016", "venue": "Johannesburg Stock Exchange",
     "jurisdiction": "South Africa", "relationship": "Introducing Broker", "prior_alerts": 2},
    {"broker_name": "Gamma Imports Ltd", "account_ref": "ACC017", "venue": "CME Globex",
     "jurisdiction": "United States", "relationship": "Prime Broker", "prior_alerts": 2},
    {"broker_name": "Alpha Trading Ltd", "account_ref": "ACC018", "venue": "EBS Market",
     "jurisdiction": "Switzerland", "relationship": "Executing Broker", "prior_alerts": 2},
    {"broker_name": "Zeta Commodities Ltd", "account_ref": "ACC019", "venue": "London Stock Exchange",
     "jurisdiction": "Cyprus", "relationship": "Prime Broker", "prior_alerts": 3},
    {"broker_name": "Continental Correspondent Bank", "account_ref": "ACC020", "venue": "CME Globex",
     "jurisdiction": "United States", "relationship": "Direct Market Access", "prior_alerts": 2},
    {"broker_name": "Ravenwood Trading Co", "account_ref": "ACC021", "venue": "Johannesburg Stock Exchange",
     "jurisdiction": "South Africa", "relationship": "Introducing Broker", "prior_alerts": 2},
    {"broker_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC022", "venue": "CME Globex",
     "jurisdiction": "United States", "relationship": "Executing Broker", "prior_alerts": 3},
]

_TABLES = {"orders.csv": ACCOUNTS, "brokers.csv": BROKERS}


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
