"""Snapshot persistence.

- outputs/latest.json   : most recent full snapshot (metrics + trimmed raw)
- outputs/history.jsonl : append-only history of metric series (for z-scores
                          and sparklines), one JSON object per line
"""

from __future__ import annotations

import json
import os
import time
from typing import Any


def load_history(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def append_snapshot(path: str, snapshot: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot) + "\n")


def trim_history(path: str, keep_days: int) -> None:
    """Drop history lines older than keep_days (best effort, keeps newest)."""
    cutoff = time.time() - keep_days * 86400
    rows = load_history(path)
    kept = [r for r in rows if r.get("ts", 0) >= cutoff]
    if len(kept) != len(rows):
        with open(path, "w", encoding="utf-8") as f:
            for r in kept:
                f.write(json.dumps(r) + "\n")


def write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
