"""Metrics engine: turn raw collected data into computed, report-ready metrics.

Everything here is pure computation (no I/O) so it is trivially unit-testable.
"""

from __future__ import annotations

import statistics
import time
from typing import Any, Optional

LAMPORTS_PER_SOL = 1_000_000_000
BLOCKS_PER_DAY = 24 * 60 * 60 / 0.4  # ~0.4s slot time => ~216,000 blocks/day


def _safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b in (None, 0):
        return None
    return a / b


def compute_metrics(raw: dict[str, Any], top_validators: int = 20) -> dict[str, Any]:
    """Compute derived metrics from a raw collection snapshot."""
    m: dict[str, Any] = {}

    # --- network performance ---------------------------------------------------
    samples = raw.get("perf_samples") or []
    tps_list: list[float] = []
    nonvote_tps_list: list[float] = []
    slot_time_list: list[float] = []
    for s in samples:
        txs = s.get("numTransactions")
        slots = s.get("numSlots")
        period = s.get("samplePeriodSecs")
        if txs and slots:
            tps_list.append(txs / slots)
        if s.get("numNonVoteTransactions") and slots:
            nonvote_tps_list.append(s["numNonVoteTransactions"] / slots)
        if slots and period:
            slot_time_list.append(period / slots)

    m["tps"] = {"avg": _mean(tps_list), "max": _max(tps_list), "samples": len(tps_list)}
    m["non_vote_tps"] = {"avg": _mean(nonvote_tps_list)}
    m["slot_time_sec"] = {"avg": _mean(slot_time_list)}

    ei = raw.get("epoch_info") or {}
    slots_in = ei.get("slotsInEpoch") or 1
    progress = _safe_div(ei.get("slotIndex"), slots_in)
    m["epoch"] = {
        "number": ei.get("epoch"),
        "slot_index": ei.get("slotIndex"),
        "slots_in_epoch": slots_in,
        "progress_pct": round(progress * 100, 2) if progress is not None else None,
        "slots_remaining": slots_in - ei.get("slotIndex", 0),
        "transaction_count": ei.get("transactionCount"),
    }
    m["block_height"] = raw.get("block_height")
    m["slot"] = raw.get("slot")
    m["health"] = raw.get("health")

    # --- validators -------------------------------------------------------------
    va = raw.get("vote_accounts") or {}
    active, delinquent = va.get("current") or [], va.get("delinquent") or []

    def _stake_sol(v: list[dict]) -> float:
        return sum(a.get("activatedStake", 0) for a in v) / LAMPORTS_PER_SOL

    active_stake = _stake_sol(active)
    delinquent_stake = _stake_sol(delinquent)
    total_stake = active_stake + delinquent_stake

    def _commission(v: list[dict]) -> Optional[float]:
        vals: list[float] = []
        for a in v:
            c = a.get("commission")
            if isinstance(c, (int, float)):
                vals.append(float(c))
        return statistics.mean(vals) if vals else None

    top = sorted(active, key=lambda a: a.get("activatedStake", 0), reverse=True)[:top_validators]
    delinq_pct = None
    if total_stake:
        ratio = _safe_div(delinquent_stake, total_stake)
        if ratio is not None:
            delinq_pct = round(ratio * 100, 2)

    # --- decentralization: Nakamoto coefficient -----------------------------
    # The minimum number of top validators whose combined activated stake
    # exceeds 33% of total active stake (the standard Byzantine threshold).
    # Computed from getVoteAccounts — no extra RPC calls, no API keys.
    nakamoto: Optional[int] = None
    stake_shares: list[float] = []
    if total_stake > 0:
        ordered = sorted(
            active, key=lambda a: a.get("activatedStake", 0), reverse=True
        )
        cumulative = 0.0
        for i, a in enumerate(ordered, 1):
            share = (a.get("activatedStake", 0) / LAMPORTS_PER_SOL) / total_stake
            stake_shares.append(round(share * 100, 3))
            cumulative += share
            if cumulative > 0.33:  # >33% = superminority can halt finality
                nakamoto = i
                break
    if nakamoto is None and total_stake > 0:
        nakamoto = len(active)  # degenerate: even all validators < 33%? impossible in practice

    m["validators"] = {
        "active_count": len(active),
        "delinquent_count": len(delinquent),
        "active_stake_sol": round(active_stake, 1),
        "delinquent_stake_sol": round(delinquent_stake, 1),
        "delinquent_stake_pct": delinq_pct,
        "avg_commission_pct": _commission(active),
        "nakamoto_coefficient": nakamoto,
        "stake_distribution_pct": stake_shares,
        "top_by_stake": [
            {
                "pubkey": a.get("votePubkey"),
                "node": a.get("nodePubkey"),
                "stake_sol": round(a.get("activatedStake", 0) / LAMPORTS_PER_SOL, 0),
                "stake_pct": (
                    round(a.get("activatedStake", 0) / LAMPORTS_PER_SOL / total_stake * 100, 2)
                    if total_stake
                    else None
                ),
                "commission_pct": a.get("commission"),
                "last_vote_slot": a.get("lastVote"),
            }
            for a in top
        ],
    }

    # --- supply ------------------------------------------------------------------
    sup = raw.get("supply") or {}
    m["supply"] = {
        "circulating_sol": round(_safe_div(sup.get("circulating"), LAMPORTS_PER_SOL) or 0, 1),
        "non_circulating_sol": round(
            _safe_div(sup.get("nonCirculating"), LAMPORTS_PER_SOL) or 0, 1
        ),
    }

    # --- fees & REV (estimated from sampled blocks) -------------------------------
    fee_stats = raw.get("fee_stats") or {}
    fees = fee_stats.get("fees_lamports") or []
    nblocks = fee_stats.get("blocks", 0)
    m["fees"] = {
        "median_fee_lamports": int(statistics.median(fees)) if fees else None,
        "median_fee_sol": (
            round(statistics.median(fees) / LAMPORTS_PER_SOL, 9) if fees else None
        ),
        "sampled_blocks": nblocks,
        "sampled_txs": len(fees),
        "rev_est_per_block_sol": (
            round(sum(fees) / LAMPORTS_PER_SOL / nblocks, 6) if fees and nblocks else None
        ),
        "rev_est_24h_sol": (
            round(sum(fees) / LAMPORTS_PER_SOL / nblocks * BLOCKS_PER_DAY, 0)
            if fees and nblocks
            else None
        ),
        "method": "sampled block meta.fee (estimates)",
    }

    # --- economics (off-chain) -----------------------------------------------------
    price = raw.get("price") or {}
    tvl_hist = raw.get("tvl_history") or []
    tvl_now = raw.get("tvl")
    tvl_24h_ago = None
    if tvl_hist:
        target = time.time() - 86400
        nearest = min(tvl_hist, key=lambda p: abs((p.get("ts") or 0) - target))
        tvl_24h_ago = nearest.get("tvl")
    m["economics"] = {
        "sol_price_usd": price.get("usd"),
        "sol_price_24h_change_pct": price.get("usd_24h_change"),
        "tvl_usd": tvl_now,
        "tvl_24h_change_pct": (
            round((tvl_now - tvl_24h_ago) / tvl_24h_ago * 100, 2)
            if tvl_now and tvl_24h_ago
            else None
        ),
        "dex_volume_24h_usd": (raw.get("dex") or {}).get("volume24h"),
        "dex_volume_24h_change_pct": (raw.get("dex") or {}).get("change_1d_pct"),
        "stablecoin_supply_usd": (raw.get("stablecoins") or {}).get("total_usd"),
    }

    # --- news / status ---------------------------------------------------------------
    m["status_page"] = raw.get("status") or {}
    m["simd"] = raw.get("simd") or []
    m["sources_ok"] = raw.get("sources_ok") or {}
    m["comparison"] = raw.get("comparison") or {}

    # --- ecosystem growth (optional Dune) -------------------------------------------
    dune = raw.get("dune") or {}
    dau = dune.get("dau") or {}
    tok = dune.get("tokenized") or {}
    m["ecosystem_growth"] = {
        "daily_active_addresses": {
            "available": bool(dau.get("available")),
            "value": dau.get("value"),
            "source": "dune",
        },
        "tokenized_equities": {
            "available": bool(tok.get("available")),
            "volume_usd": tok.get("volume_usd"),
            "aum_usd": tok.get("aum_usd"),
            "holders": tok.get("holders"),
            "source": "dune (xStocks)",
        },
    }

    # --- ecosystem / community news (X/Twitter) --------------------------------------
    tw = raw.get("twitter") or {}
    m["twitter"] = {"tweets": tw.get("tweets") or [], "degraded": tw.get("degraded") or []}

    # --- upgrade radar (Alpenglow, watched SIMDs, Agave releases) --------------------
    m["upgrades"] = raw.get("upgrades") or {
        "keyword_hits": [], "watchlist": [], "agave_releases": [], "available": False
    }

    return m


def _mean(vals: list[float]) -> Optional[float]:
    return round(statistics.mean(vals), 3) if vals else None


def _max(vals: list[float]) -> Optional[float]:
    return round(max(vals), 3) if vals else None
