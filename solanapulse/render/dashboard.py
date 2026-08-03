"""Render the report as a single-file, self-contained interactive HTML dashboard.

Design goals:
- Dark theme (per the listing's preference)
- Zero external dependencies: no CDN, no frameworks — inline CSS/JS only
- Interactive: hover tooltips on sparklines, collapsible sections, live filters
- Embeds the full latest.json so the file is portable (works offline)
"""

from __future__ import annotations

import html as _html
import json
from typing import Any


def render_dashboard(report: dict[str, Any]) -> str:
    data_json = json.dumps(report, default=str)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(str(report.get('config', {}).get('refresh_interval_min') and 'Solana Pulse'))} · Solana Ecosystem Report</title>
<style>
:root {{
  --bg: #0b0e14; --panel: #12161f; --panel2: #181d29; --border: #232a3a;
  --text: #dce3f0; --muted: #7c8698; --accent: #00d4a0; --warn: #ffb454;
  --crit: #ff5c5c; --info: #4aa8ff;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text); font: 14px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; padding: 24px; }}
header {{ display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }}
h1 {{ font-size: 22px; letter-spacing: -0.02em; }}
h1 .dot {{ color: var(--accent); }}
.sub {{ color: var(--muted); font-size: 13px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-bottom: 20px; }}
.card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }}
.card .k {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }}
.card .v {{ font-size: 20px; font-weight: 650; margin-top: 4px; font-variant-numeric: tabular-nums; }}
.card .d {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
.up {{ color: var(--accent); }} .down {{ color: var(--crit); }} .flat {{ color: var(--muted); }}
.banner {{ border-left: 4px solid var(--accent); background: var(--panel2); border-radius: 6px; padding: 12px 16px; margin-bottom: 20px; }}
.banner.warn {{ border-color: var(--warn); }} .banner.crit {{ border-color: var(--crit); }}
.banner .t {{ font-weight: 650; }}
section {{ margin-bottom: 24px; }}
h2 {{ font-size: 15px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px; }}
table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--border); font-variant-numeric: tabular-nums; }}
th {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; background: var(--panel2); }}
tr:last-child td {{ border-bottom: none; }}
td.num, th.num {{ text-align: right; }}
.spark {{ width: 100%; height: 36px; display: block; }}
.mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }}
.badge {{ display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }}
.badge.good {{ background: rgba(0,212,160,.12); color: var(--accent); }}
.badge.warn {{ background: rgba(255,180,84,.12); color: var(--warn); }}
.badge.crit {{ background: rgba(255,92,92,.12); color: var(--crit); }}
details {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; }}
summary {{ cursor: pointer; font-weight: 600; }}
.hero {{ display: flex; align-items: center; gap: 20px; background: linear-gradient(135deg, var(--panel), var(--panel2)); border: 1px solid var(--border); border-radius: 12px; padding: 18px 22px; margin-bottom: 20px; }}
.hero .score {{ font-size: 46px; font-weight: 800; line-height: 1; font-variant-numeric: tabular-nums; }}
.hero .spark {{ width: 220px; height: 44px; margin-left: auto; }}
.bar {{ height: 6px; border-radius: 3px; background: var(--accent); display: inline-block; vertical-align: middle; }}
.barwrap {{ background: var(--panel2); border-radius: 3px; height: 6px; width: 100%; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
@media (max-width: 800px) {{ .two {{ grid-template-columns: 1fr; }} }}
footer {{ color: var(--muted); font-size: 12px; margin-top: 32px; border-top: 1px solid var(--border); padding-top: 12px; }}
</style>
</head>
<body>
<div id="app"></div>
<script>
const DATA = {data_json};
const $ = (s) => document.getElementById(s);
const fmt = (x, d=2) => x==null ? 'n/a' : Number(x).toLocaleString(undefined, {{minimumFractionDigits: d, maximumFractionDigits: d}});
const usd = (x) => x==null ? 'n/a' : '$' + fmt(x);
const pct = (x) => x==null ? 'n/a' : (x>0?'+':'') + fmt(x,2) + '%';
const pctCls = (x) => x==null ? 'flat' : (x>0 ? 'up' : (x<0 ? 'down' : 'flat'));
const sevIcon = {{critical:'🔴', warning:'🟠', info:'🔵'}};

function sparkline(values, w=280, h=36) {{
  if (!values || values.length < 2) return '<div class="spark"></div>';
  const mn = Math.min(...values), mx = Math.max(...values), rng = (mx-mn)||1;
  const pts = values.map((v,i) => [i/(values.length-1)*w, h-2-((v-mn)/rng)*(h-4)]);
  const path = pts.map((p,i) => (i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');
  const last = pts[pts.length-1];
  const grad = '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00d4a0" stop-opacity=".35"/><stop offset="1" stop-color="#00d4a0" stop-opacity="0"/></linearGradient></defs>';
  return `<svg class="spark" viewBox="0 0 ${{w}} ${{h}}" preserveAspectRatio="none"><g>${{grad}}<path d="${{path}} L${{w}},${{h}} L0,${{h}} Z" fill="url(#g)"/><path d="${{path}}" fill="none" stroke="#00d4a0" stroke-width="1.6"/><circle cx="${{last[0].toFixed(1)}}" cy="${{last[1].toFixed(1)}}" r="2.4" fill="#00d4a0"/></g></svg>`;
}}

function seriesOf(path) {{
  const out = [];
  for (const s of DATA.history || []) {{
    let node = s;
    for (const k of path) {{ if (!node || typeof node !== 'object') {{ node = undefined; break; }} node = node[k]; }}
    if (typeof node === 'number' && isFinite(node)) out.push(node);
  }}
  return out;
}}

function render() {{
  const net = DATA.network, val = DATA.validators, eco = DATA.economics, fees = DATA.fees;
  const anoms = DATA.anomalies || [];
  const tps = net.tps||{{}}, slot = net.slot_time_sec||{{}}, ep = net.epoch||{{}};
  const cards = [
    {{k:'Avg TPS', v: fmt(tps.avg,0), d: 'peak '+fmt(tps.max,0), spark: seriesOf(['metrics','tps','avg'])}},
    {{k:'Slot time', v: fmt(slot.avg,4)+'s', d: 'target <0.6s', spark: seriesOf(['metrics','slot_time_sec','avg'])}},
    {{k:'Epoch '+ep.number, v: fmt(ep.progress_pct,1)+'%', d: fmt(ep.slots_remaining,0)+' slots left'}},
    {{k:'Validators', v: val.active_count, d: val.delinquent_count+' delinquent · '+fmt(val.delinquent_stake_pct,2)+'% stake'}},
    {{k:'SOL price', v: usd(eco.sol_price_usd), d: '<span class="'+pctCls(eco.sol_price_24h_change_pct)+'">'+pct(eco.sol_price_24h_change_pct)+' 24h</span>', spark: seriesOf(['metrics','economics','sol_price_usd'])}},
    {{k:'TVL', v: usd(eco.tvl_usd), d: '<span class="'+pctCls(eco.tvl_24h_change_pct)+'">'+pct(eco.tvl_24h_change_pct)+' 24h</span>', spark: seriesOf(['metrics','economics','tvl_usd'])}},
    {{k:'DEX volume 24h', v: usd(eco.dex_volume_24h_usd), d: '<span class="'+pctCls(eco.dex_volume_24h_change_pct)+'">'+pct(eco.dex_volume_24h_change_pct)+' vs 48h</span>'}},
    {{k:'Stablecoin supply', v: usd(eco.stablecoin_supply_usd), d: 'on Solana'}},
    {{k:'Median tx fee', v: fees.median_fee_sol ? fmt(fees.median_fee_sol,9)+' SOL' : 'n/a', d: fmt(fees.median_fee_lamports,0)+' lamports'}},
    {{k:'Est. fee rev 24h', v: fmt(fees.rev_est_24h_sol,0)+' SOL', d: fees.method || ''}},
    {{k:'Health', v: net.health || 'n/a', d: 'RPC endpoint'}},
  ];

  let html = `<header><div><h1><span class="dot">●</span> Solana Pulse <span style="color:var(--muted);font-weight:400;font-size:14px">· Solana Ecosystem Report</span></h1><div class="sub">Generated ${{DATA.generated_at}} UTC · refresh ${{DATA.config.refresh_interval_min}}m · keyless · stdlib-only</div></div></header>`;

  const hs = DATA.health_score;
  if (hs) {{
    const gcol = {{excellent:'#00d4a0', good:'#4aa8ff', fair:'#ffb454', 'at-risk':'#ff8c5c', critical:'#ff5c5c'}}[hs.grade] || '#00d4a0';
    html += `<div class="hero"><div class="score" style="color:${{gcol}}">${{hs.score}}</div><div><div class="k">Solana Health Score · <span style="color:${{gcol}};text-transform:uppercase">${{hs.grade}}</span></div><div style="font-size:12px;color:var(--muted);margin-top:4px">${{Object.entries(hs.components).map(([k,v])=>`${{k}} ${{v}}`).join(' · ')}}</div></div><div class="spark">${{sparkline(seriesOf(['metrics','health_score']), 220, 44)}}</div></div>`;
  }}

  html += '<div class="grid">' + cards.map(c => `<div class="card"><div class="k">${{c.k}}</div><div class="v">${{c.v}}</div><div class="d">${{c.d||''}}</div>${{c.spark?sparkline(c.spark):''}}</div>`).join('') + '</div>';

  if (anoms.length) {{
    html += anoms.map(a => `<div class="banner ${{a.severity==='warning'?'warn':a.severity==='critical'?'crit':''}}"><span class="t">${{sevIcon[a.severity]}} ${{a.metric}}</span> — ${{a.message}}</div>`).join('');
  }} else {{
    html += '<div class="banner"><span class="t">✅ No anomalies detected</span> — all monitored metrics within normal range.</div>';
  }}

  html += '<section><h2>Validators · Top 20 by stake</h2><table><tr><th>#</th><th>Vote account</th><th class="num">Stake (SOL)</th><th class="num">Commission</th></tr>';
  (val.top_by_stake||[]).forEach((v,i) => {{ html += `<tr><td>${{i+1}}</td><td class="mono">${{(v.pubkey||'').slice(0,8)}}…</td><td class="num">${{fmt(v.stake_sol,0)}}</td><td class="num">${{fmt(v.commission_pct,0)}}%</td></tr>`; }});
  html += '</table></section>';

  const simd = DATA.news?.simd || [];
  if (simd.length) {{
    html += '<section><h2>Development news · SIMD proposals</h2>' + simd.map(s => `<details><summary>#${{s.number}} ${{s.title}}</summary><div class="sub">${{(s.labels||[]).map(l=>'<span class="badge good">'+l+'</span>').join(' ')}}
    <a href="${{s.url}}" style="color:var(--info)">open ↗</a></div></details>`).join('') + '</section>';
  }}

  const sp = DATA.status_page;
  if (sp) html += `<section><h2>Network status</h2><div class="card"><div class="k">${{sp.page_name}}</div><div class="v">${{sp.indicator}}</div><div class="d">${{sp.description}}</div></div></section>`;

  html += '<section><h2>Data sources</h2><table><tr><th>Source</th><th>Status</th></tr>' + Object.entries(DATA.sources_ok||{{}}).map(([k,v]) => `<tr><td>${{k}}</td><td><span class="badge ${{v?'good':'crit'}}">${{v?'online':'failed'}}</span></td></tr>`).join('') + '</table></section>';

  const comp = DATA.comparison;
  if (comp && comp.chains && comp.chains.length) {{
    const maxTvl = Math.max(...comp.chains.map(c => comp.tvl[c]||0), 1);
    html += '<section><h2>Cross-chain comparison</h2><table><tr><th>Chain</th><th>TVL</th><th class="num">DEX 24h</th><th class="num">Stablecoins</th></tr>';
    comp.chains.forEach(c => {{
      const tvl = comp.tvl[c]||0, d = comp.dex[c]||{{}}, sc = comp.stablecoins[c]||0;
      html += `<tr><td>${{c}} ${{c==='Solana'?'<span class="badge good">us</span>':''}}</td><td><div class="barwrap"><div class="bar" style="width:${{Math.max((tvl/maxTvl*100),1).toFixed(1)}}%"></div></div><span style="font-size:12px;color:var(--muted)">${{usd(tvl)}}</span></td><td class="num">${{usd(d.volume24h)}}</td><td class="num">${{usd(sc)}}</td></tr>`;
    }});
    html += '</table></section>';
  }}

  const bl = DATA.baselines;
  if (bl && Object.keys(bl).length) {{
    html += '<section><h2>Baselines · 30-day history</h2><table><tr><th>Metric</th><th class="num">Current</th><th class="num">Median</th><th class="num">Percentile</th></tr>';
    Object.values(bl).forEach(b => {{
      const cls = b.percentile==null ? 'flat' : (b.percentile>=90||b.percentile<=10) ? 'down' : (b.percentile>=50 ? 'up' : 'flat');
      html += `<tr><td>${{b.label}}</td><td class="num">${{fmt(b.current,2)}}</td><td class="num">${{fmt(b.median,2)}}</td><td class="num ${{cls}}">${{b.percentile==null?'n/a':b.percentile+'th'}}</td></tr>`;
    }});
    html += '</table></section>';
  }}

  html += '<footer>solana-pulse · single-file dashboard (no external dependencies) · data: Solana RPC, DeFiLlama, CoinGecko, GitHub SIMD, status.solana.com · machine-readable <span class="mono">latest.json</span> &amp; <span class="mono">report.md</span> in <span class="mono">outputs/</span></footer>';
  $('app').innerHTML = html;
}}
render();
</script>
</body>
</html>"""
