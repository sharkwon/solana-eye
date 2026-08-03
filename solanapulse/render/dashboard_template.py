"""Plain-string dashboard template (no f-string escaping needed).

The placeholder __DATA_JSON__ is replaced at render time with the report JSON.
Design: premium light "Solv."-style SaaS dashboard, green accent, animated
mini bar charts, with a fully-styled dark-mode toggle (the listing prefers
dark; the user prefers light — both are first-class).
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Solana Pulse · Solana Ecosystem Report</title>
<style>
:root{
  --bg:#f4f5f0; --bg2:#eceee6; --card:#ffffff; --card2:#fafbf7;
  --border:#e4e7dd; --border2:#d6dbcc;
  --text:#14171d; --muted:#6b7480; --faint:#9aa3ae;
  --accent:#0e9f6e; --accent2:#047857; --accent-soft:rgba(14,159,110,.12);
  --warn:#d97706; --warn-soft:rgba(217,119,6,.12);
  --crit:#dc2626; --crit-soft:rgba(220,38,38,.1);
  --info:#2563eb; --info-soft:rgba(37,99,235,.1);
  --shadow:0 1px 2px rgba(20,23,29,.04),0 8px 24px -12px rgba(20,23,29,.12);
  --shadow-lg:0 2px 4px rgba(20,23,29,.05),0 20px 40px -20px rgba(20,23,29,.22);
  --r:16px; --r-sm:10px;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
[data-theme=dark]{
  --bg:#0b0e14; --bg2:#10141d; --card:#131823; --card2:#181e2b;
  --border:#222a3a; --border2:#2c3548;
  --text:#e2e8f2; --muted:#8b94a5; --faint:#5d6575;
  --accent:#10d696; --accent2:#34e0a8; --accent-soft:rgba(16,214,150,.14);
  --warn:#ffb454; --warn-soft:rgba(255,180,84,.13);
  --crit:#ff6b6b; --crit-soft:rgba(255,107,107,.12);
  --info:#5b9dff; --info-soft:rgba(91,157,255,.14);
  --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px -12px rgba(0,0,0,.5);
  --shadow-lg:0 2px 4px rgba(0,0,0,.4),0 20px 40px -20px rgba(0,0,0,.7);
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  background:var(--bg); color:var(--text);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; transition:background .3s,color .3s;
}
a{color:var(--accent2);text-decoration:none}
.mono{font-family:var(--mono);font-size:12.5px}

/* ---------- header ---------- */
.hdr{
  position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:14px;
  padding:14px 28px; background:color-mix(in srgb,var(--bg) 82%,transparent);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:16.5px;letter-spacing:-.02em}
.brand .dot{width:11px;height:11px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 4px var(--accent-soft)}
.live{display:inline-flex;align-items:center;gap:7px;font-size:11.5px;font-weight:700;color:var(--accent2);background:var(--accent-soft);padding:4px 11px;border-radius:999px;letter-spacing:.04em}
.live .pulse{width:7px;height:7px;border-radius:50%;background:var(--accent);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.8)}}
.hdr .nav{display:flex;gap:2px;margin-left:auto;flex-wrap:wrap}
.hdr .nav a{font-size:13px;font-weight:600;color:var(--muted);padding:7px 12px;border-radius:999px;transition:.18s}
.hdr .nav a:hover{color:var(--text);background:var(--card);box-shadow:var(--shadow)}
.tbtn{
  border:1px solid var(--border2);background:var(--card);color:var(--muted);
  font-size:13px;font-weight:700;padding:7px 13px;border-radius:999px;cursor:pointer;transition:.18s;
}
.tbtn:hover{color:var(--text);border-color:var(--accent)}
/* ---------- hero ---------- */
.hero{
  display:flex;align-items:center;gap:34px;flex-wrap:wrap;
  padding:34px 28px 26px;max-width:1200px;margin:0 auto;
}
.hero h1{font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:-.035em;line-height:1.1}
.hero .sub{color:var(--muted);margin-top:8px;max-width:520px;font-size:14.5px}
.hero .sub b{color:var(--text)}
.ringwrap{display:flex;align-items:center;gap:18px;margin-left:auto}
.ring{position:relative;width:132px;height:132px;flex:none}
.ring svg{transform:rotate(-90deg)}
.ring .val{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.ring .val .n{font-size:34px;font-weight:800;letter-spacing:-.03em;line-height:1}
.ring .val .g{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;margin-top:3px}
.chips{display:flex;flex-wrap:wrap;gap:7px;max-width:340px}
.chip{font-size:11.5px;font-weight:650;color:var(--muted);background:var(--card);border:1px solid var(--border);padding:5px 11px;border-radius:999px;font-variant-numeric:tabular-nums}
.chip b{color:var(--text)}

/* ---------- sections & kpi ---------- */
.section{max-width:1200px;margin:0 auto;padding:10px 28px 34px}
.sec-h{display:flex;align-items:baseline;gap:12px;margin:26px 0 14px}
.sec-h h2{font-size:15px;font-weight:800;letter-spacing:.01em}
.sec-h .n{font-size:11px;font-weight:800;color:var(--accent2);background:var(--accent-soft);padding:2px 9px;border-radius:999px}
.sec-h .d{font-size:12.5px;color:var(--muted);margin-left:auto}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:14px}
.card{
  background:var(--card);border:1px solid var(--border);border-radius:var(--r);
  padding:18px 20px;box-shadow:var(--shadow);transition:transform .2s,box-shadow .2s;
}
.card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg)}
.card .k{font-size:11.5px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;display:flex;align-items:center;gap:6px}
.card .v{font-size:24px;font-weight:800;letter-spacing:-.025em;margin-top:7px;font-variant-numeric:tabular-nums}
.card .v small{font-size:13px;font-weight:600;color:var(--muted)}
.card .d{font-size:12px;color:var(--muted);margin-top:3px}
.card .chart{margin-top:12px;height:44px}
.up{color:var(--accent2)}.down{color:var(--crit)}.flat{color:var(--muted)}

/* ---------- alerts ---------- */
.alert{display:flex;gap:13px;align-items:flex-start;background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:var(--r-sm);padding:13px 17px;margin-bottom:10px;box-shadow:var(--shadow)}
.alert.warn{border-left-color:var(--warn)}.alert.crit{border-left-color:var(--crit)}
.alert .ic{font-size:15px;line-height:1.4}
.alert .t{font-weight:750;font-size:13.5px}
.alert .m{font-size:13px;color:var(--muted);margin-top:2px}
.okbar{display:flex;align-items:center;gap:11px;background:var(--accent-soft);color:var(--accent2);border-radius:var(--r-sm);padding:13px 17px;font-weight:700;font-size:13.5px;box-shadow:var(--shadow)}

/* ---------- tables ---------- */
.tblwrap{background:var(--card);border:1px solid var(--border);border-radius:var(--r);box-shadow:var(--shadow);overflow:hidden}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{font-size:11px;font-weight:750;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;text-align:left;padding:11px 16px;background:var(--card2);border-bottom:1px solid var(--border)}
td{padding:11px 16px;border-bottom:1px solid var(--border);font-variant-numeric:tabular-nums}
tr:last-child td{border-bottom:none}
tbody tr{transition:background .15s}
tbody tr:hover{background:var(--card2)}
td.num,th.num{text-align:right}
.pill{display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;border-radius:999px}
.pill.g{background:var(--accent-soft);color:var(--accent2)}
.pill.w{background:var(--warn-soft);color:var(--warn)}
.pill.r{background:var(--crit-soft);color:var(--crit)}
.pill.b{background:var(--info-soft);color:var(--info)}

/* ---------- hbars & pct bar ---------- */
.hbar{display:flex;align-items:center;gap:12px}
.hbar .lbl{width:92px;font-size:13px;font-weight:650;flex:none}
.hbar .lbl small{display:block;font-size:10.5px;color:var(--faint);font-weight:600}
.hbar .track{flex:1;height:10px;background:var(--bg2);border-radius:6px;overflow:hidden}
.hbar .fill{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--accent),var(--accent2));width:0;transition:width 1s cubic-bezier(.2,.8,.2,1)}
.hbar .val{width:118px;text-align:right;font-weight:750;font-variant-numeric:tabular-nums;font-size:13px;flex:none}
.pctbar{height:5px;background:var(--bg2);border-radius:4px;overflow:hidden;margin-top:5px}
.pctbar i{display:block;height:100%;border-radius:4px;background:var(--accent);width:0;transition:width 1s cubic-bezier(.2,.8,.2,1)}

/* ---------- misc ---------- */
details{background:var(--card);border:1px solid var(--border);border-radius:var(--r-sm);padding:12px 16px;margin-bottom:8px;box-shadow:var(--shadow)}
summary{cursor:pointer;font-weight:700;font-size:13.5px;list-style:none}
summary::before{content:"▸ ";color:var(--accent)}
details[open] summary::before{content:"▾ "}
footer{max-width:1200px;margin:0 auto;padding:22px 28px 40px;color:var(--faint);font-size:12px;border-top:1px solid var(--border);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
/* staggered entrance */
.fade{opacity:0;transform:translateY(10px);animation:fadeUp .5s cubic-bezier(.2,.7,.3,1) forwards}
@keyframes fadeUp{to{opacity:1;transform:none}}
@media (max-width:860px){
  .hdr{flex-wrap:wrap;padding:12px 16px}
  .hdr .nav{order:3;width:100%;overflow-x:auto}
  .hero{padding:24px 16px 18px;gap:20px}
  .ringwrap{margin-left:0}
  .section{padding:8px 16px 26px}
}
</style>
</head>
<body>
<header class="hdr">
  <div class="brand"><span class="dot"></span>Solana Pulse</div>
  <span class="live"><span class="pulse"></span>LIVE</span>
  <nav class="nav">
    <a href="#overview">Overview</a><a href="#validators">Validators</a>
    <a href="#markets">Markets</a><a href="#compare">Compare</a>
    <a href="#baselines">Baselines</a><a href="#sources">Sources</a>
  </nav>
  <button class="tbtn" id="themeBtn" title="Toggle theme">◐ Dark</button>
</header>
<main id="app"></main>
<script>
const DATA = __DATA_JSON__;
const $ = id => document.getElementById(id);
const esc = s => String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = (x,d=2) => x==null?'n/a':Number(x).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const usd = (x,s='$') => x==null?'n/a':s+fmt(x);
const pct = x => x==null?'n/a':(x>0?'+':'')+fmt(x,2)+'%';
const pctCls = x => x==null?'flat':(x>0?'up':(x<0?'down':'flat'));
const sev = {critical:{i:'🔴',c:'crit'},warning:{i:'🟠',c:'warn'},info:{i:'🔵',c:'b'}};
const gradeColor = {excellent:'var(--accent2)',good:'var(--info)',fair:'var(--warn)','at-risk':'#f97316',critical:'var(--crit)'};

/* ---------- theme ---------- */
const tbtn = $('themeBtn');
function setTheme(t){document.documentElement.setAttribute('data-theme',t);tbtn.textContent = t==='dark'?'◐ Light':'◐ Dark';try{localStorage.setItem('sp-theme',t)}catch(e){}}
setTheme((()=>{try{return localStorage.getItem('sp-theme')||'light'}catch(e){return 'light'}})());
tbtn.addEventListener('click',()=>setTheme(document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark'));

/* ---------- charts ---------- */
function barchart(values,w=300,h=44){
  if(!values||values.length<2) return '<div class="mono" style="color:var(--faint);font-size:11px">collecting history…</div>';
  const mn=Math.min(...values),mx=Math.max(...values),rng=(mx-mn)||1;
  const bw=w/values.length;
  let bars='';
  values.forEach((v,i)=>{
    const bh=Math.max(3,(v-mn)/rng*(h-8));
    const last=i===values.length-1;
    bars+=`<rect x="${(i*bw+bw*.22).toFixed(1)}" y="${(h-4-bh).toFixed(1)}" width="${(bw*.56).toFixed(1)}" height="${bh.toFixed(1)}" rx="2.5" fill="${last?'var(--accent2)':'var(--accent)'}" opacity="${last?1:.55}"><title>${fmt(v)}</title></rect>`;
  });
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="width:100%;height:100%">${bars}</svg>`;
}
function ring(score){
  const r=56,c=2*Math.PI*r,off=c*(1-score/100);
  const g=gradeColor[DATA.health_score?.grade]||'var(--accent2)';
  return `<div class="ring"><svg width="132" height="132"><circle cx="66" cy="66" r="${r}" fill="none" stroke="var(--bg2)" stroke-width="11"/><circle cx="66" cy="66" r="${r}" fill="none" stroke="${g}" stroke-width="11" stroke-linecap="round" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}" style="transition:stroke-dashoffset 1.2s cubic-bezier(.2,.8,.2,1)"/></svg><div class="val"><span class="n" data-v="${score}">${score}</span><span class="g" style="color:${g}">${DATA.health_score?.grade||''}</span></div></div>`;
}
function seriesOf(path){
  const out=[];
  for(const s of DATA.history||[]){let n=s;for(const k of path){if(!n||typeof n!=='object'){n=undefined;break}n=n[k]}if(typeof n==='number'&&isFinite(n))out.push(n)}
  return out;
}
function countUp(el){
  const target=parseFloat(el.dataset.v); if(isNaN(target)) return;
  const dur=900,t0=performance.now();
  (function tick(t){const p=Math.min(1,(t-t0)/dur);el.textContent=(target*p).toLocaleString('en-US',{maximumFractionDigits:1});if(p<1)requestAnimationFrame(tick)})(t0);
}
/* ---------- render ---------- */
const net=DATA.network,val=DATA.validators,eco=DATA.economics,fees=DATA.fees;
const tps=net.tps||{},slot=net.slot_time_sec||{},ep=net.epoch||{};
const anoms=DATA.anomalies||[];

function hero(){
  const hs=DATA.health_score;
  const chips=hs?Object.entries(hs.components).map(([k,v])=>`<span class="chip">${k} <b>${v}</b></span>`).join(''):'';
  return `<div class="hero fade">
    <div>
      <h1>Solana Ecosystem<br>Health Report</h1>
      <div class="sub">Generated <b>${esc(DATA.generated_at)}</b> UTC · auto-refreshes every <b>${DATA.config.refresh_interval_min}min</b> · keyless &amp; stdlib-only — <b>${fmt(ep.slots_remaining,0)}</b> slots left in epoch ${ep.number}</div>
    </div>
    ${hs?`<div class="ringwrap fade" style="animation-delay:.1s">${ring(hs.score)}<div class="chips">${chips}</div></div>`:''}
  </div>`;
}

function kpi(){
  const cards=[
    {k:'Avg TPS',v:fmt(tps.avg,0),d:'peak '+fmt(tps.max,0),ch:seriesOf(['metrics','tps','avg'])},
    {k:'Slot time',v:fmt(slot.avg,4)+'s',d:'target &lt; 0.6s',ch:seriesOf(['metrics','slot_time_sec','avg'])},
    {k:'Epoch '+ep.number,v:fmt(ep.progress_pct,1)+'%',d:fmt(ep.slots_remaining,0)+' slots left'},
    {k:'Validators',v:val.active_count,d:val.delinquent_count+' delinquent · '+fmt(val.delinquent_stake_pct,2)+'% stake'},
    {k:'SOL price',v:usd(eco.sol_price_usd),d:`<span class="${pctCls(eco.sol_price_24h_change_pct)}">${pct(eco.sol_price_24h_change_pct)} 24h</span>`,ch:seriesOf(['metrics','economics','sol_price_usd'])},
    {k:'TVL',v:usd(eco.tvl_usd),d:`<span class="${pctCls(eco.tvl_24h_change_pct)}">${pct(eco.tvl_24h_change_pct)} 24h</span>`,ch:seriesOf(['metrics','economics','tvl_usd'])},
    {k:'DEX volume 24h',v:usd(eco.dex_volume_24h_usd),d:`<span class="${pctCls(eco.dex_volume_24h_change_pct)}">${pct(eco.dex_volume_24h_change_pct)} 24h</span>`},
    {k:'Stablecoins',v:usd(eco.stablecoin_supply_usd),d:'supply on Solana'},
    {k:'Median fee',v:fees.median_fee_sol?fmt(fees.median_fee_sol,9)+' SOL':'n/a',d:fmt(fees.median_fee_lamports,0)+' lamports'},
    {k:'Est. fee revenue',v:fmt(fees.rev_est_24h_sol,0)+' SOL',d:'24h (on-chain sample)'},
    {k:'Health',v:net.health,d:'RPC endpoint'},
    {k:'Tx all-time',v:fmt(ep.transaction_count,0),d:'lifetime transactions'},
  ];
  return `<section id="overview" class="section"><div class="sec-h fade"><h2>Overview</h2><span class="n">LIVE</span><span class="d">hover cards for details</span></div>
    <div class="grid">${cards.map((c,i)=>`<div class="card fade" style="animation-delay:${(i*.04).toFixed(2)}s"><div class="k">${c.k}</div><div class="v">${c.v}</div><div class="d">${c.d||''}</div>${c.ch?`<div class="chart">${barchart(c.ch)}</div>`:''}</div>`).join('')}
    </div></section>`;
}

function alerts(){
  if(!anoms.length) return `<section class="section"><div class="sec-h fade"><h2>Alerts</h2><span class="n">CLEAR</span></div><div class="okbar fade">✓ No anomalies detected — all monitored metrics within normal range.</div></section>`;
  const body=anoms.map((a,i)=>{const s=sev[a.severity]||sev.info;return `<div class="alert ${s.c} fade" style="animation-delay:${(i*.06).toFixed(2)}s"><span class="ic">${s.i}</span><div><div class="t">${esc(a.metric)}</div><div class="m">${esc(a.message)}</div></div></div>`}).join('');
  return `<section class="section" style="padding-bottom:0"><div class="sec-h fade"><h2>Alerts</h2><span class="n">${anoms.length}</span></div>${body}</section>`;
}

function validators(){
  const top=(val.top_by_stake||[]).map((v,i)=>`<tr><td>${i+1}</td><td class="mono">${esc((v.pubkey||'').slice(0,6))}…${esc((v.pubkey||'').slice(-4))}</td><td class="num">${fmt(v.stake_sol,0)}</td><td class="num">${fmt(v.commission_pct,0)}%</td><td class="num">${fmt(v.last_vote_slot??v.lastVote,0)}</td></tr>`).join('');
  return `<section id="validators" class="section"><div class="sec-h fade"><h2>Validators</h2><span class="n">TOP 20</span><span class="d">${val.active_count} active · ${val.delinquent_count} delinquent (${fmt(val.delinquent_stake_pct,2)}% of stake) · avg commission ${fmt(val.avg_commission_pct,1)}%</span></div>
    <div class="tblwrap fade"><table><thead><tr><th>#</th><th>Vote account</th><th class="num">Stake (SOL)</th><th class="num">Commission</th><th class="num">Last vote slot</th></tr></thead><tbody>${top}</tbody></table></div></section>`;
}

function markets(){
  const sup=net.supply||{};
  return `<section id="markets" class="section"><div class="sec-h fade"><h2>Markets &amp; Supply</h2><span class="d">on-chain + DeFiLlama + CoinGecko</span></div>
    <div class="grid">
      ${[['Circulating SOL',fmt(sup.circulating_sol,0)+' SOL'],['Non-circulating',fmt(sup.non_circulating_sol,0)+' SOL'],['Block height',fmt(net.block_height,0)],['Slot',fmt(net.slot,0)]].map((c,i)=>`<div class="card fade" style="animation-delay:${(i*.04).toFixed(2)}s"><div class="k">${c[0]}</div><div class="v">${c[1]}</div></div>`).join('')}
    </div>
    ${DATA.status_page?`<div class="card fade" style="margin-top:14px"><div class="k">Network status · ${esc(DATA.status_page.page_name)}</div><div style="margin-top:8px"><span class="pill ${DATA.status_page.indicator==='none'?'g':'w'}">${esc(DATA.status_page.indicator)}</span> <span style="font-size:13px;color:var(--muted);margin-left:8px">${esc(DATA.status_page.description)}</span></div></div>`:''}
  </section>`;
}

function compare(){
  const c=DATA.comparison;if(!c||!c.chains||!c.chains.length)return '';
  const max=Math.max(...c.chains.map(x=>c.tvl[x]||0),1);
  const rows=c.chains.map((ch,i)=>{const tvl=c.tvl[ch]||0,d=c.dex[ch]||{},sc=c.stablecoins[ch]||0;
    return `<div class="hbar fade" style="animation-delay:${(i*.05).toFixed(2)}s"><div class="lbl">${ch}${ch==='Solana'?' ★':''}<small>DEX ${usd(d.volume24h)}</small></div><div class="track"><div class="fill" data-w="${((tvl/max)*100).toFixed(1)}"></div></div><div class="val">${usd(tvl)}<small style="display:block;font-size:10.5px;color:var(--faint)">${usd(sc)} stables</small></div></div>`}).join('');
  return `<section id="compare" class="section"><div class="sec-h fade"><h2>Cross-Chain Comparison</h2><span class="n">TVL</span><span class="d">DeFiLlama · ★ Solana</span></div><div class="card fade">${rows}</div></section>`;
}

function baselines(){
  const bl=DATA.baselines;if(!bl||!Object.keys(bl).length)return '';
  const rows=Object.values(bl).map(b=>{const p=b.percentile;const cls=p==null?'flat':(p>=90||p<=10)?'down':(p>=50?'up':'flat');
    return `<tr><td>${esc(b.label)}</td><td class="num">${fmt(b.current,2)}</td><td class="num">${fmt(b.median,2)}</td><td style="min-width:130px"><span class="${cls}" style="font-weight:700">${p==null?'n/a':p+'th'}</span><div class="pctbar"><i data-w="${p==null?0:p}"></i></div></td></tr>`}).join('');
  return `<section id="baselines" class="section"><div class="sec-h fade"><h2>Baselines · 30-day</h2><span class="d">current vs own history percentile</span></div><div class="tblwrap fade"><table><thead><tr><th>Metric</th><th class="num">Current</th><th class="num">Median</th><th>Percentile</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
}

function news(){
  const s=DATA.news?.simd||[];if(!s.length)return '';
  const items=s.map(x=>`<details><summary>#${x.number} ${esc(x.title)}</summary><div style="margin-top:8px;font-size:12.5px;color:var(--muted)">${(x.labels||[]).map(l=>`<span class="pill b">${esc(l)}</span>`).join(' ')} <a href="${esc(x.url)}" target="_blank" rel="noopener">open ↗</a></div></details>`).join('');
  return `<section class="section"><div class="sec-h fade"><h2>Development News</h2><span class="n">SIMD</span></div>${items}</section>`;
}

function sources(){
  const rows=Object.entries(DATA.sources_ok||{}).map(([k,v])=>`<tr><td class="mono">${esc(k)}</td><td class="num"><span class="pill ${v?'g':'r'}">${v?'online':'failed'}</span></td></tr>`).join('');
  return `<section id="sources" class="section"><div class="sec-h fade"><h2>Data Sources</h2><span class="d">keyless endpoints</span></div><div class="tblwrap fade"><table><thead><tr><th>Source</th><th class="num">Status</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
}

$('app').innerHTML = hero()+alerts()+kpi()+validators()+markets()+compare()+baselines()+news()+sources();
document.querySelectorAll('.fill,.pctbar i').forEach(el=>{const w=el.dataset.w;requestAnimationFrame(()=>setTimeout(()=>{el.style.width=(w||0)+'%'},50))});
document.querySelectorAll('[data-v]').forEach(countUp);</script>
</body>
</html>"""
