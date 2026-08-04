"""Ecosystem / community news from key X (Twitter) accounts.

Default path is keyless: the unofficial syndication endpoint
(https://syndication.twitter.com/srv/timeline-profile/screen-name/<handle>)
returns embeddable timeline JSON without any API key. It is best-effort and
can stop working without notice — every handle degrades gracefully and the
failure is recorded in the source-health table.

Optional upgrade: set TWITTER_BEARER_TOKEN to use the official X API v2
(users/by/username/{handle}/tweets) which is more stable but requires an
approved developer account.

Zero third-party dependencies (stdlib only), consistent with the rest of
the project.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from .. import http

TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")

# Priority accounts per the program's recommended list.
DEFAULT_ACCOUNTS: list[str] = [
    "solana",
    "SolanaFndn",
    "SolanaFloor",
    "solana_daily",
    "SolanaEvents",
]

SYNDICATION_URL = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{handle}"
OFFICIAL_URL = "https://api.twitter.com/2/users/by/username/{handle}/tweets"


def _fetch_syndication(handle: str, timeout: int = 10) -> list[dict]:
    """Keyless best-effort: parse the unofficial syndication timeline JSON."""
    url = SYNDICATION_URL.format(handle=handle)
    try:
        payload = http.request_json(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; solana-pulse/1.0)"},
            timeout=timeout,
            max_retries=1,
        )
    except Exception:  # noqa: BLE001 — per-source resilience is the point
        return []
    entries = (payload or {}).get("timeline", {}).get("entries", [])
    tweets: list[dict] = []
    for e in entries[:5]:
        content = e.get("content", {})
        tweet = content.get("tweet") or content.get("status") or {}
        text = tweet.get("text") or tweet.get("full_text")
        if text:
            tweets.append(
                {
                    "handle": handle,
                    "text": text,
                    "id": tweet.get("id_str") or tweet.get("id"),
                    "created_at": tweet.get("created_at"),
                }
            )
    return tweets


def _fetch_official(handle: str, timeout: int = 10) -> list[dict]:
    """Official X API v2 — used when TWITTER_BEARER_TOKEN is set."""
    if not TWITTER_BEARER_TOKEN:
        return []
    # First resolve the user id, then fetch recent tweets.
    try:
        user_payload = http.request_json(
            f"https://api.twitter.com/2/users/by/username/{handle}",
            headers={"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"},
            timeout=timeout,
            max_retries=1,
        )
        user_id = (user_payload or {}).get("data", {}).get("id")
        if not user_id:
            return []
        tweets_payload = http.request_json(
            OFFICIAL_URL.format(handle=handle) + f"?max_results=5&user.fields=id",
            headers={"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"},
            timeout=timeout,
            max_retries=1,
        )
    except Exception:  # noqa: BLE001
        return []
    return [
        {
            "handle": handle,
            "text": t.get("text"),
            "id": t.get("id"),
            "created_at": t.get("created_at"),
        }
        for t in (tweets_payload or {}).get("data", [])
        if t.get("text")
    ]


def collect(accounts: Optional[list[str]] = None) -> dict[str, Any]:
    """Fetch the latest tweets for each account (best effort, never raises).

    Result shape (consumed by metrics.compute_metrics):
      {"tweets": [...], "degraded": [handles that failed]}
    """
    accs = accounts or DEFAULT_ACCOUNTS
    tweets: list[dict] = []
    degraded: list[str] = []
    for handle in accs:
        if TWITTER_BEARER_TOKEN:
            got = _fetch_official(handle)
        else:
            got = _fetch_syndication(handle)
        if got:
            tweets.extend(got)
        else:
            degraded.append(handle)
    # Newest first.
    tweets.sort(key=lambda t: t.get("created_at") or "", reverse=True)
    return {"tweets": tweets[:15], "degraded": degraded}
