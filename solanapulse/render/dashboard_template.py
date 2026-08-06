"""Solana Eye dashboard template (plain string; __DATA_JSON__ injected).


v5 "Obsidian Terminal" — premium fintech aesthetic.
- Editorial typography: oversized display numerals, tight tracking, mono data
- Liquid gradient accents, animated mesh aurora, fine-grain noise overlay
- Cinematic entrance: staggered reveals, number morphs, drawing chart strokes
- Signature hero: SOL price as a monumental statement with live sparkline
- Glass panels with gradient hairline borders, physics-feeling hovers
- Inline SVG icons only — no emoji. English copy throughout.
"""


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Solana Eye · Ecosystem Terminal</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0' stop-color='%2314F1B2'/%3E%3Cstop offset='1' stop-color='%239945FF'/%3E%3C/linearGradient%3E%3C/defs%3E%3Cpath d='M3 24C12 8 36 8 45 24C36 40 12 40 3 24Z' fill='%2312151C' stroke='url(%23g)' stroke-width='2.5'/%3E%3Ccircle cx='24' cy='24' r='10' fill='url(%23g)'/%3E%3Ccircle cx='24' cy='24' r='4.4' fill='%230B0E14'/%3E%3C/svg%3E">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');


  :root{
    --bg:#05070C;
    --ink:#04060A;
    --panel:#0A0E16;
    --panel-2:#0D121C;
    --line:rgba(148,163,196,.10);
    --line-2:rgba(148,163,196,.18);
    --t1:#F2F5FA;
    --t2:#A7B0C2;
    --t3:#626C80;
    --t4:#3A4152;
    --teal:#14F1B2;
    --violet:#9945FF;
    --blue:#4C8DFF;
    --rose:#FF5C7A;
    --amber:#FFB454;
    --grad:linear-gradient(92deg,#14F1B2 0%,#4C8DFF 52%,#9945FF 100%);
    --font-d:'Space Grotesk',sans-serif;
    --font-b:'Inter',sans-serif;
    --font-m:'JetBrains Mono',monospace;
    --ease:cubic-bezier(.22,.9,.28,1);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{
    background:var(--bg);color:var(--t1);
    font:14px/1.6 var(--font-b);font-weight:400;
    min-height:100vh;overflow-x:hidden;
    -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
  }
  ::selection{background:var(--teal);color:#05070C}
  ::-webkit-scrollbar{width:8px;height:8px}
  ::-webkit-scrollbar-thumb{background:#1A2233;border-radius:99px}


  /* ---- ambient scene ---- */
  .scene{position:fixed;inset:0;z-index:-2;pointer-events:none;overflow:hidden}
  .scene i{position:absolute;border-radius:50%;filter:blur(110px)}
  .scene .a1{width:60vw;height:60vw;top:-28vw;left:-18vw;background:radial-gradient(circle,rgba(20,241,178,.14),transparent 65%);animation:blob 30s ease-in-out infinite alternate}
  .scene .a2{width:56vw;height:56vw;bottom:-26vw;right:-16vw;background:radial-gradient(circle,rgba(153,69,255,.13),transparent 65%);animation:blob 38s ease-in-out infinite alternate-reverse}
  .scene .a3{width:34vw;height:34vw;top:36%;left:52%;background:radial-gradient(circle,rgba(76,141,255,.10),transparent 65%);animation:blob 46s ease-in-out infinite alternate}
  @keyframes blob{to{transform:translate(4vw,3vw) scale(1.12)}}
  .noise{position:fixed;inset:0;z-index:60;pointer-events:none;opacity:.05;mix-blend-mode:overlay;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
  .gridlines{position:fixed;inset:0;z-index:-1;pointer-events:none;
    background:linear-gradient(rgba(148,163,196,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(148,163,196,.045) 1px,transparent 1px);
    background-size:72px 72px;
    mask-image:radial-gradient(ellipse 90% 70% at 50% 0%,#000 30%,transparent 75%)}


  .mono{font-family:var(--font-m);font-variant-numeric:tabular-nums}


  /* ---- shell ---- */
  .shell{max-width:1180px;margin:0 auto;padding:28px 28px 64px}


  /* ---- header ---- */
  header{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 0 26px;border-bottom:1px solid var(--line)}
  .brand{display:flex;align-items:center;gap:13px}
  .brand .logo{filter:drop-shadow(0 0 14px rgba(20,241,178,.4))}
  .brand .nm{font-family:var(--font-d);font-weight:700;font-size:17px;letter-spacing:-.02em;line-height:1.05}
  .brand .nm small{display:block;font-family:var(--font-b);font-size:10px;font-weight:600;color:var(--t3);letter-spacing:.26em;text-transform:uppercase;margin-top:3px}
  .hdr-right{display:flex;align-items:center;gap:10px}
  .nav-pills{display:flex;gap:2px;background:var(--panel);border:1px solid var(--line);border-radius:99px;padding:3px}
  .nav-pills a{font-size:12px;font-weight:500;color:var(--t3);text-decoration:none;padding:6px 14px;border-radius:99px;transition:.18s var(--ease)}
  .nav-pills a:hover{color:var(--t1)}
  .nav-pills a.active{color:var(--teal);background:rgba(20,241,178,.08)}
  .live-pill{display:inline-flex;align-items:center;gap:8px;font-family:var(--font-m);font-size:11.5px;color:var(--t2);border:1px solid var(--line);padding:8px 15px;border-radius:99px;background:var(--panel)}
  .live-pill .pulse{width:6px;height:6px;border-radius:50%;background:var(--teal);animation:pulse 1.8s infinite}
  @keyframes pulse{0%{box-shadow:0 0 0 0 rgba(20,241,178,.55)}70%{box-shadow:0 0 0 8px rgba(20,241,178,0)}100%{box-shadow:0 0 0 0 rgba(20,241,178,0)}}


  /* ---- ticker ---- */
  .tape{margin-top:20px;border:1px solid var(--line);border-radius:14px;background:rgba(10,14,22,.6);backdrop-filter:blur(10px);overflow:hidden;position:relative}
  .tape::before,.tape::after{content:'';position:absolute;top:0;bottom:0;width:70px;z-index:2;pointer-events:none}
  .tape::before{left:0;background:linear-gradient(90deg,var(--bg),transparent)}
  .tape::after{right:0;background:linear-gradient(-90deg,var(--bg),transparent)}
  .tape .track{display:flex;gap:42px;width:max-content;padding:11px 24px;animation:scroll 42s linear infinite}
  .tape:hover .track{animation-play-state:paused}
  @keyframes scroll{to{transform:translateX(-50%)}}
  .tk{font-family:var(--font-m);font-size:12px;color:var(--t3);white-space:nowrap;letter-spacing:.01em}
  .tk b{color:var(--t1);font-weight:500;margin-left:7px}
  .tk .up{color:var(--teal)}.tk .down{color:var(--rose)}


  /* ---- hero ---- */
  .hero{display:grid;grid-template-columns:1.15fr .85fr;gap:20px;margin-top:26px;align-items:stretch}
  .hero-main{position:relative;border:1px solid var(--line);border-radius:22px;padding:34px 36px 30px;background:linear-gradient(155deg,var(--panel-2),var(--panel) 60%);overflow:hidden}
  .hero-main::before{content:'';position:absolute;inset:0;border-radius:22px;padding:1px;background:linear-gradient(135deg,rgba(20,241,178,.5),rgba(76,141,255,.15) 40%,rgba(153,69,255,.45));-webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);-webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none}
  .hero-main .glow{position:absolute;width:420px;height:420px;top:-200px;right:-140px;background:radial-gradient(circle,rgba(20,241,178,.13),transparent 60%);filter:blur(40px);pointer-events:none}
  .eyebrow{display:inline-flex;align-items:center;gap:9px;font-size:10.5px;font-weight:600;letter-spacing:.24em;text-transform:uppercase;color:var(--t3)}
  .eyebrow::before{content:'';width:22px;height:1px;background:var(--grad)}
  .hero-price{font-family:var(--font-d);font-weight:700;font-size:clamp(52px,7vw,84px);letter-spacing:-.045em;line-height:1;margin:14px 0 6px;background:linear-gradient(180deg,#fff 30%,#8EEBD4 130%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;font-variant-numeric:tabular-nums}
  .hero-sub{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
  .hero-chg{font-family:var(--font-m);font-size:15px;font-weight:600;padding:5px 13px;border-radius:99px}
  .hero-chg.up{color:var(--teal);background:rgba(20,241,178,.1);box-shadow:inset 0 0 0 1px rgba(20,241,178,.3)}
  .hero-chg.down{color:var(--rose);background:rgba(255,92,122,.1);box-shadow:inset 0 0 0 1px rgba(255,92,122,.3)}
  .hero-chg.flat{color:var(--t3);background:var(--panel);box-shadow:inset 0 0 0 1px var(--line)}
  .hero-note{font-size:12.5px;color:var(--t3)}
  .hero-spark{margin:22px -6px -4px;display:block}
  .hero-meta{display:flex;gap:26px;margin-top:18px;padding-top:18px;border-top:1px solid var(--line);flex-wrap:wrap}
  .hm{font-family:var(--font-m)}
  .hm .k{font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--t4);font-family:var(--font-b);font-weight:600}
  .hm .v{font-size:14px;color:var(--t1);font-weight:500;margin-top:4px}


  /* hero side: health */
  .hero-side{display:flex;flex-direction:column;gap:20px}
  .health-card{flex:1;border:1px solid var(--line);border-radius:22px;padding:26px;background:linear-gradient(165deg,var(--panel-2),var(--panel));display:flex;align-items:center;gap:22px}
  .gauge{position:relative;width:118px;height:118px;flex:none}
  .gauge svg{transform:rotate(-90deg)}
  .gauge .gc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
  .gauge .n{font-family:var(--font-d);font-weight:700;font-size:30px;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
  .gauge .l{font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:var(--t3);font-weight:600;margin-top:3px}
  .health-info .grade{font-family:var(--font-d);font-weight:700;font-size:19px;letter-spacing:-.01em;text-transform:capitalize}
  .health-info .hint{font-size:12px;color:var(--t3);margin-top:5px;line-height:1.55}
  .mini-cards{display:grid;grid-template-columns:1fr 1fr;gap:20px}
  .mini{border:1px solid var(--line);border-radius:18px;padding:18px 20px;background:var(--panel);transition:.22s var(--ease)}
  .mini:hover{border-color:var(--line-2);transform:translateY(-2px)}
  .mini .k{font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--t4);font-weight:600}
  .mini .v{font-family:var(--font-d);font-weight:700;font-size:23px;letter-spacing:-.02em;margin-top:8px;font-variant-numeric:tabular-nums}
  .mini .s{font-family:var(--font-m);font-size:11px;color:var(--t3);margin-top:3px}


  /* ---- section titles ---- */
  .sec-head{display:flex;align-items:baseline;justify-content:space-between;margin:44px 0 18px;flex-wrap:wrap;gap:8px}
  .sec-head h2{font-family:var(--font-d);font-weight:700;font-size:21px;letter-spacing:-.025em;display:flex;align-items:center;gap:12px}
  .sec-head h2 .idx{font-family:var(--font-m);font-size:11px;font-weight:500;color:var(--t4);letter-spacing:.1em}
  .sec-head .note{font-family:var(--font-m);font-size:11px;color:var(--t4)}


  /* ---- panels / cards ---- */
  .panel{border:1px solid var(--line);border-radius:20px;padding:24px;background:linear-gradient(165deg,var(--panel-2),var(--panel));transition:border-color .25s}
  .panel:hover{border-color:var(--line-2)}
  .panel-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;flex-wrap:wrap;gap:10px}
  .panel-head h3{font-family:var(--font-d);font-weight:600;font-size:14.5px;letter-spacing:-.01em}
  .tabs{display:flex;gap:2px;background:var(--ink);padding:3px;border-radius:10px;border:1px solid var(--line)}
  .tab{padding:5px 13px;font-size:11.5px;font-weight:500;border-radius:8px;color:var(--t3);cursor:pointer;transition:.16s;border:1px solid transparent}
  .tab:hover{color:var(--t1)}
  .tab.active{background:var(--panel-2);color:var(--teal);border-color:var(--line-2)}


  .grid-21{display:grid;grid-template-columns:2fr 1fr;gap:20px}
  .grid-11{display:grid;grid-template-columns:1fr 1fr;gap:20px}


  /* chart */
  .chart-wrap{position:relative;height:240px;cursor:crosshair}
  .chart-wrap .grid-line{stroke:var(--line);stroke-width:1}
  .chart-wrap .xhair{stroke:var(--t4);stroke-width:1;stroke-dasharray:3 3;opacity:0;transition:opacity .12s}
  .chart-wrap:hover .xhair{opacity:1}
  .chart-legend{display:flex;gap:20px;font-family:var(--font-m);font-size:11.5px;color:var(--t3);margin-top:14px}
  .chart-legend .lg{display:flex;align-items:center;gap:7px}
  .chart-legend .sw{width:8px;height:8px;border-radius:2px}
  .tt{position:absolute;pointer-events:none;background:rgba(5,7,12,.96);border:1px solid var(--line-2);border-radius:10px;padding:8px 12px;font-family:var(--font-m);font-size:11.5px;opacity:0;transition:opacity .12s;z-index:5;white-space:nowrap;box-shadow:0 12px 32px -10px rgba(0,0,0,.7)}
  .tt .ttl{color:var(--t4);font-size:10px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}
  .tt .row{display:flex;gap:8px;align-items:center}
  .empty{color:var(--t4);text-align:center;padding:70px 0;font-family:var(--font-m);font-size:12px}


  /* anomaly strip */
  .anoms{display:flex;gap:10px;overflow-x:auto;padding-bottom:2px}
  .chip{flex-shrink:0;display:flex;align-items:center;gap:9px;padding:9px 15px;border-radius:12px;font-size:12px;font-weight:500;white-space:nowrap;border:1px solid;background:rgba(255,92,122,.07);border-color:rgba(255,92,122,.32);color:#FFA5B6}
  .chip.warn{background:rgba(255,180,84,.07);border-color:rgba(255,180,84,.32);color:#FFD49B}
  .chip.info{background:rgba(76,141,255,.08);border-color:rgba(76,141,255,.35);color:#A9C8FF}
  .chip.ok{background:rgba(20,241,178,.06);border-color:rgba(20,241,178,.28);color:#8AF0D2}
  .chip .ic{width:14px;height:14px;flex:none}
  .chip b{font-weight:600}
  .chip .mono{opacity:.8;font-size:10.5px}


  /* growth */
  .growth-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}
  .g-card{position:relative;border:1px solid var(--line);border-radius:18px;padding:20px 22px;background:var(--panel);overflow:hidden;transition:.22s var(--ease)}
  .g-card:hover{border-color:var(--line-2);transform:translateY(-2px)}
  .g-card::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:var(--grad);opacity:0;transition:.25s}
  .g-card:hover::after{opacity:.8}
  .g-card .k{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--t4);font-weight:600}
  .g-card .v{font-family:var(--font-d);font-weight:700;font-size:26px;letter-spacing:-.025em;margin-top:9px;font-variant-numeric:tabular-nums}
  .g-card .v.na{color:var(--t4);font-size:14px;font-weight:500;font-family:var(--font-b);padding-top:5px}
  .g-card .s{font-family:var(--font-m);font-size:10.5px;color:var(--t4);margin-top:4px}


  /* donut */
  .donut-wrap{display:flex;align-items:center;gap:24px;flex-wrap:wrap}
  .donut{width:132px;height:132px;border-radius:50%;flex-shrink:0;background:conic-gradient(var(--teal) 0% var(--p1,50%),rgba(153,69,255,.85) var(--p1,50%) 100%);display:flex;align-items:center;justify-content:center;position:relative;filter:drop-shadow(0 0 18px rgba(20,241,178,.14))}
  .donut::before{content:'';position:absolute;width:92px;height:92px;border-radius:50%;background:var(--panel)}
  .donut-c{position:relative;text-align:center}
  .donut-c .n{font-family:var(--font-d);font-weight:700;font-size:22px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
  .donut-c .l{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--t3);font-weight:600;margin-top:2px}
  .legend{display:flex;flex-direction:column;gap:11px;font-size:12.5px;color:var(--t2);flex:1;min-width:170px}
  .legend .row{display:flex;align-items:center;gap:9px}
  .legend .sw{width:8px;height:8px;border-radius:2px;flex:none}
  .legend .mono{margin-left:auto;color:var(--t1);font-size:12px}
  .legend .dim{color:var(--t3)}
  .legend b{color:var(--amber);font-family:var(--font-m);font-weight:600}


  /* table */
  table{width:100%;border-collapse:collapse}
  th{text-align:left;color:var(--t4);font-weight:600;font-size:10.5px;text-transform:uppercase;letter-spacing:.1em;padding:0 14px 12px;border-bottom:1px solid var(--line)}
  td{padding:12px 14px;border-bottom:1px solid var(--line);font-size:13px}
  tr:last-child td{border-bottom:none}
  tbody tr{transition:background .14s}
  tbody tr:hover{background:rgba(148,163,196,.04)}
  td.num,th.num{text-align:right}
  .rank{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:8px;font-family:var(--font-m);font-size:11px;font-weight:600;background:var(--ink);color:var(--t3);border:1px solid var(--line)}
  .rank.r1{background:linear-gradient(135deg,#F6D06B,#C28F2C);color:#221803;border:none}
  .rank.r2{background:linear-gradient(135deg,#D3DCE8,#93A0B4);color:#131820;border:none}
  .rank.r3{background:linear-gradient(135deg,#E2A87E,#B26E42);color:#2B1608;border:none}
  .avatar{width:27px;height:27px;border-radius:9px;display:inline-flex;align-items:center;justify-content:center;font-family:var(--font-m);font-size:10.5px;font-weight:600;background:linear-gradient(135deg,rgba(20,241,178,.16),rgba(153,69,255,.16));color:var(--teal);margin-right:10px;vertical-align:middle;border:1px solid rgba(20,241,178,.2)}
  .dot{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:7px;vertical-align:middle}
  .dot.ok{background:var(--teal);box-shadow:0 0 8px rgba(20,241,178,.7)}
  .dot.bad{background:var(--rose)}
  .filter{background:var(--ink);border:1px solid var(--line);color:var(--t1);border-radius:10px;padding:7px 13px;font-size:12px;font-family:inherit;width:200px;outline:none;transition:.18s}
  .filter::placeholder{color:var(--t4)}
  .filter:focus{border-color:rgba(20,241,178,.5);box-shadow:0 0 0 3px rgba(20,241,178,.1)}
  th[data-sort]{cursor:pointer;user-select:none}
  th[data-sort]:hover{color:var(--teal)}
  th[data-sort] .sa{display:inline-block;width:0;height:0;margin-left:5px;border-left:4px solid transparent;border-right:4px solid transparent;opacity:.4;vertical-align:middle}
  th[data-sort].asc .sa{border-bottom:5px solid var(--teal);opacity:1}
  th[data-sort].desc .sa{border-top:5px solid var(--teal);opacity:1}


  /* news & sources */
  .news-item{padding:14px 4px;border-bottom:1px solid var(--line);cursor:pointer;transition:.18s var(--ease);border-radius:10px}
  .news-item:hover{background:rgba(148,163,196,.04);padding-left:12px;padding-right:12px}
  .news-item:last-child{border-bottom:none}
  .news-item .title{font-size:13.5px;font-weight:500;line-height:1.5;color:var(--t1)}
  .news-item .meta{color:var(--t4);font-family:var(--font-m);font-size:10.5px;margin-top:6px;display:flex;align-items:center;flex-wrap:wrap;gap:2px}
  .badge{display:inline-block;font-size:9.5px;font-weight:600;letter-spacing:.06em;padding:3px 8px;border-radius:6px;background:var(--ink);color:var(--t3);margin-right:7px;text-transform:uppercase;border:1px solid var(--line)}
  .badge.teal{background:rgba(20,241,178,.09);color:var(--teal);border-color:rgba(20,241,178,.25)}
  .badge.violet{background:rgba(153,69,255,.11);color:#C79BFF;border-color:rgba(153,69,255,.3)}
  .src{display:flex;align-items:center;justify-content:space-between;padding:11px 4px;border-bottom:1px solid var(--line);font-size:12.5px}
  .src:last-child{border-bottom:none}
  .src .name{display:flex;align-items:center;color:var(--t2)}
  .src .lat{font-family:var(--font-m);font-size:10.5px;color:var(--t4);text-transform:uppercase;letter-spacing:.08em}
  .src .lat.on{color:var(--teal)}
  .src .lat.off{color:var(--rose)}


  /* upgrade radar */
  .up-grid{display:grid;grid-template-columns:1.4fr 1fr;gap:20px}
  .up-item{display:flex;align-items:flex-start;gap:12px;padding:13px 4px;border-bottom:1px solid var(--line);cursor:pointer;transition:.18s var(--ease);border-radius:10px}
  .up-item:hover{background:rgba(148,163,196,.04);padding-left:12px;padding-right:12px}
  .up-item:last-child{border-bottom:none}
  .up-item .title{font-size:13.5px;font-weight:500;line-height:1.5;color:var(--t1);flex:1}
  .up-item .meta{color:var(--t4);font-family:var(--font-m);font-size:10.5px;margin-top:5px;display:flex;align-items:center;flex-wrap:wrap;gap:2px}
  .up-state{flex:none;font-size:9.5px;font-weight:600;letter-spacing:.08em;padding:3px 9px;border-radius:99px;text-transform:uppercase;margin-top:2px}
  .up-state.open{background:rgba(20,241,178,.09);color:var(--teal);border:1px solid rgba(20,241,178,.25)}
  .up-state.merged{background:rgba(153,69,255,.12);color:#C79BFF;border:1px solid rgba(153,69,255,.3)}
  .up-state.closed{background:rgba(148,163,196,.1);color:var(--t3);border:1px solid var(--line-2)}
  .badge.amber{background:rgba(255,180,84,.1);color:var(--amber);border-color:rgba(255,180,84,.3)}
  .rel-item{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 4px;border-bottom:1px solid var(--line);font-size:12.5px;cursor:pointer;transition:.18s;border-radius:10px}
  .rel-item:hover{background:rgba(148,163,196,.04);padding-left:12px;padding-right:12px}
  .rel-item:last-child{border-bottom:none}
  .rel-item .nm{font-weight:500;color:var(--t1);font-family:var(--font-m);font-size:12px}
  .rel-item .dt{font-family:var(--font-m);font-size:10.5px;color:var(--t4)}


  footer{margin-top:56px;padding-top:22px;border-top:1px solid var(--line);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;font-size:11.5px;color:var(--t4)}
  footer b{color:var(--t2);font-weight:600}
  footer .mono{font-size:10.5px}


  /* reveal choreography */
  .rv{opacity:0;transform:translateY(18px);animation:rv .7s var(--ease) forwards;animation-delay:var(--d,0s)}
  @keyframes rv{to{opacity:1;transform:none}}
  .draw{stroke-dasharray:1600;stroke-dashoffset:1600;animation:draw 1.6s var(--ease) .35s forwards}
  @keyframes draw{to{stroke-dashoffset:0}}
  .fade-in{opacity:0;animation:fade 1s ease .9s forwards}
  @keyframes fade{to{opacity:1}}
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}


  @media (max-width:1080px){
    .hero{grid-template-columns:1fr}
    .grid-21,.grid-11,.up-grid{grid-template-columns:1fr}
    .nav-pills{display:none}
  }
  @media (max-width:640px){
    .shell{padding:18px 16px 48px}
    .hero-main{padding:26px 22px}
    .hero-price{font-size:52px}
    .mini-cards{grid-template-columns:1fr 1fr}
  }
</style>
</head>
<body>
<div class="scene"><i class="a1"></i><i class="a2"></i><i class="a3"></i></div>
<div class="gridlines"></div>
<div class="noise"></div>


<div class="shell">


  <header class="rv">
    <div class="brand">
      <svg class="logo" width="36" height="36" viewBox="0 0 48 48" aria-hidden="true">
        <defs><linearGradient id="lgI" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#14F1B2"/><stop offset="1" stop-color="#9945FF"/></linearGradient></defs>
        <circle cx="24" cy="24" r="21" fill="url(#lgI)" opacity="0.08"/>
        <path d="M3 24C12 8 36 8 45 24C36 40 12 40 3 24Z" fill="#0A0E16" stroke="url(#lgI)" stroke-width="2.5"/>
        <circle cx="24" cy="24" r="10.5" fill="url(#lgI)"/>
        <circle cx="24" cy="24" r="4.6" fill="#05070C"/>
        <circle cx="21.2" cy="20.8" r="1.8" fill="#fff" opacity=".9"/>
      </svg>
      <div class="nm">Solana Eye<small>ecosystem terminal</small></div>
    </div>
    <div class="hdr-right">
      <nav class="nav-pills">
        <a href="#markets">Markets</a>
        <a href="#growth">Growth</a>
        <a href="#validators">Validators</a>
        <a href="#news">News</a>
        <a href="#upgrades">Upgrades</a>
        <a href="#sources">Sources</a>
      </nav>
      <div class="live-pill"><span class="pulse"></span><span id="livePill">Live</span></div>
    </div>
  </header>


  <div class="tape rv" style="--d:.08s"><div class="track" id="tapeTrack"></div></div>


  <!-- HERO -->
  <section class="hero" id="markets">
    <div class="hero-main rv" style="--d:.14s">
      <div class="glow"></div>
      <span class="eyebrow">Solana · SOL / USD</span>
      <div class="hero-price" id="heroPrice">—</div>
      <div class="hero-sub">
        <span class="hero-chg flat" id="heroChg">—</span>
        <span class="hero-note" id="heroNote">24h change &middot; aggregated from CoinGecko</span>
      </div>
      <svg class="hero-spark" id="heroSpark" width="100%" height="86" viewBox="0 0 560 86" preserveAspectRatio="none"></svg>
      <div class="hero-meta" id="heroMeta"></div>
    </div>
    <div class="hero-side">
      <div class="health-card rv" style="--d:.2s" id="healthCard"></div>
      <div class="mini-cards rv" style="--d:.26s" id="miniCards"></div>
    </div>
  </section>


  <!-- ANOMALIES -->
  <div class="sec-head rv" style="--d:.3s"><h2><span class="idx">01</span>Signal &amp; Anomalies</h2><span class="note" id="anomNote"></span></div>
  <div class="anoms rv" style="--d:.34s" id="anoms"></div>


  <!-- CHART + STAKE -->
  <div class="sec-head rv"><h2><span class="idx">02</span>Price &amp; Liquidity</h2><span class="note">hourly snapshots &middot; crosshair for detail</span></div>
  <div class="grid-21">
    <div class="panel rv">
      <div class="panel-head">
        <h3>SOL Price &amp; TVL</h3>
        <div class="tabs" id="chartTabs">
          <div class="tab" data-w="7">7H</div>
          <div class="tab active" data-w="24">24H</div>
          <div class="tab" data-w="168">7D</div>
      </div>
      <div class="chart-wrap" id="chartWrap"></div>
      <div class="chart-legend" id="chartLegend"></div>
    </div>
    <div class="panel rv" style="--d:.06s">
      <div class="panel-head"><h3>Stake Concentration</h3></div>
      <div class="donut-wrap" id="donutWrap"></div>
    </div>
  </div>


  <!-- GROWTH -->
  <div class="sec-head rv" id="growth"><h2><span class="idx">03</span>Ecosystem Growth</h2><span class="note" id="growthNote">Dune Analytics</span></div>
  <div class="growth-grid rv" id="growthGrid"></div>


  <!-- VALIDATORS -->
  <div class="sec-head rv" id="validators"><h2><span class="idx">04</span>Validator Leaderboard</h2><span class="note">ranked by active stake</span></div>
  <div class="panel rv">
    <div class="panel-head">
      <h3>Top Validators by Stake</h3>
      <input class="filter" id="valFilter" type="text" placeholder="Filter validators&hellip;" aria-label="Filter validators">
    </div>
    <table>
      <thead><tr>
        <th>#</th><th>Validator</th>
        <th class="num" data-sort="stake_sol">Stake (SOL)<span class="sa"></span></th>
        <th class="num" data-sort="stake_pct">Stake %<span class="sa"></span></th>
        <th class="num" data-sort="commission_pct">Commission<span class="sa"></span></th>
        <th class="num">Status</th>
      </tr></thead>
      <tbody id="valTbody"></tbody>
    </table>
  </div>


  <!-- NEWS + SOURCES -->
  <div class="sec-head rv" id="news"><h2><span class="idx">05</span>Intelligence Feed</h2><span class="note">SIMD proposals &middot; X / Twitter</span></div>
  <div class="grid-21">
    <div class="panel rv">
      <div class="panel-head">
        <h3>Ecosystem News</h3>
        <div class="tabs" id="newsTabs">
          <div class="tab active" data-news="simd">SIMD</div>
          <div class="tab" data-news="twitter">X / Twitter</div>
        </div>
      </div>
      <div id="newsList"></div>
    </div>
    <div class="panel rv" id="sources" style="--d:.06s">
      <div class="panel-head"><h3>Data Source Health</h3></div>
      <div id="srcList"></div>
    </div>
  </div>


  <!-- UPGRADE RADAR -->
  <div class="sec-head rv" id="upgrades"><h2><span class="idx">06</span>Upgrade Radar</h2><span class="note">Alpenglow &middot; watched SIMDs &middot; Agave releases</span></div>
  <div class="up-grid">
    <div class="panel rv">
      <div class="panel-head"><h3>Upcoming Protocol Upgrades</h3><span class="note" id="upNote">SIMD repo scan</span></div>
      <div id="upList"></div>
    </div>
    <div class="panel rv" style="--d:.06s">
      <div class="panel-head"><h3>Agave Client Releases</h3></div>
      <div id="relList"></div>
    </div>
  </div>


  <footer class="rv">
    <span><b>Solana Eye</b> &middot; zero-dependency &middot; keyless &middot; Python stdlib</span>
    <span class="mono" id="footMeta">Schema v1 &middot; MIT License</span>
  </footer>
</div>


<script>
const DATA = __DATA_JSON__;
const $ = id => document.getElementById(id);
const esc = s => String(s??'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = (x,d=2) => x==null?'n/a':Number(x).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const usd = (x,s='$') => x==null?'n/a':s+fmt(x);
const pct = x => x==null?'n/a':(x>0?'+':'')+fmt(x,2)+'%';
const cls = x => x==null?'flat':(x>0?'up':(x<0?'down':'flat'));
const gradeColor = {excellent:'#14F1B2',good:'#4C8DFF',fair:'#FFB454','at-risk':'#FF8C4A',critical:'#FF5C7A'};


const ICONS = {
  ok:   '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
  warn: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/></svg>',
  info: '<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/></svg>',
};


function seriesOf(path){
  const out=[];
  for(const s of DATA.history||[]){let n=s;for(const k of path){if(!n||typeof n!=='object'){n=undefined;break}n=n[k]}if(typeof n==='number'&&isFinite(n))out.push(n)}
  return out;
}
function relTime(iso){
  if(!iso) return '';
  const diff=Math.max(0,(Date.now()-new Date(iso).getTime())/1000);
  if(diff<60) return 'just now';
  if(diff<3600) return Math.floor(diff/60)+' min ago';
  if(diff<86400) return Math.floor(diff/3600)+'h ago';
  return Math.floor(diff/86400)+'d ago';
}
function morph(el,target,dec=2,pre=''){
  const t0=performance.now(),dur=1200;
  (function tick(n){
    const p=Math.min(1,(n-t0)/dur), e=1-Math.pow(1-p,3);
    el.textContent=pre+Number(target*e).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec});
    if(p<1)requestAnimationFrame(tick);
  })(t0);
}
function arrow(x){ return x==null?'&mdash;':(x>=0?'&#9650; ':'&#9660; ')+pct(Math.abs(x)); }


const net=DATA.network,val=DATA.validators,eco=DATA.economics,fees=DATA.fees,hs=DATA.health_score;
const tps=net.tps||{},ep=net.epoch||{};
let chartState=null, chartWindow=24;
function histDelta(path){const s=seriesOf(path);return (s.length<2||!s[0])?null:((s[s.length-1]-s[0])/s[0])*100;}


/* ---- tape ---- */
function renderTape(){
  const sup=net.supply||{};
  const items=[
    ['SOL',usd(eco.sol_price_usd),eco.sol_price_24h_change_pct],
    ['TPS',fmt(tps.avg,0),histDelta(['metrics','tps','avg'])],
    ['TVL',usd(eco.tvl_usd),eco.tvl_24h_change_pct],
    ['DEX 24h',usd(eco.dex_volume_24h_usd),eco.dex_volume_24h_change_pct],
    ['Stables',usd(eco.stablecoin_supply_usd),null],
    ['Med fee',fees.median_fee_sol?fmt(fees.median_fee_sol,8):'n/a',null],
    ['Validators',fmt(val.active_count,0),null],
    ['Delinq',fmt(val.delinquent_stake_pct,2)+'%',null],
    ['Epoch',ep.number,null],
    ['Supply',fmt(sup.circulating_sol,0),null],
  ];
  const cell=it=>`<span class="tk">${it[0]}<b>${it[1]}</b> ${it[2]==null?'':`<span class="${it[2]>=0?'up':'down'}">${arrow(it[2])}</span>`}</span>`;
  const one=items.map(cell).join('<span class="tk" style="color:var(--t4)">&middot;</span>');
  $('tapeTrack').innerHTML=one+one;
}


/* ---- hero ---- */
function renderHero(){
  const d=eco.sol_price_24h_change_pct;
  const pEl=$('heroPrice');
  if(eco.sol_price_usd!=null){ morph(pEl,eco.sol_price_usd,2,'$'); }
  else pEl.textContent='n/a';
  const chg=$('heroChg');
  chg.className='hero-chg '+cls(d);
  chg.innerHTML=arrow(d)+' <span style="opacity:.65;font-weight:400">24h</span>';
  /* monumental sparkline */
  const s=seriesOf(['metrics','economics','sol_price_usd']);
  const W=560,H=86,P=4;
  if(s.length>1){
    const mn=Math.min(...s),mx=Math.max(...s),rng=(mx-mn)||1;
    const pts=s.map((v,i)=>[P+(i/(s.length-1))*(W-2*P), H-P-((v-mn)/rng)*(H-2*P-18)]);
    const line=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');
    const col=d>=0?'#14F1B2':'#FF5C7A';
    $('heroSpark').innerHTML=`
      <defs><linearGradient id="hfill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${col}" stop-opacity=".28"/><stop offset="100%" stop-color="${col}" stop-opacity="0"/></linearGradient></defs>
      <path d="${line} L${W-P},${H} L${P},${H} Z" fill="url(#hfill)" class="fade-in"/>
      <path d="${line}" fill="none" stroke="${col}" stroke-width="2.4" stroke-linecap="round" class="draw"/>
      <circle cx="${pts[pts.length-1][0]}" cy="${pts[pts.length-1][1]}" r="4" fill="${col}" class="fade-in"><animate attributeName="r" values="4;6;4" dur="2s" repeatCount="indefinite"/></circle>`;
  }
  const st=(net.slot_time_sec||{}).avg;
  $('heroMeta').innerHTML=[
    ['Epoch','<span>'+ep.number+'</span> &middot; '+fmt(ep.progress_pct,0)+'%'],
    ['Slot time',st!=null?fmt(st,3)+'s':'n/a'],
    ['Slot',fmt(net.slot,0)],
    ['Block',fmt(net.block_height,0)],
    ['Refresh','every '+DATA.config.refresh_interval_min+' min'],
  ].map(m=>`<div class="hm"><div class="k">${m[0]}</div><div class="v">${m[1]}</div></div>`).join('');
  $('livePill').textContent='Live · synced '+relTime(DATA.generated_at);
}


/* ---- health + minis ---- */
function gaugeSVG(score,size=118,sw=10){
  const r=(size-sw)/2,c=2*Math.PI*r,off=c*(1-score/100),g=gradeColor[hs?.grade]||'#14F1B2';
  return `<svg width="${size}" height="${size}"><circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="rgba(148,163,196,.12)" stroke-width="${sw}"/><circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="${g}" stroke-width="${sw}" stroke-linecap="round" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${c.toFixed(1)}" style="transition:stroke-dashoffset 1.4s cubic-bezier(.22,.9,.28,1) .4s" onload="requestAnimationFrame(()=>this.style.strokeDashoffset=${off.toFixed(1)})"/></svg>`;
}
function renderHealth(){
  if(!hs){ $('healthCard').innerHTML='<div class="empty">n/a</div>'; return; }
  $('healthCard').innerHTML=`
    <div class="gauge">${gaugeSVG(hs.score)}<div class="gc"><div class="n">${hs.score}</div><div class="l">health</div></div></div>
    <div class="health-info">
      <div class="grade" style="color:${gradeColor[hs.grade]}">${esc(hs.grade)}</div>
      <div class="hint">Composite of ${Object.keys(hs.components||{}).length} network signals &mdash; performance, stake &amp; economics.</div>
    </div>`;
  const tpsD=histDelta(['metrics','tps','avg']), tvlD=eco.tvl_24h_change_pct;
  $('miniCards').innerHTML=[
    {k:'TPS avg',v:fmt(tps.avg,0),s:`<span class="${cls(tpsD)}" style="color:${tpsD>=0?'var(--teal)':'var(--rose)'}">${arrow(tpsD)}</span> hist`},
    {k:'TVL',v:eco.tvl_usd!=null?'$'+fmt(eco.tvl_usd/1e9,2)+'B':'n/a',s:`<span style="color:${tvlD>=0?'var(--teal)':'var(--rose)'}">${arrow(tvlD)}</span> 24h`},
    {k:'Validators',v:fmt(val.active_count,0),s:fmt(val.delinquent_stake_pct,2)+'% delinquent'},
    {k:'Med fee',v:fees.median_fee_sol?fmt(fees.median_fee_sol,5):'n/a',s:'SOL per tx'},
  ].map(c=>`<div class="mini"><div class="k">${c.k}</div><div class="v">${c.v}</div><div class="s">${c.s}</div></div>`).join('');
}


/* ---- anomalies ---- */
function renderAnoms(){
  const anoms=DATA.anomalies||[];
  $('anomNote').textContent=anoms.length?anoms.length+' active signal'+(anoms.length>1?'s':''):'all systems nominal';
  if(!anoms.length){ $('anoms').innerHTML=`<div class="chip ok">${ICONS.ok}<b>All clear</b>&nbsp;no anomalies detected</div>`; return; }
  const sevMap={critical:'',warning:'warn',info:'info'};
  const sevIcon={critical:ICONS.warn,warning:ICONS.warn,info:ICONS.info};
  $('anoms').innerHTML=anoms.map(a=>{
    const v=a.value!=null?` <span class="mono">${esc(String(a.value))}</span>`:'';
    const z=a.z!=null?` <span class="mono" style="color:var(--violet)">z=${fmt(a.z,2)}</span>`:'';
    return `<div class="chip ${sevMap[a.severity]||''}" title="${esc(a.message)}">${sevIcon[a.severity]||ICONS.info}<b>${esc(a.metric)}</b>&nbsp;${esc(a.message)}${v}${z}</div>`;
  }).join('');
}


/* ---- chart ---- */
function renderChart(){
  const hist=DATA.history||[], now=Date.now()/1000, cutoff=now-chartWindow*3600;
  const pts=hist.filter(h=>h.ts>=cutoff), W=640,H=240,PAD=10;
  if(pts.length<2){ $('chartWrap').innerHTML='<div class="empty">Not enough snapshots yet &mdash; collected hourly</div>'; $('chartLegend').innerHTML=''; chartState=null; return; }
  const pv=pts.map(h=>h.metrics?.economics?.sol_price_usd).filter(v=>typeof v==='number');
  if(pv.length<2){ $('chartWrap').innerHTML='<div class="empty">Incomplete data</div>'; return; }
  const pMin=Math.min(...pv),pMax=Math.max(...pv),pRng=(pMax-pMin)||1;
  const tvv=pts.map(h=>h.metrics?.economics?.tvl_usd).filter(v=>typeof v==='number');
  const tMin=tvv.length?Math.min(...tvv):0,tMax=tvv.length?Math.max(...tvv):1,tRng=(tMax-tMin)||1;
  const X=i=>PAD+(i/(pts.length-1))*(W-2*PAD), Yp=v=>H-PAD-((v-pMin)/pRng)*(H-2*PAD-30), Yt=v=>H-PAD-((v-tMin)/tRng)*(H-2*PAD-30);
  let pLine='',tLine='';
  pts.forEach((h,i)=>{
    const px=X(i), py=typeof h.metrics?.economics?.sol_price_usd==='number'?Yp(h.metrics.economics.sol_price_usd):null;
    const ty=typeof h.metrics?.economics?.tvl_usd==='number'?Yt(h.metrics.economics.tvl_usd):null;
    if(py!=null) pLine+=(pLine?'L':'M')+px.toFixed(1)+','+py.toFixed(1)+' ';
    if(ty!=null) tLine+=(tLine?'L':'M')+px.toFixed(1)+','+ty.toFixed(1)+' ';
  });
  const area=pLine.trim()+` L${W-PAD},${H-PAD} L${PAD},${H-PAD} Z`;
  const grid=[52,104,156,208].map(y=>`<line class="grid-line" x1="0" y1="${y}" x2="${W}" y2="${y}"/>`).join('');
  $('chartWrap').innerHTML=`<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
    <defs><linearGradient id="cFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#14F1B2" stop-opacity=".3"/><stop offset="100%" stop-color="#14F1B2" stop-opacity="0"/></linearGradient></defs>
    ${grid}
    <path d="${area}" fill="url(#cFill)" class="fade-in"/>
    <polyline fill="none" stroke="#14F1B2" stroke-width="2.4" stroke-linecap="round" points="${pLine.trim()}" class="draw"/>
    ${tvv.length>=2?`<polyline fill="none" stroke="#9945FF" stroke-width="1.8" stroke-dasharray="5 5" points="${tLine.trim()}" class="draw"/>`:''}
    <line class="xhair" id="cxLine" x1="0" y1="0" x2="0" y2="${H}"/>
  </svg><div class="tt" id="chartTT"></div>`;
  $('chartLegend').innerHTML=`<span class="lg"><span class="sw" style="background:var(--teal)"></span>SOL &middot; ${usd(eco.sol_price_usd)}</span><span class="lg"><span class="sw" style="background:var(--violet)"></span>TVL &middot; $${fmt(eco.tvl_usd/1e9,2)}B</span>`;
  chartState={pts,X,W};
}


/* ---- donut ---- */
function renderDonut(){
  const top20=(val.top_by_stake||[]).reduce((a,v)=>a+(v.stake_sol||0),0);
  const total=val.active_stake_sol||1, share=(top20/total)*100, nk=val.nakamoto_coefficient;
  $('donutWrap').innerHTML=`<div class="donut" style="--p1:${share.toFixed(1)}%"><div class="donut-c"><div class="n">${fmt(share,1)}%</div><div class="l">top 20</div></div></div>
    <div class="legend">
      <div class="row"><span class="sw" style="background:var(--teal)"></span>Top 20<span class="mono">${fmt(share,1)}%</span></div>
      <div class="row"><span class="sw" style="background:var(--violet)"></span>Others<span class="mono">${fmt(100-share,1)}%</span></div>
      <div class="row dim">Avg commission<span class="mono">${fmt(val.avg_commission_pct,1)}%</span></div>
      <div class="row dim">Delinquent<span class="mono">${fmt(val.delinquent_stake_pct,2)}%</span></div>
      ${nk!=null?`<div class="row"><span class="sw" style="background:var(--amber)"></span>Nakamoto coeff.<b>${nk}</b></div>`:''}
    </div>`;
}


/* ---- growth ---- */
function renderGrowth(){
  const eg=DATA.ecosystem_growth||{}, dau=eg.daily_active_addresses||{}, tok=eg.tokenized_equities||{};
  const cards=[
    {k:'Daily Active Addresses',v:dau.available&&dau.value!=null?fmt(dau.value,0):'n/a',na:!dau.available,s:dau.source||'dune'},
    {k:'Tokenized Equities Vol 24h',v:tok.available&&tok.volume_usd!=null?usd(tok.volume_usd,0):'n/a',na:!tok.available,s:tok.source||'dune'},
    {k:'Tokenized Equities AUM',v:tok.available&&tok.aum_usd!=null?usd(tok.aum_usd,0):'n/a',na:!tok.available,s:tok.source||'dune'},
    {k:'Tokenized Equities Holders',v:tok.available&&tok.holders!=null?fmt(tok.holders,0):'n/a',na:!tok.available,s:tok.source||'dune'},
  ];
  $('growthGrid').innerHTML=cards.map(c=>`<div class="g-card"><div class="k">${c.k}</div><div class="v ${c.na?'na':''}">${c.v}${c.na&&c.k.includes('Addresses')?' (key not set)':''}</div><div class="s">source: ${esc(c.s)}</div></div>`).join('');
  if(!dau.available&&!tok.available) $('growthNote').textContent='Dune Analytics · key not configured';
}


/* ---- validators ---- */
let valRows=[];
function renderValidators(){
  valRows=(val.top_by_stake||[]).map((v,i)=>{
    const pk=v.pubkey||'', rk=i+1;
    return {rk,pk,v,html:`<tr>
      <td><span class="rank ${rk===1?'r1':rk===2?'r2':rk===3?'r3':''}">${rk}</span></td>
      <td><span class="avatar">${esc(pk.slice(0,2).toUpperCase())}</span><span class="mono">${esc(pk.slice(0,4))}&hellip;${esc(pk.slice(-4))}</span></td>
      <td class="num mono">${fmt(v.stake_sol,0)}</td>
      <td class="num mono">${fmt(v.stake_pct,2)}%</td>
      <td class="num mono">${fmt(v.commission_pct,0)}%</td>
      <td class="num"><span class="dot ok"></span>Active</td></tr>`};
  });
  applyValView();
}
function applyValView(){
  const q=($('valFilter').value||'').toLowerCase();
  const rows=valRows.filter(r=>!q||r.pk.toLowerCase().includes(q));
  $('valTbody').innerHTML=rows.map(r=>r.html).join('')||`<tr><td colspan="6" class="empty">No validators match &ldquo;${esc(q)}&rdquo;</td></tr>`;
}


/* ---- news & sources ---- */
function renderNews(){
  const tab=(document.querySelector('#newsTabs .tab.active')||{}).dataset?.news||'simd';
  if(tab==='twitter'){
    const tw=DATA.news?.twitter||{}, tweets=tw.tweets||[];
    if(!tweets.length){ $('newsList').innerHTML=`<div class="empty">No tweets available${tw.degraded?.length?` (degraded: ${esc(tw.degraded.join(', '))})`:''}.</div>`; return; }
    $('newsList').innerHTML=tweets.slice(0,8).map(x=>{
      const txt=(x.text||'').slice(0,200), url=x.id?`https://x.com/${esc(x.handle)}/status/${esc(x.id)}`:'';
      return `<div class="news-item" ${url?`onclick="window.open('${url}','_blank')"`:''}><div class="title">@${esc(x.handle)} &mdash; ${esc(txt)}</div><div class="meta"><span class="badge teal">X</span>${relTime(x.created_at)}</div></div>`;
    }).join('');
    return;
  }
  const s=DATA.news?.simd||[];
  if(!s.length){ $('newsList').innerHTML='<div class="empty">No recent SIMD proposals.</div>'; return; }
  $('newsList').innerHTML=s.slice(0,6).map(x=>{
    const badges=[x.type==='PR'?'<span class="badge violet">PR</span>':'<span class="badge teal">Issue</span>'];
    (x.labels||[]).slice(0,2).forEach(l=>badges.push(`<span class="badge">${esc(l)}</span>`));
    return `<div class="news-item" onclick="window.open('${esc(x.url)}','_blank')"><div class="title">#${x.number} &middot; ${esc(x.title)}</div><div class="meta">${badges.join('')}updated ${relTime(x.updated_at)}</div></div>`;
  }).join('');
}
/* ---- upgrade radar ---- */
function renderUpgrades(){
  const up=DATA.upgrades||{};
  const seen=new Set(), items=[...(up.watchlist||[]),...(up.keyword_hits||[])].filter(u=>{
    if(seen.has(u.number)) return false; seen.add(u.number); return true;
  });
  if(!items.length){
    $('upList').innerHTML='<div class="empty">No tracked upgrades found this run.</div>';
  } else {
    $('upList').innerHTML=items.slice(0,8).map(u=>{
      const st=(u.state||'open').toLowerCase();
      const kw=u.keyword&&u.keyword!=='watchlist'?`<span class="badge amber">${esc(u.keyword)}</span>`:'';
      const labels=(u.labels||[]).slice(0,2).map(l=>`<span class="badge">${esc(l)}</span>`).join('');
      return `<div class="up-item" onclick="window.open('${esc(u.url)}','_blank')">
        <div style="flex:1;min-width:0"><div class="title">SIMD #${u.number} &middot; ${esc(u.title)}</div>
        <div class="meta">${kw}${labels}updated ${relTime(u.updated_at)}</div></div>
        <span class="up-state ${st}">${esc(st)}</span></div>`;
    }).join('');
    $('upNote').textContent=items.length+' tracked proposal'+(items.length>1?'s':'');
  }
  const rel=up.agave_releases||[];
  $('relList').innerHTML=rel.length?rel.map(r=>`<div class="rel-item" onclick="window.open('${esc(r.url)}','_blank')">
    <span class="nm">${esc(r.name)}${r.prerelease?' <span class="badge amber">pre</span>':''}</span>
    <span class="dt">${esc((r.published_at||'').slice(0,10))}</span></div>`).join('')
    :'<div class="empty">Release feed unavailable.</div>';
}
const SRC_NAMES={rpc_health:'Solana RPC',upgrade_radar:'Upgrade radar',rpc_epoch:'Solana RPC · epoch',rpc_slot:'Solana RPC · slot',rpc_block_height:'Solana RPC · height',rpc_perf:'Solana RPC · perf',rpc_votes:'Solana RPC · votes',rpc_supply:'Solana RPC · supply',rpc_fee_sampling:'RPC fee sampling',defillama_tvl:'DeFiLlama · TVL',defillama_tvl_history:'DeFiLlama · TVL history',defillama_dex:'DeFiLlama · DEX',defillama_stablecoins:'DeFiLlama · stablecoins',defillama_comparison:'DeFiLlama · multi-chain',coingecko:'CoinGecko',github_simd:'GitHub · SIMD',statuspage:'status.solana.com',dune:'Dune Analytics',twitter:'X / Twitter'};
function renderSources(){
  $('srcList').innerHTML=Object.entries(DATA.sources_ok||{}).map(([k,v])=>`<div class="src"><span class="name"><span class="dot ${v?'ok':'bad'}"></span>${esc(SRC_NAMES[k]||k)}</span><span class="lat ${v?'on':'off'}">${v?'online':'failed'}</span></div>`).join('');
}


/* ---- crosshair ---- */
function wireCrosshair(){
  const wrap=$('chartWrap');
  wrap.addEventListener('mousemove',e=>{
    if(!chartState) return;
    const rect=wrap.getBoundingClientRect();
    const i=Math.round(((e.clientX-rect.left)/rect.width)*(chartState.pts.length-1));
    const px=chartState.X(i), h=chartState.pts[i];
    const line=$('cxLine'), tt=$('chartTT');
    if(!line||!tt) return;
    line.setAttribute('x1',px);line.setAttribute('x2',px);
    const d=new Date(h.ts*1000).toISOString().slice(0,16).replace('T',' ');
    const p=h.metrics?.economics?.sol_price_usd, t=h.metrics?.economics?.tvl_usd;
    tt.style.opacity=1;
    tt.innerHTML=`<div class="ttl">${esc(d)}</div><div class="row"><span style="color:var(--teal)">&#9679;</span> $${fmt(p)}</div>${t!=null?`<div class="row"><span style="color:var(--violet)">&#9679;</span> $${fmt(t/1e9,2)}B</div>`:''}`;
    const tw=tt.offsetWidth, cssX=(px/chartState.W)*rect.width;
    tt.style.left=Math.min(Math.max(cssX+14,4),rect.width-tw-8)+'px';
    tt.style.top='8px';
  });
  wrap.addEventListener('mouseleave',()=>{const tt=$('chartTT');if(tt)tt.style.opacity=0});
}


/* ---- init ---- */
renderTape(); renderHero(); renderHealth(); renderAnoms(); renderChart(); renderDonut(); renderGrowth(); renderValidators(); renderNews(); renderUpgrades(); renderSources(); wireCrosshair();
$('footMeta').textContent='Schema v'+String(DATA.schema_version||1)+' · generated '+relTime(DATA.generated_at)+' · MIT License';
setInterval(()=>{const p=$('livePill');if(p)p.textContent='Live · synced '+relTime(DATA.generated_at);},30000);


/* sort + filter + tabs */
let sortKey=null, sortAsc=false;
document.querySelectorAll('th[data-sort]').forEach(th=>{
  th.addEventListener('click',()=>{
    const key=th.dataset.sort;
    if(sortKey===key) sortAsc=!sortAsc; else {sortKey=key;sortAsc=true;}
    document.querySelectorAll('th[data-sort]').forEach(x=>x.classList.remove('asc','desc'));
    th.classList.add(sortAsc?'asc':'desc');
    valRows=[...valRows].sort((a,b)=>sortAsc?(a.v[key]??0)-(b.v[key]??0):(b.v[key]??0)-(a.v[key]??0));
    applyValView();
  });
});
$('valFilter').addEventListener('input',applyValView);
document.querySelectorAll('#newsTabs .tab').forEach(t=>t.addEventListener('click',()=>{
  document.querySelectorAll('#newsTabs .tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active'); renderNews();
}));
$('chartTabs').addEventListener('click',e=>{
  const t=e.target.closest('.tab'); if(!t) return;
  document.querySelectorAll('#chartTabs .tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active'); chartWindow=parseInt(t.dataset.w,10); renderChart();
});
</script>
</body>
</html>"""