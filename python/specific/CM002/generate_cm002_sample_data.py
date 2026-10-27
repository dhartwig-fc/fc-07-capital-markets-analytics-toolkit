"""Generate synthetic sample data for CM002 Market Manipulation.

22 trading accounts (>= the 20-row sample-data standard; CM002 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Marcus Kettlebutton, 90/Critical, the single highest-scoring account
in the set) drives an abnormal price move against normal volatility, concentrated in an
outsized share of market volume, coordinated across eight linked accounts, and largely
unwound once the manipulative window closes -- in **Alpha Trading Ltd** Ordinary Shares,
an entity already in the estate network, so canonical entity resolution joins CM002 onto
the existing fused case. Being the top-scored account matters: the FC-10 adapter builds
its case/graph from the single highest exposure_score row, so the Alpha Trading Ltd
bridge has to be that row, not merely A Critical row.

Run:  python3 generate_cm002_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# account_holder_name, account_ref, desk, instrument, normal_volatility_pct,
# price_move_pct, pct_of_market_volume, linked_accounts_count,
# post_period_reversal_pct, ultimate_owner_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"account_holder_name": "Naomi Brackenmote", "account_ref": "ACC001", "desk": "Program Trading Desk",
     "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares", "normal_volatility_pct": 1.6,
     "price_move_pct": 1.86, "pct_of_market_volume": 7, "linked_accounts_count": 1,
     "post_period_reversal_pct": 0.31, "ultimate_owner_name": "Falcon Ridge Commodities Ltd"},
    {"account_holder_name": "Marco Cindercrumb", "account_ref": "ACC002", "desk": "Systematic Trading Desk",
     "instrument": "Highgate Commodities Ltd Ordinary Shares", "normal_volatility_pct": 2.0,
     "price_move_pct": 2.16, "pct_of_market_volume": 5, "linked_accounts_count": 1,
     "post_period_reversal_pct": 0.83, "ultimate_owner_name": "Highgate Commodities Ltd"},
    {"account_holder_name": "Yuki Tallowwhistle", "account_ref": "ACC003", "desk": "Equities Prop Desk",
     "instrument": "Meridian Bulk Traders Ltd Ordinary Shares", "normal_volatility_pct": 2.4,
     "price_move_pct": 1.92, "pct_of_market_volume": 5, "linked_accounts_count": 2,
     "post_period_reversal_pct": 0.38, "ultimate_owner_name": "Meridian Bulk Traders Ltd"},
    {"account_holder_name": "Fatima Umberwisp", "account_ref": "ACC004", "desk": "Algorithmic Trading Desk",
     "instrument": "Northwind Freight Co Ordinary Shares", "normal_volatility_pct": 1.8,
     "price_move_pct": 1.49, "pct_of_market_volume": 18, "linked_accounts_count": 1,
     "post_period_reversal_pct": 0.08, "ultimate_owner_name": "Northwind Freight Co"},
    {"account_holder_name": "Connor Fernfiddle", "account_ref": "ACC005", "desk": "Multi-Strategy Desk",
     "instrument": "Ravenwood Trading Co Ordinary Shares", "normal_volatility_pct": 3.0,
     "price_move_pct": 4.85, "pct_of_market_volume": 4, "linked_accounts_count": 1,
     "post_period_reversal_pct": 0.81, "ultimate_owner_name": "Ravenwood Trading Co"},
    {"account_holder_name": "Ines Tallowbutton", "account_ref": "ACC006", "desk": "Equity Derivatives Desk",
     "instrument": "Continental Correspondent Bank Ordinary Shares", "normal_volatility_pct": 2.2,
     "price_move_pct": 2.43, "pct_of_market_volume": 7, "linked_accounts_count": 2,
     "post_period_reversal_pct": 0.98, "ultimate_owner_name": "Continental Correspondent Bank"},
    {"account_holder_name": "Dmitri Brackencrumb", "account_ref": "ACC007", "desk": "Program Trading Desk",
     "instrument": "Zeta Commodities Ltd Ordinary Shares", "normal_volatility_pct": 1.5,
     "price_move_pct": 3.13, "pct_of_market_volume": 13, "linked_accounts_count": 1,
     "post_period_reversal_pct": 0.32, "ultimate_owner_name": "Zeta Commodities Ltd"},
    {"account_holder_name": "Grace Juniperwisp", "account_ref": "ACC008", "desk": "High-Frequency Trading Desk",
     "instrument": "Gammavane Imports Ltd Ordinary Shares", "normal_volatility_pct": 2.8,
     "price_move_pct": 7.52, "pct_of_market_volume": 20, "linked_accounts_count": 2,
     "post_period_reversal_pct": 1.5, "ultimate_owner_name": "Gammavane Imports Ltd"},
    {"account_holder_name": "Henrik Umberquill", "account_ref": "ACC009", "desk": "Systematic Trading Desk",
     "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares", "normal_volatility_pct": 3.5,
     "price_move_pct": 8.63, "pct_of_market_volume": 18, "linked_accounts_count": 2,
     "post_period_reversal_pct": 3.75, "ultimate_owner_name": "Falcon Ridge Commodities Ltd"},
    {"account_holder_name": "Chiara Marrowfiddle", "account_ref": "ACC010", "desk": "Equities Prop Desk",
     "instrument": "Highgate Commodities Ltd Ordinary Shares", "normal_volatility_pct": 1.9,
     "price_move_pct": 3.79, "pct_of_market_volume": 22, "linked_accounts_count": 3,
     "post_period_reversal_pct": 0.25, "ultimate_owner_name": "Highgate Commodities Ltd"},
    {"account_holder_name": "Arjun Hazeltumble", "account_ref": "ACC011", "desk": "Multi-Strategy Desk",
     "instrument": "Meridian Bulk Traders Ltd Ordinary Shares", "normal_volatility_pct": 2.6,
     "price_move_pct": 12.55, "pct_of_market_volume": 6, "linked_accounts_count": 2,
     "post_period_reversal_pct": 4.44, "ultimate_owner_name": "Meridian Bulk Traders Ltd"},
    {"account_holder_name": "Isabela Wrenbutton", "account_ref": "ACC012", "desk": "Algorithmic Trading Desk",
     "instrument": "Northwind Freight Co Ordinary Shares", "normal_volatility_pct": 2.1,
     "price_move_pct": 5.54, "pct_of_market_volume": 44, "linked_accounts_count": 2,
     "post_period_reversal_pct": 0.44, "ultimate_owner_name": "Northwind Freight Co"},
    {"account_holder_name": "Callum Wrenkettle", "account_ref": "ACC013", "desk": "Program Trading Desk",
     "instrument": "Ravenwood Trading Co Ordinary Shares", "normal_volatility_pct": 3.2,
     "price_move_pct": 25.96, "pct_of_market_volume": 64, "linked_accounts_count": 1,
     "post_period_reversal_pct": 1.87, "ultimate_owner_name": "Ravenwood Trading Co"},
    {"account_holder_name": "Petra Parsleythimble", "account_ref": "ACC014", "desk": "Equity Derivatives Desk",
     "instrument": "Continental Correspondent Bank Ordinary Shares", "normal_volatility_pct": 1.7,
     "price_move_pct": 12.24, "pct_of_market_volume": 38, "linked_accounts_count": 2,
     "post_period_reversal_pct": 0.66, "ultimate_owner_name": "Continental Correspondent Bank"},
    {"account_holder_name": "Samuel Kettlewhistle", "account_ref": "ACC015", "desk": "High-Frequency Trading Desk",
     "instrument": "Zeta Commodities Ltd Ordinary Shares", "normal_volatility_pct": 2.9,
     "price_move_pct": 9.55, "pct_of_market_volume": 35, "linked_accounts_count": 4,
     "post_period_reversal_pct": 3.23, "ultimate_owner_name": "Zeta Commodities Ltd"},
    {"account_holder_name": "Lena Gorsebutton", "account_ref": "ACC016", "desk": "Systematic Trading Desk",
     "instrument": "Gammavane Imports Ltd Ordinary Shares", "normal_volatility_pct": 2.3,
     "price_move_pct": 19.17, "pct_of_market_volume": 61, "linked_accounts_count": 2,
     "post_period_reversal_pct": 2.43, "ultimate_owner_name": "Gammavane Imports Ltd"},
    {"account_holder_name": "Rafael Wrenthimble", "account_ref": "ACC017", "desk": "Equities Prop Desk",
     "instrument": "Falcon Ridge Commodities Ltd Ordinary Shares", "normal_volatility_pct": 3.8,
     "price_move_pct": 13.46, "pct_of_market_volume": 30, "linked_accounts_count": 5,
     "post_period_reversal_pct": 5.42, "ultimate_owner_name": "Falcon Ridge Commodities Ltd"},
    {"account_holder_name": "Anastasia Quillcrumb", "account_ref": "ACC018", "desk": "Multi-Strategy Desk",
     "instrument": "Highgate Commodities Ltd Ordinary Shares", "normal_volatility_pct": 2.5,
     "price_move_pct": 23.12, "pct_of_market_volume": 34, "linked_accounts_count": 3,
     "post_period_reversal_pct": 8.28, "ultimate_owner_name": "Highgate Commodities Ltd"},
    {"account_holder_name": "Marcus Kettlebutton", "account_ref": "ACC019", "desk": "Equities Prop Desk",
     "instrument": "Alpha Trading Ltd Ordinary Shares", "normal_volatility_pct": 4.0,
     "price_move_pct": 30.06, "pct_of_market_volume": 67, "linked_accounts_count": 8,
     "post_period_reversal_pct": 28.74, "ultimate_owner_name": "Alpha Trading Ltd"},
    {"account_holder_name": "Sofia Rushquill", "account_ref": "ACC020", "desk": "Algorithmic Trading Desk",
     "instrument": "Meridian Bulk Traders Ltd Ordinary Shares", "normal_volatility_pct": 2.7,
     "price_move_pct": 23.12, "pct_of_market_volume": 40, "linked_accounts_count": 7,
     "post_period_reversal_pct": 15.4, "ultimate_owner_name": "Meridian Bulk Traders Ltd"},
    {"account_holder_name": "Tobias Lanternbutton", "account_ref": "ACC021", "desk": "Program Trading Desk",
     "instrument": "Northwind Freight Co Ordinary Shares", "normal_volatility_pct": 3.3,
     "price_move_pct": 16.17, "pct_of_market_volume": 68, "linked_accounts_count": 7,
     "post_period_reversal_pct": 13.32, "ultimate_owner_name": "Northwind Freight Co"},
    {"account_holder_name": "Ji-Yeon Umberkettle", "account_ref": "ACC022", "desk": "High-Frequency Trading Desk",
     "instrument": "Ravenwood Trading Co Ordinary Shares", "normal_volatility_pct": 1.6,
     "price_move_pct": 10.99, "pct_of_market_volume": 37, "linked_accounts_count": 6,
     "post_period_reversal_pct": 10.18, "ultimate_owner_name": "Ravenwood Trading Co"},
]

# ultimate_owner_name, account_ref, venue, jurisdiction, relationship, prior_alerts
COUNTERPARTIES: List[Dict[str, Any]] = [
    {"ultimate_owner_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC001", "venue": "London Stock Exchange",
     "jurisdiction": "Canada", "relationship": "Beneficial owner (declared)", "prior_alerts": 0},
    {"ultimate_owner_name": "Highgate Commodities Ltd", "account_ref": "ACC002", "venue": "Borsa Italiana",
     "jurisdiction": "South Africa", "relationship": "Ultimate controlling shareholder", "prior_alerts": 0},
    {"ultimate_owner_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC003", "venue": "Tokyo Stock Exchange",
     "jurisdiction": "Singapore", "relationship": "Nominee holding structure", "prior_alerts": 0},
    {"ultimate_owner_name": "Northwind Freight Co", "account_ref": "ACC004", "venue": "Nasdaq Dubai",
     "jurisdiction": "Germany", "relationship": "Corporate trading vehicle", "prior_alerts": 0},
    {"ultimate_owner_name": "Ravenwood Trading Co", "account_ref": "ACC005", "venue": "Euronext Dublin",
     "jurisdiction": "Ireland", "relationship": "Custodial nominee arrangement", "prior_alerts": 0},
    {"ultimate_owner_name": "Continental Correspondent Bank", "account_ref": "ACC006", "venue": "Deutsche Börse Xetra",
     "jurisdiction": "Sweden", "relationship": "Discretionary investment mandate holder", "prior_alerts": 1},
    {"ultimate_owner_name": "Zeta Commodities Ltd", "account_ref": "ACC007", "venue": "Warsaw Stock Exchange",
     "jurisdiction": "Cyprus", "relationship": "Beneficial owner (declared)", "prior_alerts": 0},
    {"ultimate_owner_name": "Gammavane Imports Ltd", "account_ref": "ACC008", "venue": "Nasdaq Stockholm",
     "jurisdiction": "Marshall Islands", "relationship": "Ultimate controlling shareholder", "prior_alerts": 1},
    {"ultimate_owner_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC009", "venue": "Oslo Børs",
     "jurisdiction": "Canada", "relationship": "Nominee holding structure", "prior_alerts": 1},
    {"ultimate_owner_name": "Highgate Commodities Ltd", "account_ref": "ACC010", "venue": "Johannesburg Stock Exchange",
     "jurisdiction": "South Africa", "relationship": "Corporate trading vehicle", "prior_alerts": 1},
    {"ultimate_owner_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC011", "venue": "Singapore Exchange",
     "jurisdiction": "Singapore", "relationship": "Custodial nominee arrangement", "prior_alerts": 1},
    {"ultimate_owner_name": "Northwind Freight Co", "account_ref": "ACC012", "venue": "Euronext Amsterdam",
     "jurisdiction": "Germany", "relationship": "Discretionary investment mandate holder", "prior_alerts": 2},
    {"ultimate_owner_name": "Ravenwood Trading Co", "account_ref": "ACC013", "venue": "Toronto Stock Exchange",
     "jurisdiction": "Ireland", "relationship": "Beneficial owner (declared)", "prior_alerts": 1},
    {"ultimate_owner_name": "Continental Correspondent Bank", "account_ref": "ACC014", "venue": "SIX Swiss Exchange",
     "jurisdiction": "Sweden", "relationship": "Ultimate controlling shareholder", "prior_alerts": 2},
    {"ultimate_owner_name": "Zeta Commodities Ltd", "account_ref": "ACC015", "venue": "Hong Kong Stock Exchange",
     "jurisdiction": "Cyprus", "relationship": "Nominee holding structure", "prior_alerts": 2},
    {"ultimate_owner_name": "Gammavane Imports Ltd", "account_ref": "ACC016", "venue": "Vienna Stock Exchange",
     "jurisdiction": "Marshall Islands", "relationship": "Corporate trading vehicle", "prior_alerts": 2},
    {"ultimate_owner_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC017", "venue": "Madrid Stock Exchange (BME)",
     "jurisdiction": "Canada", "relationship": "Custodial nominee arrangement", "prior_alerts": 2},
    {"ultimate_owner_name": "Highgate Commodities Ltd", "account_ref": "ACC018", "venue": "Athens Stock Exchange",
     "jurisdiction": "South Africa", "relationship": "Discretionary investment mandate holder", "prior_alerts": 2},
    {"ultimate_owner_name": "Alpha Trading Ltd", "account_ref": "ACC019", "venue": "London Stock Exchange",
     "jurisdiction": "British Virgin Islands", "relationship": "Ultimate controlling shareholder", "prior_alerts": 3},
    {"ultimate_owner_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC020", "venue": "Australian Securities Exchange",
     "jurisdiction": "Singapore", "relationship": "Nominee holding structure", "prior_alerts": 3},
    {"ultimate_owner_name": "Northwind Freight Co", "account_ref": "ACC021", "venue": "NASDAQ",
     "jurisdiction": "Germany", "relationship": "Corporate trading vehicle", "prior_alerts": 3},
    {"ultimate_owner_name": "Ravenwood Trading Co", "account_ref": "ACC022", "venue": "Bombay Stock Exchange",
     "jurisdiction": "Ireland", "relationship": "Custodial nominee arrangement", "prior_alerts": 3},
]

_TABLES = {"trading_accounts.csv": ACCOUNTS, "counterparties.csv": COUNTERPARTIES}


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
