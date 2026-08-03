"""Optional Dune Analytics integration (requires DUNE_API_KEY).

DeFiLlama covers the core on-chain metrics keylessly; Dune is an optional
bolt-on for dashboards the sponsor specifically cares about (e.g. REV,
daily active addresses, tokenized equities). Set `sources.dune.enabled=true`
in config.json and export DUNE_API_KEY to activate.

The free Dune API tier is limited to a couple of curated queries; the
official Python SDK is NOT a dependency — we call the REST API directly.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from .. import http

API = "https://api.dune.com/api/v1"


def fetch_dashboards(dashboard_ids: list[str]) -> Optional[dict]:
    """Fetch the latest results for each configured dashboard (best effort)."""
    key = os.environ.get("DUNE_API_KEY")
    if not key:
        raise RuntimeError("DUNE_API_KEY not set")
    out: dict[str, Any] = {}
    for did in dashboard_ids:
        url = f"{API}/query/{did}/results?limit=100"
        data = http.request_json(url, headers={"X-DUNE-API-KEY": key}, max_retries=1)
        out[did] = data
    return out
