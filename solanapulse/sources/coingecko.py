"""CoinGecko integration (keyless public API).

Free tier is rate-limited (~10-30 req/min) but fine for an hourly cron.
"""

from __future__ import annotations

from typing import Optional

from .. import http

BASE = "https://api.coingecko.com/api/v3"


def sol_price() -> Optional[dict]:
    """Return {'usd': float, 'usd_24h_change': float|None} or None."""
    url = f"{BASE}/simple/price?ids=solana&vs_currencies=usd&include_24hr_change=true"
    try:
        data = http.request_json(url, max_retries=1)
    except RuntimeError:
        return None
    if not data or "solana" not in data:
        return None
    return {
        "usd": data["solana"].get("usd"),
        "usd_24h_change": data["solana"].get("usd_24h_change"),
    }
