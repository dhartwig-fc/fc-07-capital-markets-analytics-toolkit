"""Generate synthetic sample data for CM010 Suspicious Order Patterns.

22 trading accounts (>= the 20-row sample-data standard; CM010 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Dominic Heronbutton, 90/Critical, the single highest-scoring account
in the set) shows a suspicious order-flow burst on Alpha Trading Ltd Ordinary Shares --
an extreme cancel/amend rate, a quote-stuffing-intensity order-submission burst,
momentum ignition well beyond the instrument's normal move, and an order-size anomaly
far beyond the account's normal size -- routed through **Alpha Trading Ltd** as venue
operator, an entity already in the estate network, so canonical entity resolution
joins CM010 onto the existing fused case. Being the top-scored account matters: the
FC-10 adapter builds its case/graph from the single highest exposure_score row, so the
Alpha Trading Ltd bridge has to be that row, not merely A Critical row.

Run:  python3 generate_cm010_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, instrument, cancelled_orders, total_orders,
# orders_per_second, price_move_after_burst_pct, normal_move_pct, avg_order_size,
# normal_order_size, venue_operator_name
ORDER_FLOW: List[Dict[str, Any]] = [
    {"trader_name": "Freya Ashbutton", "account_ref": "ACC001", "instrument": "Vantage Semiconductors Ordinary Shares",
     "cancelled_orders": 48, "total_orders": 1200, "orders_per_second": 2,
     "price_move_after_burst_pct": 0.36, "normal_move_pct": 0.40, "avg_order_size": 1100, "normal_order_size": 1000,
     "venue_operator_name": "Continental Correspondent Bank"},
    {"trader_name": "Matteo Marrowfiddle", "account_ref": "ACC002", "instrument": "FTSE 100 Index Futures",
     "cancelled_orders": 70, "total_orders": 1400, "orders_per_second": 3,
     "price_move_after_burst_pct": 0.35, "normal_move_pct": 0.35, "avg_order_size": 1260, "normal_order_size": 900,
     "venue_operator_name": "Northwind Freight Co"},
    {"trader_name": "Aisling Marrowspindle", "account_ref": "ACC003", "instrument": "Brent Crude Oil Futures",
     "cancelled_orders": 90, "total_orders": 1500, "orders_per_second": 4,
     "price_move_after_burst_pct": 0.54, "normal_move_pct": 0.30, "avg_order_size": 1265, "normal_order_size": 1100,
     "venue_operator_name": "Ravenwood Trading Co"},
    {"trader_name": "Dmitri Brackencrumb", "account_ref": "ACC004", "instrument": "EUR/USD Spot FX",
     "cancelled_orders": 91, "total_orders": 1300, "orders_per_second": 9,
     "price_move_after_burst_pct": 0.44, "normal_move_pct": 0.40, "avg_order_size": 1260, "normal_order_size": 1200,
     "venue_operator_name": "Highgate Commodities Ltd"},
    {"trader_name": "Sana Ashthimble", "account_ref": "ACC005", "instrument": "Meridian Bulk Traders Ltd Ordinary Shares",
     "cancelled_orders": 240, "total_orders": 1600, "orders_per_second": 5,
     "price_move_after_burst_pct": 0.60, "normal_move_pct": 0.50, "avg_order_size": 960, "normal_order_size": 800,
     "venue_operator_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Callum Flintmote", "account_ref": "ACC006", "instrument": "S&P 500 E-mini Futures",
     "cancelled_orders": 100, "total_orders": 1250, "orders_per_second": 1,
     "price_move_after_burst_pct": 0.70, "normal_move_pct": 0.35, "avg_order_size": 1500, "normal_order_size": 1000,
     "venue_operator_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Isabela Puddlebutton", "account_ref": "ACC007", "instrument": "Highgate Commodities Ltd Ordinary Shares",
     "cancelled_orders": 252, "total_orders": 1800, "orders_per_second": 11,
     "price_move_after_burst_pct": 0.34, "normal_move_pct": 0.40, "avg_order_size": 1404, "normal_order_size": 1300,
     "venue_operator_name": "Zeta Commodities Ltd"},
    {"trader_name": "Rurik Mosstumble", "account_ref": "ACC008", "instrument": "10-Year Gilt Futures",
     "cancelled_orders": 360, "total_orders": 2000, "orders_per_second": 8,
     "price_move_after_burst_pct": 0.66, "normal_move_pct": 0.30, "avg_order_size": 1062, "normal_order_size": 900,
     "venue_operator_name": "Gammavane Imports Ltd"},
    {"trader_name": "Naledi Thistlewisp", "account_ref": "ACC009", "instrument": "Northwind Freight Co Ordinary Shares",
     "cancelled_orders": 418, "total_orders": 1900, "orders_per_second": 13,
     "price_move_after_burst_pct": 1.00, "normal_move_pct": 0.40, "avg_order_size": 1600, "normal_order_size": 1000,
     "venue_operator_name": "Continental Correspondent Bank"},
    {"trader_name": "Yusuf Ivycrumb", "account_ref": "ACC010", "instrument": "Gold Spot (XAU/USD)",
     "cancelled_orders": 525, "total_orders": 2100, "orders_per_second": 10,
     "price_move_after_burst_pct": 1.05, "normal_move_pct": 0.30, "avg_order_size": 1232, "normal_order_size": 1100,
     "venue_operator_name": "Northwind Freight Co"},
    {"trader_name": "Ingrid Duskbristle", "account_ref": "ACC011", "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares",
     "cancelled_orders": 770, "total_orders": 2200, "orders_per_second": 3,
     "price_move_after_burst_pct": 0.86, "normal_move_pct": 0.45, "avg_order_size": 1233, "normal_order_size": 850,
     "venue_operator_name": "Ravenwood Trading Co"},
    {"trader_name": "Javier Parsleykettle", "account_ref": "ACC012", "instrument": "DAX 40 Index Futures",
     "cancelled_orders": 400, "total_orders": 2000, "orders_per_second": 22,
     "price_move_after_burst_pct": 0.81, "normal_move_pct": 0.35, "avg_order_size": 1159, "normal_order_size": 950,
     "venue_operator_name": "Highgate Commodities Ltd"},
    {"trader_name": "Petra Parsleythimble", "account_ref": "ACC013", "instrument": "Ravenwood Trading Co Ordinary Shares",
     "cancelled_orders": 1560, "total_orders": 2400, "orders_per_second": 50,
     "price_move_after_burst_pct": 0.50, "normal_move_pct": 0.50, "avg_order_size": 1284, "normal_order_size": 1200,
     "venue_operator_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Kwame Nettlethimble", "account_ref": "ACC014", "instrument": "USD/JPY Spot FX",
     "cancelled_orders": 1750, "total_orders": 2500, "orders_per_second": 28,
     "price_move_after_burst_pct": 0.84, "normal_move_pct": 0.40, "avg_order_size": 1000, "normal_order_size": 800,
     "venue_operator_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Lena Gorsebutton", "account_ref": "ACC015", "instrument": "Zeta Commodities Ltd Ordinary Shares",
     "cancelled_orders": 1040, "total_orders": 2600, "orders_per_second": 20,
     "price_move_after_burst_pct": 1.20, "normal_move_pct": 0.30, "avg_order_size": 1485, "normal_order_size": 900,
     "venue_operator_name": "Zeta Commodities Ltd"},
    {"trader_name": "Arjun Hazeltumble", "account_ref": "ACC016", "instrument": "Natural Gas Futures",
     "cancelled_orders": 2100, "total_orders": 2800, "orders_per_second": 60,
     "price_move_after_burst_pct": 0.77, "normal_move_pct": 0.45, "avg_order_size": 1526, "normal_order_size": 1400,
     "venue_operator_name": "Gammavane Imports Ltd"},
    {"trader_name": "Chloe Gorsebristle", "account_ref": "ACC017", "instrument": "Continental Correspondent Bank Ordinary Shares",
     "cancelled_orders": 1215, "total_orders": 2700, "orders_per_second": 35,
     "price_move_after_burst_pct": 2.10, "normal_move_pct": 0.30, "avg_order_size": 1550, "normal_order_size": 1000,
     "venue_operator_name": "Continental Correspondent Bank"},
    {"trader_name": "Farid Copperbristle", "account_ref": "ACC018", "instrument": "Nikkei 225 Index Futures",
     "cancelled_orders": 2400, "total_orders": 3000, "orders_per_second": 30,
     "price_move_after_burst_pct": 1.75, "normal_move_pct": 0.35, "avg_order_size": 1445, "normal_order_size": 850,
     "venue_operator_name": "Northwind Freight Co"},
    {"trader_name": "Dominic Heronbutton", "account_ref": "ACC019", "instrument": "Alpha Trading Ltd Ordinary Shares",
     "cancelled_orders": 2720, "total_orders": 3200, "orders_per_second": 70,
     "price_move_after_burst_pct": 2.40, "normal_move_pct": 0.30, "avg_order_size": 4000, "normal_order_size": 1000,
     "venue_operator_name": "Alpha Trading Ltd"},
    {"trader_name": "Simone Hazelspindle", "account_ref": "ACC020", "instrument": "Copper Futures",
     "cancelled_orders": 3150, "total_orders": 3500, "orders_per_second": 25,
     "price_move_after_burst_pct": 3.00, "normal_move_pct": 0.40, "avg_order_size": 1980, "normal_order_size": 900,
     "venue_operator_name": "Ravenwood Trading Co"},
    {"trader_name": "Tariq Willowcrumb", "account_ref": "ACC021", "instrument": "Gammavane Imports Ltd Ordinary Shares",
     "cancelled_orders": 1450, "total_orders": 2900, "orders_per_second": 55,
     "price_move_after_burst_pct": 2.38, "normal_move_pct": 0.35, "avg_order_size": 3500, "normal_order_size": 1000,
     "venue_operator_name": "Highgate Commodities Ltd"},
    {"trader_name": "Noor Flintspindle", "account_ref": "ACC022", "instrument": "GBP/USD Spot FX",
     "cancelled_orders": 2108, "total_orders": 3100, "orders_per_second": 32,
     "price_move_after_burst_pct": 2.70, "normal_move_pct": 0.30, "avg_order_size": 3600, "normal_order_size": 800,
     "venue_operator_name": "Meridian Bulk Traders Ltd"},
]

# venue_operator_name, account_ref, jurisdiction, relationship, prior_alerts
VENUES: List[Dict[str, Any]] = [
    {"venue_operator_name": "Continental Correspondent Bank", "account_ref": "ACC001", "jurisdiction": "Sweden",
     "relationship": "Regulated Market Operator", "prior_alerts": 0},
    {"venue_operator_name": "Northwind Freight Co", "account_ref": "ACC002", "jurisdiction": "Germany",
     "relationship": "MTF Operator", "prior_alerts": 0},
    {"venue_operator_name": "Ravenwood Trading Co", "account_ref": "ACC003", "jurisdiction": "United Kingdom",
     "relationship": "MTF Operator", "prior_alerts": 0},
    {"venue_operator_name": "Highgate Commodities Ltd", "account_ref": "ACC004", "jurisdiction": "Cyprus",
     "relationship": "Systematic Internaliser", "prior_alerts": 0},
    {"venue_operator_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC005", "jurisdiction": "Singapore",
     "relationship": "Dark Pool Operator", "prior_alerts": 0},
    {"venue_operator_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC006", "jurisdiction": "Hong Kong",
     "relationship": "OTF Operator", "prior_alerts": 0},
    {"venue_operator_name": "Zeta Commodities Ltd", "account_ref": "ACC007", "jurisdiction": "Cyprus",
     "relationship": "MTF Operator", "prior_alerts": 1},
    {"venue_operator_name": "Gammavane Imports Ltd", "account_ref": "ACC008", "jurisdiction": "Marshall Islands",
     "relationship": "Systematic Internaliser", "prior_alerts": 1},
    {"venue_operator_name": "Continental Correspondent Bank", "account_ref": "ACC009", "jurisdiction": "Sweden",
     "relationship": "Regulated Market Operator", "prior_alerts": 1},
    {"venue_operator_name": "Northwind Freight Co", "account_ref": "ACC010", "jurisdiction": "Germany",
     "relationship": "MTF Operator", "prior_alerts": 1},
    {"venue_operator_name": "Ravenwood Trading Co", "account_ref": "ACC011", "jurisdiction": "United Kingdom",
     "relationship": "MTF Operator", "prior_alerts": 1},
    {"venue_operator_name": "Highgate Commodities Ltd", "account_ref": "ACC012", "jurisdiction": "Cyprus",
     "relationship": "Systematic Internaliser", "prior_alerts": 1},
    {"venue_operator_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC013", "jurisdiction": "Singapore",
     "relationship": "Dark Pool Operator", "prior_alerts": 2},
    {"venue_operator_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC014", "jurisdiction": "Hong Kong",
     "relationship": "OTF Operator", "prior_alerts": 2},
    {"venue_operator_name": "Zeta Commodities Ltd", "account_ref": "ACC015", "jurisdiction": "Cyprus",
     "relationship": "MTF Operator", "prior_alerts": 2},
    {"venue_operator_name": "Gammavane Imports Ltd", "account_ref": "ACC016", "jurisdiction": "Marshall Islands",
     "relationship": "Systematic Internaliser", "prior_alerts": 2},
    {"venue_operator_name": "Continental Correspondent Bank", "account_ref": "ACC017", "jurisdiction": "Sweden",
     "relationship": "Regulated Market Operator", "prior_alerts": 2},
    {"venue_operator_name": "Northwind Freight Co", "account_ref": "ACC018", "jurisdiction": "Germany",
     "relationship": "MTF Operator", "prior_alerts": 3},
    {"venue_operator_name": "Alpha Trading Ltd", "account_ref": "ACC019", "jurisdiction": "Cayman Islands",
     "relationship": "MTF Operator", "prior_alerts": 3},
    {"venue_operator_name": "Ravenwood Trading Co", "account_ref": "ACC020", "jurisdiction": "United Kingdom",
     "relationship": "MTF Operator", "prior_alerts": 3},
    {"venue_operator_name": "Highgate Commodities Ltd", "account_ref": "ACC021", "jurisdiction": "Cyprus",
     "relationship": "Systematic Internaliser", "prior_alerts": 3},
    {"venue_operator_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC022", "jurisdiction": "Singapore",
     "relationship": "Dark Pool Operator", "prior_alerts": 3},
]

_TABLES = {"order_flow.csv": ORDER_FLOW, "venues.csv": VENUES}


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
