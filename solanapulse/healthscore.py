"""Composite Solana Health Score (0-100).

A single, interpretable number aggregating the most important health signals,
each scored 0-100 and weighted. Pure function of a metrics snapshot — no I/O.

Scoring conventions (configurable in config.json -> healthscore):
- tps            : current / target (default target 1500), capped
- slot_time      : inverse-linear ideal..bad (default 0.4s..0.8s)
- validators     : 100 - delinquent_stake% / max (default max 5%)
- tvl_trend      : 50 + tvl_24h_change_pct * 10 (a +/-5% move -> 0/100)
- price_trend    : 50 + price_24h_change_pct * 10
- network_status : statuspage indicator mapping
"""

from __future__ import annotations

from typing import Any, Optional

DEFAULT_WEIGHTS = {
    "tps": 3,
    "slot_time": 2,
    "validators": 2,
    "tvl_trend": 1,
    "price_trend": 1,
    "network_status": 2,
}

DEFAULT_TARGETS = {
    "tps_target": 1500.0,
    "slot_time_ideal": 0.4,
    "slot_time_bad": 0.8,
    "delinquent_max": 5.0,
}

STATUS_INDICATOR_SCORE = {"none": 100, "minor": 70, "major": 30, "critical": 0}


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def grade(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 80:
        return "good"
    if score >= 65:
        return "fair"
    if score >= 50:
        return "at-risk"
    return "critical"


def compute_health_score(metrics: dict[str, Any], cfg: Optional[dict] = None) -> dict[str, Any]:
    cfg = cfg or {}
    weights = {**DEFAULT_WEIGHTS, **(cfg.get("weights") or {})}
    targets = {**DEFAULT_TARGETS, **(cfg.get("targets") or {})}

    components: dict[str, float] = {}

    tps = (metrics.get("tps") or {}).get("avg")
    if tps is not None:
        components["tps"] = _clamp(tps / targets["tps_target"] * 100.0)

    slot = (metrics.get("slot_time_sec") or {}).get("avg")
    if slot is not None:
        span = targets["slot_time_bad"] - targets["slot_time_ideal"]
        if span > 0:
            components["slot_time"] = _clamp(
                100.0 - (slot - targets["slot_time_ideal"]) / span * 100.0
            )
        else:
            components["slot_time"] = 100.0

    dsp = (metrics.get("validators") or {}).get("delinquent_stake_pct")
    if dsp is not None:
        components["validators"] = _clamp(100.0 - dsp / targets["delinquent_max"] * 100.0)

    tvl = (metrics.get("economics") or {}).get("tvl_24h_change_pct")
    if tvl is not None:
        components["tvl_trend"] = _clamp(50.0 + tvl * 10.0)

    price = (metrics.get("economics") or {}).get("sol_price_24h_change_pct")
    if price is not None:
        components["price_trend"] = _clamp(50.0 + price * 10.0)

    indicator = (metrics.get("status_page") or {}).get("indicator")
    components["network_status"] = STATUS_INDICATOR_SCORE.get(indicator, 100.0)

    total_w = sum(weights.get(k, 1.0) for k in components)
    score = (
        sum(components[k] * weights.get(k, 1.0) for k in components) / total_w
        if total_w
        else 0.0
    )
    return {
        "score": round(score, 1),
        "grade": grade(score),
        "components": {k: round(v, 1) for k, v in sorted(components.items())},
    }
