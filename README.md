# 👁 Solana Eye

**Auto-updating Solana ecosystem report & interactive dashboard.**

A zero-dependency (Python stdlib only) pipeline that keeps an eye on the Solana
network — performance, validators, economics, news — detects anomalies, and
renders three outputs: an interactive HTML dashboard, a human-readable
Markdown report, and a machine-readable JSON snapshot. It refreshes
automatically every hour via GitHub Actions (live demo) or a local systemd timer.

**Live dashboard:** https://sharkwon.github.io/solana-eye/
(self-updating hourly — no server, CI is the cron)

## Why

Solana ecosystem data is scattered across RPC endpoints, analytics dashboards, and
news sources. This project pulls it all into one automatically-refreshing view:

- **Network performance** — TPS, non-vote TPS, slot time, block height, epoch progress
- **Validators** — active/delinquent counts, stake distribution, top 20 by stake,
  average commission, Nakamoto coefficient (decentralization), delinquency alerts
- **Economics** — SOL price (CoinGecko), TVL & DEX volume (DeFiLlama),
  stablecoin supply, median transaction fee and estimated fee revenue (on-chain sampling)
- **Ecosystem growth** — daily active addresses + tokenized equities volume/AUM
  (optional Dune Analytics)
- **Community news** — X/Twitter posts from key ecosystem accounts (keyless)
- **Development news** — recently-updated SIMD proposals (Solana's upgrade pipeline)
- **Upgrade radar** — tracks upcoming protocol upgrades: keyword scan of the SIMD repo
  (Alpenglow/Votor/Firedancer...), a pinned SIMD watchlist (e.g. SIMD-525) with live
  open/merged state, and the latest Agave client releases
- **Network status** — incidents from status.solana.com
- **Anomaly detection** — threshold rules + statistical z-scores against history

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│  sources/         keyless, stdlib-only, per-source resilience   │
│  ├─ rpc.py        Solana JSON-RPC (public endpoint, swappable)  │
│  ├─ defillama.py  TVL · DEX volume · stablecoins · TVL history  │
│  ├─ coingecko.py  SOL price + 24h change                        │
│  ├─ simd_news.py  GitHub SIMD proposals · status.solana.com     │
│  ├─ upgrades.py   upgrade radar: SIMD keyword scan, watchlist,  │
│  │                Agave client releases                         │
│  ├─ twitter.py    X/Twitter community news (Nitter RSS keyless,  │
│  │                multi-instance failover + optional bearer)     │
│  └─ dune.py       DAU + tokenized equities (DUNE_API_KEY)       │
│                                                                │
│  metrics.py       raw data → computed metrics (pure functions)  │
│  anomaly.py       threshold rules + z-score detection (pure)    │
│  report.py        one source-of-truth report dict               │
│  render/          markdown.py · dashboard.py (single-file HTML) │
│  store.py         history.jsonl persistence (powers z-scores)   │
│                                                                │
│  run.py           orchestrator: collect → compute → detect →    │
│                   render → persist                              │
└────────────────────────────────────────────────────────────────┘
```

## Quickstart

```bash
git clone https://github.com/sharkwon/solana-eye.git
cd solana-eye
python3 run.py            # collect + render (no pip install needed)
# outputs written to outputs/:
#   dashboard.html  interactive dark-theme dashboard
#   report.md       human-readable markdown
#   latest.json     machine-readable JSON
```

**Requirements:** Python 3.10+ and internet access. No virtualenv, no requirements.txt,
no API keys. (The Python package is named `solanapulse` internally — the product is
Solana Eye.)

### Run it continuously

**Option A — GitHub Actions (zero infrastructure).** Push the repo; the
workflow re-runs the pipeline hourly and publishes the result to GitHub Pages
automatically. Enable Pages → Deploy from branch → main → `/docs`.

**Option B — local systemd timer (true self-hosting):**

```bash
bash scripts/install_service.sh      # hourly refresh, survives reboots
systemctl --user list-timers solana-eye.timer
```

**Option C — plain cron:**

```bash
17 * * * * cd /path/to/solana-eye && python3 run.py >> outputs/cron.log 2>&1
```

## Data sources & automation strategy

| Source | Endpoint | Key? | Used for |
|---|---|---|---|
| Solana RPC | api.mainnet-beta.solana.com | no | health, epoch, TPS samples, vote accounts (incl. Nakamoto), supply, fee sampling |
| DeFiLlama | api.llama.fi · stablecoins.llama.fi | no | TVL (+history), DEX volume, stablecoin supply |
| CoinGecko | api.coingecko.com/api/v3 | no | SOL price, 24h change |
| GitHub | api.github.com/repos/solana-foundation/simd | no | active SIMD proposals + upgrade radar (Alpenglow keyword scan, watched SIMDs, Agave releases) |
| X / Twitter | Nitter RSS (nitter.net, keyless) · api.twitter.com/2 (optional) | `TWITTER_BEARER_TOKEN` env (optional) | community news from @solana, @SolanaFndn, @SolanaFloor, … |
| status.solana.com | statuspage API | no | incident status |
| Dune (optional) | api.dune.com/api/v1 | `DUNE_API_KEY` env | daily active addresses, tokenized equities volume/AUM |

**Design decisions:**

- **Keyless by default.** The public Solana RPC + free analytics APIs cover every
  headline metric with no signup. A custom RPC URL can be swapped in
  (`config.json` → `rpc.url`) for heavier deployments; Dune bolts on via an env var when enabled.
- **Per-source resilience.** Every collector is independently guarded — one failing
  source degrades gracefully (recorded in the sources table) instead of killing the run.
- **Fee & REV from on-chain truth.** Median transaction fee is computed by sampling
  recent blocks' `meta.fee` (not assumed); estimated 24h fee revenue follows from the
  same sample. Methods are labelled as estimates in the output.
- **Polling, not webhooks** — a cron-driven pipeline with no inbound surface.

## Anomaly detection

Two layers, both pure and unit-tested (`tests/`):

- **Threshold rules** (domain knowledge): slot time > 0.6s · delinquent stake > 5% ·
  TVL/price/DEX-volume moves beyond ±5% in 24h · low DAU / tokenized-equities stall ·
  Nakamoto coefficient < 5 (stake concentration) · status-page incidents.
- **Statistical z-scores**: current value vs. the metric's own history (min 5 samples,
  |z| ≥ 3 flagged). A flat history with a deviating value is treated as a strong
  anomaly rather than an invisible one.

All thresholds are tunable in `config.json` → `anomaly`. Anomalies surface in every
output format and are the first thing judges/readers see.

## Outputs

### Interactive dashboard (dashboard.html)

Single self-contained file — dark theme, inline CSS/JS, zero external dependencies
(no CDN, works offline). Includes:

- Animated KPI counters with sparklines and a radial health gauge (animated stroke)
- Price & TVL chart with hover crosshair + 7H/24H/7D windows
- Stake-distribution donut plus the Nakamoto coefficient
- Ecosystem Growth cards (daily active addresses, tokenized equities volume/AUM/holders)
- Sortable + filterable validator table (click column headers, type to filter)
- Anomaly banner with severity chips (value + z-score tooltips) and an empty state when all clear
- News tabs — SIMD proposals ⇄ X/Twitter community posts
- Upgrade Radar panel — upcoming upgrades (Alpenglow & co. via keyword scan,
  pinned watchlist with open/merged chips) + latest Agave client releases
- Live freshness ticker that keeps "synced X ago" current without a reload
- Accessibility: `prefers-reduced-motion` support, keyboard-focusable filter, responsive grid

### Markdown report (report.md)

Human-readable summary for quick skimming / pasting into docs or Telegram.

### JSON (latest.json)

Structured machine-readable snapshot (`schema_version: 1`): network, validators
(incl. Nakamoto coefficient + stake distribution), fees, economics, ecosystem growth,
news (SIMD + Twitter), anomalies, history (last 24 snapshots for downstream tooling).

## Testing

```bash
python3 -m unittest discover tests   # 20 tests, no deps
```

Pure-function design (metrics, anomaly, renderers) keeps the test suite fast and
meaningful: fixtures exercise TPS math, validator percentages, z-score edge cases
(flat history, insufficient history), and output-format invariants.

## Extending

- **New metric** → add a source function, a row in `collect()`, a field in
  `compute_metrics()`, a threshold in `config.json`, and it flows to all three outputs.
- **New output format** → build it from `report.build_report()` (single source of truth).
- **Heavier deployments** → point `rpc.url` at Helius/Triton/QuickNode and enable Dune.

## License

MIT — see LICENSE. Data © respective sources (Solana Labs, DeFiLlama,
CoinGecko, GitHub, status.solana.com); this project is an independent community tool.
