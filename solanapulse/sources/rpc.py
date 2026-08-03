"""Solana JSON-RPC client (keyless public endpoint).

Every method needed for the report is available on the public
api.mainnet-beta.solana.com endpoint with no API key. Users may swap in
their own RPC URL (Helius/Triton/QuickNode) via config.json.
"""

from __future__ import annotations

from typing import Any, Optional

from .. import http


class SolanaRPC:
    def __init__(self, url: str, timeout: int = 20, max_retries: int = 2):
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self._id = 0

    def call(self, method: str, params: Optional[list] = None) -> Any:
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or []}
        resp = http.request_json(
            self.url,
            method="POST",
            payload=payload,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
        if "error" in resp:
            raise RuntimeError(f"RPC error {method}: {resp['error']}")
        return resp.get("result")

    # --- health / chain state -------------------------------------------------
    def get_health(self) -> str:
        return self.call("getHealth")

    def get_epoch_info(self) -> dict:
        return self.call("getEpochInfo")

    def get_slot(self) -> int:
        return self.call("getSlot")

    def get_block_height(self) -> int:
        return self.call("getBlockHeight")

    def get_supply(self) -> dict:
        res = self.call("getSupply")
        if isinstance(res, dict) and "value" in res:
            return res["value"]
        return res or {}

    # --- performance ----------------------------------------------------------
    def get_recent_performance_samples(self, n: int = 10) -> list:
        return self.call("getRecentPerformanceSamples", [n])

    # --- validators -----------------------------------------------------------
    def get_vote_accounts(self) -> dict:
        return self.call("getVoteAccounts")

    # --- fee sampling ----------------------------------------------------------
    def get_block(self, slot: int) -> Optional[dict]:
        """Fetch one block with full transaction metadata (for fee stats).

        Returns None for skipped/empty blocks (common at recent slots).
        """
        params = [
            slot,
            {
                "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": 0,
                "transactionDetails": "full",
                "rewards": False,
            },
        ]
        try:
            return self.call("getBlock", params)
        except Exception:  # noqa: BLE001 — skipped/oversized blocks are normal
            return None
