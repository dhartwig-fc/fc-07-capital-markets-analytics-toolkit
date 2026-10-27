"""Generate synthetic sample data for CM006 Front Running.

22 trading accounts (>= the 20-row sample-data standard; CM006 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Vanessa Thistlethimble, 90/Critical, the single highest-scoring account in
the set) deals 1 second ahead of a client order at **Alpha Trading Ltd** -- an entity
already in the estate network -- with the trader's pre-position direction 96%
correlated to the client order's direction, 91% of the position's value captured as
profit once the client order landed, and 13 documented contact events with the desk
handling the client order in the 90 days before, so canonical entity resolution joins
CM006 onto the existing fused case. Being the top-scored account matters: the FC-10
adapter builds its case/graph from the single highest exposure_score row, so the Alpha
Trading Ltd bridge has to be that row, not merely A Critical row.

Run:  python3 generate_cm006_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, desk, instrument, seconds_ahead_of_client_order,
# correlation_pct, realized_pnl, position_value, contact_events_90d, client_firm_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"trader_name": "Marta Rushquill", "account_ref": "ACC001", "desk": "Agency Execution Desk",
     "instrument": "Gammavane Imports Ltd Ordinary Shares", "seconds_ahead_of_client_order": 180,
     "correlation_pct": 15, "realized_pnl": 96000, "position_value": 1200000,
     "contact_events_90d": 0, "client_firm_name": "Gammavane Imports Ltd"},
    {"trader_name": "Julian Thimblequill", "account_ref": "ACC002", "desk": "Program Trading Desk",
     "instrument": "Zeta Commodities Ltd Ordinary Shares", "seconds_ahead_of_client_order": 250,
     "correlation_pct": 22, "realized_pnl": 180000, "position_value": 1500000,
     "contact_events_90d": 3, "client_firm_name": "Zeta Commodities Ltd"},
    {"trader_name": "Fatima Brindlewisp", "account_ref": "ACC003", "desk": "Cash Equities Desk",
     "instrument": "Continental Correspondent Bank Ordinary Shares", "seconds_ahead_of_client_order": 320,
     "correlation_pct": 30, "realized_pnl": 540000, "position_value": 1800000,
     "contact_events_90d": 1, "client_firm_name": "Continental Correspondent Bank"},
    {"trader_name": "Erik Vellumspindle", "account_ref": "ACC004", "desk": "Electronic Trading Desk",
     "instrument": "Ravenwood Trading Co Ordinary Shares", "seconds_ahead_of_client_order": 395,
     "correlation_pct": 50, "realized_pnl": 144000, "position_value": 900000,
     "contact_events_90d": 2, "client_firm_name": "Ravenwood Trading Co"},
    {"trader_name": "Naledi Thistlewisp", "account_ref": "ACC005", "desk": "Equity Derivatives Desk",
     "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares", "seconds_ahead_of_client_order": 100,
     "correlation_pct": 12, "realized_pnl": 120000, "position_value": 2000000,
     "contact_events_90d": 0, "client_firm_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Andrei Ashquill", "account_ref": "ACC006", "desk": "Block Trading Desk",
     "instrument": "Highgate Commodities Ltd Ordinary Shares", "seconds_ahead_of_client_order": 210,
     "correlation_pct": 35, "realized_pnl": 385000, "position_value": 1100000,
     "contact_events_90d": 4, "client_firm_name": "Highgate Commodities Ltd"},
    {"trader_name": "Yuki Tallowwhistle", "account_ref": "ACC007", "desk": "Algorithmic Execution Desk",
     "instrument": "Northwind Freight Co Ordinary Shares", "seconds_ahead_of_client_order": 90,
     "correlation_pct": 55, "realized_pnl": 475000, "position_value": 2500000,
     "contact_events_90d": 1, "client_firm_name": "Northwind Freight Co"},
    {"trader_name": "Sofia Sorrelwisp", "account_ref": "ACC008", "desk": "Institutional Sales Trading Desk",
     "instrument": "Meridian Bulk Traders Ltd Ordinary Shares", "seconds_ahead_of_client_order": 75,
     "correlation_pct": 60, "realized_pnl": 680000, "position_value": 1700000,
     "contact_events_90d": 2, "client_firm_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Callum Wrenkettle", "account_ref": "ACC009", "desk": "Agency Execution Desk",
     "instrument": "Gammavane Imports Ltd Ordinary Shares", "seconds_ahead_of_client_order": 60,
     "correlation_pct": 48, "realized_pnl": 704000, "position_value": 2200000,
     "contact_events_90d": 5, "client_firm_name": "Gammavane Imports Ltd"},
    {"trader_name": "Ines Lanternquill", "account_ref": "ACC010", "desk": "Program Trading Desk",
     "instrument": "Zeta Commodities Ltd Ordinary Shares", "seconds_ahead_of_client_order": 45,
     "correlation_pct": 58, "realized_pnl": 960000, "position_value": 1600000,
     "contact_events_90d": 0, "client_firm_name": "Zeta Commodities Ltd"},
    {"trader_name": "Rajiv Thistlespindle", "account_ref": "ACC011", "desk": "Cash Equities Desk",
     "instrument": "Continental Correspondent Bank Ordinary Shares", "seconds_ahead_of_client_order": 25,
     "correlation_pct": 18, "realized_pnl": 784000, "position_value": 2800000,
     "contact_events_90d": 3, "client_firm_name": "Continental Correspondent Bank"},
    {"trader_name": "Greta Nettlewhistle", "account_ref": "ACC012", "desk": "Electronic Trading Desk",
     "instrument": "Ravenwood Trading Co Ordinary Shares", "seconds_ahead_of_client_order": 55,
     "correlation_pct": 70, "realized_pnl": 572000, "position_value": 1300000,
     "contact_events_90d": 1, "client_firm_name": "Ravenwood Trading Co"},
    {"trader_name": "Marco Cindercrumb", "account_ref": "ACC013", "desk": "Equity Derivatives Desk",
     "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares", "seconds_ahead_of_client_order": 4,
     "correlation_pct": 90, "realized_pnl": 210000, "position_value": 2100000,
     "contact_events_90d": 2, "client_firm_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Chidi Gossamerwhistle", "account_ref": "ACC014", "desk": "Block Trading Desk",
     "instrument": "Highgate Commodities Ltd Ordinary Shares", "seconds_ahead_of_client_order": 3,
     "correlation_pct": 75, "realized_pnl": 722000, "position_value": 1900000,
     "contact_events_90d": 0, "client_firm_name": "Highgate Commodities Ltd"},
    {"trader_name": "Freya Umberbutton", "account_ref": "ACC015", "desk": "Algorithmic Execution Desk",
     "instrument": "Northwind Freight Co Ordinary Shares", "seconds_ahead_of_client_order": 18,
     "correlation_pct": 80, "realized_pnl": 1632000, "position_value": 2400000,
     "contact_events_90d": 4, "client_firm_name": "Northwind Freight Co"},
    {"trader_name": "Dimitri Brackencrumb", "account_ref": "ACC016", "desk": "Institutional Sales Trading Desk",
     "instrument": "Meridian Bulk Traders Ltd Ordinary Shares", "seconds_ahead_of_client_order": 2,
     "correlation_pct": 95, "realized_pnl": 420000, "position_value": 1000000,
     "contact_events_90d": 1, "client_firm_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Isabela Brindlemote", "account_ref": "ACC017", "desk": "Agency Execution Desk",
     "instrument": "Gammavane Imports Ltd Ordinary Shares", "seconds_ahead_of_client_order": 12,
     "correlation_pct": 72, "realized_pnl": 2210000, "position_value": 2600000,
     "contact_events_90d": 5, "client_firm_name": "Gammavane Imports Ltd"},
    {"trader_name": "Owen Hazelbutton", "account_ref": "ACC018", "desk": "Program Trading Desk",
     "instrument": "Zeta Commodities Ltd Ordinary Shares", "seconds_ahead_of_client_order": 4,
     "correlation_pct": 78, "realized_pnl": 2160000, "position_value": 3000000,
     "contact_events_90d": 3, "client_firm_name": "Zeta Commodities Ltd"},
    {"trader_name": "Vanessa Thistlethimble", "account_ref": "ACC019", "desk": "Agency Execution Desk",
     "instrument": "Alpha Trading Ltd Ordinary Shares", "seconds_ahead_of_client_order": 1,
     "correlation_pct": 96, "realized_pnl": 2184000, "position_value": 2400000,
     "contact_events_90d": 13, "client_firm_name": "Alpha Trading Ltd"},
    {"trader_name": "Haruto Tansythimble", "account_ref": "ACC020", "desk": "Cash Equities Desk",
     "instrument": "Continental Correspondent Bank Ordinary Shares", "seconds_ahead_of_client_order": 3,
     "correlation_pct": 82, "realized_pnl": 1540000, "position_value": 1750000,
     "contact_events_90d": 7, "client_firm_name": "Continental Correspondent Bank"},
    {"trader_name": "Lena Gorsebutton", "account_ref": "ACC021", "desk": "Electronic Trading Desk",
     "instrument": "Ravenwood Trading Co Ordinary Shares", "seconds_ahead_of_client_order": 9,
     "correlation_pct": 92, "realized_pnl": 1900000, "position_value": 2000000,
     "contact_events_90d": 11, "client_firm_name": "Ravenwood Trading Co"},
    {"trader_name": "Tariq Willowcrumb", "account_ref": "ACC022", "desk": "Equity Derivatives Desk",
     "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares", "seconds_ahead_of_client_order": 2,
     "correlation_pct": 68, "realized_pnl": 1245000, "position_value": 1500000,
     "contact_events_90d": 14, "client_firm_name": "Falcon Ridge Commodities Ltd"},
]

# client_firm_name, account_ref, jurisdiction, relationship, prior_alerts
CLIENT_ORDERS: List[Dict[str, Any]] = [
    {"client_firm_name": "Gammavane Imports Ltd", "account_ref": "ACC001", "jurisdiction": "Marshall Islands",
     "relationship": "Institutional agency client", "prior_alerts": 0},
    {"client_firm_name": "Zeta Commodities Ltd", "account_ref": "ACC002", "jurisdiction": "Cyprus",
     "relationship": "Buy-side asset manager", "prior_alerts": 0},
    {"client_firm_name": "Continental Correspondent Bank", "account_ref": "ACC003", "jurisdiction": "Sweden",
     "relationship": "Corporate treasury client", "prior_alerts": 0},
    {"client_firm_name": "Ravenwood Trading Co", "account_ref": "ACC004", "jurisdiction": "Panama",
     "relationship": "Hedge fund client", "prior_alerts": 0},
    {"client_firm_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC005", "jurisdiction": "Malta",
     "relationship": "Pension fund client", "prior_alerts": 0},
    {"client_firm_name": "Highgate Commodities Ltd", "account_ref": "ACC006", "jurisdiction": "British Virgin Islands",
     "relationship": "Sovereign wealth client", "prior_alerts": 1},
    {"client_firm_name": "Northwind Freight Co", "account_ref": "ACC007", "jurisdiction": "Germany",
     "relationship": "Institutional agency client", "prior_alerts": 0},
    {"client_firm_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC008", "jurisdiction": "Singapore",
     "relationship": "Family office client", "prior_alerts": 1},
    {"client_firm_name": "Gammavane Imports Ltd", "account_ref": "ACC009", "jurisdiction": "Marshall Islands",
     "relationship": "Buy-side asset manager", "prior_alerts": 1},
    {"client_firm_name": "Zeta Commodities Ltd", "account_ref": "ACC010", "jurisdiction": "Cyprus",
     "relationship": "Corporate treasury client", "prior_alerts": 1},
    {"client_firm_name": "Continental Correspondent Bank", "account_ref": "ACC011", "jurisdiction": "Sweden",
     "relationship": "Hedge fund client", "prior_alerts": 1},
    {"client_firm_name": "Ravenwood Trading Co", "account_ref": "ACC012", "jurisdiction": "Panama",
     "relationship": "Pension fund client", "prior_alerts": 1},
    {"client_firm_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC013", "jurisdiction": "Malta",
     "relationship": "Sovereign wealth client", "prior_alerts": 1},
    {"client_firm_name": "Highgate Commodities Ltd", "account_ref": "ACC014", "jurisdiction": "British Virgin Islands",
     "relationship": "Family office client", "prior_alerts": 2},
    {"client_firm_name": "Northwind Freight Co", "account_ref": "ACC015", "jurisdiction": "Germany",
     "relationship": "Institutional agency client", "prior_alerts": 2},
    {"client_firm_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC016", "jurisdiction": "Singapore",
     "relationship": "Buy-side asset manager", "prior_alerts": 2},
    {"client_firm_name": "Gammavane Imports Ltd", "account_ref": "ACC017", "jurisdiction": "Marshall Islands",
     "relationship": "Corporate treasury client", "prior_alerts": 2},
    {"client_firm_name": "Zeta Commodities Ltd", "account_ref": "ACC018", "jurisdiction": "Cyprus",
     "relationship": "Hedge fund client", "prior_alerts": 2},
    {"client_firm_name": "Alpha Trading Ltd", "account_ref": "ACC019", "jurisdiction": "United Kingdom",
     "relationship": "Institutional agency client", "prior_alerts": 3},
    {"client_firm_name": "Continental Correspondent Bank", "account_ref": "ACC020", "jurisdiction": "Sweden",
     "relationship": "Pension fund client", "prior_alerts": 3},
    {"client_firm_name": "Ravenwood Trading Co", "account_ref": "ACC021", "jurisdiction": "Panama",
     "relationship": "Sovereign wealth client", "prior_alerts": 3},
    {"client_firm_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC022", "jurisdiction": "Malta",
     "relationship": "Family office client", "prior_alerts": 3},
]

_TABLES = {"trading_accounts.csv": ACCOUNTS, "client_orders.csv": CLIENT_ORDERS}


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
