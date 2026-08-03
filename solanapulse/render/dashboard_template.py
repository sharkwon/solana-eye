"""Plain-string dashboard template (no f-string escaping needed).

Design: user-provided mockup — dark premium crypto dashboard, Space Grotesk /
Inter / JetBrains Mono, teal(#14F1B2)+violet(#9945FF) gradient accent, sidebar
nav, KPI grid with sparklines, price/TVL area chart with 7H/24H/7D tabs, stake
donut, validator table, SIMD news, source health. __DATA_JSON__ is injected at
render time; all numbers/rows are rendered from live report data.
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>solana-pulse · dashboard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

  :root{
    --bg:#0B0E14;
    --surface:#12151C;
    --surface-2:#171C26;
    --border:#232838;
    --text:#E6E8EC;
    --text-dim:#8B93A7;
    --text-faint:#565E72;
    --teal:#14F1B2;
    --violet:#9945FF;
    --danger:#FF5C6C;
    --warning:#FFB020;
    --grad: linear-gradient(90deg, var(--teal), var(--violet));
  }

  *{box-sizing:border-box; margin:0; padding:0;}
  body{
    background:var(--bg);
    color:var(--text);
    font-family:'Inter',sans-serif;
    font-size:14px;
    display:flex;
    min-height:100vh;
  }
  ::selection{ background:var(--teal); color:#0B0E14; }

  /* ---------- Sidebar ---------- */
  .sidebar{
    width:220px;
    flex-shrink:0;
    background:var(--surface);
    border-right:1px solid var(--border);
    padding:24px 16px;
    display:flex;
    flex-direction:column;
    gap:28px;
    position:sticky; top:0; height:100vh;
  }
  .brand{
    display:flex; align-items:center; gap:10px;
    font-family:'Space Grotesk',sans-serif;
    font-weight:700; font-size:16px; letter-spacing:-0.02em;
  }
  .brand .dot{
    width:10px; height:10px; border-radius:50%;
    background:var(--grad);
    box-shadow:0 0 12px rgba(20,241,178,0.6);
  }
  nav{ display:flex; flex-direction:column; gap:2px; }
  .nav-item{
    display:flex; align-items:center; gap:10px;
    padding:9px 10px; border-radius:8px;
    color:var(--text-dim); font-size:13px; font-weight:500;
    cursor:pointer; transition:.15s; text-decoration:none;
  }
  .nav-item:hover{ background:var(--surface-2); color:var(--text); }
  .nav-item.active{
    background:var(--surface-2); color:var(--text);
    box-shadow:inset 2px 0 0 var(--teal);
  }
  .sidebar-footer{
    margin-top:auto; padding-top:16px; border-top:1px solid var(--border);
    font-size:11px; color:var(--text-faint); line-height:1.6;
  }

  /* ---------- Main ---------- */
  .main{ flex:1; padding:24px 32px 60px; max-width:1400px; min-width:0; }

  .topbar{ display:flex; align-items:center; justify-content:space-between; margin-bottom:24px; flex-wrap:wrap; gap:10px; }
  .topbar h1{
    font-family:'Space Grotesk',sans-serif; font-size:22px; font-weight:600; letter-spacing:-0.02em;
  }
  .topbar .sub{ color:var(--text-dim); font-size:12.5px; margin-top:3px; }
  .live-pill{
    display:flex; align-items:center; gap:8px;
    background:var(--surface); border:1px solid var(--border);
    padding:7px 14px; border-radius:100px; font-size:12px; color:var(--text-dim);
  }
  .live-pill .pulse{
    width:7px; height:7px; border-radius:50%; background:var(--teal);
    animation:pulse 1.8s infinite;
  }
  @keyframes pulse{
    0%{ box-shadow:0 0 0 0 rgba(20,241,178,.55); }
    70%{ box-shadow:0 0 0 7px rgba(20,241,178,0); }
    100%{ box-shadow:0 0 0 0 rgba(20,241,178,0); }
  }

  /* ---------- Anomaly banner ---------- */
  .anomaly-banner{
    display:flex; gap:10px; overflow-x:auto;
    margin-bottom:20px; padding-bottom:2px;
  }
  .anomaly-chip{
    flex-shrink:0;
    display:flex; align-items:center; gap:8px;
    background:rgba(255,92,108,.08); border:1px solid rgba(255,92,108,.35);
    color:#FF9BA5; padding:8px 14px; border-radius:10px; font-size:12px; font-weight:500;
    white-space:nowrap;
  }
  .anomaly-chip.warn{ background:rgba(255,176,32,.08); border-color:rgba(255,176,32,.35); color:#FFCB6B; }
  .anomaly-chip.info{ background:rgba(20,241,178,.08); border-color:rgba(20,241,178,.35); color:#7DF5D6; }
  .anomaly-chip.ok{ background:rgba(20,241,178,.06); border-color:rgba(20,241,178,.25); color:#7DF5D6; }
  .anomaly-chip b{ font-weight:600; }

  /* ---------- KPI grid ---------- */
  .kpi-grid{ display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin-bottom:20px; }
  .kpi-card{
    background:var(--surface); border:1px solid var(--border); border-radius:14px;
    padding:16px 18px; position:relative; overflow:hidden; transition:border-color .2s, transform .2s;
  }
  .kpi-card:hover{ border-color:#2c3350; transform:translateY(-1px); }
  .kpi-card .label{ color:var(--text-dim); font-size:11.5px; font-weight:500; text-transform:uppercase; letter-spacing:.04em; }
  .kpi-card .value{
    font-family:'JetBrains Mono',monospace; font-size:22px; font-weight:600; margin-top:8px; letter-spacing:-0.01em;
  }
  .kpi-card .delta{ font-size:12px; margin-top:4px; font-weight:500; }
  .delta.up{ color:var(--teal); }
  .delta.down{ color:var(--danger); }
  .delta.flat{ color:var(--text-faint); }
  .kpi-card svg.spark{ position:absolute; bottom:6px; right:8px; opacity:.9; }

  /* ---------- Content grid ---------- */
  .content-grid{ display:grid; grid-template-columns:2fr 1fr; gap:16px; margin-bottom:16px; }
  .panel{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:20px; }
  .panel-head{ display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; flex-wrap:wrap; gap:8px; }
  .panel-head h3{ font-family:'Space Grotesk',sans-serif; font-size:14.5px; font-weight:600; }
  .panel-head .tabs{ display:flex; gap:4px; background:var(--surface-2); padding:3px; border-radius:8px; }
  .panel-head .tab{ padding:5px 12px; font-size:11.5px; border-radius:6px; color:var(--text-dim); cursor:pointer; transition:.15s; }
  .panel-head .tab.active{ background:var(--bg); color:var(--text); }

  .chart-wrap{ position:relative; height:200px; }
  .chart-wrap .grid-line{ stroke:var(--border); stroke-width:1; }
  .chart-legend{ display:flex; gap:16px; font-size:11.5px; color:var(--text-dim); margin-top:10px; }
  .chart-legend .lg{ display:flex; align-items:center; gap:6px; }
  .chart-legend .sw{ width:9px; height:9px; border-radius:3px; }

  .donut-wrap{ display:flex; align-items:center; gap:20px; flex-wrap:wrap; }
  .donut{
    width:120px; height:120px; border-radius:50%; flex-shrink:0;
    background:conic-gradient(var(--teal) 0% var(--p1,50%), var(--violet) var(--p1,50%) 100%);
    display:flex; align-items:center; justify-content:center; position:relative;
  }
  .donut::before{ content:''; position:absolute; width:80px; height:80px; border-radius:50%; background:var(--surface); }
  .donut-center{ position:relative; text-align:center; font-family:'JetBrains Mono',monospace; }
  .donut-center .n{ font-size:18px; font-weight:600; }
  .donut-center .l{ font-size:9px; color:var(--text-dim); }
  .legend{ display:flex; flex-direction:column; gap:10px; font-size:12.5px; }
  .legend .row{ display:flex; align-items:center; gap:8px; }
  .legend .sw{ width:9px; height:9px; border-radius:3px; }

  /* ---------- Validator table ---------- */
  table{ width:100%; border-collapse:collapse; font-size:12.5px; }
  th{ text-align:left; color:var(--text-faint); font-weight:500; font-size:11px; text-transform:uppercase; letter-spacing:.04em; padding:0 10px 10px; border-bottom:1px solid var(--border); }
  td{ padding:10px; border-bottom:1px solid var(--border); }
  tr:last-child td{ border-bottom:none; }
  tr:hover td{ background:var(--surface-2); }
  .mono{ font-family:'JetBrains Mono',monospace; }
  .status-dot{ width:7px; height:7px; border-radius:50%; display:inline-block; margin-right:6px; }
  .status-dot.ok{ background:var(--teal); }
  .status-dot.bad{ background:var(--danger); }
  .rank{ color:var(--text-faint); }

  /* ---------- Bottom row ---------- */
  .bottom-grid{ display:grid; grid-template-columns:1.3fr 1fr; gap:16px; }
  .news-item{ padding:12px 0; border-bottom:1px solid var(--border); }
  .news-item:last-child{ border-bottom:none; }
  .news-item .title{ font-size:13px; font-weight:500; }
  .news-item .meta{ color:var(--text-faint); font-size:11px; margin-top:4px; }
  .badge{ display:inline-block; font-size:10px; padding:2px 7px; border-radius:5px; background:var(--surface-2); color:var(--text-dim); margin-right:6px; }
  .badge.teal{ background:rgba(20,241,178,.1); color:var(--teal); }
  .badge.violet{ background:rgba(153,69,255,.12); color:#c69bff; }
  .source-row{ display:flex; align-items:center; justify-content:space-between; padding:9px 0; border-bottom:1px solid var(--border); font-size:12.5px; }
  .source-row:last-child{ border-bottom:none; }
  .source-row .name{ display:flex; align-items:center; }
  .source-row .lat{ color:var(--text-faint); font-family:'JetBrains Mono',monospace; font-size:11.5px; }

  footer{ margin-top:24px; color:var(--text-faint); font-size:11px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; }

  .sec{ scroll-margin-top:16px; }
  @media (max-width:1100px){ .kpi-grid{ grid-template-columns:repeat(3,1fr); } .content-grid{ grid-template-columns:1fr; } .bottom-grid{ grid-template-columns:1fr; } }
  @media (max-width:760px){
    .sidebar{ display:none; }
    .kpi-grid{ grid-template-columns:repeat(2,1fr); }
    .main{ padding:18px 16px 40px; }
  }
</style>
</head>
<body>
<aside class="sidebar">
  <div class="brand"><span class="dot"></span> solana-pulse</div>
  <nav>
    <a class="nav-item active" href="#overview"><span>▣</span> Overview</a>
    <a class="nav-item" href="#validators"><span>◇</span> Validators</a>
    <a class="nav-item" href="#economics"><span>◆</span> Economics</a>
    <a class="nav-item" href="#news"><span>▤</span> News (SIMD)</a>
    <a class="nav-item" href="#anomalies"><span>▲</span> Anomalies</a>
    <a class="nav-item" href="#sources"><span>●</span> Sources</a>
  </nav>
  <div class="sidebar-footer">
    schema_version: 1<br>
    refreshed hourly via GitHub Actions<br>
    MIT · data © respective sources
  </div>
</aside>

<main class="main">

  <div class="topbar" id="overview">
    <div>
      <h1>Ringkasan Jaringan</h1>
      <div class="sub" id="topbarSub">memuat data…</div>
    </div>
    <div class="live-pill"><span class="pulse"></span> <span id="livePill">Live</span></div>
  </div>

  <div class="anomaly-banner" id="anomBanner"></div>

  <div class="kpi-grid" id="kpiGrid"></div>

  <div class="content-grid" id="economics">
    <div class="panel">
      <div class="panel-head">
        <h3>Pergerakan Harga &amp; TVL</h3>
        <div class="tabs" id="chartTabs">
          <div class="tab" data-w="7h">7H</div>
          <div class="tab active" data-w="24h">24H</div>
          <div class="tab" data-w="7d">7D</div>
        </div>
      </div>
      <div class="chart-wrap" id="chartWrap"></div>
      <div class="chart-legend" id="chartLegend"></div>
    </div>

    <div class="panel">
      <div class="panel-head"><h3>Distribusi Stake</h3></div>
      <div class="donut-wrap" id="donutWrap"></div>
    </div>
  </div>

  <div class="panel sec" id="validators" style="margin-bottom:16px;">
    <div class="panel-head"><h3>Top Validator berdasarkan Stake</h3></div>
    <table>
      <thead><tr><th>#</th><th>Validator</th><th>Stake (SOL)</th><th>Komisi</th><th>Status</th></tr></thead>
      <tbody id="valTbody"></tbody>
    </table>
  </div>

  <div class="bottom-grid">
    <div class="panel sec" id="news">
      <div class="panel-head"><h3>Berita SIMD Terbaru</h3></div>
      <div id="newsList"></div>
    </div>
    <div class="panel sec" id="sources">
      <div class="panel-head"><h3>Kesehatan Sumber Data</h3></div>
      <div id="srcList"></div>
    </div>
  </div>

  <footer>
    <span>solana-pulse · dibuat dengan Python stdlib, tanpa dependency</span>
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

function seriesOf(path){
  const out=[];
  for(const s of DATA.history||[]){let n=s;for(const k of path){if(!n||typeof n!=='object'){n=undefined;break}n=n[k]}if(typeof n==='number'&&isFinite(n))out.push(n)}
  return out;
}
function relTime(iso){
  if(!iso) return '';
  const t=new Date(iso).getTime(), diff=Math.max(0,(Date.now()-t)/1000);
  if(diff<60) return 'baru saja';
  if(diff<3600) return Math.floor(diff/60)+' menit lalu';
  if(diff<86400) return Math.floor(diff/3600)+' jam lalu';
  return Math.floor(diff/86400)+' hari lalu';
}
function spark(values,color='#14F1B2',w=90,h=36){
  if(!values||values.length<2) return '';
  const mn=Math.min(...values),mx=Math.max(...values),rng=(mx-mn)||1;
  const pts=values.map((v,i)=>((i/(values.length-1))*(w-4)+2)+','+(h-4-((v-mn)/rng)*(h-8)).toFixed(1));
  return `<svg class="spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><polyline fill="none" stroke="${color}" stroke-width="2" points="${pts.join(' ')}"/></svg>`;
}
/* ---------- render ---------- */
const net=DATA.network,val=DATA.validators,eco=DATA.economics,fees=DATA.fees,hs=DATA.health_score;
const tps=net.tps||{},ep=net.epoch||{};

function histDelta(path){
  const s=seriesOf(path);
  if(s.length<2||!s[0]) return null;
  return ((s[s.length-1]-s[0])/s[0])*100;
}
function arrow(x){ return x==null?'—':(x>=0?'▲ ':'▼ ')+pct(Math.abs(x)); }

function renderTopbar(){
  $('topbarSub').textContent = `Epoch ${ep.number} · slot ${fmt(net.slot,0)} · diperbarui otomatis tiap ${DATA.config.refresh_interval_min} menit`;
  $('livePill').textContent = `Live · sinkron ${relTime(DATA.generated_at)}`;
}

function renderAnoms(){
  const anoms=DATA.anomalies||[];
  if(!anoms.length){ $('anomBanner').innerHTML='<div class="anomaly-chip ok"><b>✓ Normal</b>&nbsp;tidak ada anomali terdeteksi</div>'; return; }
  const sevCls={critical:'',warning:'warn',info:'info'};
  $('anomBanner').innerHTML=anoms.map(a=>`<div class="anomaly-chip ${sevCls[a.severity]||''}"><b>${a.severity==='critical'?'⚠️':a.severity==='warning'?'⚠️':'ℹ️'} ${esc(a.metric)}</b>&nbsp;${esc(a.message)}</div>`).join('');
}

function renderKpi(){
  const priceD=eco.sol_price_24h_change_pct, tvlD=eco.tvl_24h_change_pct, tpsD=histDelta(['metrics','tps','avg']);
  const cards=[
    {l:'Harga SOL', v:usd(eco.sol_price_usd), d:`<span class="${deltaCls(priceD)}">${arrow(priceD)} / 24 jam</span>`, sp:spark(seriesOf(['metrics','economics','sol_price_usd']), priceD>=0?'#14F1B2':'#FF5C6C')},
    {l:'TPS (non-vote)', v:fmt(tps.avg,0), d:`<span class="${deltaCls(tpsD)}">${arrow(tpsD)} / rentang historis</span>`, sp:spark(seriesOf(['metrics','tps','avg']), tpsD>=0?'#14F1B2':'#FF5C6C')},
    {l:'TVL Total', v:usd(eco.tvl_usd), d:`<span class="${deltaCls(tvlD)}">${arrow(tvlD)} / 24 jam</span>`, sp:spark(seriesOf(['metrics','economics','tvl_usd']), tvlD>=0?'#14F1B2':'#FF5C6C')},
    {l:'Validator Aktif', v:fmt(val.active_count,0), d:`<span class="${(val.delinquent_stake_pct||0)>0?'down':'up'}">▼ ${fmt(val.delinquent_stake_pct,1)}% delinquent</span>`, sp:spark(seriesOf(['metrics','validators','active_count']),'#9945FF')},
    {l:'Median Fee', v:fees.median_fee_sol?fmt(fees.median_fee_sol,6):'n/a', d:`<span class="up">▲ REV est. ${fmt(fees.rev_est_24h_sol,0)} SOL</span>`, sp:spark(seriesOf(['metrics','fees','median_fee_sol']),'#14F1B2')},
  ];
  $('kpiGrid').innerHTML=cards.map(c=>`<div class="kpi-card"><div class="label">${c.l}</div><div class="value">${c.v}</div><div class="delta">${c.d}</div>${c.sp}</div>`).join('');
}

let chartWindow=24;
function renderChart(){
  const hist=DATA.history||[];
  const now=Date.now()/1000, cutoff=now-chartWindow*3600;
  const pts=hist.filter(h=>h.ts>=cutoff);
  const W=600,H=200,PAD=6;
  if(pts.length<2){
    $('chartWrap').innerHTML='<div class="mono" style="color:var(--text-faint);font-size:12px;padding-top:80px;text-align:center">Belum cukup data untuk rentang ini — snapshot dikumpulkan tiap jam</div>';
    $('chartLegend').innerHTML='';
    return;
  }
  const price=pts.map(h=>h.metrics?.economics?.sol_price_usd), tvl=pts.map(h=>h.metrics?.economics?.tvl_usd);
  const pv=price.filter(v=>typeof v==='number'), tv=tvl.filter(v=>typeof v==='number');
  if(pv.length<2){ $('chartWrap').innerHTML='<div class="mono" style="color:var(--text-faint);font-size:12px;padding-top:80px;text-align:center">Data tidak lengkap</div>'; return; }
  const pMin=Math.min(...pv),pMax=Math.max(...pv),pRng=(pMax-pMin)||1;
  const tMin=Math.min(...tv),tMax=Math.max(...tv),tRng=(tMax-tMin)||1;
  const X=i=>PAD+(i/(pts.length-1))*(W-2*PAD), Yp=v=>H-PAD-((v-pMin)/pRng)*(H-2*PAD-30), Yt=v=>H-PAD-((v-tMin)/tRng)*(H-2*PAD-30);
  let pLine='',tLine='',area='';
  pts.forEach((h,i)=>{
    const px=X(i); const py=typeof h.metrics?.economics?.sol_price_usd==='number'?Yp(h.metrics.economics.sol_price_usd):null;
    const ty=typeof h.metrics?.economics?.tvl_usd==='number'?Yt(h.metrics.economics.tvl_usd):null;
    if(py!=null){ pLine+=(pLine?'L':'M')+px.toFixed(1)+','+py.toFixed(1)+' '; }
    if(ty!=null){ tLine+=(tLine?'L':'M')+px.toFixed(1)+','+ty.toFixed(1)+' '; }
  });
  area=pLine.trim()+` L${W-PAD},${H-PAD} L${PAD},${H-PAD} Z`;
  const grid=[40,90,140].map(y=>`<line class="grid-line" x1="0" y1="${y}" x2="${W}" y2="${y}"/>`).join('');
  $('chartWrap').innerHTML=`<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    <defs><linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#14F1B2" stop-opacity="0.35"/><stop offset="100%" stop-color="#14F1B2" stop-opacity="0"/>
    </linearGradient></defs>
    ${grid}
    <path d="${area}" fill="url(#areaFill)"/>
    <polyline fill="none" stroke="#14F1B2" stroke-width="2.5" points="${pLine.trim()}"/>
    ${tv.length>=2?`<polyline fill="none" stroke="#9945FF" stroke-width="2" stroke-dasharray="5 4" points="${tLine.trim()}"/>`:''}
  </svg>`;
  $('chartLegend').innerHTML=`<span class="lg"><span class="sw" style="background:var(--teal)"></span>Harga SOL ($${fmt(eco.sol_price_usd)})</span><span class="lg"><span class="sw" style="background:var(--violet)"></span>TVL ($${fmt(eco.tvl_usd/1e9,2)}B)</span>`;
}

function renderDonut(){
  const top20=(val.top_by_stake||[]).reduce((a,v)=>a+(v.stake_sol||0),0);
  const total=val.active_stake_sol||1;
  const share=(top20/total)*100;
  $('donutWrap').innerHTML=`<div class="donut" style="--p1:${share.toFixed(1)}%"><div class="donut-center"><div class="n">${fmt(share,1)}%</div><div class="l">TOP 20</div></div></div>
    <div class="legend">
      <div class="row"><span class="sw" style="background:var(--teal)"></span> Top 20 validator — ${fmt(share,1)}%</div>
      <div class="row"><span class="sw" style="background:var(--violet)"></span> Sisanya — ${fmt(100-share,1)}%</div>
      <div class="row" style="color:var(--text-dim); margin-top:6px;">Komisi rata-rata: ${fmt(val.avg_commission_pct,1)}%</div>
      <div class="row" style="color:var(--text-dim);">Delinquent: ${fmt(val.delinquent_stake_pct,2)}% stake</div>
    </div>`;
}

function renderValidators(){
  const rows=(val.top_by_stake||[]).slice(0,8).map((v,i)=>`<tr><td class="rank">${i+1}</td><td class="mono">${esc((v.pubkey||'').slice(0,4))}…${esc((v.pubkey||'').slice(-4))}</td><td class="mono">${fmt(v.stake_sol,0)}</td><td class="mono">${fmt(v.commission_pct,0)}%</td><td><span class="status-dot ok"></span>Aktif</td></tr>`).join('');
  $('valTbody').innerHTML=rows;
}

function renderNews(){
  const s=DATA.news?.simd||[];
  if(!s.length){ $('newsList').innerHTML='<div style="color:var(--text-faint);font-size:12.5px;padding:8px 0">Belum ada proposal SIMD terbaru.</div>'; return; }
  $('newsList').innerHTML=s.slice(0,6).map(x=>{
    const badges=[x.type==='PR'?'<span class="badge violet">PR</span>':'<span class="badge teal">Issue</span>'];
    (x.labels||[]).slice(0,2).forEach(l=>badges.push(`<span class="badge">${esc(l)}</span>`));
    return `<div class="news-item"><div class="title">#${x.number} ${esc(x.title)}</div><div class="meta">${badges.join('')}diperbarui ${relTime(x.updated_at)}</div></div>`;
  }).join('');
}

const SRC_NAMES={rpc_health:'Solana RPC',rpc_epoch:'Solana RPC (epoch)',rpc_slot:'Solana RPC (slot)',rpc_block_height:'Solana RPC (height)',rpc_perf:'Solana RPC (perf)',rpc_votes:'Solana RPC (votes)',rpc_supply:'Solana RPC (supply)',rpc_fee_sampling:'RPC fee sampling',defillama_tvl:'DeFiLlama TVL',defillama_tvl_history:'DeFiLlama TVL history',defillama_dex:'DeFiLlama DEX',defillama_stablecoins:'DeFiLlama stablecoins',defillama_comparison:'DeFiLlama multi-chain',coingecko:'CoinGecko',github_simd:'GitHub (SIMD)',statuspage:'status.solana.com',dune:'Dune (opsional)'};
function renderSources(){
  const rows=Object.entries(DATA.sources_ok||{}).map(([k,v])=>`<div class="source-row"><span class="name"><span class="status-dot ${v?'ok':'bad'}"></span>${esc(SRC_NAMES[k]||k)}</span><span class="lat">${v?'online':'gagal'}</span></div>`).join('');
  $('srcList').innerHTML=rows;
}

/* ---------- init ---------- */
renderTopbar(); renderAnoms(); renderKpi(); renderChart(); renderDonut(); renderValidators(); renderNews(); renderSources();

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
