"""Generate synthetic sample data for CM005 Wash Trading.

22 trading accounts (>= the 20-row sample-data standard; CM005 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Grigor Puddlequill, 90/Critical, the single highest-scoring account
in the set) crosses matched buy and sell orders that produce no genuine change in
beneficial ownership, cleared through **Continental Correspondent Bank** -- an entity
already in the estate network -- so canonical entity resolution joins CM005 onto the
existing fused case. Being the top-scored account matters: the FC-10 adapter builds its
case/graph from the single highest exposure_score row, so the Continental Correspondent
Bank bridge has to be that row, not merely A Critical row.

Run:  python3 generate_cm005_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, instrument, self_matched_volume, total_volume, overlap_score,
# reported_volume, genuine_economic_volume, distinct_counterparties, clearing_broker_name
TRADES: List[Dict[str, Any]] = [
    {"trader_name": "Marco Thistlebristle", "account_ref": "ACC001", "instrument": "Gammavane Imports Ltd Common Stock",
     "self_matched_volume": 12600, "total_volume": 420000, "overlap_score": 5,
     "reported_volume": 187200, "genuine_economic_volume": 180000, "distinct_counterparties": 8,
     "clearing_broker_name": "Gammavane Imports Ltd"},
    {"trader_name": "Freya Brackenwhistle", "account_ref": "ACC002", "instrument": "Alpha Trading Ltd Corporate Bond",
     "self_matched_volume": 17500, "total_volume": 350000, "overlap_score": 8,
     "reported_volume": 159000, "genuine_economic_volume": 150000, "distinct_counterparties": 4,
     "clearing_broker_name": "Alpha Trading Ltd"},
    {"trader_name": "Rajiv Cindertumble", "account_ref": "ACC003", "instrument": "Zeta Commodities Ltd Futures",
     "self_matched_volume": 36600, "total_volume": 610000, "overlap_score": 11,
     "reported_volume": 262500, "genuine_economic_volume": 210000, "distinct_counterparties": 9,
     "clearing_broker_name": "Zeta Commodities Ltd"},
    {"trader_name": "Isabela Lanternquill", "account_ref": "ACC004", "instrument": "Ravenwood Trading Co Common Stock",
     "self_matched_volume": 19250, "total_volume": 275000, "overlap_score": 28,
     "reported_volume": 103550, "genuine_economic_volume": 95000, "distinct_counterparties": 7,
     "clearing_broker_name": "Ravenwood Trading Co"},
    {"trader_name": "Conor Flintwisp", "account_ref": "ACC005", "instrument": "Falcon Ridge Commodities Ltd Pref Shares",
     "self_matched_volume": 67200, "total_volume": 480000, "overlap_score": 14,
     "reported_volume": 226600, "genuine_economic_volume": 220000, "distinct_counterparties": 10,
     "clearing_broker_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Mireille Puddlekettle", "account_ref": "ACC006", "instrument": "Highgate Commodities Ltd Futures",
     "self_matched_volume": 35100, "total_volume": 390000, "overlap_score": 6,
     "reported_volume": 166400, "genuine_economic_volume": 130000, "distinct_counterparties": 3,
     "clearing_broker_name": "Highgate Commodities Ltd"},
    {"trader_name": "Dmitri Brackencrumb", "account_ref": "ACC007", "instrument": "Northwind Freight Co Corporate Bond",
     "self_matched_volume": 89250, "total_volume": 525000, "overlap_score": 32,
     "reported_volume": 196000, "genuine_economic_volume": 175000, "distinct_counterparties": 6,
     "clearing_broker_name": "Northwind Freight Co"},
    {"trader_name": "Naledi Marrowmote", "account_ref": "ACC008", "instrument": "Meridian Bulk Traders Ltd Common Stock",
     "self_matched_volume": 62000, "total_volume": 310000, "overlap_score": 36,
     "reported_volume": 184800, "genuine_economic_volume": 140000, "distinct_counterparties": 8,
     "clearing_broker_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Hassan Brindlecrumb", "account_ref": "ACC009", "instrument": "Gammavane Imports Ltd Futures",
     "self_matched_volume": 105800, "total_volume": 460000, "overlap_score": 40,
     "reported_volume": 216000, "genuine_economic_volume": 160000, "distinct_counterparties": 4,
     "clearing_broker_name": "Gammavane Imports Ltd"},
    {"trader_name": "Yuki Tallowwhistle", "account_ref": "ACC010", "instrument": "Alpha Trading Ltd Pref Shares",
     "self_matched_volume": 153400, "total_volume": 590000, "overlap_score": 44,
     "reported_volume": 210000, "genuine_economic_volume": 120000, "distinct_counterparties": 9,
     "clearing_broker_name": "Alpha Trading Ltd"},
    {"trader_name": "Petra Sáltthimblea", "account_ref": "ACC011", "instrument": "Zeta Commodities Ltd Common Stock",
     "self_matched_volume": 119000, "total_volume": 340000, "overlap_score": 16,
     "reported_volume": 200100, "genuine_economic_volume": 145000, "distinct_counterparties": 3,
     "clearing_broker_name": "Zeta Commodities Ltd"},
    {"trader_name": "Diego Quillspindle", "account_ref": "ACC012", "instrument": "Ravenwood Trading Co Corporate Bond",
     "self_matched_volume": 95950, "total_volume": 505000, "overlap_score": 58,
     "reported_volume": 235600, "genuine_economic_volume": 190000, "distinct_counterparties": 7,
     "clearing_broker_name": "Ravenwood Trading Co"},
    {"trader_name": "Astrid Vellumspindle", "account_ref": "ACC013", "instrument": "Falcon Ridge Commodities Ltd Futures",
     "self_matched_volume": 173250, "total_volume": 275000, "overlap_score": 87,
     "reported_volume": 221400, "genuine_economic_volume": 205000, "distinct_counterparties": 10,
     "clearing_broker_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Chidi Gossamerwhistle", "account_ref": "ACC014", "instrument": "Highgate Commodities Ltd Common Stock",
     "self_matched_volume": 217600, "total_volume": 320000, "overlap_score": 62,
     "reported_volume": 155100, "genuine_economic_volume": 110000, "distinct_counterparties": 6,
     "clearing_broker_name": "Highgate Commodities Ltd"},
    {"trader_name": "Selin Umberwhistle", "account_ref": "ACC015", "instrument": "Northwind Freight Co Pref Shares",
     "self_matched_volume": 184800, "total_volume": 440000, "overlap_score": 66,
     "reported_volume": 263250, "genuine_economic_volume": 135000, "distinct_counterparties": 4,
     "clearing_broker_name": "Northwind Freight Co"},
    {"trader_name": "Magnus Yarrowkettle", "account_ref": "ACC016", "instrument": "Meridian Bulk Traders Ltd Futures",
     "self_matched_volume": 281200, "total_volume": 380000, "overlap_score": 90,
     "reported_volume": 180000, "genuine_economic_volume": 125000, "distinct_counterparties": 8,
     "clearing_broker_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Fatima Brindlewisp", "account_ref": "ACC017", "instrument": "Gammavane Imports Ltd Corporate Bond",
     "self_matched_volume": 147500, "total_volume": 295000, "overlap_score": 70,
     "reported_volume": 270000, "genuine_economic_volume": 100000, "distinct_counterparties": 3,
     "clearing_broker_name": "Gammavane Imports Ltd"},
    {"trader_name": "Lucas Copperwisp", "account_ref": "ACC018", "instrument": "Alpha Trading Ltd Common Stock",
     "self_matched_volume": 323900, "total_volume": 410000, "overlap_score": 74,
     "reported_volume": 247250, "genuine_economic_volume": 115000, "distinct_counterparties": 4,
     "clearing_broker_name": "Alpha Trading Ltd"},
    {"trader_name": "Grigor Puddlequill", "account_ref": "ACC019", "instrument": "Continental Correspondent Bank Pref Shares",
     "self_matched_volume": 450000, "total_volume": 500000, "overlap_score": 95,
     "reported_volume": 480000, "genuine_economic_volume": 150000, "distinct_counterparties": 1,
     "clearing_broker_name": "Continental Correspondent Bank"},
    {"trader_name": "Renata Puddlebutton", "account_ref": "ACC020", "instrument": "Zeta Commodities Ltd Corporate Bond",
     "self_matched_volume": 306000, "total_volume": 360000, "overlap_score": 60,
     "reported_volume": 315000, "genuine_economic_volume": 90000, "distinct_counterparties": 2,
     "clearing_broker_name": "Zeta Commodities Ltd"},
    {"trader_name": "Baldwin Tallowcrumb", "account_ref": "ACC021", "instrument": "Ravenwood Trading Co Futures",
     "self_matched_volume": 181500, "total_volume": 330000, "overlap_score": 98,
     "reported_volume": 304500, "genuine_economic_volume": 105000, "distinct_counterparties": 1,
     "clearing_broker_name": "Ravenwood Trading Co"},
    {"trader_name": "Noor Copperthimble", "account_ref": "ACC022", "instrument": "Falcon Ridge Commodities Ltd Common Stock",
     "self_matched_volume": 446500, "total_volume": 470000, "overlap_score": 76,
     "reported_volume": 361000, "genuine_economic_volume": 95000, "distinct_counterparties": 1,
     "clearing_broker_name": "Falcon Ridge Commodities Ltd"},
]

# clearing_broker_name, account_ref, jurisdiction, relationship, prior_alerts
COUNTERPARTIES: List[Dict[str, Any]] = [
    {"clearing_broker_name": "Gammavane Imports Ltd", "account_ref": "ACC001", "jurisdiction": "Marshall Islands",
     "relationship": "Clearing broker", "prior_alerts": 0},
    {"clearing_broker_name": "Alpha Trading Ltd", "account_ref": "ACC002", "jurisdiction": "Cyprus",
     "relationship": "Clearing broker", "prior_alerts": 0},
    {"clearing_broker_name": "Zeta Commodities Ltd", "account_ref": "ACC003", "jurisdiction": "Cyprus",
     "relationship": "Give-up clearing agreement", "prior_alerts": 0},
    {"clearing_broker_name": "Ravenwood Trading Co", "account_ref": "ACC004", "jurisdiction": "Hong Kong",
     "relationship": "Clearing broker", "prior_alerts": 0},
    {"clearing_broker_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC005", "jurisdiction": "United Kingdom",
     "relationship": "Prime brokerage relationship", "prior_alerts": 0},
    {"clearing_broker_name": "Highgate Commodities Ltd", "account_ref": "ACC006", "jurisdiction": "United Kingdom",
     "relationship": "Clearing broker", "prior_alerts": 1},
    {"clearing_broker_name": "Northwind Freight Co", "account_ref": "ACC007", "jurisdiction": "Germany",
     "relationship": "Clearing broker", "prior_alerts": 0},
    {"clearing_broker_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC008", "jurisdiction": "Singapore",
     "relationship": "Give-up clearing agreement", "prior_alerts": 1},
    {"clearing_broker_name": "Gammavane Imports Ltd", "account_ref": "ACC009", "jurisdiction": "Marshall Islands",
     "relationship": "Clearing broker", "prior_alerts": 1},
    {"clearing_broker_name": "Alpha Trading Ltd", "account_ref": "ACC010", "jurisdiction": "Cyprus",
     "relationship": "Prime brokerage relationship", "prior_alerts": 1},
    {"clearing_broker_name": "Zeta Commodities Ltd", "account_ref": "ACC011", "jurisdiction": "Cyprus",
     "relationship": "Clearing broker", "prior_alerts": 1},
    {"clearing_broker_name": "Ravenwood Trading Co", "account_ref": "ACC012", "jurisdiction": "Hong Kong",
     "relationship": "Clearing broker", "prior_alerts": 1},
    {"clearing_broker_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC013", "jurisdiction": "United Kingdom",
     "relationship": "Give-up clearing agreement", "prior_alerts": 1},
    {"clearing_broker_name": "Highgate Commodities Ltd", "account_ref": "ACC014", "jurisdiction": "United Kingdom",
     "relationship": "Prime brokerage relationship", "prior_alerts": 2},
    {"clearing_broker_name": "Northwind Freight Co", "account_ref": "ACC015", "jurisdiction": "Germany",
     "relationship": "Clearing broker", "prior_alerts": 2},
    {"clearing_broker_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC016", "jurisdiction": "Singapore",
     "relationship": "Clearing broker", "prior_alerts": 2},
    {"clearing_broker_name": "Gammavane Imports Ltd", "account_ref": "ACC017", "jurisdiction": "Marshall Islands",
     "relationship": "Give-up clearing agreement", "prior_alerts": 2},
    {"clearing_broker_name": "Alpha Trading Ltd", "account_ref": "ACC018", "jurisdiction": "Cyprus",
     "relationship": "Clearing broker", "prior_alerts": 2},
    {"clearing_broker_name": "Continental Correspondent Bank", "account_ref": "ACC019", "jurisdiction": "Sweden",
     "relationship": "Prime brokerage relationship", "prior_alerts": 3},
    {"clearing_broker_name": "Zeta Commodities Ltd", "account_ref": "ACC020", "jurisdiction": "Cyprus",
     "relationship": "Clearing broker", "prior_alerts": 3},
    {"clearing_broker_name": "Ravenwood Trading Co", "account_ref": "ACC021", "jurisdiction": "Hong Kong",
     "relationship": "Give-up clearing agreement", "prior_alerts": 3},
    {"clearing_broker_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC022", "jurisdiction": "United Kingdom",
     "relationship": "Clearing broker", "prior_alerts": 3},
]

_TABLES = {"trades.csv": TRADES, "counterparties.csv": COUNTERPARTIES}


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
