"""Generate synthetic sample data for CM004 Layering.

22 trading accounts (>= the 20-row sample-data standard; CM004 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Renata Quillmote, 90/Critical, the single highest-scoring account in
the set) stagers a book of orders across ten distinct price levels, at a 60:1 order-to-
trade ratio, creating a 0.75 book imbalance, and reversing (pulling) the staggered
orders in 3 seconds once the book has moved -- on venue **Gammavane Imports Ltd** -- an
entity already in the estate network -- so canonical entity resolution joins CM004 onto
the existing fused case. Being the top-scored account matters: the FC-10 adapter builds
its case/graph from the single highest exposure_score row, so the Gammavane Imports Ltd
bridge has to be that row, not merely A Critical row.

Run:  python3 generate_cm004_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, instrument, distinct_price_levels, orders_placed,
# orders_executed, imbalance_ratio, seconds_to_reversal, venue_operator_name
ORDERS: List[Dict[str, Any]] = [
    {"trader_name": "Marta Rushquilla", "account_ref": "ACC001",
     "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares",
     "distinct_price_levels": 1, "orders_placed": 28, "orders_executed": 14,
     "imbalance_ratio": 0.03, "seconds_to_reversal": 180, "venue_operator_name": "Northwind Freight Co"},
    {"trader_name": "Diego Hazelkettle", "account_ref": "ACC002",
     "instrument": "Highgate Commodities Ltd Ordinary Shares",
     "distinct_price_levels": 2, "orders_placed": 33, "orders_executed": 11,
     "imbalance_ratio": 0.05, "seconds_to_reversal": 45, "venue_operator_name": "Highgate Commodities Ltd"},
    {"trader_name": "Anneke van der Berg", "account_ref": "ACC003",
     "instrument": "Meridian Bulk Traders Ltd Front-Month Future",
     "distinct_price_levels": 1, "orders_placed": 40, "orders_executed": 16,
     "imbalance_ratio": 0.15, "seconds_to_reversal": 150, "venue_operator_name": "Continental Correspondent Bank"},
    {"trader_name": "Samuel Kettlewhistle", "account_ref": "ACC004",
     "instrument": "Northwind Freight Co Ordinary Shares",
     "distinct_price_levels": 2, "orders_placed": 72, "orders_executed": 9,
     "imbalance_ratio": 0.04, "seconds_to_reversal": 120, "venue_operator_name": "Ravenwood Trading Co"},
    {"trader_name": "Ines Mosstumblea", "account_ref": "ACC005",
     "instrument": "Ravenwood Trading Co Ordinary Shares",
     "distinct_price_levels": 3, "orders_placed": 39, "orders_executed": 13,
     "imbalance_ratio": 0.06, "seconds_to_reversal": 100, "venue_operator_name": "Alpha Trading Ltd"},
    {"trader_name": "Callum Hazelfiddle", "account_ref": "ACC006",
     "instrument": "Alpha Trading Ltd Ordinary Shares",
     "distinct_price_levels": 1, "orders_placed": 38, "orders_executed": 19,
     "imbalance_ratio": 0.20, "seconds_to_reversal": 40, "venue_operator_name": "Zeta Commodities Ltd"},
    {"trader_name": "Yuki Brindlekettle", "account_ref": "ACC007",
     "instrument": "Zeta Commodities Ltd Front-Month Future",
     "distinct_price_levels": 4, "orders_placed": 70, "orders_executed": 7,
     "imbalance_ratio": 0.08, "seconds_to_reversal": 90, "venue_operator_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Fatima Umberwisp", "account_ref": "ACC008",
     "instrument": "Falcon Ridge Commodities Ltd 4.25% 2028 Bond",
     "distinct_price_levels": 3, "orders_placed": 72, "orders_executed": 6,
     "imbalance_ratio": 0.18, "seconds_to_reversal": 110, "venue_operator_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Piotr Copperfiddle", "account_ref": "ACC009",
     "instrument": "Highgate Commodities Ltd Front-Month Future",
     "distinct_price_levels": 4, "orders_placed": 99, "orders_executed": 11,
     "imbalance_ratio": 0.22, "seconds_to_reversal": 35, "venue_operator_name": "Northwind Freight Co"},
    {"trader_name": "Isabela Sorrelcrumb", "account_ref": "ACC010",
     "instrument": "Meridian Bulk Traders Ltd Ordinary Shares",
     "distinct_price_levels": 3, "orders_placed": 105, "orders_executed": 15,
     "imbalance_ratio": 0.40, "seconds_to_reversal": 95, "venue_operator_name": "Highgate Commodities Ltd"},
    {"trader_name": "Magnus Yarrowkettle", "account_ref": "ACC011",
     "instrument": "Northwind Freight Co Front-Month Future",
     "distinct_price_levels": 6, "orders_placed": 66, "orders_executed": 22,
     "imbalance_ratio": 0.25, "seconds_to_reversal": 50, "venue_operator_name": "Ravenwood Trading Co"},
    {"trader_name": "Chidi Gossamerwhistle", "account_ref": "ACC012",
     "instrument": "Ravenwood Trading Co Ordinary Shares",
     "distinct_price_levels": 4, "orders_placed": 160, "orders_executed": 8,
     "imbalance_ratio": 0.24, "seconds_to_reversal": 140, "venue_operator_name": "Alpha Trading Ltd"},
    {"trader_name": "Naomi Kettlemote", "account_ref": "ACC013",
     "instrument": "Alpha Trading Ltd Front-Month Future",
     "distinct_price_levels": 9, "orders_placed": 350, "orders_executed": 7,
     "imbalance_ratio": 0.07, "seconds_to_reversal": 130, "venue_operator_name": "Zeta Commodities Ltd"},
    {"trader_name": "Lars Wrencrumb", "account_ref": "ACC014",
     "instrument": "Zeta Commodities Ltd Ordinary Shares",
     "distinct_price_levels": 10, "orders_placed": 225, "orders_executed": 9,
     "imbalance_ratio": 0.26, "seconds_to_reversal": 160, "venue_operator_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Katarina Parsleythimble", "account_ref": "ACC015",
     "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares",
     "distinct_price_levels": 6, "orders_placed": 220, "orders_executed": 10,
     "imbalance_ratio": 0.45, "seconds_to_reversal": 30, "venue_operator_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Ahmed Mossbristle", "account_ref": "ACC016",
     "instrument": "Highgate Commodities Ltd 3.75% 2027 Bond",
     "distinct_price_levels": 11, "orders_placed": 440, "orders_executed": 8,
     "imbalance_ratio": 0.14, "seconds_to_reversal": 170, "venue_operator_name": "Northwind Freight Co"},
    {"trader_name": "Sophie Puddlekettle", "account_ref": "ACC017",
     "instrument": "Meridian Bulk Traders Ltd Front-Month Future",
     "distinct_price_levels": 5, "orders_placed": 216, "orders_executed": 12,
     "imbalance_ratio": 0.70, "seconds_to_reversal": 28, "venue_operator_name": "Continental Correspondent Bank"},
    {"trader_name": "Tobias Kettlebristle", "account_ref": "ACC018",
     "instrument": "Northwind Freight Co Ordinary Shares",
     "distinct_price_levels": 12, "orders_placed": 270, "orders_executed": 9,
     "imbalance_ratio": 0.35, "seconds_to_reversal": 55, "venue_operator_name": "Highgate Commodities Ltd"},
    {"trader_name": "Renata Quillmote", "account_ref": "ACC019",
     "instrument": "Gammavane Imports Ltd 4.5% 2029 Conv Bond",
     "distinct_price_levels": 10, "orders_placed": 300, "orders_executed": 5,
     "imbalance_ratio": 0.75, "seconds_to_reversal": 3, "venue_operator_name": "Gammavane Imports Ltd"},
    {"trader_name": "Henrik Parsleybutton", "account_ref": "ACC020",
     "instrument": "Zeta Commodities Ltd Front-Month Future",
     "distinct_price_levels": 13, "orders_placed": 352, "orders_executed": 11,
     "imbalance_ratio": 0.80, "seconds_to_reversal": 12, "venue_operator_name": "Ravenwood Trading Co"},
    {"trader_name": "Grace Juniperbutton", "account_ref": "ACC021",
     "instrument": "Ravenwood Trading Co Front-Month Future",
     "distinct_price_levels": 7, "orders_placed": 280, "orders_executed": 4,
     "imbalance_ratio": 0.65, "seconds_to_reversal": 2, "venue_operator_name": "Continental Correspondent Bank"},
    {"trader_name": "Dmitri Brackencrumb", "account_ref": "ACC022",
     "instrument": "Alpha Trading Ltd Ordinary Shares",
     "distinct_price_levels": 14, "orders_placed": 280, "orders_executed": 8,
     "imbalance_ratio": 0.85, "seconds_to_reversal": 4, "venue_operator_name": "Alpha Trading Ltd"},
]

# venue_operator_name, account_ref, jurisdiction, relationship, prior_alerts
VENUES: List[Dict[str, Any]] = [
    {"venue_operator_name": "Northwind Freight Co", "account_ref": "ACC001", "jurisdiction": "Germany",
     "relationship": "Direct Market Access", "prior_alerts": 0},
    {"venue_operator_name": "Highgate Commodities Ltd", "account_ref": "ACC002", "jurisdiction": "United Kingdom",
     "relationship": "Sponsored Access", "prior_alerts": 0},
    {"venue_operator_name": "Continental Correspondent Bank", "account_ref": "ACC003", "jurisdiction": "Sweden",
     "relationship": "Prime Brokerage DMA", "prior_alerts": 0},
    {"venue_operator_name": "Ravenwood Trading Co", "account_ref": "ACC004", "jurisdiction": "Ireland",
     "relationship": "MTF Membership", "prior_alerts": 0},
    {"venue_operator_name": "Alpha Trading Ltd", "account_ref": "ACC005", "jurisdiction": "Netherlands",
     "relationship": "Direct Market Access", "prior_alerts": 0},
    {"venue_operator_name": "Zeta Commodities Ltd", "account_ref": "ACC006", "jurisdiction": "Cyprus",
     "relationship": "Algo Trading Facility", "prior_alerts": 0},
    {"venue_operator_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC007", "jurisdiction": "Luxembourg",
     "relationship": "Sponsored Access", "prior_alerts": 0},
    {"venue_operator_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC008", "jurisdiction": "Singapore",
     "relationship": "Direct Market Access", "prior_alerts": 1},
    {"venue_operator_name": "Northwind Freight Co", "account_ref": "ACC009", "jurisdiction": "Germany",
     "relationship": "MTF Membership", "prior_alerts": 1},
    {"venue_operator_name": "Highgate Commodities Ltd", "account_ref": "ACC010", "jurisdiction": "United Kingdom",
     "relationship": "Algo Trading Facility", "prior_alerts": 1},
    {"venue_operator_name": "Ravenwood Trading Co", "account_ref": "ACC011", "jurisdiction": "Ireland",
     "relationship": "Prime Brokerage DMA", "prior_alerts": 1},
    {"venue_operator_name": "Alpha Trading Ltd", "account_ref": "ACC012", "jurisdiction": "Netherlands",
     "relationship": "Sponsored Access", "prior_alerts": 1},
    {"venue_operator_name": "Zeta Commodities Ltd", "account_ref": "ACC013", "jurisdiction": "Cyprus",
     "relationship": "Direct Market Access", "prior_alerts": 2},
    {"venue_operator_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC014", "jurisdiction": "Luxembourg",
     "relationship": "Algo Trading Facility", "prior_alerts": 2},
    {"venue_operator_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC015", "jurisdiction": "Singapore",
     "relationship": "MTF Membership", "prior_alerts": 2},
    {"venue_operator_name": "Northwind Freight Co", "account_ref": "ACC016", "jurisdiction": "Germany",
     "relationship": "Prime Brokerage DMA", "prior_alerts": 2},
    {"venue_operator_name": "Continental Correspondent Bank", "account_ref": "ACC017", "jurisdiction": "Sweden",
     "relationship": "Sponsored Access", "prior_alerts": 2},
    {"venue_operator_name": "Highgate Commodities Ltd", "account_ref": "ACC018", "jurisdiction": "United Kingdom",
     "relationship": "Direct Market Access", "prior_alerts": 2},
    {"venue_operator_name": "Gammavane Imports Ltd", "account_ref": "ACC019", "jurisdiction": "Marshall Islands",
     "relationship": "Sponsored Access", "prior_alerts": 3},
    {"venue_operator_name": "Ravenwood Trading Co", "account_ref": "ACC020", "jurisdiction": "Ireland",
     "relationship": "Algo Trading Facility", "prior_alerts": 3},
    {"venue_operator_name": "Continental Correspondent Bank", "account_ref": "ACC021", "jurisdiction": "Sweden",
     "relationship": "MTF Membership", "prior_alerts": 3},
    {"venue_operator_name": "Alpha Trading Ltd", "account_ref": "ACC022", "jurisdiction": "Netherlands",
     "relationship": "Prime Brokerage DMA", "prior_alerts": 3},
]

_TABLES = {"orders.csv": ORDERS, "venues.csv": VENUES}


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
