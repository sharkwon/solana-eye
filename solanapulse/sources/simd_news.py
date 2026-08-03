"""GitHub-based news + Solana status page (both keyless).

- simd: recently updated proposals in solana-foundation/simd
- status: status.solana.com statuspage API (incidents / components)
"""

from __future__ import annotations

from typing import Optional

from .. import http

SIMD_REPO = "solana-foundation/simd"
STATUS_URL = "https://status.solana.com/api/v2/status.json"


def recent_simd(n: int = 8) -> list[dict]:
    """Most recently updated open SIMD issues/PRs (proposals in flight)."""
    url = (
        f"https://api.github.com/repos/{SIMD_REPO}/issues"
        f"?state=open&sort=updated&per_page={n}"
    )
    try:
        data = http.request_json(url, max_retries=1)
    except RuntimeError:
        return []
    out = []
    for item in data or []:
        if "pull_request" in item:
            continue  # proposals live as issues; PRs are mostly housekeeping
        labels = [l["name"] for l in item.get("labels", [])]
        out.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "labels": labels,
                "updated_at": item.get("updated_at"),
                "url": item.get("html_url"),
            }
        )
        if len(out) >= n:
            break
    return out


def status_overview() -> Optional[dict]:
    """Return {'indicator': str, 'description': str, 'page_name': str} or None."""
    try:
        data = http.request_json(STATUS_URL, max_retries=1)
    except RuntimeError:
        return None
    status = (data or {}).get("status", {})
    if not status:
        return None
    return {
        "indicator": status.get("indicator"),
        "description": status.get("description"),
        "page_name": (data or {}).get("page", {}).get("name"),
    }
