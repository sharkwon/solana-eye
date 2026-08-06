"""Solana.com official news feed (keyless RSS).

Parses https://solana.com/news/rss.xml with stdlib only. Each item carries a
direct article link and a hero image (<enclosure url="..."/>) which the
dashboard renders as editorial thumbnails.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from typing import Optional

from .. import http

RSS_URL = "https://solana.com/news/rss.xml"


def _epoch(pub_date: Optional[str]) -> Optional[int]:
    if not pub_date:
        return None
    try:
        return int(parsedate_to_datetime(pub_date).timestamp())
    except (TypeError, ValueError):
        return None


def collect(n: int = 9) -> Optional[list[dict]]:
    """Latest n official Solana news items with images. Never raises."""
    try:
        body = http.request_raw(RSS_URL, max_retries=1)
        root = ET.fromstring(body)
    except Exception:  # noqa: BLE001 — guarded source, degrades to offline
        return None
    out: list[dict] = []
    for item in root.iter("item"):
        def txt(tag: str) -> str:
            el = item.find(tag)
            return (el.text or "").strip() if el is not None else ""

        image = None
        enc = item.find("enclosure")
        if enc is not None and (enc.get("type") or "").startswith("image"):
            image = enc.get("url")
        title = txt("title")
        link = txt("link")
        if not title or not link:
            continue
        out.append(
            {
                "title": title,
                "url": link,
                "description": txt("description")[:220],
                "image": image,
                "published_ts": _epoch(txt("pubDate")),
                "source": "solana.com",
            }
        )
        if len(out) >= n:
            break
    return out