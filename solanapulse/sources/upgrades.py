"""Upgrade radar: track upcoming Solana protocol upgrades, keyless.

Two complementary strategies, both stdlib-only and keyless:

1. Keyword scan — recently updated SIMD issues/PRs are filtered for
   high-signal keywords ("alpenglow", "votor", "firedancer", ...) so major
   consensus/runtime upgrades surface automatically without hardcoding numbers.
2. Explicit watchlist — specific SIMD numbers (e.g. 525) pinned in config,
   each resolved to its live GitHub state (open / merged / closed).

Plus: latest Agave validator client releases (anza-xyz/agave) — the channel
through which upgrades actually ship to mainnet.
"""

from __future__ import annotations

from typing import Optional

from .. import http
from .simd_news import SIMD_REPOS

AGAVE_REPOS = ["anza-xyz/agave", "solana-labs/solana"]


def _repo_issues_url(repo: str, path: str) -> str:
    return f"https://api.github.com/repos/{repo}/issues{path}"


def _first_working_repo() -> Optional[str]:
    for repo in SIMD_REPOS:
        try:
            data = http.request_json(_repo_issues_url(repo, "?state=all&per_page=1"), max_retries=1)
            if isinstance(data, list):
                return repo
        except RuntimeError:
            continue
    return None


def scan_keywords(keywords: list[str], n: int = 30) -> Optional[list[dict]]:
    """Recent SIMD issues/PRs whose title matches an upgrade keyword."""
    if not keywords:
        return []
    repo = _first_working_repo()
    if not repo:
        return None
    try:
        data = http.request_json(
            _repo_issues_url(repo, f"?state=all&sort=updated&per_page={n}"), max_retries=1
        )
    except RuntimeError:
        return None
    if not isinstance(data, list):
        return None
    kw = [k.lower() for k in keywords]
    out: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").lower()
        hit = next((k for k in kw if k in title), None)
        if not hit:
            continue
        out.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": "merged" if (item.get("pull_request") or {}).get("merged_at") else item.get("state"),
                "type": "PR" if "pull_request" in item else "issue",
                "keyword": hit,
                "labels": [l.get("name") for l in item.get("labels", []) if isinstance(l, dict)],
                "updated_at": item.get("updated_at"),
                "url": item.get("html_url"),
            }
        )
    return out


def watch_simds(numbers: list[int]) -> Optional[list[dict]]:
    """Resolve pinned SIMD numbers to their live GitHub state."""
    if not numbers:
        return []
    repo = _first_working_repo()
    if not repo:
        return None
    out: list[dict] = []
    for num in numbers:
        try:
            item = http.request_json(_repo_issues_url(repo, f"/{num}"), max_retries=1)
        except RuntimeError:
            continue
        if not isinstance(item, dict) or "number" not in item:
            continue
        out.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": "merged" if (item.get("pull_request") or {}).get("merged_at") else item.get("state"),
                "type": "PR" if "pull_request" in item else "issue",
                "keyword": "watchlist",
                "labels": [l.get("name") for l in item.get("labels", []) if isinstance(l, dict)],
                "updated_at": item.get("updated_at"),
                "url": item.get("html_url"),
            }
        )
    return out


def agave_releases(n: int = 3) -> Optional[list[dict]]:
    """Latest Agave client releases (the delivery vehicle for upgrades)."""
    for repo in AGAVE_REPOS:
        url = f"https://api.github.com/repos/{repo}/releases?per_page={n}"
        try:
            data = http.request_json(url, max_retries=1)
        except RuntimeError:
            continue
        if not isinstance(data, list):
            continue
        out = []
        for r in data[:n]:
            if not isinstance(r, dict):
                continue
            out.append(
                {
                    "name": r.get("name") or r.get("tag_name"),
                    "tag": r.get("tag_name"),
                    "published_at": r.get("published_at"),
                    "prerelease": bool(r.get("prerelease")),
                    "url": r.get("html_url"),
                    "repo": repo,
                }
            )
        return out
    return None


def collect(cfg: Optional[dict] = None) -> dict:
    """Gather the full upgrade radar payload. Never raises."""
    cfg = cfg or {}
    keywords = cfg.get("keywords") or ["alpenglow", "votor", "rotor", "firedancer", "frankendancer"]
    watchlist = cfg.get("watch_simds") or [525]
    try:
        kw_hits = scan_keywords(keywords)
    except Exception:  # noqa: BLE001
        kw_hits = None
    try:
        watched = watch_simds(watchlist)
    except Exception:  # noqa: BLE001
        watched = None
    try:
        releases = agave_releases(cfg.get("agave_releases", 3))
    except Exception:  # noqa: BLE001
        releases = None
    return {
        "keyword_hits": kw_hits or [],
        "watchlist": watched or [],
        "agave_releases": releases or [],
        "available": bool(kw_hits is not None or watched is not None or releases is not None),
    }