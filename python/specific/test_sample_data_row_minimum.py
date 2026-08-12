"""Forward standard: every typology ships >= 20 rows per sample-data component.

Real analytics are judged on volume as well as logic; a three-row sample can hide a
scoring bug that only a populated table surfaces, and it reads as a toy next to the
rest of the estate. So each sample-data CSV a typology ships must carry at least
MIN_ROWS data rows (header excluded).

The typologies that predate the standard would be GRANDFATHERED -- listed explicitly,
not detected -- so this guard does not retro-break them. Every OTHER typology under
python/specific/ is enforced automatically: add a new one with a thin table and this
test fails and names the file. Back a grandfathered typology's data up to the standard
and remove it from the set.

Every CM00N Capital Markets typology in this toolkit is NEW, so GRANDFATHERED starts
empty and must stay empty for CM001-CM010: each must pass the >= 20-row rule live, not
be exempted.
"""

from __future__ import annotations

import csv
from pathlib import Path

MIN_ROWS = 20

# Typologies authored before the 20-row standard. Enforced once backfilled.
# Empty for fc-07: every CM00N typology is new and must pass the standard live.
GRANDFATHERED: set = set()

_SPECIFIC = Path(__file__).resolve().parent


def _row_count(csv_path: Path) -> int:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    return max(len(rows) - 1, 0)  # minus the header


def test_new_typologies_ship_at_least_twenty_rows_per_component():
    violations = []
    for typology_dir in sorted(p for p in _SPECIFIC.iterdir() if p.is_dir()):
        name = typology_dir.name
        if name in GRANDFATHERED:
            continue
        sample_dir = typology_dir / "sample-data"
        if not sample_dir.is_dir():
            continue
        for csv_path in sorted(sample_dir.glob("*.csv")):
            count = _row_count(csv_path)
            if count < MIN_ROWS:
                violations.append(
                    "%s/%s has %d rows (< %d)" % (name, csv_path.name, count, MIN_ROWS)
                )
    assert not violations, (
        "Sample-data components below the %d-row standard for non-grandfathered "
        "typologies:\n  %s\nAdd rows to the generator, or grandfather the typology in "
        "GRANDFATHERED if it is a deliberate exception." % (MIN_ROWS, "\n  ".join(violations))
    )
