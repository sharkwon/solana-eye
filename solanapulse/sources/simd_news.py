"""GitHub-based news + Solana status page (both keyless).

- simd: recently updated proposals in solana-foundation/simd
- status: status.solana.com statuspage API (incidents / components)
"""

from __future__ import annotations

from typing import Optional

from .. import http

SIMD_REPOS = [
    "solana-foundation/solana-improvement-documents",  # current name (renamed)
    "solana-foundation/simd",                          # legacy name
    "solana-labs/simd",
]
STATUS_URL = "https://status.solana.com/api/v2/status.json"


def recent_simd(n: int = 8) -> Optional[list[dict]]:
    """Most recently updated open SIMD issues/PRs (proposals in flight).

    Tries each known repo name (the repo was renamed at least once; the API
    returns 404 for stale names), and only treats a list response as success.
    """
    for repo in SIMD_REPOS:
        url = (
            f"https://api.github.com/repos/{repo}/issues"
            f"?state=open&sort=updated&per_page={n}"
        )
        try:
            data = http.request_json(url, max_retries=1)
        except RuntimeError:
            continue
        if not isinstance(data, list):
            continue  # dict with "message" = 404/rate-limit — try next repo
        out = []
        for item in data:
            if not isinstance(item, dict):
                continue
            # In solana-improvement-documents the proposals ARE pull requests
            # (SIMD-0401, SIMD-0571, ...) — include both issues and PRs.
            labels = [l.get("name") for l in item.get("labels", []) if isinstance(l, dict)]
            out.append(
                {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "type": "PR" if "pull_request" in item else "issue",
                    "labels": labels,
                    "updated_at": item.get("updated_at"),
                    "url": item.get("html_url"),
                }
            )
            if len(out) >= n:
                break
        return out
    return None  # every candidate repo failed — caller can mark source offline


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
