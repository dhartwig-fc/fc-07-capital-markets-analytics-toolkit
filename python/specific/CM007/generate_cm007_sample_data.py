"""Generate synthetic sample data for CM007 Pump and Dump.

22 trading accounts (>= the 20-row sample-data standard; CM007 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (33-46)
  ACC013-ACC018   High      (60-72)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Desmond Clarke, 90/Critical, the single highest-scoring account
in the set) accumulates and pumps Corvus Aerospace Inc, a thinly-traded micro-cap, on
promotion run by **John Smith** -- the network's PEP, carried on the shared local id
P001 -- so canonical entity resolution joins CM007 onto the existing fused case via the
promoter, not the instrument (persons never name-merge under canonical resolution the
same way companies do; the stable id is what carries the bridge). Being the top-scored
account matters: the FC-10 adapter builds its case/graph from the single highest
exposure_score row, so the John Smith / P001 bridge has to be that row, not merely A
Critical row.

Run:  python3 generate_cm007_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# trader_name, account_ref, instrument, pct_of_float_accumulated,
# coordinated_posts_count, price_peak, price_baseline, volume_sold_to_retail,
# total_position, promoter_name, promoter_id
ACCOUNTS: List[Dict[str, Any]] = [
    {"trader_name": "Isabelle Laurent", "account_ref": "ACC001", "instrument": "Solstice Biotech Corp",
     "pct_of_float_accumulated": 4, "coordinated_posts_count": 1, "price_peak": 2.59, "price_baseline": 2.40,
     "volume_sold_to_retail": 20000, "total_position": 200000,
     "promoter_name": "Renata Cruz", "promoter_id": "PR002"},
    {"trader_name": "Magnus Eriksson", "account_ref": "ACC002", "instrument": "Kestrel Nano Materials Inc",
     "pct_of_float_accumulated": 6, "coordinated_posts_count": 2, "price_peak": 3.57, "price_baseline": 3.10,
     "volume_sold_to_retail": 82500, "total_position": 250000,
     "promoter_name": "Felix Brandt", "promoter_id": "PR003"},
    {"trader_name": "Fatima Al-Sayed", "account_ref": "ACC003", "instrument": "Vantage Rare Earth Corp",
     "pct_of_float_accumulated": 3, "coordinated_posts_count": 0, "price_peak": 2.61, "price_baseline": 1.80,
     "volume_sold_to_retail": 24000, "total_position": 300000,
     "promoter_name": "Amara Okafor", "promoter_id": "PR004"},
    {"trader_name": "Connor O'Brien", "account_ref": "ACC004", "instrument": "Pinnacle Graphene Ltd",
     "pct_of_float_accumulated": 7, "coordinated_posts_count": 4, "price_peak": 4.70, "price_baseline": 4.20,
     "volume_sold_to_retail": 27000, "total_position": 180000,
     "promoter_name": "Liu Wei", "promoter_id": "PR005"},
    {"trader_name": "Yuki Tanaka", "account_ref": "ACC005", "instrument": "Auric Mining Ventures Inc",
     "pct_of_float_accumulated": 18, "coordinated_posts_count": 1, "price_peak": 6.00, "price_baseline": 5.00,
     "volume_sold_to_retail": 26400, "total_position": 220000,
     "promoter_name": "Sofia Kowalska", "promoter_id": "PR006"},
    {"trader_name": "Dimitri Volkov", "account_ref": "ACC006", "instrument": "Cobalt Frontier Resources Inc",
     "pct_of_float_accumulated": 5, "coordinated_posts_count": 2, "price_peak": 3.20, "price_baseline": 2.00,
     "volume_sold_to_retail": 104000, "total_position": 260000,
     "promoter_name": "Trevor Nkosi", "promoter_id": "PR007"},
    {"trader_name": "Ana Beatriz Souza", "account_ref": "ACC007", "instrument": "Nimbus Cloud Robotics Inc",
     "pct_of_float_accumulated": 20, "coordinated_posts_count": 3, "price_peak": 4.13, "price_baseline": 3.50,
     "volume_sold_to_retail": 36000, "total_position": 200000,
     "promoter_name": "Elif Kaya", "promoter_id": "PR008"},
    {"trader_name": "Piotr Nowicki", "account_ref": "ACC008", "instrument": "Vertex Quantum Systems Inc",
     "pct_of_float_accumulated": 15, "coordinated_posts_count": 5, "price_peak": 3.90, "price_baseline": 2.60,
     "volume_sold_to_retail": 21600, "total_position": 240000,
     "promoter_name": "Bastian Hoffmann", "promoter_id": "PR009"},
    {"trader_name": "Leila Haidari", "account_ref": "ACC009", "instrument": "Halcyon Biosciences Corp",
     "pct_of_float_accumulated": 22, "coordinated_posts_count": 4, "price_peak": 4.95, "price_baseline": 3.00,
     "volume_sold_to_retail": 98000, "total_position": 280000,
     "promoter_name": "Priya Nair", "promoter_id": "PR010"},
    {"trader_name": "Callum Reid", "account_ref": "ACC010", "instrument": "Ironclad Defense Tech Inc",
     "pct_of_float_accumulated": 16, "coordinated_posts_count": 3, "price_peak": 4.62, "price_baseline": 2.10,
     "volume_sold_to_retail": 29400, "total_position": 210000,
     "promoter_name": "Aleksander Novak", "promoter_id": "PR011"},
    {"trader_name": "Sanjay Mehta", "account_ref": "ACC011", "instrument": "Lumina Solar Dynamics Inc",
     "pct_of_float_accumulated": 32, "coordinated_posts_count": 2, "price_peak": 6.20, "price_baseline": 4.00,
     "volume_sold_to_retail": 90000, "total_position": 300000,
     "promoter_name": "Camila Torres", "promoter_id": "PR012"},
    {"trader_name": "Greta Lindqvist", "account_ref": "ACC012", "instrument": "Cascade Hydrogen Corp",
     "pct_of_float_accumulated": 19, "coordinated_posts_count": 7, "price_peak": 3.23, "price_baseline": 1.90,
     "volume_sold_to_retail": 18200, "total_position": 260000,
     "promoter_name": "Ravi Shankar", "promoter_id": "PR013"},
    {"trader_name": "Marco Rinaldi", "account_ref": "ACC013", "instrument": "Emberstone Mining Ltd",
     "pct_of_float_accumulated": 52, "coordinated_posts_count": 11, "price_peak": 2.42, "price_baseline": 2.20,
     "volume_sold_to_retail": 18000, "total_position": 300000,
     "promoter_name": "Ingrid Johansson", "promoter_id": "PR014"},
    {"trader_name": "Chioma Eze", "account_ref": "ACC014", "instrument": "Sable Peak Resources Inc",
     "pct_of_float_accumulated": 55, "coordinated_posts_count": 8, "price_peak": 2.24, "price_baseline": 1.60,
     "volume_sold_to_retail": 29700, "total_position": 270000,
     "promoter_name": "Kwame Boateng", "promoter_id": "PR015"},
    {"trader_name": "Hendrik van der Berg", "account_ref": "ACC015", "instrument": "Tundra Wave Energy Inc",
     "pct_of_float_accumulated": 36, "coordinated_posts_count": 9, "price_peak": 3.12, "price_baseline": 1.30,
     "volume_sold_to_retail": 95000, "total_position": 250000,
     "promoter_name": "Yasmin El-Sayed", "promoter_id": "PR016"},
    {"trader_name": "Soo-jin Park", "account_ref": "ACC016", "instrument": "Zenith Micro Devices Inc",
     "pct_of_float_accumulated": 60, "coordinated_posts_count": 13, "price_peak": 4.42, "price_baseline": 2.80,
     "volume_sold_to_retail": 46400, "total_position": 290000,
     "promoter_name": "Dmitri Ivanov", "promoter_id": "PR017"},
    {"trader_name": "Alistair Cunningham", "account_ref": "ACC017", "instrument": "Obsidian Data Systems Inc",
     "pct_of_float_accumulated": 40, "coordinated_posts_count": 6, "price_peak": 3.96, "price_baseline": 1.10,
     "volume_sold_to_retail": 130200, "total_position": 310000,
     "promoter_name": "Chiara Bianchi", "promoter_id": "PR018"},
    {"trader_name": "Valentina Moreno", "account_ref": "ACC018", "instrument": "Wraith Cyber Security Inc",
     "pct_of_float_accumulated": 64, "coordinated_posts_count": 9, "price_peak": 3.90, "price_baseline": 1.50,
     "volume_sold_to_retail": 140800, "total_position": 320000,
     "promoter_name": "Hiroshi Endo", "promoter_id": "PR019"},
    {"trader_name": "Desmond Clarke", "account_ref": "ACC019", "instrument": "Corvus Aerospace Inc",
     "pct_of_float_accumulated": 68, "coordinated_posts_count": 14, "price_peak": 3.57, "price_baseline": 0.85,
     "volume_sold_to_retail": 315000, "total_position": 350000,
     "promoter_name": "John Smith", "promoter_id": "P001"},
    {"trader_name": "Ingrid Halvorsen", "account_ref": "ACC020", "instrument": "Aetherium Battery Corp",
     "pct_of_float_accumulated": 50, "coordinated_posts_count": 7, "price_peak": 3.30, "price_baseline": 1.00,
     "volume_sold_to_retail": 168000, "total_position": 280000,
     "promoter_name": "Freya Lindgren", "promoter_id": "PR020"},
    {"trader_name": "Tariq Farouk", "account_ref": "ACC021", "instrument": "Driftwood Timber Holdings Inc",
     "pct_of_float_accumulated": 30, "coordinated_posts_count": 12, "price_peak": 4.05, "price_baseline": 0.90,
     "volume_sold_to_retail": 255000, "total_position": 300000,
     "promoter_name": "Omar Haddad", "promoter_id": "PR021"},
    {"trader_name": "Naomi Osei", "account_ref": "ACC022", "instrument": "Palladian Robotics Inc",
     "pct_of_float_accumulated": 58, "coordinated_posts_count": 8, "price_peak": 4.56, "price_baseline": 1.20,
     "volume_sold_to_retail": 290400, "total_position": 330000,
     "promoter_name": "Bianca Silva", "promoter_id": "PR022"},
]

# promoter_name, promoter_id, account_ref, channel, jurisdiction, prior_alerts
PROMOTERS: List[Dict[str, Any]] = [
    {"promoter_name": "Renata Cruz", "promoter_id": "PR002", "account_ref": "ACC001",
     "channel": "Telegram Channel", "jurisdiction": "Brazil", "prior_alerts": 0},
    {"promoter_name": "Felix Brandt", "promoter_id": "PR003", "account_ref": "ACC002",
     "channel": "Discord Server", "jurisdiction": "Germany", "prior_alerts": 0},
    {"promoter_name": "Amara Okafor", "promoter_id": "PR004", "account_ref": "ACC003",
     "channel": "X (Twitter) Group", "jurisdiction": "Nigeria", "prior_alerts": 0},
    {"promoter_name": "Liu Wei", "promoter_id": "PR005", "account_ref": "ACC004",
     "channel": "WeChat Group", "jurisdiction": "China", "prior_alerts": 0},
    {"promoter_name": "Sofia Kowalska", "promoter_id": "PR006", "account_ref": "ACC005",
     "channel": "Stock Forum Thread", "jurisdiction": "Poland", "prior_alerts": 0},
    {"promoter_name": "Trevor Nkosi", "promoter_id": "PR007", "account_ref": "ACC006",
     "channel": "YouTube Channel", "jurisdiction": "South Africa", "prior_alerts": 0},
    {"promoter_name": "Elif Kaya", "promoter_id": "PR008", "account_ref": "ACC007",
     "channel": "WhatsApp Broadcast", "jurisdiction": "Turkey", "prior_alerts": 1},
    {"promoter_name": "Bastian Hoffmann", "promoter_id": "PR009", "account_ref": "ACC008",
     "channel": "Investment Newsletter", "jurisdiction": "Germany", "prior_alerts": 1},
    {"promoter_name": "Priya Nair", "promoter_id": "PR010", "account_ref": "ACC009",
     "channel": "Reddit Community", "jurisdiction": "India", "prior_alerts": 1},
    {"promoter_name": "Aleksander Novak", "promoter_id": "PR011", "account_ref": "ACC010",
     "channel": "Telegram Channel", "jurisdiction": "Slovenia", "prior_alerts": 1},
    {"promoter_name": "Camila Torres", "promoter_id": "PR012", "account_ref": "ACC011",
     "channel": "Discord Server", "jurisdiction": "Chile", "prior_alerts": 1},
    {"promoter_name": "Ravi Shankar", "promoter_id": "PR013", "account_ref": "ACC012",
     "channel": "X (Twitter) Group", "jurisdiction": "India", "prior_alerts": 1},
    {"promoter_name": "Ingrid Johansson", "promoter_id": "PR014", "account_ref": "ACC013",
     "channel": "Facebook Group", "jurisdiction": "Sweden", "prior_alerts": 2},
    {"promoter_name": "Kwame Boateng", "promoter_id": "PR015", "account_ref": "ACC014",
     "channel": "Signal Broadcast Group", "jurisdiction": "Ghana", "prior_alerts": 2},
    {"promoter_name": "Yasmin El-Sayed", "promoter_id": "PR016", "account_ref": "ACC015",
     "channel": "Telegram Channel", "jurisdiction": "Egypt", "prior_alerts": 2},
    {"promoter_name": "Dmitri Ivanov", "promoter_id": "PR017", "account_ref": "ACC016",
     "channel": "Investment Newsletter", "jurisdiction": "Cyprus", "prior_alerts": 2},
    {"promoter_name": "Chiara Bianchi", "promoter_id": "PR018", "account_ref": "ACC017",
     "channel": "Stock Forum Thread", "jurisdiction": "Italy", "prior_alerts": 2},
    {"promoter_name": "Hiroshi Endo", "promoter_id": "PR019", "account_ref": "ACC018",
     "channel": "YouTube Channel", "jurisdiction": "Japan", "prior_alerts": 2},
    {"promoter_name": "John Smith", "promoter_id": "P001", "account_ref": "ACC019",
     "channel": "Telegram Channel", "jurisdiction": "Cyprus", "prior_alerts": 3},
    {"promoter_name": "Freya Lindgren", "promoter_id": "PR020", "account_ref": "ACC020",
     "channel": "Discord Server", "jurisdiction": "Sweden", "prior_alerts": 3},
    {"promoter_name": "Omar Haddad", "promoter_id": "PR021", "account_ref": "ACC021",
     "channel": "WhatsApp Broadcast", "jurisdiction": "Lebanon", "prior_alerts": 3},
    {"promoter_name": "Bianca Silva", "promoter_id": "PR022", "account_ref": "ACC022",
     "channel": "X (Twitter) Group", "jurisdiction": "Portugal", "prior_alerts": 3},
]

_TABLES = {"trading_accounts.csv": ACCOUNTS, "promoters.csv": PROMOTERS}


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
