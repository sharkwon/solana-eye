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
    """Return {'volume24h': float, 'change_1d_pct': float|None} for a chain."""
    url = (
        f"{BASE}/overview/dexs?volumeChain={chain}"
        "&excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
    )
    data = http.request_json(url)
    if not data or not isinstance(data, dict):
        return None
    t24 = data.get("total24h")
    t48 = data.get("total48hto24h")
    change = None
    if t24 is not None and t48:
        change = (t24 - t48) / t48 * 100.0
    return {"volume24h": t24, "change_1d_pct": change}


def stablecoin_supply(chain: str = "Solana") -> Optional[dict]:
    """Return {'total_usd': float} for a chain, or None."""
    data = http.request_json(f"{STABLE_BASE}/stablecoinchains")
    for row in data or []:
        if row.get("name", "").lower() == chain.lower():
            tcu = row.get("totalCirculatingUSD") or {}
            total = sum(v for v in tcu.values() if isinstance(v, (int, float)))
            return {"total_usd": total}
    return None
