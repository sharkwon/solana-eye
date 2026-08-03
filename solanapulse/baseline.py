"""Percentile baselines: where does the current value sit vs. its own history?

More interpretable than a raw z-score: "TPS is at the 92nd percentile of the
last 30 days" tells an operator exactly how unusual the current reading is.
Pure functions — no I/O.
"""

from __future__ import annotations

import statistics
from typing import Any, Optional


def percentile_rank(history_values: list[float], current: float) -> Optional[float]:
    """Fraction (0-100) of history values <= current. None if no history."""
    if not history_values:
        return None
    below = sum(1 for v in history_values if v <= current)
    return round(below / len(history_values) * 100.0, 1)


def _series_of(snapshot: dict[str, Any], path: list[str]) -> Optional[float]:
    node: Any = snapshot
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return float(node) if isinstance(node, (int, float)) else None


def compute_baselines(
    metrics: dict[str, Any], history: list[dict], cfg: dict[str, Any]
) -> dict[str, Any]:
    """Compute 30-day percentiles + medians for each configured series.

    cfg: {"series": [{"key", "path", "label", "higher_is_better"}]}
    history: list of snapshots, each {"ts":..., "metrics":{...}} (or bare metrics).
    """
    out: dict[str, Any] = {}
    for s in cfg.get("series", []):
        path = s["path"]
        key = s["key"]
        current = _series_of(metrics, path)
        if current is None:
            continue
        values = []
        for snap in history:
            node = snap.get("metrics") if "metrics" in snap else snap
            v = _series_of(node, path)
            if v is not None:
                values.append(v)
        if not values:
            continue
        out[key] = {
            "label": s.get("label", key),
            "current": round(current, 2),
            "median": round(statistics.median(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "percentile": percentile_rank(values, current),
            "higher_is_better": s.get("higher_is_better", True),
            "samples": len(values),
        }
    return out
