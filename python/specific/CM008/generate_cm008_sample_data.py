"""Generate synthetic sample data for CM008 Cross Market Abuse.

22 trading accounts (>= the 20-row sample-data standard; CM008 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Natasha Ivybristlea, 90/Critical, the single highest-scoring account
in the set) trades a correlated cash/derivative pair in **Zeta Commodities Ltd** -- an
entity already in the estate network -- with near-perfect cross-venue position
correlation, six distinct venues, almost total price-impact transfer and trades
synchronised within 2 seconds across venues, so canonical entity resolution joins
CM008 onto the existing fused case. Being the top-scored account matters: the FC-10
adapter builds its case/graph from the single highest exposure_score row, so the
Zeta Commodities Ltd bridge has to be that row, not merely A Critical row.

Run:  python3 generate_cm008_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, primary_instrument, correlated_instrument, correlation_pct,
# distinct_venues, impact_transfer_ratio, seconds_between_venue_trades, issuer_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"trader_name": "Elif Umberwhistle", "account_ref": "ACC001",
     "primary_instrument": "Falcon Ridge Commodities Ltd Ordinary Shares",
     "correlated_instrument": "Falcon Ridge Commodities Ltd Single-Stock Futures",
     "correlation_pct": 14, "distinct_venues": 1, "impact_transfer_ratio": 0.04,
     "seconds_between_venue_trades": 210, "issuer_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Marco Thistlebristle", "account_ref": "ACC002",
     "primary_instrument": "Highgate Commodities Ltd Ordinary Shares",
     "correlated_instrument": "Highgate Commodities Ltd Contract for Difference (CFD)",
     "correlation_pct": 18, "distinct_venues": 1, "impact_transfer_ratio": 0.06,
     "seconds_between_venue_trades": 95, "issuer_name": "Highgate Commodities Ltd"},
    {"trader_name": "Fatima Umberwisp", "account_ref": "ACC003",
     "primary_instrument": "Continental Correspondent Bank Ordinary Shares",
     "correlated_instrument": "Continental Correspondent Bank American Depositary Receipt (ADR)",
     "correlation_pct": 22, "distinct_venues": 1, "impact_transfer_ratio": 0.19,
     "seconds_between_venue_trades": 260, "issuer_name": "Continental Correspondent Bank"},
    {"trader_name": "Johan Yarrowkettle", "account_ref": "ACC004",
     "primary_instrument": "Northwind Freight Co Ordinary Shares",
     "correlated_instrument": "Northwind Freight Co Single-Stock Futures",
     "correlation_pct": 27, "distinct_venues": 2, "impact_transfer_ratio": 0.05,
     "seconds_between_venue_trades": 320, "issuer_name": "Northwind Freight Co"},
    {"trader_name": "Grace Flintthimble", "account_ref": "ACC005",
     "primary_instrument": "Ravenwood Trading Co Ordinary Shares",
     "correlated_instrument": "Ravenwood Trading Co Contract for Difference (CFD)",
     "correlation_pct": 52, "distinct_venues": 1, "impact_transfer_ratio": 0.07,
     "seconds_between_venue_trades": 180, "issuer_name": "Ravenwood Trading Co"},
    {"trader_name": "Liam Copperbutton", "account_ref": "ACC006",
     "primary_instrument": "Alpha Trading Ltd Ordinary Shares",
     "correlated_instrument": "Alpha Trading Ltd Exchange-Traded Options",
     "correlation_pct": 31, "distinct_venues": 1, "impact_transfer_ratio": 0.24,
     "seconds_between_venue_trades": 70, "issuer_name": "Alpha Trading Ltd"},
    {"trader_name": "Ana Ashquill", "account_ref": "ACC007",
     "primary_instrument": "Meridian Bulk Traders Ltd Ordinary Shares",
     "correlated_instrument": "Meridian Bulk Traders Ltd Single-Stock Futures",
     "correlation_pct": 58, "distinct_venues": 2, "impact_transfer_ratio": 0.08,
     "seconds_between_venue_trades": 240, "issuer_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Dimitri Brackencrumb", "account_ref": "ACC008",
     "primary_instrument": "Gammavane Imports Ltd Ordinary Shares",
     "correlated_instrument": "Gammavane Imports Ltd Total Return Swap",
     "correlation_pct": 47, "distinct_venues": 2, "impact_transfer_ratio": 0.15,
     "seconds_between_venue_trades": 175, "issuer_name": "Gammavane Imports Ltd"},
    {"trader_name": "Yuki Tallowwhistle", "account_ref": "ACC009",
     "primary_instrument": "Falcon Ridge Commodities Ltd Ordinary Shares",
     "correlated_instrument": "Falcon Ridge Commodities Ltd Contract for Difference (CFD)",
     "correlation_pct": 55, "distinct_venues": 2, "impact_transfer_ratio": 0.21,
     "seconds_between_venue_trades": 60, "issuer_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Isabela Wrenbutton", "account_ref": "ACC010",
     "primary_instrument": "Highgate Commodities Ltd Ordinary Shares",
     "correlated_instrument": "Highgate Commodities Ltd Single-Stock Futures",
     "correlation_pct": 61, "distinct_venues": 2, "impact_transfer_ratio": 0.44,
     "seconds_between_venue_trades": 300, "issuer_name": "Highgate Commodities Ltd"},
    {"trader_name": "Connor Kettletumble", "account_ref": "ACC011",
     "primary_instrument": "Alpha Trading Ltd Ordinary Shares",
     "correlated_instrument": "Alpha Trading Ltd American Depositary Receipt (ADR)",
     "correlation_pct": 75, "distinct_venues": 1, "impact_transfer_ratio": 0.26,
     "seconds_between_venue_trades": 100, "issuer_name": "Alpha Trading Ltd"},
    {"trader_name": "Mireille Puddlekettle", "account_ref": "ACC012",
     "primary_instrument": "Continental Correspondent Bank Ordinary Shares",
     "correlated_instrument": "Continental Correspondent Bank Cross-Listed Ordinary Shares",
     "correlation_pct": 50, "distinct_venues": 3, "impact_transfer_ratio": 0.18,
     "seconds_between_venue_trades": 350, "issuer_name": "Continental Correspondent Bank"},
    {"trader_name": "Pieter van der Berg", "account_ref": "ACC013",
     "primary_instrument": "Northwind Freight Co Ordinary Shares",
     "correlated_instrument": "Northwind Freight Co Single-Stock Futures",
     "correlation_pct": 91, "distinct_venues": 5, "impact_transfer_ratio": 0.05,
     "seconds_between_venue_trades": 220, "issuer_name": "Northwind Freight Co"},
    {"trader_name": "Astrid Umberbutton", "account_ref": "ACC014",
     "primary_instrument": "Ravenwood Trading Co Ordinary Shares",
     "correlated_instrument": "Ravenwood Trading Co Contract for Difference (CFD)",
     "correlation_pct": 94, "distinct_venues": 4, "impact_transfer_ratio": 0.20,
     "seconds_between_venue_trades": 190, "issuer_name": "Ravenwood Trading Co"},
    {"trader_name": "Rafael Quillspindle", "account_ref": "ACC015",
     "primary_instrument": "Meridian Bulk Traders Ltd Ordinary Shares",
     "correlated_instrument": "Meridian Bulk Traders Ltd Exchange-Traded Options",
     "correlation_pct": 80, "distinct_venues": 3, "impact_transfer_ratio": 0.48,
     "seconds_between_venue_trades": 85, "issuer_name": "Meridian Bulk Traders Ltd"},
    {"trader_name": "Chen Mossthimble", "account_ref": "ACC016",
     "primary_instrument": "Gammavane Imports Ltd Ordinary Shares",
     "correlated_instrument": "Gammavane Imports Ltd Total Return Swap",
     "correlation_pct": 89, "distinct_venues": 6, "impact_transfer_ratio": 0.27,
     "seconds_between_venue_trades": 160, "issuer_name": "Gammavane Imports Ltd"},
    {"trader_name": "Katarzyna Umbercrumb", "account_ref": "ACC017",
     "primary_instrument": "Falcon Ridge Commodities Ltd Ordinary Shares",
     "correlated_instrument": "Falcon Ridge Commodities Ltd Single-Stock Futures",
     "correlation_pct": 83, "distinct_venues": 4, "impact_transfer_ratio": 0.70,
     "seconds_between_venue_trades": 45, "issuer_name": "Falcon Ridge Commodities Ltd"},
    {"trader_name": "Sean Marrowspindle", "account_ref": "ACC018",
     "primary_instrument": "Highgate Commodities Ltd Ordinary Shares",
     "correlated_instrument": "Highgate Commodities Ltd American Depositary Receipt (ADR)",
     "correlation_pct": 92, "distinct_venues": 3, "impact_transfer_ratio": 0.55,
     "seconds_between_venue_trades": 110, "issuer_name": "Highgate Commodities Ltd"},
    {"trader_name": "Natasha Ivybristlea", "account_ref": "ACC019",
     "primary_instrument": "Zeta Commodities Ltd Ordinary Shares",
     "correlated_instrument": "Zeta Commodities Ltd Single-Stock Futures",
     "correlation_pct": 97, "distinct_venues": 6, "impact_transfer_ratio": 0.85,
     "seconds_between_venue_trades": 2, "issuer_name": "Zeta Commodities Ltd"},
    {"trader_name": "Omar Quillbristle", "account_ref": "ACC020",
     "primary_instrument": "Alpha Trading Ltd Ordinary Shares",
     "correlated_instrument": "Alpha Trading Ltd Total Return Swap",
     "correlation_pct": 90, "distinct_venues": 4, "impact_transfer_ratio": 0.66,
     "seconds_between_venue_trades": 15, "issuer_name": "Alpha Trading Ltd"},
    {"trader_name": "Freya Vellumspindle", "account_ref": "ACC021",
     "primary_instrument": "Continental Correspondent Bank Ordinary Shares",
     "correlated_instrument": "Continental Correspondent Bank Contract for Difference (CFD)",
     "correlation_pct": 78, "distinct_venues": 7, "impact_transfer_ratio": 0.72,
     "seconds_between_venue_trades": 3, "issuer_name": "Continental Correspondent Bank"},
    {"trader_name": "Tobias Kettlebristle", "account_ref": "ACC022",
     "primary_instrument": "Ravenwood Trading Co Ordinary Shares",
     "correlated_instrument": "Ravenwood Trading Co Exchange-Traded Options",
     "correlation_pct": 95, "distinct_venues": 4, "impact_transfer_ratio": 0.80,
     "seconds_between_venue_trades": 4, "issuer_name": "Ravenwood Trading Co"},
]

# issuer_name, account_ref, venue, jurisdiction, relationship, prior_alerts
INSTRUMENTS: List[Dict[str, Any]] = [
    {"issuer_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC001", "venue": "ICE Futures Europe",
     "jurisdiction": "United Kingdom", "relationship": "Single-stock futures", "prior_alerts": 0},
    {"issuer_name": "Highgate Commodities Ltd", "account_ref": "ACC002", "venue": "CMC Markets CFD Venue",
     "jurisdiction": "United Kingdom", "relationship": "Contract for Difference (CFD)", "prior_alerts": 0},
    {"issuer_name": "Continental Correspondent Bank", "account_ref": "ACC003", "venue": "NYSE Arca",
     "jurisdiction": "United States", "relationship": "American Depositary Receipt (ADR)", "prior_alerts": 0},
    {"issuer_name": "Northwind Freight Co", "account_ref": "ACC004", "venue": "Eurex",
     "jurisdiction": "Germany", "relationship": "Single-stock futures", "prior_alerts": 0},
    {"issuer_name": "Ravenwood Trading Co", "account_ref": "ACC005", "venue": "CMC Markets CFD Venue",
     "jurisdiction": "United Kingdom", "relationship": "Contract for Difference (CFD)", "prior_alerts": 1},
    {"issuer_name": "Alpha Trading Ltd", "account_ref": "ACC006", "venue": "Chicago Board Options Exchange",
     "jurisdiction": "United States", "relationship": "Exchange-traded options", "prior_alerts": 0},
    {"issuer_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC007", "venue": "Eurex",
     "jurisdiction": "Germany", "relationship": "Single-stock futures", "prior_alerts": 1},
    {"issuer_name": "Gammavane Imports Ltd", "account_ref": "ACC008", "venue": "Over-the-Counter Swap Venue",
     "jurisdiction": "Marshall Islands", "relationship": "Total return swap", "prior_alerts": 1},
    {"issuer_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC009", "venue": "CMC Markets CFD Venue",
     "jurisdiction": "United Kingdom", "relationship": "Contract for Difference (CFD)", "prior_alerts": 1},
    {"issuer_name": "Highgate Commodities Ltd", "account_ref": "ACC010", "venue": "ICE Futures Europe",
     "jurisdiction": "United Kingdom", "relationship": "Single-stock futures", "prior_alerts": 2},
    {"issuer_name": "Alpha Trading Ltd", "account_ref": "ACC011", "venue": "NYSE Arca",
     "jurisdiction": "United States", "relationship": "American Depositary Receipt (ADR)", "prior_alerts": 1},
    {"issuer_name": "Continental Correspondent Bank", "account_ref": "ACC012", "venue": "Euronext Paris",
     "jurisdiction": "France", "relationship": "Cross-listed ordinary shares", "prior_alerts": 1},
    {"issuer_name": "Northwind Freight Co", "account_ref": "ACC013", "venue": "Eurex",
     "jurisdiction": "Germany", "relationship": "Single-stock futures", "prior_alerts": 1},
    {"issuer_name": "Ravenwood Trading Co", "account_ref": "ACC014", "venue": "CMC Markets CFD Venue",
     "jurisdiction": "United Kingdom", "relationship": "Contract for Difference (CFD)", "prior_alerts": 2},
    {"issuer_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC015", "venue": "Chicago Board Options Exchange",
     "jurisdiction": "United States", "relationship": "Exchange-traded options", "prior_alerts": 2},
    {"issuer_name": "Gammavane Imports Ltd", "account_ref": "ACC016", "venue": "Over-the-Counter Swap Venue",
     "jurisdiction": "Marshall Islands", "relationship": "Total return swap", "prior_alerts": 2},
    {"issuer_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC017", "venue": "ICE Futures Europe",
     "jurisdiction": "United Kingdom", "relationship": "Single-stock futures", "prior_alerts": 2},
    {"issuer_name": "Highgate Commodities Ltd", "account_ref": "ACC018", "venue": "NYSE Arca",
     "jurisdiction": "United States", "relationship": "American Depositary Receipt (ADR)", "prior_alerts": 2},
    {"issuer_name": "Zeta Commodities Ltd", "account_ref": "ACC019", "venue": "ICE Futures Europe",
     "jurisdiction": "Cyprus", "relationship": "Single-stock futures", "prior_alerts": 3},
    {"issuer_name": "Alpha Trading Ltd", "account_ref": "ACC020", "venue": "Over-the-Counter Swap Venue",
     "jurisdiction": "United Kingdom", "relationship": "Total return swap", "prior_alerts": 3},
    {"issuer_name": "Continental Correspondent Bank", "account_ref": "ACC021", "venue": "CMC Markets CFD Venue",
     "jurisdiction": "Sweden", "relationship": "Contract for Difference (CFD)", "prior_alerts": 3},
    {"issuer_name": "Ravenwood Trading Co", "account_ref": "ACC022", "venue": "Chicago Board Options Exchange",
     "jurisdiction": "Germany", "relationship": "Exchange-traded options", "prior_alerts": 3},
]

_TABLES = {"trading_accounts.csv": ACCOUNTS, "instruments.csv": INSTRUMENTS}


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
