"""Generate synthetic sample data for CM001 Insider Trading.

22 trading accounts (>= the 20-row sample-data standard; CM001 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Viktor Sokolov, 90/Critical, the single highest-scoring account
in the set) trades ahead of a material non-public event at **Gamma Imports Ltd** -- an
entity already in the estate network -- with the position built and profit realised on
information from Marcus Webb, Gamma Imports Ltd's Head of Investor Relations, so
canonical entity resolution joins CM001 onto the existing fused case. Being the top-
scored account matters: the FC-10 adapter builds its case/graph from the single highest
exposure_score row, so the Gamma Imports Ltd bridge has to be that row, not merely A
Critical row.

Run:  python3 generate_cm001_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, desk, issuer_name, normal_average_position,
# pre_event_position_increase, days_before_event, contact_events_90d,
# position_value_at_entry, realized_pnl, information_source_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"trader_name": "Elena Marchetti", "account_ref": "ACC001", "desk": "Convertibles Desk",
     "issuer_name": "Falcon Ridge Commodities Ltd", "normal_average_position": 55000,
     "pre_event_position_increase": 3520, "days_before_event": 20, "contact_events_90d": 2,
     "position_value_at_entry": 1500000, "realized_pnl": 232500,
     "information_source_name": "Julia Costa (Sell-Side Research)"},
    {"trader_name": "Bjorn Kallstrom", "account_ref": "ACC002", "desk": "Special Situations Desk",
     "issuer_name": "Highgate Commodities Ltd", "normal_average_position": 50000,
     "pre_event_position_increase": 3800, "days_before_event": 11, "contact_events_90d": 2,
     "position_value_at_entry": 1500000, "realized_pnl": 528000,
     "information_source_name": "Anders Berg (Corporate Access Desk)"},
    {"trader_name": "Priya Chandrasekaran", "account_ref": "ACC003", "desk": "Equities Prop Desk",
     "issuer_name": "Continental Correspondent Bank", "normal_average_position": 60000,
     "pre_event_position_increase": 2160, "days_before_event": 10, "contact_events_90d": 4,
     "position_value_at_entry": 1800000, "realized_pnl": 318600,
     "information_source_name": "Anders Berg (Corporate Access Desk)"},
    {"trader_name": "Tomás Reyes", "account_ref": "ACC004", "desk": "Event-Driven Desk",
     "issuer_name": "Northwind Freight Co", "normal_average_position": 65000,
     "pre_event_position_increase": 5720, "days_before_event": 7, "contact_events_90d": 0,
     "position_value_at_entry": 2400000, "realized_pnl": 319200,
     "information_source_name": "Anders Berg (Corporate Access Desk)"},
    {"trader_name": "Wei Zhang", "account_ref": "ACC005", "desk": "Equities Prop Desk",
     "issuer_name": "Ravenwood Trading Co", "normal_average_position": 45000,
     "pre_event_position_increase": 5715, "days_before_event": 12, "contact_events_90d": 1,
     "position_value_at_entry": 3000000, "realized_pnl": 594000,
     "information_source_name": "Helena Voss (Independent Consultant)"},
    {"trader_name": "Aoife Byrne", "account_ref": "ACC006", "desk": "Event-Driven Desk",
     "issuer_name": "Alpha Trading Ltd", "normal_average_position": 45000,
     "pre_event_position_increase": 2565, "days_before_event": 14, "contact_events_90d": 3,
     "position_value_at_entry": 2700000, "realized_pnl": 926100,
     "information_source_name": "Karim Idris (Prime Brokerage Contact)"},
    {"trader_name": "Sven Lindberg", "account_ref": "ACC007", "desk": "Equity Derivatives Desk",
     "issuer_name": "Northwind Freight Co", "normal_average_position": 50000,
     "pre_event_position_increase": 10250, "days_before_event": 5, "contact_events_90d": 0,
     "position_value_at_entry": 2700000, "realized_pnl": 321300,
     "information_source_name": "Nils Petterson (Investor Relations Contact)"},
    {"trader_name": "Camille Dubois", "account_ref": "ACC008", "desk": "Event-Driven Desk",
     "issuer_name": "Alpha Trading Ltd", "normal_average_position": 50000,
     "pre_event_position_increase": 12750, "days_before_event": 4, "contact_events_90d": 3,
     "position_value_at_entry": 2100000, "realized_pnl": 363300,
     "information_source_name": "Sofia Lindqvist (Gamma Imports Ltd, Finance Director)"},
    {"trader_name": "Kenji Watanabe", "account_ref": "ACC009", "desk": "Convertibles Desk",
     "issuer_name": "Meridian Bulk Traders Ltd", "normal_average_position": 55000,
     "pre_event_position_increase": 14630, "days_before_event": 6, "contact_events_90d": 3,
     "position_value_at_entry": 2700000, "realized_pnl": 1055700,
     "information_source_name": "Helena Voss (Independent Consultant)"},
    {"trader_name": "Nadia Farouk", "account_ref": "ACC010", "desk": "Special Situations Desk",
     "issuer_name": "Meridian Bulk Traders Ltd", "normal_average_position": 55000,
     "pre_event_position_increase": 7810, "days_before_event": 6, "contact_events_90d": 9,
     "position_value_at_entry": 1800000, "realized_pnl": 333000,
     "information_source_name": "Ruben Almeida (Legal Counsel, Gamma Imports Ltd)"},
    {"trader_name": "Lucas Ferreira", "account_ref": "ACC011", "desk": "Convertibles Desk",
     "issuer_name": "Alpha Trading Ltd", "normal_average_position": 45000,
     "pre_event_position_increase": 15480, "days_before_event": 9, "contact_events_90d": 3,
     "position_value_at_entry": 3000000, "realized_pnl": 918000,
     "information_source_name": "Marcus Webb (Gamma Imports Ltd, Head of IR)"},
    {"trader_name": "Ingrid Solberg", "account_ref": "ACC012", "desk": "Equities Prop Desk",
     "issuer_name": "Alpha Trading Ltd", "normal_average_position": 60000,
     "pre_event_position_increase": 10860, "days_before_event": 3, "contact_events_90d": 5,
     "position_value_at_entry": 3000000, "realized_pnl": 264000,
     "information_source_name": "Helena Voss (Independent Consultant)"},
    {"trader_name": "Rashid Al-Mansoori", "account_ref": "ACC013", "desk": "Equities Prop Desk",
     "issuer_name": "Falcon Ridge Commodities Ltd", "normal_average_position": 45000,
     "pre_event_position_increase": 39330, "days_before_event": 1, "contact_events_90d": 0,
     "position_value_at_entry": 2100000, "realized_pnl": 197400,
     "information_source_name": "Karim Idris (Prime Brokerage Contact)"},
    {"trader_name": "Beatrix Hofmann", "account_ref": "ACC014", "desk": "Equity Derivatives Desk",
     "issuer_name": "Northwind Freight Co", "normal_average_position": 65000,
     "pre_event_position_increase": 51220, "days_before_event": 2, "contact_events_90d": 5,
     "position_value_at_entry": 2400000, "realized_pnl": 228000,
     "information_source_name": "Karim Idris (Prime Brokerage Contact)"},
    {"trader_name": "Diego Alvarez", "account_ref": "ACC015", "desk": "Equities Prop Desk",
     "issuer_name": "Highgate Commodities Ltd", "normal_average_position": 55000,
     "pre_event_position_increase": 22935, "days_before_event": 2, "contact_events_90d": 6,
     "position_value_at_entry": 1200000, "realized_pnl": 458400,
     "information_source_name": "Helena Voss (Independent Consultant)"},
    {"trader_name": "Mei-Ling Tan", "account_ref": "ACC016", "desk": "Convertibles Desk",
     "issuer_name": "Alpha Trading Ltd", "normal_average_position": 40000,
     "pre_event_position_increase": 27960, "days_before_event": 0, "contact_events_90d": 5,
     "position_value_at_entry": 2700000, "realized_pnl": 518400,
     "information_source_name": "Karim Idris (Prime Brokerage Contact)"},
    {"trader_name": "Oskar Nowak", "account_ref": "ACC017", "desk": "Equity Derivatives Desk",
     "issuer_name": "Ravenwood Trading Co", "normal_average_position": 60000,
     "pre_event_position_increase": 21180, "days_before_event": 3, "contact_events_90d": 14,
     "position_value_at_entry": 3000000, "realized_pnl": 924000,
     "information_source_name": "Sofia Lindqvist (Gamma Imports Ltd, Finance Director)"},
    {"trader_name": "Layla Haddad", "account_ref": "ACC018", "desk": "Event-Driven Desk",
     "issuer_name": "Continental Correspondent Bank", "normal_average_position": 65000,
     "pre_event_position_increase": 60255, "days_before_event": 2, "contact_events_90d": 8,
     "position_value_at_entry": 2700000, "realized_pnl": 939600,
     "information_source_name": "Ruben Almeida (Legal Counsel, Gamma Imports Ltd)"},
    {"trader_name": "Viktor Sokolov", "account_ref": "ACC019", "desk": "Special Situations Desk",
     "issuer_name": "Gamma Imports Ltd", "normal_average_position": 60000,
     "pre_event_position_increase": 39600, "days_before_event": 0, "contact_events_90d": 10,
     "position_value_at_entry": 2400000, "realized_pnl": 2090400,
     "information_source_name": "Marcus Webb (Gamma Imports Ltd, Head of IR)"},
    {"trader_name": "Charlotte Whitfield", "account_ref": "ACC020", "desk": "Equities Prop Desk",
     "issuer_name": "Zeta Commodities Ltd", "normal_average_position": 40000,
     "pre_event_position_increase": 32560, "days_before_event": 2, "contact_events_90d": 10,
     "position_value_at_entry": 1500000, "realized_pnl": 1038000,
     "information_source_name": "Nils Petterson (Investor Relations Contact)"},
    {"trader_name": "Amara Nwosu", "account_ref": "ACC021", "desk": "Special Situations Desk",
     "issuer_name": "Continental Correspondent Bank", "normal_average_position": 45000,
     "pre_event_position_increase": 15210, "days_before_event": 0, "contact_events_90d": 12,
     "position_value_at_entry": 2400000, "realized_pnl": 2208000,
     "information_source_name": "Sofia Lindqvist (Gamma Imports Ltd, Finance Director)"},
    {"trader_name": "Hiroshi Sato", "account_ref": "ACC022", "desk": "Event-Driven Desk",
     "issuer_name": "Ravenwood Trading Co", "normal_average_position": 65000,
     "pre_event_position_increase": 57135, "days_before_event": 3, "contact_events_90d": 11,
     "position_value_at_entry": 2100000, "realized_pnl": 1751400,
     "information_source_name": "Marcus Webb (Gamma Imports Ltd, Head of IR)"},
]

# information_source_name, account_ref, role, employer, jurisdiction, relationship, prior_alerts
INFORMATION_SOURCES: List[Dict[str, Any]] = [
    {"information_source_name": "Julia Costa (Sell-Side Research)", "account_ref": "ACC001", "role": "Sell-Side Analyst",
     "employer": "Meridian Trust Bank Research", "jurisdiction": "United Kingdom", "relationship": "Research contact", "prior_alerts": 0},
    {"information_source_name": "Anders Berg (Corporate Access Desk)", "account_ref": "ACC002", "role": "Corporate Access",
     "employer": "Continental Correspondent Bank", "jurisdiction": "Sweden", "relationship": "Corporate access desk", "prior_alerts": 0},
    {"information_source_name": "Anders Berg (Corporate Access Desk)", "account_ref": "ACC003", "role": "Corporate Access",
     "employer": "Continental Correspondent Bank", "jurisdiction": "Sweden", "relationship": "Corporate access desk", "prior_alerts": 0},
    {"information_source_name": "Anders Berg (Corporate Access Desk)", "account_ref": "ACC004", "role": "Corporate Access",
     "employer": "Continental Correspondent Bank", "jurisdiction": "Sweden", "relationship": "Corporate access desk", "prior_alerts": 1},
    {"information_source_name": "Helena Voss (Independent Consultant)", "account_ref": "ACC005", "role": "Independent Consultant",
     "employer": "Voss Advisory", "jurisdiction": "Switzerland", "relationship": "Consulting retainer", "prior_alerts": 0},
    {"information_source_name": "Karim Idris (Prime Brokerage Contact)", "account_ref": "ACC006", "role": "Prime Brokerage",
     "employer": "Pacific Rim Commercial Bank", "jurisdiction": "Hong Kong", "relationship": "Prime brokerage contact", "prior_alerts": 0},
    {"information_source_name": "Nils Petterson (Investor Relations Contact)", "account_ref": "ACC007", "role": "Investor Relations",
     "employer": "Northwind Freight Co", "jurisdiction": "Germany", "relationship": "IR contact", "prior_alerts": 0},
    {"information_source_name": "Sofia Lindqvist (Gamma Imports Ltd, Finance Director)", "account_ref": "ACC008", "role": "Finance Director",
     "employer": "Gamma Imports Ltd", "jurisdiction": "Marshall Islands", "relationship": "Corporate insider", "prior_alerts": 1},
    {"information_source_name": "Helena Voss (Independent Consultant)", "account_ref": "ACC009", "role": "Independent Consultant",
     "employer": "Voss Advisory", "jurisdiction": "Switzerland", "relationship": "Consulting retainer", "prior_alerts": 1},
    {"information_source_name": "Ruben Almeida (Legal Counsel, Gamma Imports Ltd)", "account_ref": "ACC010", "role": "Legal Counsel",
     "employer": "Gamma Imports Ltd", "jurisdiction": "Marshall Islands", "relationship": "Corporate insider", "prior_alerts": 1},
    {"information_source_name": "Marcus Webb (Gamma Imports Ltd, Head of IR)", "account_ref": "ACC011", "role": "Head of Investor Relations",
     "employer": "Gamma Imports Ltd", "jurisdiction": "Marshall Islands", "relationship": "Corporate insider", "prior_alerts": 1},
    {"information_source_name": "Helena Voss (Independent Consultant)", "account_ref": "ACC012", "role": "Independent Consultant",
     "employer": "Voss Advisory", "jurisdiction": "Switzerland", "relationship": "Consulting retainer", "prior_alerts": 2},
    {"information_source_name": "Karim Idris (Prime Brokerage Contact)", "account_ref": "ACC013", "role": "Prime Brokerage",
     "employer": "Pacific Rim Commercial Bank", "jurisdiction": "Hong Kong", "relationship": "Prime brokerage contact", "prior_alerts": 1},
    {"information_source_name": "Karim Idris (Prime Brokerage Contact)", "account_ref": "ACC014", "role": "Prime Brokerage",
     "employer": "Pacific Rim Commercial Bank", "jurisdiction": "Hong Kong", "relationship": "Prime brokerage contact", "prior_alerts": 2},
    {"information_source_name": "Helena Voss (Independent Consultant)", "account_ref": "ACC015", "role": "Independent Consultant",
     "employer": "Voss Advisory", "jurisdiction": "Switzerland", "relationship": "Consulting retainer", "prior_alerts": 2},
    {"information_source_name": "Karim Idris (Prime Brokerage Contact)", "account_ref": "ACC016", "role": "Prime Brokerage",
     "employer": "Pacific Rim Commercial Bank", "jurisdiction": "Hong Kong", "relationship": "Prime brokerage contact", "prior_alerts": 2},
    {"information_source_name": "Sofia Lindqvist (Gamma Imports Ltd, Finance Director)", "account_ref": "ACC017", "role": "Finance Director",
     "employer": "Gamma Imports Ltd", "jurisdiction": "Marshall Islands", "relationship": "Corporate insider", "prior_alerts": 2},
    {"information_source_name": "Ruben Almeida (Legal Counsel, Gamma Imports Ltd)", "account_ref": "ACC018", "role": "Legal Counsel",
     "employer": "Gamma Imports Ltd", "jurisdiction": "Marshall Islands", "relationship": "Corporate insider", "prior_alerts": 2},
    {"information_source_name": "Marcus Webb (Gamma Imports Ltd, Head of IR)", "account_ref": "ACC019", "role": "Head of Investor Relations",
     "employer": "Gamma Imports Ltd", "jurisdiction": "Marshall Islands", "relationship": "Corporate insider", "prior_alerts": 3},
    {"information_source_name": "Nils Petterson (Investor Relations Contact)", "account_ref": "ACC020", "role": "Investor Relations",
     "employer": "Zeta Commodities Ltd", "jurisdiction": "Cyprus", "relationship": "IR contact", "prior_alerts": 3},
    {"information_source_name": "Sofia Lindqvist (Gamma Imports Ltd, Finance Director)", "account_ref": "ACC021", "role": "Finance Director",
     "employer": "Gamma Imports Ltd", "jurisdiction": "Marshall Islands", "relationship": "Corporate insider", "prior_alerts": 3},
    {"information_source_name": "Marcus Webb (Gamma Imports Ltd, Head of IR)", "account_ref": "ACC022", "role": "Head of Investor Relations",
     "employer": "Gamma Imports Ltd", "jurisdiction": "Marshall Islands", "relationship": "Corporate insider", "prior_alerts": 3},
]

_TABLES = {"trading_accounts.csv": ACCOUNTS, "information_sources.csv": INFORMATION_SOURCES}


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
