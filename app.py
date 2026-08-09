from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

from src.macrofund.engine import run_engine

app = FastAPI(
    title="AI Global Macro Hedge Fund Engine",
    version="0.1.0",
    description="Systematic global-macro regime, signal, portfolio and backtest research engine.",
)

DASHBOARD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#151916">
<meta name="description" content="AI Global Macro Hedge Fund Engine, a systematic cross-asset macro research platform.">
<title>AI Global Macro Hedge Fund Engine</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..125,100..900&family=Manrope:wght@300..800&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#151916;
  --ink-2:#202621;
  --paper:#f6f4ed;
  --paper-2:#efede5;
  --stone:#e7e4da;
  --line:rgba(21,25,22,.14);
  --line-dark:rgba(255,255,255,.15);
  --sage:#3f725c;
  --sage-dark:#2c5646;
  --sage-soft:#c8d8cf;
  --mint:#92bba7;
  --red:#a6534c;
  --white:#fffdf7;
  --muted:#777c76;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'Manrope','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased}
button,a{font:inherit;color:inherit}button{cursor:pointer}
::selection{background:var(--sage);color:#fff}
.presentation-shell{min-height:100vh;overflow:clip}
.topbar{position:fixed;z-index:80;top:0;left:0;right:0;height:62px;display:grid;grid-template-columns:260px 1fr auto;align-items:center;gap:20px;padding:0 24px;background:rgba(246,244,237,.9);backdrop-filter:blur(18px);border-bottom:1px solid rgba(21,25,22,.1)}
.brand-mark{display:flex;align-items:center;gap:10px;border:0;background:transparent;padding:0;font-size:10px;letter-spacing:.12em;font-weight:800;text-transform:uppercase}
.brand-block{width:17px;height:17px;display:inline-block;background:var(--sage);position:relative}.brand-block:after{content:'';position:absolute;width:7px;height:7px;right:-4px;top:-4px;border:1px solid var(--ink)}
.nav-links{display:flex;align-items:center;justify-content:center;gap:2px;overflow-x:auto;scrollbar-width:none}.nav-links::-webkit-scrollbar{display:none}
.nav-links button{white-space:nowrap;border:0;background:transparent;padding:9px 8px;font-size:9px;text-transform:uppercase;letter-spacing:.09em;opacity:.44;transition:.2s}.nav-links button:hover,.nav-links button.active{opacity:1}.nav-links button.active{color:var(--sage);font-weight:800}
.top-actions{display:flex;gap:7px;align-items:center}.icon-action,.refresh-action{height:34px;border:1px solid rgba(21,25,22,.15);background:rgba(255,255,255,.38);display:grid;place-items:center;transition:.2s}.icon-action{width:34px}.refresh-action{padding:0 12px;font-size:9px;text-transform:uppercase;letter-spacing:.08em;font-weight:700}.icon-action:hover,.refresh-action:hover{background:var(--ink);color:#fff;border-color:var(--ink)}
.live-dot{display:flex;align-items:center;gap:6px;font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--sage);font-weight:800;margin-left:5px}.live-dot i{display:block;width:6px;height:6px;border-radius:50%;background:var(--sage);box-shadow:0 0 0 4px rgba(63,114,92,.09)}
.slide{min-height:100vh;position:relative;scroll-margin-top:0;display:flex;align-items:center;overflow:hidden}
.slide-inner{width:min(1240px,calc(100% - 96px));margin:0 auto;padding:104px 0 78px;position:relative;z-index:2}
.light-slide{background:var(--paper)}.stone-slide{background:var(--stone)}.dark-slide{background:var(--ink);color:var(--white)}.sage-slide{background:var(--sage-dark);color:var(--white)}
.eyebrow{display:inline-flex;font-size:9px;line-height:1;letter-spacing:.18em;text-transform:uppercase;font-weight:800;color:var(--sage);margin-bottom:20px}.eyebrow-dark{color:#b8d1c4}
.section-heading{max-width:980px;margin-bottom:44px}.section-heading h2{font-family:'Archivo',sans-serif;font-weight:530;letter-spacing:-.048em;font-size:clamp(44px,5vw,74px);line-height:.96;margin:0;max-width:1000px}.section-copy{max-width:760px;font-size:14px;line-height:1.76;opacity:.68;margin:22px 0 0}
.cover-slide{background:var(--ink);color:var(--white)}
.blueprint-grid{position:absolute;inset:0;opacity:.17;background-image:linear-gradient(rgba(255,255,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.08) 1px,transparent 1px);background-size:46px 46px}
.cover-slide:before{content:'';position:absolute;right:-11vw;top:-16vh;width:62vw;height:132vh;border:1px solid rgba(255,255,255,.14);transform:rotate(18deg)}
.cover-slide:after{content:'';position:absolute;right:8vw;top:14vh;width:27vw;height:70vh;border:28px solid rgba(63,114,92,.56);transform:skew(-11deg)}
.cover-line{position:absolute;border:1px solid rgba(255,255,255,.11);z-index:1}.cover-line.a{right:18%;top:17%;width:16%;height:66%}.cover-line.b{right:9%;top:29%;width:35%;height:34%}
.cover-inner{min-height:100vh;display:flex;flex-direction:column;justify-content:center}.cover-kicker{font-size:9px;letter-spacing:.18em;font-weight:800;opacity:.55;margin-bottom:28px;text-transform:uppercase}
.cover-inner h1{font-family:'Archivo',sans-serif;font-size:clamp(76px,10.2vw,154px);line-height:.79;letter-spacing:-.072em;font-weight:560;margin:0;max-width:1020px;position:relative;z-index:2}.cover-inner h1 span{display:block;color:#78a58e;margin-left:8vw}
.cover-meta-grid{margin-top:54px;display:grid;grid-template-columns:1.35fr .65fr;gap:48px;align-items:end;max-width:1030px}.cover-subtitle{font-family:'Archivo',sans-serif;font-size:clamp(19px,2.2vw,29px);line-height:1.22;margin:0;max-width:590px;font-weight:430}.cover-tagline{opacity:.55;margin:12px 0 0;font-size:12px}
.live-card{padding-left:22px;border-left:1px solid rgba(255,255,255,.24);display:flex;flex-direction:column;gap:5px}.live-card span,.live-card small{font-size:9px;text-transform:uppercase;letter-spacing:.12em;opacity:.52}.live-card strong{font-family:'Archivo',sans-serif;font-size:18px;font-weight:500;color:#a8c8b8}
.scroll-cue{margin-top:48px;display:flex;align-items:center;gap:11px;width:fit-content;background:transparent;color:#fff;border:0;padding:0;opacity:.55;font-size:10px;letter-spacing:.09em;text-transform:uppercase}.scroll-cue b{font-size:17px;font-weight:400}
.state-layout{display:grid;grid-template-columns:.92fr 1.08fr;gap:34px;align-items:stretch}.regime-panel{background:var(--ink);color:var(--white);padding:38px;min-height:420px;position:relative;overflow:hidden}.regime-panel:after{content:'';position:absolute;width:300px;height:300px;border:1px solid rgba(255,255,255,.08);right:-90px;bottom:-115px;transform:rotate(26deg)}
.regime-label{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:#a7c6b6;font-weight:800}.regime-name{font-family:'Archivo',sans-serif;font-size:clamp(48px,6vw,88px);line-height:.88;letter-spacing:-.06em;font-weight:530;margin:22px 0 16px;color:#8eb9a4}.regime-date{font-size:11px;opacity:.52}.confidence-wrap{margin-top:55px;max-width:430px}.confidence-head{display:flex;justify-content:space-between;font-size:10px;letter-spacing:.06em;text-transform:uppercase;opacity:.68}.confidence-track{height:3px;background:rgba(255,255,255,.12);margin-top:10px}.confidence-fill{height:100%;background:#8eb9a4;width:0;transition:width .55s ease}
.factor-grid{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line);border-left:1px solid var(--line)}.factor-card{min-height:210px;padding:26px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);display:flex;flex-direction:column;justify-content:space-between}.factor-card .factor-no{font-size:9px;letter-spacing:.14em;opacity:.4}.factor-card h3{font-family:'Archivo',sans-serif;font-size:22px;font-weight:520;margin:0}.factor-card .factor-value{font-family:'Archivo',sans-serif;font-size:39px;letter-spacing:-.05em;color:var(--sage);font-weight:560}.factor-card .factor-copy{font-size:10px;opacity:.5;margin-top:6px}.factor-card.negative .factor-value{color:var(--red)}
.table-shell{border:1px solid var(--line);background:rgba(255,255,255,.34)}.table-headline{display:grid;grid-template-columns:1.1fr .9fr;border-bottom:1px solid var(--line)}.table-headline>div{padding:24px}.table-headline>div+div{border-left:1px solid var(--line)}.table-headline strong{font-family:'Archivo',sans-serif;font-size:22px;font-weight:520;display:block}.table-headline p{font-size:11px;line-height:1.55;opacity:.55;margin:6px 0 0}.signal-table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;min-width:780px}th{font-size:8px;letter-spacing:.13em;text-transform:uppercase;opacity:.45;font-weight:800;padding:12px 14px;text-align:right;border-bottom:1px solid var(--line)}td{padding:16px 14px;text-align:right;border-bottom:1px solid var(--line);font-size:11px}th:first-child,td:first-child{text-align:left}tbody tr:last-child td{border-bottom:0}tbody tr:hover{background:rgba(63,114,92,.045)}
.asset-name strong{display:block;font-family:'Archivo',sans-serif;font-size:17px;font-weight:550}.asset-name small{display:block;font-size:9px;opacity:.45;margin-top:3px}.signal-pill{display:inline-flex;align-items:center;gap:6px;font-size:9px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}.signal-pill:before{content:'';width:6px;height:6px;border-radius:50%;background:currentColor}.long{color:var(--sage)}.short{color:var(--red)}.neutral{color:#858984}.positive{color:var(--sage)}.negative{color:var(--red)}
.portfolio-layout{display:grid;grid-template-columns:.72fr 1.28fr;border:1px solid rgba(255,255,255,.17);min-height:460px}.portfolio-intro{padding:34px;border-right:1px solid rgba(255,255,255,.17);position:relative}.portfolio-intro>span{font-size:9px;letter-spacing:.16em;color:#a7c6b6;text-transform:uppercase;font-weight:800}.portfolio-intro h3{font-family:'Archivo',sans-serif;font-size:43px;line-height:.96;font-weight:520;margin:22px 0 16px}.portfolio-intro p{font-size:13px;line-height:1.7;opacity:.57}.book-stats{display:grid;grid-template-columns:1fr 1fr;margin-top:52px;border-top:1px solid rgba(255,255,255,.15);border-left:1px solid rgba(255,255,255,.15)}.book-stat{padding:18px;border-right:1px solid rgba(255,255,255,.15);border-bottom:1px solid rgba(255,255,255,.15)}.book-stat small{display:block;font-size:8px;letter-spacing:.12em;text-transform:uppercase;opacity:.44}.book-stat strong{font-family:'Archivo',sans-serif;font-size:24px;font-weight:500;display:block;margin-top:7px}
.exposure-panel{padding:31px}.exposure-list{display:flex;flex-direction:column;gap:20px}.exposure-row{display:grid;grid-template-columns:58px 1fr 68px;gap:13px;align-items:center}.exposure-row .sym{font-family:'Archivo',sans-serif;font-size:14px}.exposure-track{height:4px;background:rgba(255,255,255,.1);position:relative}.exposure-track:after{content:'';position:absolute;left:50%;top:-4px;bottom:-4px;width:1px;background:rgba(255,255,255,.2)}.exposure-bar{position:absolute;top:0;height:100%}.exposure-bar.longbar{left:50%;background:#8eb9a4}.exposure-bar.shortbar{right:50%;background:#c97670}.exposure-value{text-align:right;font-size:11px;font-weight:700}
.performance-hero{display:grid;grid-template-columns:.7fr 1.3fr;border-top:1px solid var(--line);border-left:1px solid var(--line)}.performance-lead{padding:32px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);display:flex;flex-direction:column;justify-content:space-between;min-height:390px}.performance-lead small{font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:var(--sage);font-weight:800}.performance-lead strong{font-family:'Archivo',sans-serif;font-size:84px;line-height:.86;font-weight:530;letter-spacing:-.065em;color:var(--sage)}.performance-lead p{font-size:12px;line-height:1.7;opacity:.55;max-width:330px}.performance-grid{display:grid;grid-template-columns:repeat(3,1fr)}.perf-card{padding:27px 23px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);min-height:195px}.perf-card small{font-size:8px;letter-spacing:.13em;text-transform:uppercase;opacity:.45}.perf-card strong{font-family:'Archivo',sans-serif;font-size:30px;font-weight:520;display:block;margin-top:42px}.perf-card span{font-size:9px;opacity:.43;display:block;margin-top:7px}
.benchmark-band{margin-top:28px;display:grid;grid-template-columns:1.2fr repeat(3,.6fr);border:1px solid var(--line);background:rgba(255,255,255,.38)}.benchmark-band>div{padding:18px;border-right:1px solid var(--line)}.benchmark-band>div:last-child{border-right:0}.benchmark-band small{font-size:8px;letter-spacing:.12em;text-transform:uppercase;opacity:.45}.benchmark-band strong{font-family:'Archivo',sans-serif;font-size:18px;font-weight:520;display:block;margin-top:5px}
.memo-layout{display:grid;grid-template-columns:.65fr 1.35fr;gap:0;border:1px solid rgba(255,255,255,.17)}.memo-side{padding:34px;border-right:1px solid rgba(255,255,255,.17);display:flex;flex-direction:column;justify-content:space-between}.memo-side .giant{font-family:'Archivo',sans-serif;font-size:105px;line-height:.8;letter-spacing:-.07em;color:#9bc2ae}.memo-side h3{font-family:'Archivo',sans-serif;font-size:30px;line-height:1.02;font-weight:510;margin:18px 0}.memo-side p{font-size:12px;line-height:1.7;opacity:.57}.memo-body{padding:34px;min-height:500px}.memo{white-space:pre-wrap;margin:0;color:rgba(255,255,255,.78);font:500 11px/1.9 'Manrope',sans-serif}.memo-note{margin-top:24px;padding-top:18px;border-top:1px solid rgba(255,255,255,.16);font-size:9px;line-height:1.65;opacity:.5}
.close-slide{text-align:left}.close-grid{position:absolute;inset:0;opacity:.17;background-image:linear-gradient(rgba(255,255,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.08) 1px,transparent 1px);background-size:46px 46px}.close-inner{min-height:100vh;display:flex;flex-direction:column;justify-content:center}.close-inner h2{font-family:'Archivo',sans-serif;font-size:clamp(64px,9vw,132px);line-height:.82;letter-spacing:-.07em;font-weight:550;margin:0;max-width:1030px}.close-inner h2 span{display:block;color:#7fae96;margin-left:7vw}.close-copy{font-size:14px;line-height:1.7;opacity:.57;max-width:610px;margin:40px 0 0}.close-meta{display:flex;gap:34px;flex-wrap:wrap;margin-top:38px;font-size:9px;text-transform:uppercase;letter-spacing:.12em;opacity:.48}.footer-note{position:absolute;bottom:28px;left:0;right:0;width:min(1240px,calc(100% - 96px));margin:auto;display:flex;justify-content:space-between;gap:20px;font-size:8px;text-transform:uppercase;letter-spacing:.12em;opacity:.35}
.loading{min-height:260px;display:grid;place-items:center;border:1px solid var(--line);font-size:10px;text-transform:uppercase;letter-spacing:.12em;opacity:.55}.error{border:1px solid rgba(166,83,76,.4);background:rgba(166,83,76,.09);padding:18px;color:#7d302c;font-size:12px;line-height:1.6}.mobile-menu{display:none}
@media(max-width:1000px){.state-layout,.portfolio-layout,.performance-hero,.memo-layout{grid-template-columns:1fr}.regime-panel,.portfolio-intro,.memo-side{border-right:0;border-bottom:1px solid var(--line-dark)}.performance-grid{grid-template-columns:repeat(2,1fr)}.benchmark-band{grid-template-columns:1fr 1fr}.benchmark-band>div:nth-child(2){border-right:0}.benchmark-band>div:nth-child(-n+2){border-bottom:1px solid var(--line)}}
@media(max-width:760px){.topbar{grid-template-columns:1fr auto;height:58px;padding:0 14px}.nav-links{display:none}.brand-mark{font-size:9px}.live-dot{display:none}.mobile-menu{display:grid}.slide-inner{width:min(100% - 32px,1240px);padding:86px 0 60px}.cover-inner{min-height:100vh}.cover-inner h1{font-size:clamp(62px,20vw,104px)}.cover-meta-grid{grid-template-columns:1fr;gap:28px}.live-card{padding-left:0;padding-top:17px;border-left:0;border-top:1px solid rgba(255,255,255,.22)}.section-heading{margin-bottom:30px}.section-heading h2{font-size:clamp(39px,12vw,62px)}.factor-grid{grid-template-columns:1fr}.table-headline{grid-template-columns:1fr}.table-headline>div+div{border-left:0;border-top:1px solid var(--line)}.performance-grid{grid-template-columns:1fr 1fr}.benchmark-band{grid-template-columns:1fr 1fr}.memo-side .giant{font-size:80px}.footer-note{width:calc(100% - 32px)}}
@media(max-width:480px){.top-actions .icon-action{display:none}.cover-inner h1{font-size:58px}.performance-grid,.benchmark-band{grid-template-columns:1fr}.benchmark-band>div{border-right:0!important;border-bottom:1px solid var(--line)}.exposure-row{grid-template-columns:45px 1fr 58px}.regime-panel,.portfolio-intro,.exposure-panel,.memo-side,.memo-body{padding:25px}.performance-lead strong{font-size:68px}.factor-card{min-height:175px}.close-inner h2{font-size:58px}}
</style>
</head>
<body>
<div class="presentation-shell">
<header class="topbar">
  <button class="brand-mark" onclick="goTo('cover')"><span class="brand-block"></span><span>Global Macro Engine</span></button>
  <nav class="nav-links" aria-label="Presentation sections">
    <button data-section="cover" onclick="goTo('cover')" class="active">Cover</button>
    <button data-section="state" onclick="goTo('state')">Macro State</button>
    <button data-section="signals" onclick="goTo('signals')">Signals</button>
    <button data-section="portfolio" onclick="goTo('portfolio')">Portfolio</button>
    <button data-section="performance" onclick="goTo('performance')">Performance</button>
    <button data-section="memo-section" onclick="goTo('memo-section')">IC Memo</button>
    <button data-section="close" onclick="goTo('close')">Close</button>
  </nav>
  <div class="top-actions">
    <a class="icon-action" href="/docs" title="API">API</a>
    <button class="icon-action" onclick="toggleFullscreen()" title="Fullscreen">⛶</button>
    <button class="refresh-action" id="refreshBtn" onclick="loadData(true)">Refresh</button>
    <div class="live-dot"><i></i>Live</div>
  </div>
</header>

<main>
<section id="cover" class="slide cover-slide">
  <div class="blueprint-grid"></div><div class="cover-line a"></div><div class="cover-line b"></div>
  <div class="slide-inner cover-inner">
    <div class="cover-kicker">Systematic cross-asset research platform</div>
    <h1>GLOBAL<span>MACRO</span></h1>
    <div class="cover-meta-grid">
      <div><p class="cover-subtitle">From economic regime to signal, risk and portfolio.</p><p class="cover-tagline">A systematic research engine for cross-asset macro positioning.</p></div>
      <div class="live-card"><span>Current state</span><strong id="coverRegime">Loading</strong><small id="coverDate">Fetching live market data</small></div>
    </div>
    <button class="scroll-cue" onclick="goTo('state')"><span>Enter engine</span><b>↓</b></button>
  </div>
</section>

<section id="state" class="slide light-slide"><div class="slide-inner">
  <div class="section-heading"><div class="eyebrow">01 · Macro State</div><h2>One regime. Four dimensions.</h2><p class="section-copy">The engine compresses growth, inflation, liquidity and market risk into a single interpretable macro state, then measures how confidently the current environment belongs to that regime.</p></div>
  <div id="stateContent" class="loading">Loading macro state</div>
</div></section>

<section id="signals" class="slide stone-slide"><div class="slide-inner">
  <div class="section-heading"><div class="eyebrow">02 · Signal Book</div><h2>Conviction is earned across multiple signals.</h2><p class="section-copy">Regime alignment is combined with short and medium-term momentum, trend and liquidity. The result is a directional view, not a prediction.</p></div>
  <div id="signalsContent" class="loading">Loading cross-asset signal book</div>
</div></section>

<section id="portfolio" class="slide dark-slide"><div class="slide-inner">
  <div class="section-heading"><div class="eyebrow eyebrow-dark">03 · Portfolio Construction</div><h2>Views become positions only after risk control.</h2><p class="section-copy">The signal book is converted into volatility-scaled long and short exposures, constrained by gross exposure, net exposure and single-position limits.</p></div>
  <div id="portfolioContent" class="loading" style="border-color:rgba(255,255,255,.17);color:#fff">Loading portfolio</div>
</div></section>

<section id="performance" class="slide light-slide"><div class="slide-inner">
  <div class="section-heading"><div class="eyebrow">04 · Performance</div><h2>The strategy must survive comparison.</h2><p class="section-copy">Walk-forward research performance is shown beside a simple 60/40 reference portfolio. The objective is not to hide weak periods, but to make the evidence visible.</p></div>
  <div id="performanceContent" class="loading">Loading backtest evidence</div>
</div></section>

<section id="memo-section" class="slide sage-slide"><div class="slide-inner">
  <div class="section-heading"><div class="eyebrow eyebrow-dark">05 · Investment Committee</div><h2>Turn the model into an investment thesis.</h2><p class="section-copy">The current regime, signal evidence and portfolio are translated into a concise machine-generated IC brief with risk interpretation and thesis invalidation.</p></div>
  <div id="memoContent" class="loading" style="border-color:rgba(255,255,255,.2);color:#fff">Building IC memo</div>
</div></section>

<section id="close" class="slide dark-slide close-slide">
  <div class="close-grid"></div>
  <div class="slide-inner close-inner">
    <div class="eyebrow eyebrow-dark">Systematic Macro Research</div>
    <h2>REGIME TO<span>PORTFOLIO.</span></h2>
    <p class="close-copy">The engine is designed as a transparent research system: economic state, market evidence, portfolio construction and backtest results remain visible at every stage.</p>
    <div class="close-meta"><span>FRED macro data</span><span>Yahoo market data</span><span>10% target volatility</span><span>Research use only</span></div>
  </div>
  <div class="footer-note"><span>AI Global Macro Hedge Fund Engine</span><span>Research platform · Not investment advice</span></div>
</section>
</main>
</div>
<script>
const sectionIds=['cover','state','signals','portfolio','performance','memo-section','close'];
let activeIndex=0;
const $=id=>document.getElementById(id);
const pct=x=>(100*Number(x||0)).toFixed(1)+'%';
const num=(x,d=2)=>Number(x||0).toFixed(d);
const signed=x=>(Number(x)>=0?'+':'')+num(x,2);
const cls=x=>Number(x)>0?'positive':Number(x)<0?'negative':'';
const esc=s=>String(s??'').replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));
function goTo(id){document.getElementById(id)?.scrollIntoView({behavior:'smooth',block:'start'});}
function step(delta){activeIndex=Math.max(0,Math.min(sectionIds.length-1,activeIndex+delta));goTo(sectionIds[activeIndex]);}
async function toggleFullscreen(){try{if(!document.fullscreenElement)await document.documentElement.requestFullscreen();else await document.exitFullscreen();}catch(e){}}
const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting&&entry.intersectionRatio>=.45){activeIndex=sectionIds.indexOf(entry.target.id);document.querySelectorAll('.nav-links button').forEach(b=>b.classList.toggle('active',b.dataset.section===entry.target.id));}})},{threshold:[.45,.6,.75]});
sectionIds.forEach(id=>{const el=$(id);if(el)observer.observe(el)});
window.addEventListener('keydown',e=>{if(['INPUT','TEXTAREA','SELECT'].includes(e.target?.tagName))return;if(['ArrowRight','PageDown'].includes(e.key)){e.preventDefault();step(1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();step(-1)}});
function factorCard(no,title,value,copy){return `<div class="factor-card ${Number(value)<0?'negative':''}"><span class="factor-no">0${no}</span><div><h3>${title}</h3><div class="factor-value">${signed(value)}</div><div class="factor-copy">${copy}</div></div></div>`}
function exposureWidth(v){return Math.min(50,Math.abs(Number(v||0))*125)}
async function loadData(force=false){
  const btn=$('refreshBtn');if(btn){btn.disabled=true;btn.textContent='Loading'}
  try{
    const r=await fetch('/snapshot'+(force?'?refresh=true':''));if(!r.ok)throw new Error('HTTP '+r.status);const d=await r.json();
    const rg=d.regime||{},bt=d.backtest?.strategy||{},bm=d.backtest?.benchmark_60_40||{},portfolio=d.portfolio||{};
    $('coverRegime').textContent=String(rg.regime||'Unknown').toUpperCase();$('coverDate').textContent='As of '+d.as_of+' · '+(rg.confidence==null?'N/A':pct(rg.confidence))+' confidence';
    $('stateContent').className='state-layout';$('stateContent').innerHTML=`<div class="regime-panel"><div><div class="regime-label">Current macro regime</div><div class="regime-name">${esc(String(rg.regime||'Unknown').toUpperCase())}</div><div class="regime-date">As of ${esc(d.as_of)}</div></div><div class="confidence-wrap"><div class="confidence-head"><span>Cluster confidence</span><strong>${rg.confidence==null?'N/A':pct(rg.confidence)}</strong></div><div class="confidence-track"><div class="confidence-fill" style="width:${Math.max(0,Math.min(100,Number(rg.confidence||0)*100))}%"></div></div></div></div><div class="factor-grid">${factorCard(1,'Growth',rg.growth,'Economic activity impulse')}${factorCard(2,'Inflation',rg.inflation,'Price pressure impulse')}${factorCard(3,'Liquidity',rg.liquidity,'Policy and financial conditions')}${factorCard(4,'Risk',rg.risk,'Cross-market stress state')}</div>`;
    const rows=(d.signals||[]).map(x=>`<tr><td><div class="asset-name"><strong>${esc(x.symbol)}</strong><small>${esc(x.asset)}</small></div></td><td><span class="signal-pill ${String(x.direction||'neutral').toLowerCase()}">${esc(x.direction)}</span></td><td class="${cls(x.score)}">${signed(x.score)}</td><td class="${cls(x.momentum_3m)}">${pct(x.momentum_3m)}</td><td class="${cls(x.momentum_12m)}">${pct(x.momentum_12m)}</td><td class="${cls(x.weight)}"><strong>${pct(x.weight)}</strong></td></tr>`).join('');
    $('signalsContent').className='table-shell';$('signalsContent').innerHTML=`<div class="table-headline"><div><strong>Cross-Asset Signal Book</strong><p>${(d.signals||[]).length} liquid macro instruments ranked by current conviction.</p></div><div><strong>Regime + Momentum + Liquidity</strong><p>Neutral signals remain unallocated. Long and short views pass through portfolio risk controls before becoming positions.</p></div></div><div class="signal-table-wrap"><table><thead><tr><th>Instrument</th><th>View</th><th>Score</th><th>3M Momentum</th><th>12M Momentum</th><th>Weight</th></tr></thead><tbody>${rows}</tbody></table></div>`;
    const exposures=Object.entries(portfolio.weights||{}).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1])).map(([k,v])=>{const w=exposureWidth(v);const bar=Number(v)>=0?`<span class="exposure-bar longbar" style="width:${w}%"></span>`:`<span class="exposure-bar shortbar" style="width:${w}%"></span>`;return `<div class="exposure-row"><span class="sym">${esc(k)}</span><div class="exposure-track">${bar}</div><span class="exposure-value ${cls(v)}">${pct(v)}</span></div>`}).join('');
    $('portfolioContent').className='portfolio-layout';$('portfolioContent').innerHTML=`<div class="portfolio-intro"><div><span>Target book</span><h3>Risk before return.</h3><p>The engine scales conviction by realized volatility, then applies portfolio-level exposure constraints. Neutral signals remain at zero weight.</p></div><div class="book-stats"><div class="book-stat"><small>Gross exposure</small><strong>${pct(portfolio.gross_exposure)}</strong></div><div class="book-stat"><small>Net exposure</small><strong>${pct(portfolio.net_exposure)}</strong></div><div class="book-stat"><small>Long book</small><strong>${pct(portfolio.long_exposure)}</strong></div><div class="book-stat"><small>Short book</small><strong>${pct(portfolio.short_exposure)}</strong></div></div></div><div class="exposure-panel"><div class="exposure-list">${exposures}</div></div>`;
    $('performanceContent').className='';$('performanceContent').innerHTML=`<div class="performance-hero"><div class="performance-lead"><small>Strategy Sharpe</small><strong>${num(bt.sharpe)}</strong><p>${d.backtest?.months||0} months of walk-forward research performance after transaction costs.</p></div><div class="performance-grid"><div class="perf-card"><small>CAGR</small><strong>${pct(bt.cagr)}</strong><span>Annualized return</span></div><div class="perf-card"><small>Sortino</small><strong>${num(bt.sortino)}</strong><span>Downside-adjusted return</span></div><div class="perf-card"><small>Max drawdown</small><strong>${pct(bt.max_drawdown)}</strong><span>Peak-to-trough decline</span></div><div class="perf-card"><small>Annual volatility</small><strong>${pct(bt.annual_volatility)}</strong><span>Realized volatility</span></div><div class="perf-card"><small>Calmar</small><strong>${num(bt.calmar)}</strong><span>Return vs drawdown</span></div><div class="perf-card"><small>Positive months</small><strong>${pct(bt.positive_months)}</strong><span>Monthly hit rate</span></div></div></div><div class="benchmark-band"><div><small>60/40 reference</small><strong>Strategy vs benchmark</strong></div><div><small>CAGR</small><strong>${pct(bt.cagr)} / ${pct(bm.cagr)}</strong></div><div><small>Sharpe</small><strong>${num(bt.sharpe)} / ${num(bm.sharpe)}</strong></div><div><small>Max DD</small><strong>${pct(bt.max_drawdown)} / ${pct(bm.max_drawdown)}</strong></div></div>`;
    $('memoContent').className='memo-layout';$('memoContent').innerHTML=`<div class="memo-side"><div><div class="giant">IC</div><h3>Current investment thesis</h3><p>A concise interpretation of the model state, highest-conviction positions and the conditions that would invalidate the thesis.</p></div><a href="/memo" style="font-size:9px;text-transform:uppercase;letter-spacing:.12em;color:#b8d1c4;text-decoration:none">Open plain-text memo →</a></div><div class="memo-body"><pre class="memo">${esc(d.memo)}</pre><div class="memo-note">${esc(d.data_notes?.revised_data_warning||'Research output. Validate signals independently before investment use.')}</div></div>`;
  }catch(e){['stateContent','signalsContent','portfolioContent','performanceContent','memoContent'].forEach(id=>{const el=$(id);if(el){el.className='error';el.innerHTML='<strong>Data engine unavailable.</strong><br>'+esc(e.message)}})}finally{if(btn){btn.disabled=false;btn.textContent='Refresh'}}
}
loadData(false);
</script>
</body>
</html>'''


@app.get('/', response_class=HTMLResponse)
def dashboard():
    return DASHBOARD


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/snapshot')
def snapshot(refresh: bool = False):
    try:
        return run_engine(force=refresh)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get('/regime')
def regime():
    return snapshot()['regime']


@app.get('/signals')
def signals():
    return snapshot()['signals']


@app.get('/portfolio')
def portfolio():
    return snapshot()['portfolio']


@app.get('/backtest')
def backtest():
    return snapshot()['backtest']


@app.get('/memo', response_class=PlainTextResponse)
def memo():
    return snapshot()['memo']
