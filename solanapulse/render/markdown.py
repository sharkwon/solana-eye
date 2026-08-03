"""Render the report as a human-readable Markdown document."""

from __future__ import annotations

import json
from typing import Any


def _fmt(x: Any, nd: int = 2) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return f"{x:,.{nd}f}"
    if isinstance(x, int):
        return f"{x:,}"
    return str(x)


def _usd(x: Any) -> str:
    if x is None:
        return "n/a"
    return f"${_fmt(x)}"


def _pct(x: Any) -> str:
    if x is None:
        return "n/a"
    return f"{x:+.2f}%" if isinstance(x, (int, float)) else str(x)


def render_markdown(report: dict[str, Any]) -> str:
    net = report["network"]
    val = report["validators"]
    eco = report["economics"]
    fees = report["fees"]
    anomalies = report["anomalies"]
    lines: list[str] = []

    lines.append(f"# {report['config'].get('refresh_interval_min') and '🟢 ' or ''}Solana Ecosystem Report")
    lines.append(f"_Auto-generated at {report['generated_at']} UTC — refresh every "
                 f"{report['config'].get('refresh_interval_min')} min_")
    lines.append("")

    # --- anomalies ---
    sev_icons = {"critical": "🔴", "warning": "🟠", "info": "🔵"}
    if anomalies:
        lines.append("## ⚠️ Anomalies Detected")
        for a in anomalies:
            lines.append(f"- {sev_icons.get(a['severity'], '•')} **{a['metric']}**: {a['message']}")
        lines.append("")
    else:
        lines.append("## ✅ No Anomalies Detected")
        lines.append("")

    # --- network ---
    tps = net["tps"] or {}
    slot = net["slot_time_sec"] or {}
    ep = net["epoch"] or {}
    lines.append("## Network Performance")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Health | {net.get('health')} |")
    lines.append(f"| Avg TPS (10 samples) | {_fmt(tps.get('avg'))} |")
    lines.append(f"| Peak TPS | {_fmt(tps.get('max'))} |")
    lines.append(f"| Non-vote TPS | {_fmt((net.get('non_vote_tps') or {}).get('avg'))} |")
    lines.append(f"| Avg slot time | {_fmt(slot.get('avg'), 4)} s |")
    lines.append(f"| Slot | {_fmt(net.get('slot'), 0)} |")
    lines.append(f"| Block height | {_fmt(net.get('block_height'), 0)} |")
    lines.append("")

    lines.append("### Epoch")
    lines.append("")
    lines.append(f"- **Epoch {ep.get('number')}** — {_fmt(ep.get('progress_pct'))}% complete "
                 f"({_fmt(ep.get('slot_index'), 0)}/{_fmt(ep.get('slots_in_epoch'), 0)} slots)")
    lines.append(f"- Slots remaining: {_fmt(ep.get('slots_remaining'), 0)}")
    lines.append(f"- Total transactions (all-time): {_fmt(ep.get('transaction_count'), 0)}")
    lines.append("")

    # --- validators ---
    lines.append("## Validators")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Active validators | {_fmt(val.get('active_count'), 0)} |")
    lines.append(f"| Delinquent validators | {_fmt(val.get('delinquent_count'), 0)} |")
    lines.append(f"| Total active stake | {_fmt(val.get('active_stake_sol'), 0)} SOL |")
    lines.append(f"| Delinquent stake | {_fmt(val.get('delinquent_stake_sol'), 0)} SOL "
                 f"({_fmt(val.get('delinquent_stake_pct'))}%) |")
    lines.append(f"| Avg commission | {_fmt(val.get('avg_commission_pct'))}% |")
    lines.append("")
    top = val.get("top_by_stake") or []
    if top:
        lines.append(f"### Top {len(top)} Validators by Stake")
        lines.append("")
        lines.append("| Rank | Vote Account (prefix) | Stake (SOL) | Commission |")
        lines.append("|---|---|---|---|")
        for i, tv in enumerate(top, 1):
            pk = (tv.get("pubkey") or "")[:8] + "…"
            lines.append(f"| {i} | `{pk}` | {_fmt(tv.get('stake_sol'), 0)} | {_fmt(tv.get('commission_pct'))}% |")
        lines.append("")

    # --- economics ---
    lines.append("## Economics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| SOL price | {_usd(eco.get('sol_price_usd'))} ({_pct(eco.get('sol_price_24h_change_pct'))} 24h) |")
    lines.append(f"| TVL | {_usd(eco.get('tvl_usd'))} ({_pct(eco.get('tvl_24h_change_pct'))} 24h) |")
    lines.append(f"| DEX volume 24h | {_usd(eco.get('dex_volume_24h_usd'))} ({_pct(eco.get('dex_volume_24h_change_pct'))}) |")
    lines.append(f"| Stablecoin supply | {_usd(eco.get('stablecoin_supply_usd'))} |")
    lines.append(f"| Median tx fee | {_fmt(fees.get('median_fee_sol'), 9)} SOL ({_fmt(fees.get('median_fee_lamports'), 0)} lamports) |")
    lines.append(f"| Est. fee revenue 24h | {_fmt(fees.get('rev_est_24h_sol'), 0)} SOL ({fees.get('method')}) |")
    lines.append("")

    # --- supply ---
    sup = net.get("supply") or {}
    lines.append("## Supply")
    lines.append("")
    lines.append(f"- Circulating: {_fmt(sup.get('circulating_sol'), 0)} SOL")
    lines.append(f"- Non-circulating: {_fmt(sup.get('non_circulating_sol'), 0)} SOL")
    lines.append("")

    # --- news / SIMD ---
    simd = report["news"].get("simd") or []
    if simd:
        lines.append("## Ecosystem / Development News")
        lines.append("")
        lines.append("Recently updated SIMD proposals (solana-foundation/simd):")
        lines.append("")
        for s in simd[:8]:
            labels = ", ".join(s.get("labels") or []) or "—"
            lines.append(f"- **#{s.get('number')} {s.get('title')}** (labels: {labels}) — [link]({s.get('url')})")
        lines.append("")

    sp = report.get("status_page") or {}
    if sp:
        lines.append("## Network Status")
        lines.append("")
        lines.append(f"- {sp.get('page_name')}: **{sp.get('indicator')}** — {sp.get('description')}")
        lines.append("")

    # --- sources ---
    lines.append("## Data Sources")
    lines.append("")
    lines.append("| Source | Status |")
    lines.append("|---|---|")
    for name, ok in (report.get("sources_ok") or {}).items():
        lines.append(f"| {name} | {'✅' if ok else '❌'} |")
    lines.append("")
    lines.append("_Generated by [solana-pulse](https://github.com/sharkwon/solana-pulse) — "
                 "keyless, stdlib-only, reproducible._")
    return "\n".join(lines)
