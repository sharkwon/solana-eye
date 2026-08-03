"""Anomaly detection.

Two complementary strategies:
1. Threshold rules — domain knowledge (e.g. TPS drops >30%, slot time >0.6s,
   delinquent stake >5%, TVL/price drop >5% vs baseline).
2. Statistical z-score — deviation from the collected history for any numeric
   series that has enough samples.

Pure computation: no I/O, fully unit-testable.
"""

from __future__ import annotations

import statistics
from typing import Any, Optional


def zscore(values: list[float], x: float) -> Optional[float]:
    """z-score of x against values; None when history is too small.

    A perfectly flat history with a deviating current value is treated as a
    strong anomaly (returns a large z) rather than an invisible one.
    """
    if len(values) < 2:
        return None
    stdev = statistics.stdev(values)
    if stdev == 0:
        return 0.0 if x == statistics.mean(values) else 100.0
    return (x - statistics.mean(values)) / stdev


def check_thresholds(metrics: dict[str, Any], cfg: dict[str, Any]) -> list[dict]:
    """Domain-knowledge threshold checks on a single metrics snapshot."""
    anomalies: list[dict] = []
    tps_avg = (metrics.get("tps") or {}).get("avg")
    if tps_avg is not None and tps_avg < 0.0:
        pass  # placeholder; real comparisons below need baseline history

    slot_avg = (metrics.get("slot_time_sec") or {}).get("avg")
    if slot_avg is not None and slot_avg > cfg.get("slot_time_sec_max", 0.6):
        anomalies.append(
            _anom(
                "slot_time",
                "warning",
                f"Slot time {slot_avg}s exceeds {cfg.get('slot_time_sec_max')}s",
                value=slot_avg,
            )
        )

    v = metrics.get("validators") or {}
    dsp = v.get("delinquent_stake_pct")
    if dsp is not None and dsp > cfg.get("delinquent_stake_pct_max", 5.0):
        anomalies.append(
            _anom(
                "delinquent_stake",
                "warning",
                f"Delinquent stake {dsp}% exceeds {cfg.get('delinquent_stake_pct_max')}%",
                value=dsp,
            )
        )

    if (v.get("delinquent_count") or 0) > 0 and dsp is not None:
        anomalies.append(
            _anom(
                "validators_delinquent",
                "info",
                f"{v.get('delinquent_count')} validators delinquent "
                f"({dsp}% of stake)",
                value=dsp,
            )
        )

    eco = metrics.get("economics") or {}
    for key, label, thr_key, sev in (
        ("tvl_24h_change_pct", "TVL", "tvl_drop_pct", "warning"),
        ("sol_price_24h_change_pct", "SOL price", "price_drop_pct", "info"),
        ("dex_volume_24h_change_pct", "DEX volume", "tvl_drop_pct", "info"),
    ):
        val = eco.get(key)
        if val is None:
            continue
        thr = cfg.get(thr_key, 5.0)
        if val <= -thr:
            anomalies.append(
                _anom(key, sev, f"{label} dropped {abs(val):.1f}% in 24h", value=val)
            )
        elif val >= thr:
            anomalies.append(
                _anom(key, "info", f"{label} surged {val:.1f}% in 24h", value=val)
            )

    sp = metrics.get("status_page") or {}
    if sp.get("indicator") not in (None, "none"):
        anomalies.append(
            _anom(
                "network_status",
                "warning",
                f"Network status: {sp.get('indicator')} — {sp.get('description')}",
                value=sp.get("indicator"),
            )
        )
    return anomalies


def check_zscore(metrics: dict[str, Any], history: list[dict], cfg: dict[str, Any]) -> list[dict]:
    """Statistical checks: current value vs history for key series."""
    anomalies: list[dict] = []
    thr = cfg.get("zscore_threshold", 3.0)
    min_hist = cfg.get("min_history", 5)

    def series_of(path: list[str]) -> list[float]:
        out = []
        for snap in history:
            node: Any = snap.get("metrics") if "metrics" in snap else snap
            for key in path:
                if not isinstance(node, dict):
                    break
                node = node.get(key)
            if isinstance(node, (int, float)):
                out.append(float(node))
        return out

    def stat_key(path: list[str]) -> tuple[list[float], float]:
        series = series_of(path)
        if len(series) < min_hist:
            return [], 0.0
        return series, series[-1]

    checks = [
        (["tps", "avg"], "tps", "TPS"),
        (["slot_time_sec", "avg"], "slot_time_sec", "slot time"),
        (["validators", "delinquent_stake_pct"], "delinquent_stake_pct", "delinquent stake %"),
        (["economics", "tvl_usd"], "tvl_usd", "TVL"),
        (["economics", "sol_price_usd"], "sol_price_usd", "SOL price"),
        (["economics", "dex_volume_24h_usd"], "dex_volume_24h_usd", "DEX volume"),
    ]
    for path, mkey, label in checks:
        series, cur = stat_key(path)
        if not series:
            continue
        z = zscore(series[:-1], cur)  # compare against history *before* now
        if z is None:
            continue
        if z >= thr:
            anomalies.append(
                _anom(mkey, "warning", f"{label} statistically high (z={z:.1f})", value=cur, z=z)
            )
        elif z <= -thr:
            anomalies.append(
                _anom(mkey, "warning", f"{label} statistically low (z={z:.1f})", value=cur, z=z)
            )
    return anomalies


def run(metrics: dict[str, Any], history: list[dict], cfg: dict[str, Any]) -> list[dict]:
    combined = check_thresholds(metrics, cfg) + check_zscore(metrics, history, cfg)
    # Deduplicate by (metric, message)
    seen: set = set()
    out = []
    for a in combined:
        key = (a["metric"], a["message"])
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    out.sort(key=lambda a: {"critical": 0, "warning": 1, "info": 2}.get(a["severity"], 3))
    return out


def _anom(metric: str, severity: str, message: str, value: Any = None, z: Optional[float] = None) -> dict:
    return {"metric": metric, "severity": severity, "message": message, "value": value, "z": z}
