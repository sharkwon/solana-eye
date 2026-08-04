"""Minimal dependency-free HTTP helpers (Python stdlib only).

Zero third-party dependencies: urllib + json are enough for every source
used by this project (Solana RPC, DeFiLlama, CoinGecko, GitHub API,
status.solana.com). This keeps the whole pipeline installable with just
`python3` and no virtualenv.
"""

from __future__ import annotations

import http.client
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

DEFAULT_UA = "solana-pulse/1.0 (auto-updating ecosystem report)"


def _build_request(
    url: str,
    *,
    method: str = "GET",
    payload: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> urllib.request.Request:
    hdrs = {"User-Agent": DEFAULT_UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    return urllib.request.Request(url, data=data, headers=hdrs, method=method)


def request_raw(
    url: str,
    *,
    method: str = "GET",
    payload: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = 20,
    max_retries: int = 2,
    backoff: float = 1.5,
) -> str:
    """Fetch a URL and return the raw text body (non-JSON endpoints).

    Returns the decoded body string. Raises RuntimeError if all retries fail.
    """
    last_err: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        req = _build_request(url, method=method, payload=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < max_retries:
                time.sleep(backoff * (2**attempt))
                continue
            raise RuntimeError(f"HTTP {e.code} for {url}: {e.reason}") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(backoff * (2**attempt))
                continue
            raise RuntimeError(f"Request failed for {url}: {e}") from e
        except http.client.HTTPException as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(backoff * (2**attempt))
                continue
            raise RuntimeError(f"Truncated/invalid response for {url}: {e}") from e
    raise RuntimeError(f"Request failed for {url}: {last_err}")


def request_json(
    url: str,
    *,
    method: str = "GET",
    payload: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = 20,
    max_retries: int = 2,
    backoff: float = 1.5,
) -> Any:
    """Fetch a URL and parse the JSON response, with retry on 429/5xx.

    Returns the parsed JSON body. Raises RuntimeError if all retries fail.
    """
    last_err: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        req = _build_request(url, method=method, payload=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                if not body:
                    return None
                return json.loads(body)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < max_retries:
                time.sleep(backoff * (2**attempt))
                continue
            raise RuntimeError(f"HTTP {e.code} for {url}: {e.reason}") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(backoff * (2**attempt))
                continue
            raise RuntimeError(f"Request failed for {url}: {e}") from e
        except http.client.HTTPException as e:
            # includes IncompleteRead (truncated body) — retry
            last_err = e
            if attempt < max_retries:
                time.sleep(backoff * (2**attempt))
                continue
            raise RuntimeError(f"Truncated/invalid response for {url}: {e}") from e
    raise RuntimeError(f"Request failed for {url}: {last_err}")
