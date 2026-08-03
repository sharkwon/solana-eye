"""DeFiLlama integration (keyless public API).

Sources:
- https://api.llama.fi/v2/chains                  -> chain TVL
- https://api.llama.fi/v2/historicalChainTvl/{c}  -> TVL history (anomalies)
- https://api.llama.fi/overview/dexs              -> DEX volume (per chain)
- https://stablecoins.llama.fi/stablecoinchains   -> stablecoin supply per chain
"""

from __future__ import annotations

from typing import Any, Optional

from .. import http

BASE = "https://api.llama.fi"
STABLE_BASE = "https://stablecoins.llama.fi"


def chain_tvl(chain: str = "Solana") -> Optional[float]:
    data = http.request_json(f"{BASE}/v2/chains")
    for row in data or []:
        if row.get("name", "").lower() == chain.lower():
            return row.get("tvl")
    return None


def historical_chain_tvl(chain: str = "Solana", days: int = 30) -> list[dict]:
    data = http.request_json(f"{BASE}/v2/historicalChainTvl/{chain}")
    if not data:
        return []
    cutoff = days * 86400
    now = __import__("time").time()
    out = []
    for p in data:
        ts = p.get("date") or p.get("timestamp")
        if isinstance(ts, int) and ts > 10_000_000_000:  # ms -> s
            ts = ts / 1000
        if ts is not None and now - ts <= cutoff:
            out.append({"ts": ts, "tvl": p.get("tvl")})
    return out


def dex_volume_24h(chain: str = "Solana") -> Optional[dict]:
    """Return {'volume24h': float, 'change_1d_pct': float|None} for a chain.

    NOTE: use the /overview/dexs/{chain} path form. The query-param form
    (?volumeChain=...) silently ignores the parameter and returns the
    all-chains aggregate — verified against live responses.
    """
    url = (
        f"{BASE}/overview/dexs/{chain.lower()}"
        "?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
    )
    data = http.request_json(url)
    if not data or not isinstance(data, dict):
        return None
    return {"volume24h": data.get("total24h"), "change_1d_pct": data.get("change_1d")}


def stablecoin_supply(chain: str = "Solana") -> Optional[dict]:
    """Return {'total_usd': float} for a chain, or None."""
    data = http.request_json(f"{STABLE_BASE}/stablecoinchains")
    for row in data or []:
        if row.get("name", "").lower() == chain.lower():
            tcu = row.get("totalCirculatingUSD") or {}
            total = sum(v for v in tcu.values() if isinstance(v, (int, float)))
            return {"total_usd": total}
    return None


# --- multi-chain comparison (one call per dataset, all chains at once) --------

def multi_chain_tvl(chains: list[str]) -> dict:
    """TVL for many chains from a single /v2/chains call."""
    data = http.request_json(f"{BASE}/v2/chains")
    by_name = {row.get("name", "").lower(): row.get("tvl") for row in data or []}
    return {c: by_name.get(c.lower()) for c in chains}


def multi_chain_stablecoins(chains: list[str]) -> dict:
    """Stablecoin supply for many chains from a single stablecoinchains call."""
    data = http.request_json(f"{STABLE_BASE}/stablecoinchains")
    by_name = {}
    for row in data or []:
        tcu = row.get("totalCirculatingUSD") or {}
        by_name[row.get("name", "").lower()] = sum(
            v for v in tcu.values() if isinstance(v, (int, float))
        )
    return {c: by_name.get(c.lower()) for c in chains}


def multi_chain_dex(chains: list[str]) -> dict:
    """DEX volume 24h per chain (one call per chain — bounded, keyless)."""
    out: dict = {}
    for c in chains:
        try:
            out[c] = dex_volume_24h(c)
        except Exception:  # noqa: BLE001 — one chain failing shouldn't kill the panel
            out[c] = None
    return out
