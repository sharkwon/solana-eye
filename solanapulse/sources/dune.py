"""Optional Dune Analytics integration (requires DUNE_API_KEY).

DeFiLlama covers the core on-chain metrics keylessly; Dune is an optional
bolt-on for dashboards the sponsor specifically cares about: daily active
addresses (DAU) and tokenized equities volume on Solana.

Set `sources.dune.enabled=true` in config.json, list query ids under
`sources.dune.queries`, and export DUNE_API_KEY to activate. Every metric
degrades gracefully when the key is missing, a query id is invalid, or the
Dune API is unreachable — the rest of the report is unaffected.

We call the REST API directly (stdlib only); the official SDK is NOT a
dependency. We read the "latest results" endpoint (cached executions) so a
run never consumes Dune credits.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from .. import http

API = "https://api.dune.com/api/v1"

# Canonical query ids (overridable via config `sources.dune.queries`):
#   dau                — Solana Daily Active Addresses
#   tokenized_volume   — Tokenized equities 30d volume (xStocks, stocks only)
#   tokenized_aum      — Tokenized equities total TVL/AUM (xStocks + Ondo GM)
#   tokenized_holders  — Tokenized equities unique holders (cross-chain aggregate)
DEFAULT_QUERIES: dict[str, int] = {
    "dau": 5941260,
    "tokenized_volume": 7750330,
    "tokenized_aum": 7750327,
    "tokenized_holders": 7750444,
}


def _api_key() -> Optional[str]:
    return os.environ.get("DUNE_API_KEY") or None


def _fetch_latest_result(query_id: int, timeout: int = 15) -> Optional[list[dict]]:
    """Fetch the latest cached execution for a query id (best effort).

    Returns the result rows, or None on any failure. Never raises.
    """
    key = _api_key()
    if not key or not query_id:
        return None
    url = f"{API}/query/{query_id}/results?limit=100"
    try:
        data = http.request_json(
            url, headers={"X-Dune-API-Key": key}, max_retries=1, timeout=timeout
        )
        rows = (data or {}).get("result", {}).get("rows")
        return rows if isinstance(rows, list) else None
    except Exception:  # noqa: BLE001 — per-source resilience is the point
        return None


def collect(queries: Optional[dict[str, int]] = None) -> dict[str, Any]:
    """Collect DAU + tokenized equities. Never raises; returns {} on failure.

    Result shape (consumed by metrics.compute_metrics):
      {"dau": {"available": bool, "value": int|None, "raw": rows|None},
       "tokenized": {"available": bool, "volume_usd": float|None,
                     "aum_usd": float|None, "holders": int|None,
                     "raw": rows|None}}
    """
    q = {**DEFAULT_QUERIES, **(queries or {})}
    out: dict[str, Any] = {}

    dau_rows = _fetch_latest_result(int(q.get("dau") or 0))
    if dau_rows:
        # Column names vary by query; accept the common ones.
        last = dau_rows[-1]
        value = (
            last.get("active_wallets")
            or last.get("dau")
            or last.get("n_signers")
            or last.get("unique_signers")
            or last.get("daily_active_addresses")
            or last.get("daily_active_wallets")
        )
        out["dau"] = {
            "available": value is not None,
            "value": value,
            "raw": dau_rows[-1:],
        }
    else:
        out["dau"] = {"available": False, "value": None, "raw": None}

    # Tokenized equities come from up to three separate queries (volume,
    # AUM/TVL, holders). Accept legacy "tokenized" (single query) too.
    vol_rows = _fetch_latest_result(int(q.get("tokenized_volume") or q.get("tokenized") or 0))
    aum_rows = _fetch_latest_result(int(q.get("tokenized_aum") or 0))
    hold_rows = _fetch_latest_result(int(q.get("tokenized_holders") or 0))
    vol = vol_rows[-1] if vol_rows else {}
    aum = aum_rows[-1] if aum_rows else {}
    hold = hold_rows[-1] if hold_rows else {}
    volume_usd = (
        vol.get("volume_usd")
        or vol.get("total_volume")
        or vol.get("transaction_volume")
        or vol.get("total_volume_30d_usd")
    )
    aum_usd = aum.get("aum_usd") or aum.get("total_aum") or aum.get("total_tvl_usd") or aum.get("tvl_total_usd")
    holders = hold.get("holders") or hold.get("unique_holders")
    if vol_rows or aum_rows or hold_rows:
        out["tokenized"] = {
            "available": True,
            "volume_usd": volume_usd,
            "aum_usd": aum_usd,
            "holders": holders,
            "raw": {"volume": vol_rows[-1:] if vol_rows else None,
                    "aum": aum_rows[-1:] if aum_rows else None,
                    "holders": hold_rows[-1:] if hold_rows else None},
        }
    else:
        out["tokenized"] = {
            "available": False,
            "volume_usd": None,
            "aum_usd": None,
            "holders": None,
            "raw": None,
        }

    return out


# Back-compat alias: the old entry point fetched arbitrary dashboard ids.
def fetch_dashboards(dashboard_ids: list[str]) -> Optional[dict]:
    """Legacy entry point — kept for callers that pass raw query ids."""
    if not dashboard_ids:
        return None
    out: dict[str, Any] = {}
    key = _api_key()
    if not key:
        raise RuntimeError("DUNE_API_KEY not set")
    for did in dashboard_ids:
        try:
            url = f"{API}/query/{did}/results?limit=100"
            data = http.request_json(
                url, headers={"X-Dune-API-Key": key}, max_retries=1
            )
            out[did] = data
        except Exception as e:  # noqa: BLE001
            out[did] = {"error": str(e)}
    return out
