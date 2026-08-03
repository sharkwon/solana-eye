"""Assemble the unified report object (source of truth for all outputs)."""

from __future__ import annotations

import time
from typing import Any


def build_report(
    metrics: dict[str, Any],
    anomalies: list[dict],
    history: list[dict],
    cfg: dict[str, Any],
    collected_at: float | None = None,
) -> dict[str, Any]:
    """Combine everything into one machine-readable report dict.

    This dict is what gets dumped to latest.json, and is the input for both
    the Markdown and HTML renderers — one source of truth, three outputs.
    """
    return {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(collected_at or time.time())),
        "generated_at_ts": int(collected_at or time.time()),
        "config": {
            "refresh_interval_min": (cfg.get("render") or {}).get("refresh_interval_min"),
            "rpc_url": (cfg.get("rpc") or {}).get("url"),
        },
        "network": {
            "health": metrics.get("health"),
            "tps": metrics.get("tps"),
            "non_vote_tps": metrics.get("non_vote_tps"),
            "slot_time_sec": metrics.get("slot_time_sec"),
            "epoch": metrics.get("epoch"),
            "slot": metrics.get("slot"),
            "block_height": metrics.get("block_height"),
            "supply": metrics.get("supply"),
        },
        "validators": metrics.get("validators"),
        "fees": metrics.get("fees"),
        "economics": metrics.get("economics"),
        "news": {"simd": metrics.get("simd") or []},
        "status_page": metrics.get("status_page"),
        "anomalies": anomalies,
        "history": history[-24:],  # last 24 snapshots for sparklines
        "sources_ok": metrics.get("sources_ok") or {},
    }
