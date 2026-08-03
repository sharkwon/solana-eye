#!/usr/bin/env python3
"""solana-pulse — one-shot pipeline: collect -> compute -> detect -> render.

Usage:
    python3 run.py                 # full run, all outputs
    python3 run.py --once          # collect + report, skip history z-scores
    python3 run.py --json-only     # just refresh latest.json (fast)

Outputs (written to ./outputs):
    latest.json    machine-readable snapshot of the current state
    report.md      human-readable markdown report
    dashboard.html single-file interactive dark-theme dashboard
    history.jsonl  append-only metric history (powers z-scores & sparklines)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solanapulse import store
from solanapulse import anomaly as anomaly_mod
from solanapulse.metrics import compute_metrics
from solanapulse.report import build_report
from solanapulse.render.markdown import render_markdown
from solanapulse.render.dashboard import render_dashboard

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def collect(cfg: dict) -> tuple[dict, dict]:
    """Gather raw data from every configured source. Never raises — each
    source is guarded and its success recorded in sources_ok."""
    from solanapulse.sources.rpc import SolanaRPC
    from solanapulse.sources import defillama, coingecko, simd_news

    raw: dict = {}
    ok: dict = {}
    rpc = SolanaRPC(cfg["rpc"]["url"], cfg["rpc"].get("timeout", 20),
                    cfg["rpc"].get("max_retries", 2))

    # --- on-chain ---
    # canonical raw keys are consumed by compute_metrics(); ok[] keeps
    # descriptive per-call names for the sources table
    rpc_calls = (
        ("health", "rpc_health", rpc.get_health),
        ("epoch_info", "rpc_epoch", rpc.get_epoch_info),
        ("slot", "rpc_slot", rpc.get_slot),
        ("block_height", "rpc_block_height", rpc.get_block_height),
        ("perf_samples", "rpc_perf", lambda: rpc.get_recent_performance_samples(cfg["collect"]["performance_samples"])),
        ("vote_accounts", "rpc_votes", rpc.get_vote_accounts),
        ("supply", "rpc_supply", rpc.get_supply),
    )
    for key, label, fn in rpc_calls:
        try:
            raw[key] = fn()
            ok[label] = True
        except Exception as e:  # noqa: BLE001 — per-source resilience is the point
            raw[key] = None
            ok[label] = False
            print(f"  [!] {label} failed: {e}", file=sys.stderr)

    # --- fee sampling (a few recent blocks) ---
    fees: list[int] = []
    blocks = 0
    try:
        latest = raw.get("rpc_slot") or rpc.get_slot()
        # sample every 2nd slot: adjacent blocks are near-identical, this halves
        # the chance of hitting an oversized block and the RPC load
        for s in range(latest - 2 * cfg["collect"]["fee_sample_blocks"], latest + 1, 2):
            b = rpc.get_block(s)
            if not b or not b.get("transactions"):
                continue
            blocks += 1
            for t in b["transactions"]:
                meta = t.get("meta") or {}
                if meta.get("err") is None and isinstance(meta.get("fee"), int):
                    fees.append(meta["fee"])
            if blocks >= cfg["collect"]["fee_sample_blocks"]:
                break
        raw["fee_stats"] = {"fees_lamports": fees, "blocks": blocks}
        ok["rpc_fee_sampling"] = blocks > 0
    except Exception as e:  # noqa: BLE001
        raw["fee_stats"] = {"fees_lamports": [], "blocks": 0}
        ok["rpc_fee_sampling"] = False
        print(f"  [!] fee sampling failed: {e}", file=sys.stderr)

    # --- off-chain (keyless) ---
    if cfg["sources"].get("defillama", True):
        for name, fn in (
            ("tvl", lambda: defillama.chain_tvl()),
            ("tvl_history", lambda: defillama.historical_chain_tvl(days=2)),
            ("dex", lambda: defillama.dex_volume_24h()),
            ("stablecoins", lambda: defillama.stablecoin_supply()),
        ):
            try:
                raw[name] = fn()
                ok[f"defillama_{name}"] = True
            except Exception as e:  # noqa: BLE001
                raw[name] = None
                ok[f"defillama_{name}"] = False
                print(f"  [!] defillama/{name} failed: {e}", file=sys.stderr)

        # multi-chain comparison panel
        chains = (cfg.get("comparison") or {}).get("chains", [])
        if chains:
            try:
                raw["comparison"] = {
                    "chains": chains,
                    "tvl": defillama.multi_chain_tvl(chains),
                    "dex": defillama.multi_chain_dex(chains),
                    "stablecoins": defillama.multi_chain_stablecoins(chains),
                }
                ok["defillama_comparison"] = True
            except Exception as e:  # noqa: BLE001
                raw["comparison"] = {}
                ok["defillama_comparison"] = False
                print(f"  [!] defillama/comparison failed: {e}", file=sys.stderr)

    if cfg["sources"].get("coingecko", True):
        try:
            raw["price"] = coingecko.sol_price()
            ok["coingecko"] = raw["price"] is not None
        except Exception as e:  # noqa: BLE001
            raw["price"] = None
            ok["coingecko"] = False
            print(f"  [!] coingecko failed: {e}", file=sys.stderr)

    if cfg["sources"].get("github_simd", True):
        try:
            raw["simd"] = simd_news.recent_simd()
            ok["github_simd"] = raw["simd"] is not None
        except Exception as e:  # noqa: BLE001
            raw["simd"] = []
            ok["github_simd"] = False
            print(f"  [!] github_simd failed: {e}", file=sys.stderr)

    if cfg["sources"].get("statuspage", True):
        try:
            raw["status"] = simd_news.status_overview()
            ok["statuspage"] = raw["status"] is not None
        except Exception as e:  # noqa: BLE001
            raw["status"] = None
            ok["statuspage"] = False
            print(f"  [!] statuspage failed: {e}", file=sys.stderr)

    # --- optional Dune (needs DUNE_API_KEY env) ---
    dune_cfg = cfg["sources"].get("dune") or {}
    if dune_cfg.get("enabled"):
        try:
            from solanapulse.sources import dune as dune_mod

            raw["dune"] = dune_mod.fetch_dashboards(dune_cfg.get("dashboards") or [])
            ok["dune"] = raw["dune"] is not None
        except Exception as e:  # noqa: BLE001
            raw["dune"] = None
            ok["dune"] = False
            print(f"  [!] dune failed: {e}", file=sys.stderr)

    raw["sources_ok"] = ok
    return raw, ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Solana ecosystem auto-report")
    ap.add_argument("--once", action="store_true", help="skip z-score (no history needed)")
    ap.add_argument("--json-only", action="store_true", help="only write latest.json")
    args = ap.parse_args()

    cfg = json.load(open(CONFIG_PATH, encoding="utf-8"))
    os.makedirs(OUT_DIR, exist_ok=True)
    history_path = os.path.join(OUT_DIR, "history.jsonl")

    print("== solana-pulse: collecting ==")
    raw, ok = collect(cfg)
    ok_ratio = sum(1 for v in ok.values() if v) / max(len(ok), 1)
    print(f"   sources ok: {ok_ratio:.0%}")

    metrics = compute_metrics(raw, top_validators=cfg["collect"].get("top_validators", 20))

    # composite health score + percentile baselines
    from solanapulse.healthscore import compute_health_score
    from solanapulse.baseline import compute_baselines

    metrics["health_score"] = compute_health_score(metrics, cfg.get("healthscore"))

    history = store.load_history(history_path)
    metrics["baselines"] = compute_baselines(metrics, history, cfg.get("baselines") or {})

    if not args.once and history:
        anoms = anomaly_mod.run(metrics, history, cfg["anomaly"])
    else:
        anoms = anomaly_mod.check_thresholds(metrics, cfg["anomaly"])

    ts = int(time.time())
    report = build_report(metrics, anoms, history, cfg, collected_at=ts)

    # persist history snapshot (metrics only, compact)
    store.append_snapshot(history_path, {"ts": ts, "metrics": metrics})
    store.trim_history(history_path, cfg["collect"].get("history_keep_days", 90))

    store.write_json(os.path.join(OUT_DIR, "latest.json"), report)
    if not args.json_only:
        with open(os.path.join(OUT_DIR, "report.md"), "w", encoding="utf-8") as f:
            f.write(render_markdown(report))
        with open(os.path.join(OUT_DIR, "dashboard.html"), "w", encoding="utf-8") as f:
            f.write(render_dashboard(report))

    print(f"   anomalies: {len(anoms)} ({', '.join(a['metric'] for a in anoms[:5]) or 'none'})")
    print(f"   outputs written to {OUT_DIR}/")
    print(f"   dashboard: file://{os.path.join(OUT_DIR, 'dashboard.html')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
