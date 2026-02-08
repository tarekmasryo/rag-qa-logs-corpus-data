#!/usr/bin/env python3
"""Sync docs/data_dictionary.csv and root data_dictionary.csv.

Usage:
    python scripts/update_dictionary.py

Policy:
- `data_dictionary.csv` is canonical for distribution (root).
- `docs/data_dictionary.csv` is a copy for docs browsing.
This script makes them identical.
"""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    root = Path("data_dictionary.csv")
    docs = Path("docs") / "data_dictionary.csv"

    if not root.exists():
        raise FileNotFoundError(root)
    docs.parent.mkdir(parents=True, exist_ok=True)
    docs.write_bytes(root.read_bytes())
    print("✅ Synced docs/data_dictionary.csv from root data_dictionary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
