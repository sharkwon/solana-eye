"""Solana Eye dashboard template (plain string; __DATA_JSON__ injected).

v3 design: dark, alive, intuitive.
- Custom Solana Eye logo (gradient eye SVG) + favicon (data URI, self-contained)
- Aurora ambient background (slow-drifting teal/violet/blue glows)
- Glass cards (blur, gradient border on hover), count-up numbers, glow sparklines
- Live ticker strip (SOL/TPS/TVL/...) that pauses on hover
- Price & TVL area chart with animated draw + hover crosshair tooltip + 7H/24H/7D tabs
- Network Health radial gauge + Stake distribution donut (right column)
- Rank-medal validator table, SIMD news, source health
- English copy everywhere
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Solana Eye · Solana Ecosystem Report</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0' stop-color='%2314F1B2'/%3E%3Cstop offset='1' stop-color='%239945FF'/%3E%3C/linearGradient%3E%3C/defs%3E%3Cpath d='M3 24C12 8 36 8 45 24C36 40 12 40 3 24Z' fill='%2312151C' stroke='url(%23g)' stroke-width='2.5'/%3E%3Ccircle cx='24' cy='24' r='10' fill='url(%23g)'/%3E%3Ccircle cx='24' cy='24' r='4.4' fill='%230B0E14'/%3E%3Ccircle cx='21' cy='20.6' r='1.7' fill='%23fff' opacity='.9'/%3E%3C/svg%3E">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

  :root{
    --bg:#07090F; --surface:#0E1219; --surface-2:#141A26; --surface-3:#1A2230;
    --border:#1E2637; --border-2:#2A3550;
    --text:#E8ECF4; --text-dim:#8B93A7; --text-faint:#565E72;
    --teal:#14F1B2; --violet:#9945FF; --blue:#3B82F6;
    --danger:#FF5C6C; --warning:#FFB020;
    --grad:linear-gradient(90deg,var(--teal),var(--violet));
    --shadow:0 10px 30px -12px rgba(0,0,0,.6);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{
    background:var(--bg); color:var(--text);
    font:14.5px/1.55 'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    display:flex; min-height:100vh; overflow-x:hidden;
    -webkit-font-smoothing:antialiased;
  }
  ::selection{background:var(--teal);color:#07090F}
  ::-webkit-scrollbar{width:9px;height:9px}
  ::-webkit-scrollbar-thumb{background:var(--surface-3);border-radius:6px}
  ::-webkit-scrollbar-track{background:transparent}

  /* ambient aurora */
  .aurora{position:fixed;inset:0;z-index:-1;pointer-events:none;overflow:hidden}
  .aurora i{position:absolute;border-radius:50%;filter:blur(90px);opacity:.16}
  .aurora .a1{width:520px;height:520px;background:var(--teal);top:-160px;left:-120px;animation:drift 26s ease-in-out infinite alternate}
  .aurora .a2{width:620px;height:620px;background:var(--violet);bottom:-220px;right:-160px;animation:drift 32s ease-in-out infinite alternate-reverse}
  .aurora .a3{width:420px;height:420px;background:var(--blue);top:40%;left:55%;animation:drift 38s ease-in-out infinite alternate}
  @keyframes drift{from{transform:translate(0,0) scale(1)}to{transform:translate(60px,40px) scale(1.15)}}

  .mono{font-family:'JetBrains Mono',ui-monospace,Menlo,monospace}

  /* ---------- sidebar ---------- */
  .sidebar{
    width:236px; flex-shrink:0; position:sticky; top:0; height:100vh;
    display:flex; flex-direction:column; gap:26px;
    background:linear-gradient(180deg,rgba(14,18,25,.92),rgba(10,13,19,.96));
    border-right:1px solid var(--border); padding:22px 14px;
    backdrop-filter:blur(14px); z-index:20;
  }
  .brand{display:flex;align-items:center;gap:11px;padding:0 6px}
  .brand .logo{filter:drop-shadow(0 0 10px rgba(20,241,178,.35));flex:none}
  .brand .nm{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:17px;letter-spacing:-.02em;line-height:1.1}
  .brand .nm small{display:block;font-family:'Inter',sans-serif;font-size:9.5px;font-weight:600;color:var(--text-faint);letter-spacing:.22em;text-transform:uppercase}
  nav{display:flex;flex-direction:column;gap:3px}
  .nav-item{
    display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:10px;
    color:var(--text-dim);font-size:13.5px;font-weight:500;text-decoration:none;
    transition:.16s;position:relative;
  }
  .nav-item svg{width:17px;height:17px;flex:none;opacity:.85}
  .nav-item:hover{background:var(--surface-2);color:var(--text)}
  .nav-item.active{background:linear-gradient(90deg,rgba(20,241,178,.09),rgba(153,69,255,.09));color:var(--text);box-shadow:inset 0 0 0 1px var(--border)}
  .nav-item.active::before{content:'';position:absolute;left:0;top:20%;bottom:20%;width:3px;border-radius:3px;background:var(--grad)}
  .nav-item.active svg{color:var(--teal)}
  .side-health{margin-top:auto;background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px;display:flex;align-items:center;gap:12px}
  .side-health .gh{width:52px;height:52px;flex:none}
  .side-health .t{font-size:10.5px;font-weight:700;letter-spacing:.1em;color:var(--text-faint);text-transform:uppercase}
  .side-health .s{font-family:'JetBrains Mono',monospace;font-size:19px;font-weight:600;margin-top:2px}
  .side-health .g{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
  .side-foot{font-size:10.5px;color:var(--text-faint);line-height:1.7;padding:0 6px}

  /* ---------- main ---------- */
  .main{flex:1;min-width:0;padding:0 30px 52px}
  .ticker{
    display:flex;align-items:center;gap:14px;margin:18px 0 0;
    background:linear-gradient(90deg,rgba(20,241,178,.06),rgba(153,69,255,.06));
    border:1px solid var(--border);border-radius:12px;padding:9px 16px;overflow:hidden;
  }
  .ticker .tl{font-size:10px;font-weight:800;letter-spacing:.14em;color:var(--text-faint);text-transform:uppercase;flex:none}
  .ticker .track{display:flex;gap:34px;width:max-content;animation:scroll 36s linear infinite}
  .ticker:hover .track{animation-play-state:paused}
  @keyframes scroll{to{transform:translateX(-50%)}}
  .tick-item{font-family:'JetBrains Mono',monospace;font-size:12.5px;color:var(--text-dim);white-space:nowrap}
  .tick-item b{color:var(--text);font-weight:600}
  .tick-item .up{color:var(--teal)}.tick-item .down{color:var(--danger)}

  .topbar{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;margin:26px 0 20px;flex-wrap:wrap}
  .topbar h1{font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:700;letter-spacing:-.03em;background:var(--grad);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
  .topbar .sub{color:var(--text-dim);font-size:12.5px;margin-top:4px}
  .topbar .sub b{color:var(--text)}
  .live-pill{display:inline-flex;align-items:center;gap:8px;background:var(--surface);border:1px solid var(--border);padding:7px 14px;border-radius:100px;font-size:12px;color:var(--text-dim)}
  .live-pill .pulse{width:7px;height:7px;border-radius:50%;background:var(--teal);animation:pulse 1.8s infinite}
  @keyframes pulse{0%{box-shadow:0 0 0 0 rgba(20,241,178,.55)}70%{box-shadow:0 0 0 7px rgba(20,241,178,0)}100%{box-shadow:0 0 0 0 rgba(20,241,178,0)}}

  /* ---------- anomaly chips ---------- */
  .anomaly-banner{display:flex;gap:10px;overflow-x:auto;margin-bottom:20px;padding-bottom:2px}
  .anomaly-chip{
    flex-shrink:0;display:flex;align-items:center;gap:8px;
    background:rgba(255,92,108,.08);border:1px solid rgba(255,92,108,.35);
    color:#FF9BA5;padding:8px 14px;border-radius:10px;font-size:12px;font-weight:500;white-space:nowrap;
  }
  .anomaly-chip.warn{background:rgba(255,176,32,.08);border-color:rgba(255,176,32,.35);color:#FFCB6B}
  .anomaly-chip.info{background:rgba(59,130,246,.09);border-color:rgba(59,130,246,.4);color:#8FB8FF}
  .anomaly-chip.ok{background:rgba(20,241,178,.06);border-color:rgba(20,241,178,.25);color:#7DF5D6}
  .anomaly-chip b{font-weight:650}
  .anom-val,.anom-z{opacity:.85;font-size:10.5px}
  .anom-z{color:var(--violet)}
  .nk-row{margin-top:6px;color:var(--text-dim)}
  .nk-row b{color:var(--warning);font-family:'JetBrains Mono',monospace}
  .nk-hint{color:var(--text-faint);font-size:10.5px}

  /* ---------- KPI ---------- */
  .kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:20px}
  .kpi-card{
    position:relative;overflow:hidden;border-radius:16px;padding:16px 18px;
    background:linear-gradient(160deg,var(--surface),var(--surface-2));
    border:1px solid var(--border);transition:.22s;
  }
  .kpi-card::after{content:'';position:absolute;inset:0;border-radius:16px;padding:1px;background:linear-gradient(140deg,rgba(20,241,178,.5),rgba(153,69,255,.4));-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:0;transition:.22s;pointer-events:none}
  .kpi-card:hover{transform:translateY(-3px);border-color:var(--border-2)}
  .kpi-card:hover::after{opacity:1}
  .kpi-card .label{color:var(--text-dim);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em}
  .kpi-card .value{font-family:'JetBrains Mono',monospace;font-size:23px;font-weight:600;margin-top:8px;letter-spacing:-.01em}
  .kpi-card .delta{font-size:12px;margin-top:4px;font-weight:500}
  .delta.up{color:var(--teal)}.delta.down{color:var(--danger)}.delta.flat{color:var(--text-faint)}
  .kpi-card svg.spark{position:absolute;bottom:6px;right:8px;opacity:.95;filter:drop-shadow(0 0 6px rgba(20,241,178,.25))}

  /* ---------- panels ---------- */
  .content-grid{display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:16px}
  .panel{
    background:linear-gradient(160deg,var(--surface),var(--surface-2));
    border:1px solid var(--border);border-radius:18px;padding:20px;
    box-shadow:var(--shadow);transition:border-color .2s;
  }
  .panel:hover{border-color:var(--border-2)}
  .panel-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px}
  .panel-head h3{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:600}
  .panel-head .tabs{display:flex;gap:4px;background:var(--surface-3);padding:3px;border-radius:9px}
  .panel-head .tab{padding:5px 12px;font-size:11.5px;border-radius:7px;color:var(--text-dim);cursor:pointer;transition:.15s;border:1px solid transparent}
  .panel-head .tab:hover{color:var(--text)}
  .panel-head .tab.active{background:var(--bg);color:var(--teal);border-color:var(--border-2)}
  .chart-wrap{position:relative;height:210px;cursor:crosshair}
  .chart-wrap .grid-line{stroke:var(--border);stroke-width:1}
  .chart-wrap .xhair{stroke:var(--text-faint);stroke-width:1;stroke-dasharray:3 3;opacity:0;transition:opacity .1s}
  .chart-wrap:hover .xhair{opacity:1}
  .chart-legend{display:flex;gap:18px;font-size:11.5px;color:var(--text-dim);margin-top:10px}
  .chart-legend .lg{display:flex;align-items:center;gap:6px}
  .chart-legend .sw{width:9px;height:9px;border-radius:3px}
  .tt{
    position:absolute;pointer-events:none;background:rgba(10,13,19,.94);border:1px solid var(--border-2);
    border-radius:9px;padding:7px 11px;font-size:11.5px;font-family:'JetBrains Mono',monospace;
    box-shadow:var(--shadow);opacity:0;transition:opacity .12s;z-index:5;white-space:nowrap;
  }
  .tt .ttl{color:var(--text-faint);font-size:10px;text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px}
  .tt .row{display:flex;gap:8px;align-items:center}

  /* gauge + donut */
  .gauge-wrap{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
  .gauge{position:relative;width:120px;height:120px;flex:none}
  .gauge svg{transform:rotate(-90deg)}
  .gauge .gc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
  .gauge .gc .n{font-family:'JetBrains Mono',monospace;font-size:25px;font-weight:600}
  .gauge .gc .l{font-size:9px;color:var(--text-dim);letter-spacing:.1em;text-transform:uppercase;font-weight:700}
  .glist{display:flex;flex-direction:column;gap:8px;font-size:12px;flex:1;min-width:150px}
  .glist .grow{display:flex;align-items:center;gap:8px}
  .glist .grow .k{color:var(--text-dim);width:96px}
  .glist .grow .v{margin-left:auto;font-family:'JetBrains Mono',monospace;font-weight:600}
  .glist .bar{height:4px;border-radius:3px;background:var(--surface-3);overflow:hidden;flex:1}
  .glist .bar i{display:block;height:100%;border-radius:3px;background:var(--grad);width:0;transition:width 1.1s cubic-bezier(.2,.8,.2,1)}
  .donut-wrap{display:flex;align-items:center;gap:20px;flex-wrap:wrap}
  .donut{width:120px;height:120px;border-radius:50%;flex-shrink:0;background:conic-gradient(var(--teal) 0% var(--p1,50%),var(--violet) var(--p1,50%) 100%);display:flex;align-items:center;justify-content:center;position:relative;filter:drop-shadow(0 0 14px rgba(20,241,178,.15))}
  .donut::before{content:'';position:absolute;width:82px;height:82px;border-radius:50%;background:var(--surface)}
  .donut-center{position:relative;text-align:center;font-family:'JetBrains Mono',monospace}
  .donut-center .n{font-size:18px;font-weight:600}
  .donut-center .l{font-size:9px;color:var(--text-dim)}
  .legend{display:flex;flex-direction:column;gap:10px;font-size:12.5px}
  .legend .row{display:flex;align-items:center;gap:8px}
  .legend .sw{width:9px;height:9px;border-radius:3px}

  /* ---------- table ---------- */
  .sec{scroll-margin-top:14px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{text-align:left;color:var(--text-faint);font-weight:600;font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;padding:0 12px 10px;border-bottom:1px solid var(--border)}
  td{padding:10px 12px;border-bottom:1px solid var(--border)}
  tr:last-child td{border-bottom:none}
  tbody tr{transition:background .14s}
  tbody tr:hover{background:var(--surface-2)}
  td.num,th.num{text-align:right}
  .rank-badge{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:7px;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;background:var(--surface-3);color:var(--text-dim)}
  .rank-badge.r1{background:linear-gradient(135deg,#f7d774,#c9972b);color:#241a02}
  .rank-badge.r2{background:linear-gradient(135deg,#cdd6e4,#8b96a8);color:#11151c}
  .rank-badge.r3{background:linear-gradient(135deg,#e0a17a,#b06a3e);color:#2a1407}
  .vavatar{width:26px;height:26px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-family:'JetBrains Mono',monospace;font-size:10.5px;font-weight:600;background:linear-gradient(135deg,rgba(20,241,178,.18),rgba(153,69,255,.18));color:var(--teal);margin-right:9px;vertical-align:middle}
  .status-dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:6px;vertical-align:middle}
  .status-dot.ok{background:var(--teal);box-shadow:0 0 6px rgba(20,241,178,.6)}
  .status-dot.bad{background:var(--danger)}

  /* ---------- news & sources ---------- */
  .bottom-grid{display:grid;grid-template-columns:1.3fr 1fr;gap:16px}
  .news-item{padding:12px 2px;border-bottom:1px solid var(--border);cursor:pointer;transition:.15s;border-radius:8px}
  .news-item:hover{background:var(--surface-2);padding-left:10px;padding-right:10px}
  .news-item:last-child{border-bottom:none}
  .news-item .title{font-size:13px;font-weight:500}
  .news-item .meta{color:var(--text-faint);font-size:11px;margin-top:4px}
  .badge{display:inline-block;font-size:10px;padding:2px 7px;border-radius:5px;background:var(--surface-3);color:var(--text-dim);margin-right:6px;font-weight:600}
  .badge.teal{background:rgba(20,241,178,.1);color:var(--teal)}
  .badge.violet{background:rgba(153,69,255,.14);color:#c69bff}
  .source-row{display:flex;align-items:center;justify-content:space-between;padding:9px 2px;border-bottom:1px solid var(--border);font-size:12.5px}
  .source-row:last-child{border-bottom:none}
  .source-row .name{display:flex;align-items:center}
  .source-row .lat{color:var(--text-faint);font-family:'JetBrains Mono',monospace;font-size:11px}

  /* ---------- ecosystem growth ---------- */
  .growth-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}
  .growth-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:14px 16px;transition:.16s}
  .growth-card:hover{border-color:var(--border-2)}
  .growth-card .gc-label{font-size:11px;color:var(--text-dim);text-transform:uppercase;letter-spacing:.06em;font-weight:600}
  .growth-card .gc-value{font-size:22px;font-weight:650;margin-top:5px;font-variant-numeric:tabular-nums;font-family:'Space Grotesk',sans-serif}
  .growth-card .gc-sub{font-size:11px;color:var(--text-faint);margin-top:3px}
  .growth-card .gc-value.na{color:var(--text-faint);font-size:14px;font-weight:500;padding-top:6px}
  .sub-note{color:var(--text-faint);font-size:11px;font-weight:500}

  /* ---------- sortable / filterable table ---------- */
  .table-tools{margin-left:auto}
  .filter-input{background:var(--surface-2);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:6px 11px;font-size:12px;font-family:inherit;width:190px;outline:none;transition:.15s}
  .filter-input::placeholder{color:var(--text-faint)}
  .filter-input:focus{border-color:var(--teal);box-shadow:0 0 0 3px rgba(20,241,178,.12)}
  th[data-sort]{cursor:pointer;user-select:none;transition:.12s}
  th[data-sort]:hover{color:var(--teal)}
  th[data-sort] .sort-arrow{display:inline-block;width:0;height:0;margin-left:4px;border-left:4px solid transparent;border-right:4px solid transparent;opacity:.45;vertical-align:middle}
  th[data-sort].asc .sort-arrow{border-bottom:5px solid var(--teal);border-top:none;opacity:1}
  th[data-sort].desc .sort-arrow{border-top:5px solid var(--teal);border-bottom:none;opacity:1}
  .sortable tbody tr{transition:background .12s}
  .sortable tbody tr:hover{background:var(--surface-2)}

  footer{margin-top:26px;color:var(--text-faint);font-size:11.5px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;border-top:1px solid var(--border);padding-top:16px}
  footer b{color:var(--text-dim)}

  /* reveal */
  .rv{opacity:0;transform:translateY(14px);animation:rv .55s cubic-bezier(.2,.7,.3,1) forwards}
  @keyframes rv{to{opacity:1;transform:none}}
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

  @media (max-width:1120px){.kpi-grid{grid-template-columns:repeat(3,1fr)}.content-grid{grid-template-columns:1fr}.bottom-grid{grid-template-columns:1fr}}
  @media (max-width:780px){
    .sidebar{display:none}
    .kpi-grid{grid-template-columns:repeat(2,1fr)}
    .main{padding:0 14px 40px}
    .ticker .tl{display:none}
  }
</style>
</head>
<body>
<div class="aurora"><i class="a1"></i><i class="a2"></i><i class="a3"></i></div>
<aside class="sidebar">
  <div class="brand">
    <svg class="logo" width="34" height="34" viewBox="0 0 48 48" aria-hidden="true">
      <defs>
        <linearGradient id="lgI" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#14F1B2"/><stop offset="1" stop-color="#9945FF"/></linearGradient>
      </defs>
      <circle cx="24" cy="24" r="21" fill="url(#lgI)" opacity="0.10"/>
      <path d="M3 24C12 8 36 8 45 24C36 40 12 40 3 24Z" fill="#0E1219" stroke="url(#lgI)" stroke-width="2.5"/>
      <circle cx="24" cy="24" r="10.5" fill="url(#lgI)"/>
      <circle cx="24" cy="24" r="4.6" fill="#07090F"/>
      <circle cx="21.2" cy="20.8" r="1.8" fill="#fff" opacity=".9"/>
      <path d="M13 24h22" stroke="#fff" stroke-opacity=".14" stroke-width="1.4" stroke-dasharray="2 5"/>
    </svg>
    <div class="nm">Solana Eye<small>ecosystem watch</small></div>
  </div>

  <nav>
    <a class="nav-item active" href="#overview"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>Overview</a>
    <a class="nav-item" href="#validators"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/></svg>Validators</a>
    <a class="nav-item" href="#economics"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 17l5-6 4 3 6-8"/><path d="M15 6h3v3"/></svg>Economics</a>
    <a class="nav-item" href="#news"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 5h13v14H6a2 2 0 0 1-2-2V5z"/><path d="M17 8h3v9a2 2 0 0 1-2 2"/><path d="M7 9h7M7 12h7"/></svg>News (SIMD)</a>
    <a class="nav-item" href="#anomalies"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 3l9 16H3l9-16z"/><path d="M12 10v4M12 17.5v.5"/></svg>Anomalies</a>
    <a class="nav-item" href="#sources"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/></svg>Sources</a>
  </nav>

  <div class="side-health" id="sideHealth"></div>
  <div class="side-foot">schema_version 1 · refreshed hourly via GitHub Actions<br>MIT · data © respective sources</div>
</aside>

<main class="main">

  <div class="ticker rv"><span class="tl">Live tape</span><div class="track" id="tickerTrack"></div></div>

  <div class="topbar rv" id="overview" style="animation-delay:.06s">
    <div>
      <h1>Solana Ecosystem Report</h1>
      <div class="sub" id="topbarSub">loading…</div>
    </div>
    <div class="live-pill"><span class="pulse"></span> <span id="livePill">Live</span></div>
  </div>

  <div class="anomaly-banner rv" id="anomBanner" style="animation-delay:.1s"></div>
  <div class="kpi-grid rv" id="kpiGrid" style="animation-delay:.14s"></div>

  <div class="content-grid" id="economics">
    <div class="panel rv">
      <div class="panel-head">
        <h3>Price &amp; TVL</h3>
        <div class="tabs" id="chartTabs">
          <div class="tab" data-w="7">7H</div>
          <div class="tab active" data-w="24">24H</div>
          <div class="tab" data-w="168">7D</div>
        </div>
      </div>
      <div class="chart-wrap" id="chartWrap"></div>
      <div class="chart-legend" id="chartLegend"></div>
    </div>

    <div style="display:flex;flex-direction:column;gap:16px">
      <div class="panel rv" style="animation-delay:.1s">
        <div class="panel-head"><h3>Network Health</h3></div>
        <div class="gauge-wrap" id="gaugeWrap"></div>
      </div>
      <div class="panel rv" style="animation-delay:.16s">
        <div class="panel-head"><h3>Stake Distribution</h3></div>
        <div class="donut-wrap" id="donutWrap"></div>
      </div>
    </div>
  </div>

  <div class="panel sec rv" id="growth" style="margin-bottom:16px">
    <div class="panel-head"><h3>Ecosystem Growth</h3><span class="sub-note" id="growthNote">Dune Analytics</span></div>
    <div class="growth-grid" id="growthGrid"></div>
  </div>

  <div class="panel sec rv" id="validators" style="margin-bottom:16px">
    <div class="panel-head">
      <h3>Top Validators by Stake</h3>
      <div class="table-tools">
        <input class="filter-input" id="valFilter" type="text" placeholder="Filter validator…" aria-label="Filter validators">
      </div>
    </div>
    <table class="sortable">
      <thead><tr>
        <th>#</th>
        <th>Validator</th>
        <th class="num" data-sort="stake_sol">Stake (SOL) <span class="sort-arrow"></span></th>
        <th class="num" data-sort="stake_pct">Stake % <span class="sort-arrow"></span></th>
        <th class="num" data-sort="commission_pct">Commission <span class="sort-arrow"></span></th>
        <th class="num">Status</th>
      </tr></thead>
      <tbody id="valTbody"></tbody>
    </table>
  </div>

  <div class="bottom-grid">
    <div class="panel sec rv" id="news">
      <div class="panel-head"><h3>Ecosystem News</h3>
        <div class="tabs" id="newsTabs">
          <div class="tab active" data-news="simd">SIMD</div>
          <div class="tab" data-news="twitter">X / Twitter</div>
        </div>
      </div>
      <div id="newsList"></div>
    </div>
    <div class="panel sec rv" id="sources" style="animation-delay:.08s">
      <div class="panel-head"><h3>Data Source Health</h3></div>
      <div id="srcList"></div>
    </div>
  </div>

  <footer class="rv">
    <span><b>Solana Eye</b> · zero-dependency · keyless · Python stdlib</span>
    <span>schema_version 1 · MIT License</span>
  </footer>

</main>

<script>
const DATA = __DATA_JSON__;
const $ = id => document.getElementById(id);
const esc = s => String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = (x,d=2) => x==null?'n/a':Number(x).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const usd = (x,s='$') => x==null?'n/a':s+fmt(x);
const pct = x => x==null?'n/a':(x>0?'+':'')+fmt(x,2)+'%';
const deltaCls = x => x==null?'flat':(x>0?'up':(x<0?'down':'flat'));
const gradeColor = {excellent:'#14F1B2',good:'#3B82F6',fair:'#FFB020','at-risk':'#FF8C4A',critical:'#FF5C6C'};

function seriesOf(path){
  const out=[];
  for(const s of DATA.history||[]){let n=s;for(const k of path){if(!n||typeof n!=='object'){n=undefined;break}n=n[k]}if(typeof n==='number'&&isFinite(n))out.push(n)}
  return out;
}
function relTime(iso){
  if(!iso) return '';
  const t=new Date(iso).getTime(), diff=Math.max(0,(Date.now()-t)/1000);
  if(diff<60) return 'just now';
  if(diff<3600) return Math.floor(diff/60)+' min ago';
  if(diff<86400) return Math.floor(diff/3600)+'h ago';
  return Math.floor(diff/86400)+'d ago';
}
function spark(values,color='#14F1B2',w=96,h=38){
  if(!values||values.length<2) return '';
  const mn=Math.min(...values),mx=Math.max(...values),rng=(mx-mn)||1;
  const pts=values.map((v,i)=>((i/(values.length-1))*(w-4)+2)+','+(h-4-((v-mn)/rng)*(h-8)).toFixed(1));
  return `<svg class="spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><polyline fill="none" stroke="${color}" stroke-width="2" points="${pts.join(' ')}"/></svg>`;
}
function countUp(el){
  const t=parseFloat(el.dataset.v); if(isNaN(t)) return;
  const d=parseInt(el.dataset.d||'0',10),dur=950,t0=performance.now();
  (function tick(n){const p=Math.min(1,(n-t0)/dur);el.textContent=Number(t*p).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});if(p<1)requestAnimationFrame(tick)})(t0);
}
/* ---------- state & data ---------- */
const net=DATA.network,val=DATA.validators,eco=DATA.economics,fees=DATA.fees,hs=DATA.health_score;
const tps=net.tps||{},ep=net.epoch||{};
let chartState=null, chartWindow=24;

function histDelta(path){
  const s=seriesOf(path);
  if(s.length<2||!s[0]) return null;
  return ((s[s.length-1]-s[0])/s[0])*100;
}
function arrow(x){ return x==null?'—':(x>=0?'▲ ':'▼ ')+pct(Math.abs(x)); }

/* ---------- ticker ---------- */
function renderTicker(){
  const d=eco, sup=net.supply||{};
  const items=[
    ['SOL', usd(d.sol_price_usd), d.sol_price_24h_change_pct],
    ['TPS', fmt(tps.avg,0), histDelta(['metrics','tps','avg'])],
    ['TVL', usd(d.tvl_usd), d.tvl_24h_change_pct],
    ['DEX 24h', usd(d.dex_volume_24h_usd), d.dex_volume_24h_change_pct],
    ['Stablecoins', usd(d.stablecoin_supply_usd), null],
    ['Median fee', fees.median_fee_sol?fmt(fees.median_fee_sol,8):'n/a', null],
    ['Validators', fmt(val.active_count,0)+' active', null],
    ['Delinquent', fmt(val.delinquent_stake_pct,2)+'% stake', null],
    ['Epoch', ep.number+' ('+fmt(ep.progress_pct,0)+'%)', null],
    ['Supply', fmt(sup.circulating_sol,0)+' SOL', null],
  ];
  const cell=(it,i)=>`<span class="tick-item"><b>${it[0]}</b> ${it[1]} ${it[2]==null?'':`<span class="${it[2]>=0?'up':'down'}">${arrow(it[2])}</span>`}</span>`;
  const one=items.map(cell).join('');
  $('tickerTrack').innerHTML=one+one; /* duplicated for seamless loop */
}

/* ---------- topbar / anomalies / kpi ---------- */
function renderTopbar(){
  $('topbarSub').innerHTML=`Epoch <b>${ep.number}</b> · slot <b>${fmt(net.slot,0)}</b> · block <b>${fmt(net.block_height,0)}</b> · auto-refresh every <b>${DATA.config.refresh_interval_min} min</b>`;
  $('livePill').textContent=`Live · synced ${relTime(DATA.generated_at)}`;
}
function renderAnoms(){
  const anoms=DATA.anomalies||[];
  if(!anoms.length){ $('anomBanner').innerHTML='<div class="anomaly-chip ok"><b>✓ All clear</b>&nbsp;no anomalies detected</div>'; return; }
  const sevCls={critical:'',warning:'warn',info:'info'};
  $('anomBanner').innerHTML=anoms.map(a=>{
    const val=a.value!=null?` <span class="anom-val mono">${esc(String(a.value))}</span>`:'';
    const z=a.z!=null?` <span class="anom-z mono">z=${fmt(a.z,2)}</span>`:'';
    return `<div class="anomaly-chip ${sevCls[a.severity]||''}" title="${esc(a.message)}${val}${z}"><b>${a.severity==='info'?'ℹ️':'⚠️'} ${esc(a.metric)}</b>&nbsp;${esc(a.message)}${val}${z}</div>`;
  }).join('');
}
function renderKpi(){
  const priceD=eco.sol_price_24h_change_pct, tvlD=eco.tvl_24h_change_pct, tpsD=histDelta(['metrics','tps','avg']);
  const cards=[
    {l:'SOL Price', v:usd(eco.sol_price_usd), vd:2, d:`<span class="${deltaCls(priceD)}">${arrow(priceD)} 24h</span>`, sp:spark(seriesOf(['metrics','economics','sol_price_usd']), priceD>=0?'#14F1B2':'#FF5C6C')},
    {l:'TPS (avg)', v:fmt(tps.avg,0), vd:0, d:`<span class="${deltaCls(tpsD)}">${arrow(tpsD)} hist</span>`, sp:spark(seriesOf(['metrics','tps','avg']), tpsD>=0?'#14F1B2':'#FF5C6C')},
    {l:'TVL', v:usd(eco.tvl_usd), vd:0, d:`<span class="${deltaCls(tvlD)}">${arrow(tvlD)} 24h</span>`, sp:spark(seriesOf(['metrics','economics','tvl_usd']), tvlD>=0?'#14F1B2':'#FF5C6C')},
    {l:'Active Validators', v:fmt(val.active_count,0), vd:0, d:`<span class="${(val.delinquent_stake_pct||0)>0?'down':'up'}">▼ ${fmt(val.delinquent_stake_pct,2)}% delinquent</span>`, sp:spark(seriesOf(['metrics','validators','active_count']),'#9945FF')},
    {l:'Median Fee', v:fees.median_fee_sol?fmt(fees.median_fee_sol,5):'n/a', vd:5, d:`<span class="up">▲ REV est. ${fmt(fees.rev_est_24h_sol,0)} SOL</span>`, sp:spark(seriesOf(['metrics','fees','median_fee_sol']),'#14F1B2')},
  ];
  $('kpiGrid').innerHTML=cards.map(c=>`<div class="kpi-card"><div class="label">${c.l}</div><div class="value" data-v="${c.v.replace(/,/g,'').replace('$','')}" data-d="${c.vd}">${c.v}</div><div class="delta">${c.d}</div>${c.sp}</div>`).join('');
  document.querySelectorAll('.kpi-card .value').forEach(countUp);
}

/* ---------- price & TVL chart (with crosshair) ---------- */
function renderChart(){
  const hist=DATA.history||[];
  const now=Date.now()/1000, cutoff=now-chartWindow*3600;
  const pts=hist.filter(h=>h.ts>=cutoff);
  const W=620,H=210,PAD=8;
  if(pts.length<2){
    $('chartWrap').innerHTML='<div class="mono" style="color:var(--text-faint);font-size:12px;padding-top:84px;text-align:center">Not enough snapshots yet for this window — collected hourly</div>';
    $('chartLegend').innerHTML=''; chartState=null; return;
  }
  const price=pts.map(h=>h.metrics?.economics?.sol_price_usd), tvl=pts.map(h=>h.metrics?.economics?.tvl_usd);
  const pv=price.filter(v=>typeof v==='number');
  if(pv.length<2){ $('chartWrap').innerHTML='<div class="mono" style="color:var(--text-faint);font-size:12px;padding-top:84px;text-align:center">Incomplete data</div>'; return; }
  const pMin=Math.min(...pv),pMax=Math.max(...pv),pRng=(pMax-pMin)||1;
  const tvv=tvl.filter(v=>typeof v==='number');
  const tMin=tvv.length?Math.min(...tvv):0,tMax=tvv.length?Math.max(...tvv):1,tRng=(tMax-tMin)||1;
  const X=i=>PAD+(i/(pts.length-1))*(W-2*PAD), Yp=v=>H-PAD-((v-pMin)/pRng)*(H-2*PAD-34), Yt=v=>H-PAD-((v-tMin)/tRng)*(H-2*PAD-34);
  let pLine='',tLine='';
  pts.forEach((h,i)=>{
    const px=X(i), py=typeof h.metrics?.economics?.sol_price_usd==='number'?Yp(h.metrics.economics.sol_price_usd):null;
    const ty=typeof h.metrics?.economics?.tvl_usd==='number'?Yt(h.metrics.economics.tvl_usd):null;
    if(py!=null) pLine+=(pLine?'L':'M')+px.toFixed(1)+','+py.toFixed(1)+' ';
    if(ty!=null) tLine+=(tLine?'L':'M')+px.toFixed(1)+','+ty.toFixed(1)+' ';
  });
  const area=pLine.trim()+` L${W-PAD},${H-PAD} L${PAD},${H-PAD} Z`;
  const grid=[45,95,145].map(y=>`<line class="grid-line" x1="0" y1="${y}" x2="${W}" y2="${y}"/>`).join('');
  $('chartWrap').innerHTML=`<svg id="csvg" width="100%" height="${H}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    <defs><linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#14F1B2" stop-opacity=".32"/><stop offset="100%" stop-color="#14F1B2" stop-opacity="0"/></linearGradient></defs>
    ${grid}
    <path d="${area}" fill="url(#areaFill)"/>
    <polyline id="pLine" fill="none" stroke="#14F1B2" stroke-width="2.5" stroke-linecap="round" points="${pLine.trim()}"/>
    ${tvv.length>=2?`<polyline id="tLine" fill="none" stroke="#9945FF" stroke-width="2" stroke-dasharray="5 4" points="${tLine.trim()}"/>`:''}
    <line class="xhair" id="cxLine" x1="0" y1="0" x2="0" y2="${H}"/>
  </svg>
  <div class="tt" id="chartTT"></div>`;
  $('chartLegend').innerHTML=`<span class="lg"><span class="sw" style="background:var(--teal)"></span>SOL price ($${fmt(eco.sol_price_usd)})</span><span class="lg"><span class="sw" style="background:var(--violet)"></span>TVL ($${fmt(eco.tvl_usd/1e9,2)}B)</span>`;
  chartState={pts,X,Yp,Yt,W,H};
}

/* ---------- health gauge ---------- */
function gaugeSVG(score,size=120,sw=11){
  const r=(size-sw)/2,c=2*Math.PI*r,off=c*(1-score/100),g=gradeColor[hs?.grade]||'#14F1B2';
  return `<svg width="${size}" height="${size}"><circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="var(--surface-3)" stroke-width="${sw}"/><circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="${g}" stroke-width="${sw}" stroke-linecap="round" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}" style="transition:stroke-dashoffset 1.2s cubic-bezier(.2,.8,.2,1)"/></svg>`;
}
function renderGauge(){
  if(!hs){ $('gaugeWrap').innerHTML='<div style="color:var(--text-faint);font-size:12px">n/a</div>'; $('sideHealth').innerHTML=''; return; }
  $('gaugeWrap').innerHTML=`
    <div class="gauge">${gaugeSVG(hs.score)}<div class="gc"><div class="n">${hs.score}</div><div class="l" style="color:${gradeColor[hs.grade]}">${hs.grade}</div></div></div>
    <div class="glist">${Object.entries(hs.components).map(([k,v])=>`<div class="grow"><span class="k">${k}</span><div class="bar"><i data-w="${v}"></i></div><span class="v">${v}</span></div>`).join('')}</div>`;
  document.querySelectorAll('.glist .bar i').forEach(el=>{const w=el.dataset.w;requestAnimationFrame(()=>setTimeout(()=>el.style.width=w+'%',80))});
  $('sideHealth').innerHTML=`${gaugeSVG(hs.score,52,6)}<div><div class="t">Health</div><div class="s">${hs.score}</div><div class="g" style="color:${gradeColor[hs.grade]}">${hs.grade}</div></div>`;
}

/* ---------- stake donut ---------- */
function renderDonut(){
  const top20=(val.top_by_stake||[]).reduce((a,v)=>a+(v.stake_sol||0),0);
  const total=val.active_stake_sol||1, share=(top20/total)*100;
  const nk=val.nakamoto_coefficient;
  $('donutWrap').innerHTML=`<div class="donut" style="--p1:${share.toFixed(1)}%"><div class="donut-center"><div class="n">${fmt(share,1)}%</div><div class="l">TOP 20</div></div></div>
    <div class="legend">
      <div class="row"><span class="sw" style="background:var(--teal)"></span> Top 20 validators — ${fmt(share,1)}%</div>
      <div class="row"><span class="sw" style="background:var(--violet)"></span> Others — ${fmt(100-share,1)}%</div>
      <div class="row" style="color:var(--text-dim);margin-top:6px">Avg commission: ${fmt(val.avg_commission_pct,1)}%</div>
      <div class="row" style="color:var(--text-dim)">Delinquent: ${fmt(val.delinquent_stake_pct,2)}% of stake</div>
      ${nk!=null?`<div class="row nk-row"><span class="sw" style="background:var(--warning)"></span> Nakamoto coefficient: <b>${nk}</b> <span class="nk-hint">(validators &gt;33% stake)</span></div>`:''}
    </div>`;
}

/* ---------- ecosystem growth ---------- */
function renderGrowth(){
  const eg=DATA.ecosystem_growth||{};
  const dau=eg.daily_active_addresses||{}, tok=eg.tokenized_equities||{};
  const dauV=dau.available&&dau.value!=null?fmt(dau.value,0):'n/a (Dune key not set)';
  const tokV=tok.available&&tok.volume_usd!=null?usd(tok.volume_usd,0):'n/a';
  const aumV=tok.available&&tok.aum_usd!=null?usd(tok.aum_usd,0):'n/a';
  const holV=tok.available&&tok.holders!=null?fmt(tok.holders,0):'n/a';
  $('growthGrid').innerHTML=[
    `<div class="growth-card"><div class="gc-label">Daily Active Addresses</div><div class="gc-value ${dau.available?'':'na'}">${dauV}</div><div class="gc-sub">source: ${esc(dau.source||'dune')}</div></div>`,
    `<div class="growth-card"><div class="gc-label">Tokenized Equities Vol (24h)</div><div class="gc-value ${tok.available?'':'na'}">${tokV}</div><div class="gc-sub">source: ${esc(tok.source||'dune')}</div></div>`,
    `<div class="growth-card"><div class="gc-label">Tokenized Equities AUM</div><div class="gc-value ${tok.available?'':'na'}">${aumV}</div><div class="gc-sub">source: ${esc(tok.source||'dune')}</div></div>`,
    `<div class="growth-card"><div class="gc-label">Tokenized Equities Holders</div><div class="gc-value ${tok.available?'':'na'}">${holV}</div><div class="gc-sub">source: ${esc(tok.source||'dune')}</div></div>`,
  ].join('');
  if(!dau.available&&!tok.available) $('growthNote').textContent='Dune Analytics · key not configured';
}

/* ---------- validators / news / sources ---------- */
let valRows=[];
function renderValidators(){
  valRows=(val.top_by_stake||[]).map((v,i)=>{
    const pk=v.pubkey||''; const rk=i+1;
    return {rk,pk,v,
      html:`<tr data-pk="${esc(pk)}" data-stake="${v.stake_sol??0}" data-pct="${v.stake_pct??0}" data-comm="${v.commission_pct??0}">
      <td><span class="rank-badge ${rk===1?'r1':rk===2?'r2':rk===3?'r3':''}">${rk}</span></td>
      <td><span class="vavatar">${esc(pk.slice(0,2).toUpperCase())}</span><span class="mono">${esc(pk.slice(0,4))}…${esc(pk.slice(-4))}</span></td>
      <td class="num mono">${fmt(v.stake_sol,0)}</td><td class="num mono">${fmt(v.stake_pct,2)}%</td>
      <td class="num mono">${fmt(v.commission_pct,0)}%</td>
      <td class="num"><span class="status-dot ok"></span>Active</td></tr>`};
  });
  applyValView();
}
function applyValView(){
  const q=($('valFilter').value||'').toLowerCase();
  const rows=valRows.filter(r=>!q||r.pk.toLowerCase().includes(q));
  $('valTbody').innerHTML=rows.map(r=>r.html).join('')||'<tr><td colspan="6" style="color:var(--text-faint);text-align:center;padding:14px">No validators match “'+esc(q)+'”</td></tr>';
}
function renderNews(){
  const tab=(document.querySelector('#newsTabs .tab.active')||{}).dataset?.news||'simd';
  if(tab==='twitter'){
    const tw=DATA.news?.twitter||{};
    const tweets=tw.tweets||[];
    if(!tweets.length){ $('newsList').innerHTML='<div style="color:var(--text-faint);font-size:12.5px;padding:8px 0">No tweets available'+(tw.degraded&&tw.degraded.length?` (degraded: ${esc(tw.degraded.join(', '))})`:'')+'.</div>'; return; }
    $('newsList').innerHTML=tweets.slice(0,8).map(x=>{
      const txt=(x.text||'').slice(0,200);
      const url=x.id?`https://x.com/${esc(x.handle)}/status/${esc(x.id)}`:'';
      return `<div class="news-item" ${url?`onclick="window.open('${url}','_blank')"`:''}><div class="title">@${esc(x.handle)} — ${esc(txt)}</div><div class="meta"><span class="badge teal">X</span>${relTime(x.created_at)}</div></div>`;
    }).join('');
    return;
  }
  const s=DATA.news?.simd||[];
  if(!s.length){ $('newsList').innerHTML='<div style="color:var(--text-faint);font-size:12.5px;padding:8px 0">No recent SIMD proposals.</div>'; return; }
  $('newsList').innerHTML=s.slice(0,6).map(x=>{
    const badges=[x.type==='PR'?'<span class="badge violet">PR</span>':'<span class="badge teal">Issue</span>'];
    (x.labels||[]).slice(0,2).forEach(l=>badges.push(`<span class="badge">${esc(l)}</span>`));
    return `<div class="news-item" onclick="window.open('${esc(x.url)}','_blank')"><div class="title">#${x.number} ${esc(x.title)}</div><div class="meta">${badges.join('')}updated ${relTime(x.updated_at)}</div></div>`;
  }).join('');
}
const SRC_NAMES={rpc_health:'Solana RPC',rpc_epoch:'Solana RPC · epoch',rpc_slot:'Solana RPC · slot',rpc_block_height:'Solana RPC · height',rpc_perf:'Solana RPC · perf',rpc_votes:'Solana RPC · votes',rpc_supply:'Solana RPC · supply',rpc_fee_sampling:'RPC fee sampling',defillama_tvl:'DeFiLlama · TVL',defillama_tvl_history:'DeFiLlama · TVL history',defillama_dex:'DeFiLlama · DEX',defillama_stablecoins:'DeFiLlama · stablecoins',defillama_comparison:'DeFiLlama · multi-chain',coingecko:'CoinGecko',github_simd:'GitHub · SIMD',statuspage:'status.solana.com',dune:'Dune Analytics',twitter:'X / Twitter'};
function renderSources(){
  const rows=Object.entries(DATA.sources_ok||{}).map(([k,v])=>`<div class="source-row"><span class="name"><span class="status-dot ${v?'ok':'bad'}"></span>${esc(SRC_NAMES[k]||k)}</span><span class="lat">${v?'online':'failed'}</span></div>`).join('');
  $('srcList').innerHTML=rows;
}

/* ---------- crosshair ---------- */
function wireCrosshair(){
  const wrap=$('chartWrap');
  wrap.addEventListener('mousemove',e=>{
    if(!chartState) return;
    const rect=wrap.getBoundingClientRect(), x=e.clientX-rect.left;
    const r=(x/rect.width), i=Math.round(r*(chartState.pts.length-1));
    const px=chartState.X(i), h=chartState.pts[i];
    const line=$('cxLine'), tt=$('chartTT');
    if(!line||!tt) return;
    line.setAttribute('x1',px);line.setAttribute('x2',px);
    const d=new Date(h.ts*1000).toISOString().slice(0,16).replace('T',' ');
    const p=h.metrics?.economics?.sol_price_usd, t=h.metrics?.economics?.tvl_usd;
    tt.style.opacity=1;
    tt.innerHTML=`<div class="ttl">${esc(d)}</div><div class="row"><span style="color:var(--teal)">●</span> $${fmt(p)}</div>${t!=null?`<div class="row"><span style="color:var(--violet)">●</span> $${fmt(t/1e9,2)}B</div>`:''}`;
    const tw=tt.offsetWidth;
    const cssX=(px/chartState.W)*rect.width;
    tt.style.left=Math.min(Math.max(cssX+12,4),rect.width-tw-8)+'px';
    tt.style.top='6px';
  });
  wrap.addEventListener('mouseleave',()=>{const tt=$('chartTT');if(tt)tt.style.opacity=0});
}

/* ---------- init ---------- */
renderTicker(); renderTopbar(); renderAnoms(); renderKpi(); renderChart(); renderGauge(); renderDonut(); renderGrowth(); renderValidators(); renderNews(); renderSources(); wireCrosshair();

/* freshness ticker — keep "synced X ago" alive without a reload */
setInterval(()=>{ const pill=$('livePill'); if(pill) pill.textContent=`Live · synced ${relTime(DATA.generated_at)}`; },30000);

/* sortable validator table */
let sortKey=null, sortAsc=false;
document.querySelectorAll('th[data-sort]').forEach(th=>{
  th.addEventListener('click',()=>{
    const key=th.dataset.sort;
    if(sortKey===key){ sortAsc=!sortAsc; } else { sortKey=key; sortAsc=true; }
    document.querySelectorAll('th[data-sort]').forEach(x=>x.classList.remove('asc','desc'));
    th.classList.add(sortAsc?'asc':'desc');
    const rows=[...valRows];
    rows.sort((a,b)=>{
      const av=a.v[key]??0, bv=b.v[key]??0;
      return sortAsc?av-bv:bv-av;
    });
    valRows=rows; applyValView();
  });
});

/* filter validators */
$('valFilter').addEventListener('input',applyValView);

/* news tabs */
document.querySelectorAll('#newsTabs .tab').forEach(t=>t.addEventListener('click',()=>{
  document.querySelectorAll('#newsTabs .tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active'); renderNews();
}));

$('chartTabs').addEventListener('click',e=>{
  const t=e.target.closest('.tab'); if(!t) return;
  document.querySelectorAll('#chartTabs .tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  chartWindow=parseInt(t.dataset.w,10);
  renderChart();
});
document.querySelectorAll('.nav-item').forEach(n=>n.addEventListener('click',()=>{
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
  n.classList.add('active');
}));
</script>
</body>
</html>"""
