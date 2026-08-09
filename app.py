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
<meta name="color-scheme" content="dark">
<title>AI Global Macro Hedge Fund Engine</title>
<style>
:root{
  --bg:#05070a;
  --bg-soft:#080c11;
  --panel:#0b1016;
  --panel-2:#0e151d;
  --line:#1a2531;
  --line-soft:#121b24;
  --text:#f3f6f8;
  --text-2:#c7d0d8;
  --muted:#778594;
  --muted-2:#52606d;
  --green:#73efbb;
  --green-soft:rgba(115,239,187,.10);
  --red:#ff7080;
  --red-soft:rgba(255,112,128,.10);
  --amber:#f3c96b;
  --blue:#79adff;
  --shadow:0 22px 70px rgba(0,0,0,.28);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;
  min-height:100vh;
  color:var(--text);
  background:
    linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px),
    radial-gradient(circle at 78% -10%,rgba(115,239,187,.075),transparent 31%),
    radial-gradient(circle at 8% 0%,rgba(121,173,255,.045),transparent 24%),
    var(--bg);
  background-size:48px 48px,48px 48px,auto,auto,auto;
  font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:14px;
  -webkit-font-smoothing:antialiased;
}
button,a{font:inherit}
a{color:inherit}
.shell{max-width:1460px;margin:0 auto;padding:0 28px 72px}
.topbar{
  height:72px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  border-bottom:1px solid var(--line-soft);
}
.brand-wrap{display:flex;align-items:center;gap:13px}
.mark{
  width:34px;height:34px;border:1px solid #263441;border-radius:9px;
  display:grid;place-items:center;background:linear-gradient(145deg,#101821,#090d12);
  color:var(--green);font:800 11px/1 ui-monospace,SFMono-Regular,Menlo,monospace;
  letter-spacing:.03em;box-shadow:inset 0 1px 0 rgba(255,255,255,.035)
}
.brand{font-weight:720;letter-spacing:-.015em;font-size:14px}
.brand-sub{font-size:10px;color:var(--muted);margin-top:3px;letter-spacing:.06em;text-transform:uppercase}
.nav{display:flex;align-items:center;gap:6px}
.nav a,.refresh{
  border:1px solid transparent;background:transparent;color:var(--muted);
  text-decoration:none;padding:8px 11px;border-radius:8px;cursor:pointer;transition:.16s ease;
}
.nav a:hover,.refresh:hover{color:var(--text-2);border-color:var(--line);background:#0b1117}
.status-pill{
  margin-left:10px;display:flex;align-items:center;gap:7px;padding:7px 10px;
  border:1px solid #1d312b;border-radius:999px;background:rgba(115,239,187,.045);
  color:#9ee9ca;font:650 10px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase
}
.status-dot{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 0 4px rgba(115,239,187,.08),0 0 14px rgba(115,239,187,.65)}
.hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(330px,.65fr);gap:16px;padding:30px 0 16px}
.hero-main,.regime-card,.panel,.metric-card{
  border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.018),rgba(255,255,255,.005));
  box-shadow:var(--shadow)
}
.hero-main{min-height:272px;border-radius:16px;padding:32px 34px;position:relative;overflow:hidden}
.hero-main:after{
  content:"";position:absolute;width:360px;height:360px;border-radius:50%;right:-180px;top:-210px;
  border:1px solid rgba(115,239,187,.09);box-shadow:0 0 0 52px rgba(115,239,187,.015),0 0 0 104px rgba(115,239,187,.01)
}
.kicker{color:var(--green);font:700 10px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.15em;text-transform:uppercase}
h1{font-size:clamp(37px,4.6vw,65px);line-height:.98;letter-spacing:-.055em;margin:23px 0 19px;max-width:880px;font-weight:720}
.hero-copy{max-width:760px;color:#9aa8b5;font-size:14px;line-height:1.75}
.hero-meta{display:flex;gap:22px;flex-wrap:wrap;margin-top:26px;color:var(--muted);font:600 10px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;text-transform:uppercase;letter-spacing:.07em}
.hero-meta strong{color:var(--text-2);font-weight:650}
.regime-card{border-radius:16px;padding:25px;display:flex;flex-direction:column;justify-content:space-between;min-height:272px;position:relative;overflow:hidden}
.regime-card:before{content:"";position:absolute;inset:0 0 auto 0;height:2px;background:linear-gradient(90deg,var(--green),transparent 70%)}
.label{font:650 9px/1.3 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.105em;text-transform:uppercase;color:var(--muted)}
.regime{font-size:38px;font-weight:760;letter-spacing:-.045em;margin:8px 0 4px;color:var(--green)}
.regime-date{color:var(--muted);font:500 11px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
.confidence{margin-top:25px}
.conf-head{display:flex;justify-content:space-between;gap:20px;margin-bottom:9px;color:var(--text-2);font-size:11px}
.track{height:5px;background:#121b23;border-radius:999px;overflow:hidden}
.fill{height:100%;background:linear-gradient(90deg,#38ca91,var(--green));border-radius:999px;box-shadow:0 0 14px rgba(115,239,187,.25)}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 16px}
.metric-card{border-radius:12px;padding:17px 18px;box-shadow:none}
.metric-head{display:flex;justify-content:space-between;gap:12px;align-items:center}
.metric-dot{width:5px;height:5px;border-radius:50%;background:#43515f}
.metric-value{font:650 25px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:-.04em;margin-top:14px}
.metric-caption{font-size:10px;color:var(--muted-2);margin-top:8px}
.pulse{height:2px;margin-top:14px;background:#131d26;position:relative;overflow:hidden}
.pulse span{position:absolute;top:0;bottom:0;left:50%;background:var(--blue)}
.dashboard-grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(320px,.72fr);gap:16px;margin-bottom:16px}
.panel{border-radius:14px;padding:20px;box-shadow:none;overflow:hidden}
.panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;margin-bottom:18px}
.panel-title{font-size:14px;font-weight:680;letter-spacing:-.01em}
.panel-sub{font-size:10px;color:var(--muted);margin-top:5px;line-height:1.45}
.panel-tag{white-space:nowrap;border:1px solid var(--line);padding:6px 8px;border-radius:7px;color:var(--muted);font:600 9px/1 ui-monospace,SFMono-Regular,Menlo,monospace;text-transform:uppercase;letter-spacing:.08em}
.table-wrap{overflow-x:auto;margin:0 -2px}
table{width:100%;border-collapse:collapse;min-width:680px}
th{font:600 9px/1.2 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;text-align:right;padding:10px 10px;border-bottom:1px solid var(--line)}
td{padding:13px 10px;border-bottom:1px solid var(--line-soft);text-align:right;color:#c8d1d9;font:500 11px/1.35 ui-monospace,SFMono-Regular,Menlo,monospace}
th:first-child,td:first-child{text-align:left;padding-left:4px}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:rgba(255,255,255,.012)}
.asset-cell{display:flex;align-items:center;gap:10px;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.asset-icon{width:28px;height:28px;border:1px solid #1c2b36;border-radius:7px;background:#0d151d;display:grid;place-items:center;font:700 9px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:#9daeba}
.asset-symbol{font-size:12px;color:var(--text);font-weight:700}
.asset-name{font-size:9px;color:var(--muted);margin-top:2px}
.view{display:inline-flex;align-items:center;gap:5px;font:700 9px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.04em;text-transform:uppercase}
.view:before{content:"";width:5px;height:5px;border-radius:50%;background:currentColor}
.long{color:var(--green)}.short{color:var(--red)}.neutral{color:var(--muted)}
.positive{color:var(--green)}.negative{color:var(--red)}
.exposure-list{display:flex;flex-direction:column;gap:15px}
.exposure-row{display:grid;grid-template-columns:48px 1fr 60px;gap:10px;align-items:center}
.exposure-symbol{font:650 10px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:#b7c2cb}
.exposure-track{height:5px;background:#121b23;border-radius:999px;position:relative;overflow:hidden}
.exposure-track:after{content:"";position:absolute;left:50%;top:0;bottom:0;width:1px;background:#2b3946}
.exposure-bar{height:100%;position:absolute;top:0;border-radius:999px}
.exposure-bar.longbar{left:50%;background:var(--green)}
.exposure-bar.shortbar{right:50%;background:var(--red)}
.exposure-value{text-align:right;font:600 10px/1 ui-monospace,SFMono-Regular,Menlo,monospace}
.exposure-summary{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:21px;padding-top:17px;border-top:1px solid var(--line)}
.mini-stat{padding:10px 11px;border:1px solid var(--line-soft);border-radius:8px;background:#090e13}
.mini-stat .v{font:650 14px/1 ui-monospace,SFMono-Regular,Menlo,monospace;margin-top:6px;color:var(--text-2)}
.performance{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;margin-bottom:16px}
.performance-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.perf-card{border:1px solid var(--line-soft);border-radius:9px;padding:12px;background:#080d12}
.perf-card .v{font:650 18px/1 ui-monospace,SFMono-Regular,Menlo,monospace;margin-top:10px}
.benchmark-row{display:grid;grid-template-columns:1fr 82px 82px;gap:12px;align-items:center;padding:11px 0;border-bottom:1px solid var(--line-soft);font-size:11px}
.benchmark-row:last-child{border-bottom:0}
.benchmark-row .name{color:var(--text-2)}
.benchmark-row .num{text-align:right;font:600 11px/1 ui-monospace,SFMono-Regular,Menlo,monospace}
.memo{white-space:pre-wrap;margin:0;color:#aebbc5;font:500 11px/1.82 ui-monospace,SFMono-Regular,Menlo,monospace}
.data-note{margin-top:13px;padding-top:13px;border-top:1px solid var(--line-soft);display:flex;gap:10px;align-items:flex-start;color:var(--muted-2);font-size:9px;line-height:1.6}
.loading{border:1px solid var(--line);border-radius:14px;padding:25px;background:var(--panel);color:var(--muted);font:500 11px/1.7 ui-monospace,SFMono-Regular,Menlo,monospace}
.loading-line{height:8px;border-radius:5px;background:linear-gradient(90deg,#101821,#17212b,#101821);background-size:200% 100%;animation:shimmer 1.4s infinite;margin:10px 0;max-width:580px}
@keyframes shimmer{to{background-position:-200% 0}}
.error{border:1px solid rgba(255,112,128,.35);background:var(--red-soft);color:#ffc3ca;padding:18px;border-radius:12px;font-size:12px;line-height:1.65}
.footer{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;padding-top:20px;color:var(--muted-2);font:500 9px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;text-transform:uppercase;letter-spacing:.06em}
@media(max-width:980px){.hero,.dashboard-grid,.performance{grid-template-columns:1fr}.performance-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:720px){.shell{padding:0 14px 48px}.topbar{height:auto;padding:15px 0;gap:14px}.brand-sub{display:none}.nav a{display:none}.status-pill{margin-left:0}.hero{padding-top:16px}.hero-main,.regime-card{min-height:auto}.hero-main{padding:24px}.metrics{grid-template-columns:repeat(2,1fr)}.performance-grid{grid-template-columns:repeat(2,1fr)}.panel{padding:16px}}
@media(max-width:460px){.metrics,.performance-grid{grid-template-columns:1fr}.nav{gap:2px}.refresh{padding:8px}.status-pill{font-size:8px}.hero-main{padding:22px 19px}h1{font-size:40px}.regime{font-size:32px}}
</style>
</head>
<body>
<div class="shell">
  <header class="topbar">
    <div class="brand-wrap">
      <div class="mark">GM</div>
      <div>
        <div class="brand">AI Global Macro Hedge Fund Engine</div>
        <div class="brand-sub">Systematic Research Platform</div>
      </div>
    </div>
    <nav class="nav">
      <a href="/docs">API</a>
      <a href="/memo">Memo</a>
      <button class="refresh" id="refreshBtn" type="button">Refresh</button>
      <div class="status-pill"><span class="status-dot"></span>System live</div>
    </nav>
  </header>

  <section class="hero">
    <div class="hero-main">
      <div class="kicker">Global cross-asset intelligence</div>
      <h1>Macro regime to portfolio, systematically.</h1>
      <div class="hero-copy">A transparent research engine translating economic regimes, momentum, liquidity and volatility into risk-controlled cross-asset positioning.</div>
      <div class="hero-meta">
        <span>Universe <strong>8 liquid macro proxies</strong></span>
        <span>Target vol <strong>10%</strong></span>
        <span>Max gross <strong>150%</strong></span>
      </div>
    </div>
    <aside class="regime-card">
      <div>
        <div class="label">Current macro regime</div>
        <div id="regime" class="regime">Loading</div>
        <div id="regimeDate" class="regime-date">Fetching macro state...</div>
      </div>
      <div class="confidence">
        <div class="conf-head"><span>Cluster confidence</span><strong id="confidenceText">0.0%</strong></div>
        <div class="track"><div id="confidenceBar" class="fill" style="width:0%"></div></div>
      </div>
    </aside>
  </section>

  <main id="content">
    <div class="loading">
      INITIALIZING MARKET + MACRO DATA
      <div class="loading-line"></div>
      <div class="loading-line" style="width:72%"></div>
    </div>
  </main>

  <footer class="footer">
    <span>AI Global Macro Hedge Fund Engine · Research use only</span>
    <span>FRED macro data · Yahoo market data</span>
  </footer>
</div>
<script>
const $=id=>document.getElementById(id);
const pct=x=>(100*Number(x||0)).toFixed(1)+'%';
const num=(x,d=2)=>Number(x||0).toFixed(d);
const sign=x=>Number(x)>=0?'+':'';
const signed=x=>sign(x)+num(x,2);
const cls=x=>Number(x)>0?'positive':Number(x)<0?'negative':'';
const esc=s=>String(s??'').replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));
const widthFor=x=>Math.min(50,Math.abs(Number(x||0))*125);
const pulse=(x)=>{
  const v=Math.max(-2.5,Math.min(2.5,Number(x||0)));
  const w=Math.abs(v)/2.5*50;
  const left=v>=0?50:50-w;
  const color=v>=0?'var(--green)':'var(--red)';
  return `<div class="pulse"><span style="left:${left}%;width:${w}%;background:${color}"></span></div>`;
};
const factorCard=(name,value,caption)=>`<div class="metric-card"><div class="metric-head"><div class="label">${name}</div><span class="metric-dot"></span></div><div class="metric-value ${cls(value)}">${signed(value)}</div><div class="metric-caption">${caption}</div>${pulse(value)}</div>`;
const perfCard=(label,value,kind='num')=>`<div class="perf-card"><div class="label">${label}</div><div class="v">${kind==='pct'?pct(value):num(value,kind==='num'?2:3)}</div></div>`;

async function load(force=false){
  const btn=$('refreshBtn');
  if(btn){btn.disabled=true;btn.textContent='Loading';}
  try{
    const r=await fetch('/snapshot'+(force?'?refresh=true':''));
    if(!r.ok) throw new Error('HTTP '+r.status);
    const d=await r.json();
    const rg=d.regime||{};
    const confidence=rg.confidence==null?0:Number(rg.confidence);
    $('regime').textContent=String(rg.regime||'Unknown').toUpperCase();
    $('regimeDate').textContent='As of '+d.as_of;
    $('confidenceText').textContent=rg.confidence==null?'N/A':pct(confidence);
    $('confidenceBar').style.width=Math.max(0,Math.min(100,confidence*100))+'%';

    const rows=(d.signals||[]).map(x=>{
      const dir=String(x.direction||'Neutral');
      const dclass=dir.toLowerCase();
      return `<tr>
        <td><div class="asset-cell"><div class="asset-icon">${esc(x.symbol).slice(0,3)}</div><div><div class="asset-symbol">${esc(x.symbol)}</div><div class="asset-name">${esc(x.asset)}</div></div></div></td>
        <td><span class="view ${dclass}">${esc(dir)}</span></td>
        <td class="${cls(x.score)}">${signed(x.score)}</td>
        <td class="${cls(x.momentum_3m)}">${pct(x.momentum_3m)}</td>
        <td class="${cls(x.momentum_12m)}">${pct(x.momentum_12m)}</td>
        <td class="${cls(x.weight)}"><strong>${pct(x.weight)}</strong></td>
      </tr>`;
    }).join('');

    const exposures=Object.entries((d.portfolio||{}).weights||{}).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1])).map(([k,v])=>{
      const val=Number(v||0), w=widthFor(val);
      const bar=val>=0
        ?`<span class="exposure-bar longbar" style="width:${w}%"></span>`
        :`<span class="exposure-bar shortbar" style="width:${w}%"></span>`;
      return `<div class="exposure-row"><div class="exposure-symbol">${esc(k)}</div><div class="exposure-track">${bar}</div><div class="exposure-value ${cls(val)}">${pct(val)}</div></div>`;
    }).join('');

    const bt=(d.backtest||{}).strategy||{};
    const bm=(d.backtest||{}).benchmark_60_40||{};
    const months=(d.backtest||{}).months||0;
    const notes=d.data_notes||{};

    $('content').innerHTML=`
      <section class="metrics">
        ${factorCard('Growth',rg.growth,'Economic activity impulse')}
        ${factorCard('Inflation',rg.inflation,'Price pressure impulse')}
        ${factorCard('Liquidity',rg.liquidity,'Policy + financial conditions')}
        ${factorCard('Risk',rg.risk,'Cross-market stress state')}
      </section>

      <section class="dashboard-grid">
        <div class="panel">
          <div class="panel-head"><div><div class="panel-title">Cross-Asset Signal Book</div><div class="panel-sub">Regime, trend and liquidity translated into directional conviction.</div></div><div class="panel-tag">${(d.signals||[]).length} instruments</div></div>
          <div class="table-wrap"><table><thead><tr><th>Instrument</th><th>View</th><th>Score</th><th>3M</th><th>12M</th><th>Weight</th></tr></thead><tbody>${rows}</tbody></table></div>
        </div>

        <aside class="panel">
          <div class="panel-head"><div><div class="panel-title">Portfolio Exposure</div><div class="panel-sub">Current volatility-scaled allocation.</div></div><div class="panel-tag">Target book</div></div>
          <div class="exposure-list">${exposures}</div>
          <div class="exposure-summary">
            <div class="mini-stat"><div class="label">Gross</div><div class="v">${pct(d.portfolio.gross_exposure)}</div></div>
            <div class="mini-stat"><div class="label">Net</div><div class="v ${cls(d.portfolio.net_exposure)}">${pct(d.portfolio.net_exposure)}</div></div>
          </div>
        </aside>
      </section>

      <section class="performance">
        <div class="panel">
          <div class="panel-head"><div><div class="panel-title">Strategy Performance</div><div class="panel-sub">Walk-forward research backtest after transaction costs.</div></div><div class="panel-tag">${months} months</div></div>
          <div class="performance-grid">
            ${perfCard('CAGR',bt.cagr,'pct')}
            ${perfCard('Sharpe',bt.sharpe)}
            ${perfCard('Sortino',bt.sortino)}
            ${perfCard('Max drawdown',bt.max_drawdown,'pct')}
            ${perfCard('Volatility',bt.annual_volatility,'pct')}
            ${perfCard('Calmar',bt.calmar)}
            ${perfCard('Positive months',bt.positive_months,'pct')}
            ${perfCard('Growth of $1',bt.ending_growth_of_1)}
          </div>
        </div>

        <div class="panel">
          <div class="panel-head"><div><div class="panel-title">Benchmark Monitor</div><div class="panel-sub">Strategy compared with a 60/40 reference portfolio.</div></div><div class="panel-tag">Relative view</div></div>
          <div class="benchmark-row"><div class="name">Metric</div><div class="label" style="text-align:right">Strategy</div><div class="label" style="text-align:right">60/40</div></div>
          <div class="benchmark-row"><div class="name">CAGR</div><div class="num">${pct(bt.cagr)}</div><div class="num">${pct(bm.cagr)}</div></div>
          <div class="benchmark-row"><div class="name">Sharpe</div><div class="num">${num(bt.sharpe)}</div><div class="num">${num(bm.sharpe)}</div></div>
          <div class="benchmark-row"><div class="name">Sortino</div><div class="num">${num(bt.sortino)}</div><div class="num">${num(bm.sortino)}</div></div>
          <div class="benchmark-row"><div class="name">Max drawdown</div><div class="num">${pct(bt.max_drawdown)}</div><div class="num">${pct(bm.max_drawdown)}</div></div>
          <div class="benchmark-row"><div class="name">Annual volatility</div><div class="num">${pct(bt.annual_volatility)}</div><div class="num">${pct(bm.annual_volatility)}</div></div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head"><div><div class="panel-title">Investment Committee Memo</div><div class="panel-sub">Machine-generated rationale from the current regime and portfolio state.</div></div><div class="panel-tag">IC brief</div></div>
        <pre class="memo">${esc(d.memo)}</pre>
        <div class="data-note"><span>●</span><span>${esc(notes.revised_data_warning||'Research output. Validate all signals independently before investment use.')}</span></div>
      </section>`;
  }catch(e){
    $('content').innerHTML=`<div class="error"><strong>Data engine unavailable.</strong><br>${esc(e.message)}<br><br>Check external provider connectivity or API logs.</div>`;
  }finally{
    if(btn){btn.disabled=false;btn.textContent='Refresh';}
  }
}
$('refreshBtn').addEventListener('click',()=>load(true));
load(false);
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
