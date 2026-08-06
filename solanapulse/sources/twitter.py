"""Ecosystem / community news from key X (Twitter) accounts.

Keyless by default. Source priority:
1. **Nitter RSS** (`/solana/rss`) — public mirrors of X timelines; we try a
   list of instances in order and use the first that responds. Rate-limited
   instances are skipped.
2. **Syndication endpoint** — unofficial `syndication.twitter.com` embed JSON.
   Best-effort; often rate-limited (429) from datacenter IPs.
3. **Official X API v2** — only when `TWITTER_BEARER_TOKEN` is set (requires
   an approved developer account). Most stable but needs a key.

Every handle degrades gracefully: failures are recorded in the source-health
table and never kill the run. Zero third-party dependencies (stdlib only),
consistent with the rest of the project.
"""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
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

NITTER_INSTANCES: list[str] = [
    "https://nitter.net",
    "https://xcancel.com",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
]

SYNDICATION_URL = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{handle}"
OFFICIAL_URL = "https://api.twitter.com/2/users/by/username/{handle}/tweets"

_NITTER_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
_NITTER_DATE_RE = re.compile(r"<pubDate>(.*?)</pubDate>", re.S)
_NITTER_GUID_RE = re.compile(r"<guid[^>]*>(.*?)</guid>", re.S)


def _clean_text(s: str) -> str:
    """Strip HTML entities / tags that Nitter embeds in titles."""
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    s = s.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    return s.strip()


_RT_RE = re.compile(r"^(RT\b|RT by\b|Reposted by\b|Retweeted by\b|R to\b)", re.I)
_REPLY_RE = re.compile(r"^[.·•]?\s*@[\w]+")
_SPAM_RE = re.compile(r"(click here|sign up now|subscribe to|sponsor|full episode)", re.I)


def _is_useful_tweet(text: str) -> bool:
    """Keep only original news posts — drop retweets, replies, and junk."""
    if not text:
        return False
    t = text.strip()
    if len(t) < 10:
        return False
    if _RT_RE.match(t):
        return False
    # A reply is a leading @mention (but a normal post may quote-@ later)
    if _REPLY_RE.match(t) and not re.search(r"\n", t):
        return False
    if _SPAM_RE.search(t):
        return False
    # Thread continuation (ends mid-sentence with "..." or contains "thread 🧵")
    if re.search(r"(thread|🧵|\b1/|\.\.\.\s*$)", t, re.I):
        return False
    return True


def _fetch_nitter(handle: str, timeout: int = 12) -> list[dict]:
    """Fetch the RSS timeline from the first working Nitter instance."""
    for base in NITTER_INSTANCES:
        url = f"{base}/{handle}/rss"
        try:
            raw = http.request_raw(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; solana-pulse/1.0)"},
                timeout=timeout,
                max_retries=1,
            )
        except Exception:  # noqa: BLE001 — try next instance
            continue
        if not raw:
            continue
        tweets: list[dict] = []
        for item in re.findall(r"<item>(.*?)</item>", raw, re.S):
            title = _NITTER_TITLE_RE.search(item)
            date = _NITTER_DATE_RE.search(item)
            guid = _NITTER_GUID_RE.search(item)
            text = _clean_text(title.group(1)) if title else ""
            if not text:
                continue
            tweets.append(
                {
                    "handle": handle,
                    "text": text,
                    "id": guid.group(1).strip() if guid else None,
                    "created_at": date.group(1).strip() if date else None,
                }
            )
        if tweets:
            return tweets
    return []


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
            got = _fetch_nitter(handle)
            if not got:
                got = _fetch_syndication(handle)
        if got:
            tweets.extend([t for t in got if _is_useful_tweet(t.get("text") or "")])
        else:
            degraded.append(handle)
    # Newest first (Nitter dates are RFC-822; syndication ISO — sort defensively).
    tweets.sort(key=lambda t: str(t.get("created_at") or ""), reverse=True)
    return {"tweets": tweets[:15], "degraded": degraded}
