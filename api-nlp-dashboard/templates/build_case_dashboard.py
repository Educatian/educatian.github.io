"""
Build the standalone interactive dashboard used by the simulation case study.

Run from api-nlp-dashboard:
  python templates/build_case_dashboard.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORDS_PATH = ROOT / "simulations" / "dashboard_records_simulated.jsonl"
SOURCE_HEALTH_PATH = ROOT / "simulations" / "source_health.csv"
REPORT_PATH = ROOT / "simulations" / "validation_report.json"
OUT_PATH = ROOT / "case-study-dashboard.html"


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    records = read_jsonl(RECORDS_PATH)
    source_health = read_csv(SOURCE_HEALTH_PATH)
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    html = (
        TEMPLATE.replace("__RECORDS__", json.dumps(records, ensure_ascii=False))
        .replace("__HEALTH__", json.dumps(source_health, ensure_ascii=False))
        .replace("__REPORT__", json.dumps(report, ensure_ascii=False))
    )
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"wrote {OUT_PATH}")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>API-to-NLP Simulation Dashboard</title>
<style>
:root{--bg:#efe4d4;--paper:#fffdf8;--ink:#142029;--muted:#66727a;--line:#d4c6b4;--blue:#254f68;--blue2:#102d40;--clay:#b85f35;--sage:#55724c;--gold:#b8872d;--red:#b34538;--soft:#f8f1e6;--green:#2f6b45;--shadow:0 16px 34px rgba(20,32,41,.08)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.36}button,input,select{font:inherit}button{cursor:pointer}
.app{display:grid;grid-template-columns:286px minmax(0,1fr);min-height:100vh}.side{position:sticky;top:0;height:100vh;overflow:auto;background:var(--paper);border-right:2px solid var(--ink);padding:20px}.main{min-width:0;padding:22px 24px 34px}.topbar{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;margin-bottom:14px}.kicker{font-size:11px;font-weight:950;letter-spacing:.22em;color:var(--clay);text-transform:uppercase}.title{font-size:30px;line-height:1.03;font-weight:950;margin:8px 0;letter-spacing:0}.sub{font-size:13px;color:var(--muted);margin:0 0 14px;max-width:860px}.status{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.status span{border:1px solid var(--line);background:var(--paper);border-radius:999px;padding:7px 10px;font-size:12px;font-weight:850;color:var(--blue)}
.filter{display:grid;gap:6px;margin:11px 0}.filter label{font-size:12px;font-weight:900;color:var(--blue)}select,input[type=search],input[type=range]{width:100%;border:1.5px solid var(--line);border-radius:8px;background:#fff;padding:8px;color:var(--ink)}.side-note{border-top:1px solid var(--line);margin-top:16px;padding-top:14px;font-size:12px;color:var(--muted)}.mini-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}.mini-actions button{border:1.5px solid var(--ink);background:#fff;border-radius:8px;padding:8px;font-size:12px;font-weight:900;color:var(--blue)}
.kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin-bottom:12px}.kpi{background:var(--paper);border:1.5px solid var(--ink);border-radius:8px;padding:12px;min-height:94px;box-shadow:var(--shadow)}.kpi small{display:block;font-size:10px;font-weight:950;color:var(--muted);letter-spacing:.11em;text-transform:uppercase}.kpi b{display:block;font-size:28px;line-height:1;margin:8px 0 5px}.kpi em{font-style:normal;font-size:11px;color:var(--muted)}
.layout{display:grid;grid-template-columns:1.04fr .96fr .9fr;gap:12px;align-items:start}.stack{display:grid;gap:12px}.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}.panel{background:var(--paper);border:1.5px solid var(--line);border-radius:8px;padding:13px;min-width:0;box-shadow:var(--shadow)}.panel.strong{border-color:var(--ink)}.panel h2{font-size:15px;line-height:1.15;margin:0 0 10px;font-weight:950;letter-spacing:.01em}.panel h3{font-size:13px;margin:12px 0 7px;color:var(--blue)}.micro{font-size:12px;color:var(--muted)}.caption{font-size:11px;color:var(--muted);margin-top:7px}
.source-list{display:grid;gap:8px}.source-card{border:1px solid var(--line);border-radius:8px;padding:9px;background:#fff}.source-card header{display:flex;justify-content:space-between;gap:8px;font-weight:900}.health{font-size:11px;border-radius:999px;padding:3px 7px}.ok{background:#e6f1e4;color:var(--green)}.warn{background:#fff3d9;color:#8a5c10}.bar{height:24px;background:#eadcc8;border-radius:6px;overflow:hidden;position:relative}.source-card .bar{height:7px;margin-top:8px}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--blue),#1f6b84)}.bar span{position:absolute;left:8px;top:3px;font-size:12px;font-weight:900;color:#fff}
.row{display:flex;justify-content:space-between;gap:10px;border-top:1px solid var(--line);padding:8px 0}.row:first-child{border-top:0}.spark{display:flex;gap:3px;align-items:end;height:36px;margin-top:8px}.spark i{width:100%;background:var(--blue);border-radius:3px 3px 1px 1px;min-height:3px;opacity:.86}.hbars{display:grid;gap:8px}.hbar label{display:flex;justify-content:space-between;font-size:12px;font-weight:850;margin-bottom:3px}
.trend svg,.network svg,.scatter svg{display:block;width:100%;height:224px;border:1px solid var(--line);border-radius:8px;background:linear-gradient(180deg,#fffdf8,#f8f0e3)}.hist{display:grid;grid-template-columns:repeat(9,1fr);align-items:end;gap:6px;height:168px;border-left:1px solid var(--line);border-bottom:1px solid var(--line);padding:10px 6px 22px}.hist div{display:grid;align-items:end;height:100%;gap:4px}.hist i{display:block;background:var(--sage);border-radius:5px 5px 2px 2px;min-height:5px}.hist b{font-size:9px;text-align:center;color:var(--muted)}
.vbars{display:grid;grid-template-columns:repeat(auto-fit,minmax(54px,1fr));align-items:end;gap:8px;height:188px;border-left:1px solid var(--line);border-bottom:1px solid var(--line);padding:8px 6px 28px}.vbar{display:grid;align-items:end;height:100%;gap:5px;min-width:0}.vbar i{display:block;background:linear-gradient(180deg,var(--blue),var(--blue2));border-radius:7px 7px 3px 3px;min-height:7px}.vbar b{font-size:10px;text-align:center;overflow-wrap:anywhere}.vbar span{font-size:11px;color:var(--clay);font-weight:900;text-align:center}
.queue{display:grid;gap:7px;max-height:430px;overflow:auto;padding-right:2px}.item{background:#fff;border:1.5px solid var(--line);border-radius:8px;padding:9px;cursor:pointer}.item.active{border-color:var(--blue);box-shadow:0 0 0 3px rgba(37,79,104,.13)}.item strong{display:block;font-size:13px}.meta{display:flex;gap:5px;flex-wrap:wrap;margin-top:6px}.pill{font-size:10px;font-weight:900;border:1px solid var(--line);border-radius:999px;padding:3px 6px}.high{background:var(--red);border-color:var(--red);color:#fff}.medium{background:var(--gold);border-color:var(--gold);color:#fff}.low{background:var(--sage);border-color:var(--sage);color:#fff}
.detail-title{font-size:18px;font-weight:950;margin:2px 0 8px}.evidence{background:#f7efe1;border:1px solid var(--line);border-radius:8px;padding:10px;font-size:12px;color:#344247}.entity-grid{display:flex;gap:6px;flex-wrap:wrap}.rationale{display:grid;gap:7px}.check{display:flex;gap:8px;align-items:flex-start;font-size:12px}.check:before{content:"OK";font-size:9px;font-weight:950;color:#fff;background:var(--green);border-radius:999px;padding:2px 5px;line-height:1.2}.actions{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;margin-top:10px}.action{border:1.5px solid var(--line);background:#fff;border-radius:7px;padding:8px;font-size:12px;font-weight:900}.primary{background:var(--blue);border-color:var(--blue);color:#fff}.danger{color:#fff;background:var(--red);border-color:var(--red)}.pass{color:var(--green)}.bad{color:var(--red)}.empty{padding:18px;text-align:center;color:var(--muted);border:1px dashed var(--line);border-radius:8px;background:#fff}
.net-link{stroke:#a77931;stroke-opacity:.45}.net-node{cursor:pointer}.net-node circle{stroke:#173142;stroke-width:1.3}.net-node text{font-size:11px;font-weight:850;fill:#172127;paint-order:stroke;stroke:#fffdf8;stroke-width:4px}.net-node:hover circle{stroke:var(--red);stroke-width:3}.activity{display:grid;gap:7px}.activity div{border-left:3px solid var(--blue);background:#fff;border-radius:0 8px 8px 0;padding:7px 9px;font-size:12px}.quality{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}.quality div{background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px}.quality b{display:block;font-size:18px}.quality span{font-size:10px;color:var(--muted);font-weight:900;text-transform:uppercase}
@media(max-width:1240px){.layout{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(3,1fr)}.side{position:relative;height:auto}.app{display:block}.main{padding:18px}.two{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.kpis,.two,.quality{grid-template-columns:1fr}.title{font-size:24px}.topbar{display:block}.status{justify-content:flex-start;margin-top:10px}.actions{grid-template-columns:1fr}.main{padding:14px}.side{padding:16px}}
</style>
</head>
<body>
<div class="app">
  <aside class="side">
    <div class="kicker">Case Study Console</div>
    <div class="title">Simulation NLP Review Dashboard</div>
    <p class="sub">A richer, operations-grade dashboard for the guidebook case study. Every panel is driven by the same validated synthetic dataset.</p>
    <div class="filter"><label for="source">Source</label><select id="source"></select></div>
    <div class="filter"><label for="topic">Topic</label><select id="topic"></select></div>
    <div class="filter"><label for="priority">Priority</label><select id="priority"></select></div>
    <div class="filter"><label for="review">Review State</label><select id="review"></select></div>
    <div class="filter"><label for="confidence">Minimum Confidence <b id="confLabel">0.00</b></label><input id="confidence" type="range" min="0" max="1" step="0.05" value="0"></div>
    <div class="filter"><label for="search">Search</label><input id="search" type="search" placeholder="topic, phrase, source, title"></div>
    <div class="mini-actions"><button id="reset">Reset</button><button id="highRisk">Risk View</button></div>
    <div class="side-note">
      <b>Dataset:</b> 120 synthetic records<br>
      <b>Loop:</b> collect -> normalize -> NLP -> validate -> review<br>
      <b>Purpose:</b> show what a real dashboard should contain, not only a chart.
    </div>
  </aside>
  <main class="main">
    <div class="topbar">
      <div>
        <div class="kicker">Validated Simulation</div>
        <div class="title">API-to-NLP Dashboard Case Study</div>
        <p class="sub">Filters, source health, topic trend, semantic network, review queue, record detail, model rationale, and action controls remain synchronized on the same record slice.</p>
      </div>
      <div class="status"><span id="statusSchema">Schema 0</span><span id="statusDup">Duplicates 0</span><span id="statusModel">simulation-nlp-v1</span></div>
    </div>
    <section class="kpis">
      <div class="kpi"><small>Filtered Records</small><b id="kRecords">0</b><em id="kRecordShare">0% of dataset</em></div>
      <div class="kpi"><small>Needs Review</small><b id="kReview">0</b><em>human queue</em></div>
      <div class="kpi"><small>High Priority</small><b id="kHigh">0</b><em>urgent first</em></div>
      <div class="kpi"><small>Low Confidence</small><b id="kLowConf">0</b><em>below 0.65</em></div>
      <div class="kpi"><small>Avg Confidence</small><b id="kConf">0.00</b><em>filtered mean</em></div>
      <div class="kpi"><small>Active Sources</small><b id="kSources">0</b><em>feeds represented</em></div>
    </section>
    <section class="layout">
      <div class="stack">
        <div class="panel strong"><h2>Source Health</h2><div id="sourceCards" class="source-list"></div></div>
        <div class="panel"><h2>Topic Trend</h2><div id="trendChart" class="trend"></div><div class="caption">Daily record volume with a confidence overlay.</div></div>
        <div class="two">
          <div class="panel"><h2>Topic Bar Graph</h2><div id="topicBars" class="vbars"></div></div>
          <div class="panel"><h2>Confidence Histogram</h2><div id="confidenceHistogram" class="hist"></div></div>
        </div>
        <div class="panel"><h2>Recent Pipeline Activity</h2><div id="activity" class="activity"></div></div>
      </div>
      <div class="stack">
        <div class="panel strong"><h2>Semantic Network</h2><div id="semanticNetwork" class="network"></div><div class="caption">Topic nodes connect to high-frequency key phrases. Click a node to filter.</div></div>
        <div class="panel"><h2>Source Bar Graph</h2><div id="sourceBars" class="vbars"></div></div>
        <div class="panel"><h2>Priority vs Confidence</h2><div id="scatter" class="scatter"></div></div>
        <div class="panel"><h2>Validation Gates</h2><div id="validationCards"></div></div>
      </div>
      <div class="stack">
        <div class="panel strong"><h2>Review Queue</h2><div id="queueList" class="queue"></div></div>
        <div class="panel"><h2>Selected Record Detail</h2><div id="detail"></div></div>
        <div class="panel"><h2>NLP Rationale & Actions</h2><div id="rationale"></div><div class="actions"><button class="action primary" data-action="approved">Approve</button><button class="action" data-action="labels">Update Labels</button><button class="action" data-action="note">Add Note</button><button class="action danger" data-action="dismissed">Dismiss</button></div></div>
      </div>
    </section>
  </main>
</div>
<script>
const records = __RECORDS__;
const sourceHealth = __HEALTH__;
const report = __REPORT__;
const $ = sel => document.querySelector(sel);
const state = {source:'all', topic:'all', priority:'all', review:'all', confidence:0, search:'', selected:null, log:[]};
const rank = {high:0, medium:1, low:2};
function esc(v){return String(v ?? '').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
function uniq(arr){return [...new Set(arr)].filter(Boolean).sort()}
function countBy(rows, fn){return rows.reduce((a,r)=>{const k=fn(r); a[k]=(a[k]||0)+1; return a}, {})}
function fillSelect(id, values, label){$(id).innerHTML=`<option value="all">${label}</option>`+values.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('')}
function pct(n,d){return d?Math.round(n/d*100):0}
function topicOf(r){return r.nlp.topic_labels[0] || 'unknown'}
function filtered(){const q=state.search.toLowerCase();return records.filter(r=>(state.source==='all'||r.source_id===state.source)&&(state.topic==='all'||topicOf(r)===state.topic)&&(state.priority==='all'||r.nlp.priority===state.priority)&&(state.review==='all'||r.review_state===state.review)&&r.nlp.confidence>=state.confidence&&(!q||JSON.stringify(r).toLowerCase().includes(q)))}
function vbars(el, counts){const entries=Object.entries(counts).sort((a,b)=>b[1]-a[1]);const max=Math.max(1,...entries.map(x=>x[1]));el.innerHTML=entries.map(([k,v])=>`<div class="vbar"><span>${v}</span><i style="height:${Math.max(7,v/max*100)}%"></i><b>${esc(k)}</b></div>`).join('')}
function histogram(el, rows){const bins=Array.from({length:9},(_,i)=>({label:`${(0.5+i*.05).toFixed(2)}`,count:0}));rows.forEach(r=>{const idx=Math.max(0,Math.min(8,Math.floor((r.nlp.confidence-.5)/.05)));bins[idx].count++});const max=Math.max(1,...bins.map(b=>b.count));el.innerHTML=bins.map(b=>`<div><i style="height:${Math.max(5,b.count/max*100)}%"></i><b>${b.label}</b></div>`).join('')}
function trend(el, rows){const byDate={};rows.forEach(r=>{const d=r.collected_at.slice(5,10); if(!byDate[d])byDate[d]={n:0,c:0}; byDate[d].n++; byDate[d].c+=r.nlp.confidence});const entries=Object.entries(byDate).sort((a,b)=>a[0].localeCompare(b[0])).slice(-12);const max=Math.max(1,...entries.map(x=>x[1].n));const pts=entries.map(([d,v],i)=>[34+i*(410/Math.max(1,entries.length-1)),190-(v.n/max*150),d,v.n,v.c/v.n]);const conf=pts.map(p=>[p[0],190-((p[4]-.5)/.5*150)]);el.innerHTML=`<svg viewBox="0 0 480 220"><path d="M34 20V190H456" fill="none" stroke="#d2c5b2"/><polyline points="${pts.map(p=>p[0]+','+p[1]).join(' ')}" fill="none" stroke="#254f68" stroke-width="4"/><polyline points="${conf.map(p=>p[0]+','+p[1]).join(' ')}" fill="none" stroke="#55724c" stroke-width="3" opacity=".74"/>${pts.map(p=>`<circle cx="${p[0]}" cy="${p[1]}" r="4" fill="#254f68"><title>${p[2]}: ${p[3]} records</title></circle>`).join('')}<text x="326" y="32" font-size="11" fill="#254f68">Records</text><text x="326" y="50" font-size="11" fill="#55724c">Mean confidence</text></svg>`}
function network(el, rows){const topicCounts=countBy(rows,topicOf);const phraseCounts={};const pairs=[];rows.forEach(r=>{const t=topicOf(r);(r.nlp.key_phrases||[]).forEach(p=>{phraseCounts[p]=(phraseCounts[p]||0)+1;pairs.push([t,p])})});const topics=Object.entries(topicCounts).sort((a,b)=>b[1]-a[1]).slice(0,5);const phrases=Object.entries(phraseCounts).sort((a,b)=>b[1]-a[1]).slice(0,9);const nodes=[...topics.map(([id,count],i)=>({id,count,type:'topic',x:120,y:48+i*35})),...phrases.map(([id,count],i)=>({id,count,type:'phrase',x:318+(i%2)*92,y:34+Math.floor(i/2)*36}))];const by=Object.fromEntries(nodes.map(n=>[n.id,n]));const links={};pairs.forEach(([a,b])=>{if(by[a]&&by[b])links[`${a}|||${b}`]=(links[`${a}|||${b}`]||0)+1});const max=Math.max(1,...nodes.map(n=>n.count));const edges=Object.entries(links).map(([k,c])=>{const [a,b]=k.split('|||');return{a:by[a],b:by[b],c}}).sort((a,b)=>b.c-a.c).slice(0,18);el.innerHTML=`<svg viewBox="0 0 520 224">${edges.map(e=>`<line class="net-link" x1="${e.a.x}" y1="${e.a.y}" x2="${e.b.x}" y2="${e.b.y}" stroke-width="${1+e.c*.28}"/>`).join('')}${nodes.map(n=>`<g class="net-node" data-value="${esc(n.id)}"><circle cx="${n.x}" cy="${n.y}" r="${8+n.count/max*17}" fill="${n.type==='topic'?'#254f68':'#f0d9a8'}"/><text x="${n.x+18}" y="${n.y+4}">${esc(n.id)}</text><title>${esc(n.id)}: ${n.count}</title></g>`).join('')}</svg>`;el.querySelectorAll('.net-node').forEach(n=>n.onclick=()=>{$('#search').value=n.dataset.value;state.search=n.dataset.value.toLowerCase();state.selected=null;render()})}
function scatter(el, rows){const y={high:48,medium:112,low:176};el.innerHTML=`<svg viewBox="0 0 480 224"><path d="M48 24V194H444" fill="none" stroke="#d2c5b2"/><text x="8" y="52" font-size="11">High</text><text x="8" y="116" font-size="11">Medium</text><text x="8" y="180" font-size="11">Low</text>${rows.slice(0,90).map(r=>`<circle cx="${48+(r.nlp.confidence*.38*1000)}" cy="${y[r.nlp.priority]+((r.record_id.length%9)-4)}" r="4.5" fill="${r.review_state==='needs_review'?'#b34538':'#254f68'}" opacity=".74"><title>${esc(r.title)} (${r.nlp.confidence.toFixed(2)})</title></circle>`).join('')}<text x="308" y="212" font-size="11" fill="#66727a">Confidence -></text></svg>`}
function renderSources(rows){const sourceCounts=countBy(rows,r=>r.source_id);const max=Math.max(1,...Object.values(sourceCounts));$('#sourceCards').innerHTML=sourceHealth.map(s=>{const c=sourceCounts[s.source_id]||0;const errors=Number(s.error_count);const spark=Array.from({length:9},(_,i)=>Math.max(8,((c+i*3+Number(s.records))%31)+10));return`<div class="source-card"><header><span>${esc(s.source_name)}</span><span class="health ${errors?'warn':'ok'}">${errors?'Warning':'Healthy'}</span></header><div class="micro">${esc(s.source_id)} | last success ${esc(s.last_success_at)} | errors ${esc(s.error_count)} | avg conf ${esc(s.avg_confidence)}</div><div class="bar"><i style="width:${Math.max(3,c/max*100)}%"></i><span>${c} filtered / ${esc(s.records)} total</span></div><div class="spark">${spark.map(v=>`<i style="height:${v}px"></i>`).join('')}</div></div>`}).join('')}
function queue(rows){const q=[...rows].sort((a,b)=>(rank[a.nlp.priority]-rank[b.nlp.priority])||(b.nlp.confidence-a.nlp.confidence)).slice(0,36);if((!state.selected||!rows.some(r=>r.record_id===state.selected))&&q[0])state.selected=q[0].record_id;$('#queueList').innerHTML=q.length?q.map(r=>`<div class="item ${state.selected===r.record_id?'active':''}" data-id="${esc(r.record_id)}"><strong>${esc(r.title)}</strong><div class="micro">${esc(r.nlp.summary)}</div><div class="meta"><span class="pill ${r.nlp.priority}">${esc(r.nlp.priority)}</span><span class="pill">${esc(r.review_state)}</span><span class="pill">${r.nlp.confidence.toFixed(2)}</span><span class="pill">${esc(r.source_id)}</span></div></div>`).join(''):`<div class="empty">No records match the current filters.</div>`;document.querySelectorAll('.item').forEach(el=>el.onclick=()=>{state.selected=el.dataset.id;detail();queue(rows)})}
function detail(){const r=records.find(x=>x.record_id===state.selected);if(!r){$('#detail').innerHTML='<div class="empty">Select a record.</div>';$('#rationale').innerHTML='';return}$('#detail').innerHTML=`<div class="detail-title">${esc(r.title)}</div><div class="meta"><span class="pill ${r.nlp.priority}">${esc(r.nlp.priority)}</span><span class="pill">${esc(r.review_state)}</span><span class="pill">${r.nlp.confidence.toFixed(2)}</span><span class="pill">${esc(topicOf(r))}</span></div><h3>Source Evidence</h3><div class="evidence">${esc(r.text)}</div><h3>Entities</h3><div class="entity-grid">${r.nlp.entities.map(e=>`<span class="pill">${esc(e.text)} | ${esc(e.label)}</span>`).join('')}</div>`;$('#rationale').innerHTML=`<div class="rationale"><div class="check">${esc(r.nlp.review_reason)}</div><div class="check">Topic labels: ${esc(r.nlp.topic_labels.join(', '))}</div><div class="check">Key phrases: ${esc(r.nlp.key_phrases.join(', '))}</div><div class="check">Model version: ${esc(r.nlp.model_version)}</div></div>`}
function validation(){const rows=[['Schema errors',report.schema_error_count,report.schema_error_count===0],['Duplicate IDs',report.duplicate_count,report.duplicate_count===0],['Average confidence',report.avg_confidence,report.avg_confidence>=0.7],['Low-confidence routed',report.low_confidence_count,report.low_confidence_count>0],['High-priority routed',report.high_priority_review_count,report.high_priority_review_count>0]];$('#validationCards').innerHTML=rows.map(([k,v,ok])=>`<div class="row"><b>${esc(k)}</b><span class="${ok?'pass':'bad'}">${esc(v)} ${ok?'PASS':'CHECK'}</span></div>`).join('')}
function activity(){const logs=state.log.slice(-4).reverse();const base=[`Ingested ${records.length} records from ${sourceHealth.length} sources`,`Validated ${report.schema_error_count} schema errors and ${report.duplicate_count} duplicate IDs`,`Routed ${report.high_priority_review_count} high-priority records to review`];$('#activity').innerHTML=[...logs,...base].slice(0,5).map(x=>`<div>${esc(x)}</div>`).join('')}
function quality(rows){return `<div class="quality"><div><b>${report.schema_error_count}</b><span>Schema errors</span></div><div><b>${report.duplicate_count}</b><span>Duplicate IDs</span></div><div><b>${rows.filter(r=>r.review_state==='needs_review').length}</b><span>Open reviews</span></div></div>`}
function render(){const rows=filtered();$('#statusSchema').textContent=`Schema ${report.schema_error_count}`;$('#statusDup').textContent=`Duplicates ${report.duplicate_count}`;$('#kRecords').textContent=rows.length;$('#kRecordShare').textContent=`${pct(rows.length,records.length)}% of dataset`;$('#kReview').textContent=rows.filter(r=>r.review_state==='needs_review').length;$('#kHigh').textContent=rows.filter(r=>r.nlp.priority==='high').length;$('#kLowConf').textContent=rows.filter(r=>r.nlp.confidence<.65).length;$('#kConf').textContent=rows.length?(rows.reduce((a,r)=>a+r.nlp.confidence,0)/rows.length).toFixed(2):'0.00';$('#kSources').textContent=uniq(rows.map(r=>r.source_id)).length;renderSources(rows);trend($('#trendChart'),rows);vbars($('#topicBars'),countBy(rows,topicOf));vbars($('#sourceBars'),countBy(rows,r=>r.source_id));histogram($('#confidenceHistogram'),rows);network($('#semanticNetwork'),rows);scatter($('#scatter'),rows);queue(rows);detail();validation();activity();$('#validationCards').insertAdjacentHTML('beforeend', quality(rows))}
fillSelect('#source',uniq(records.map(r=>r.source_id)),'All sources');fillSelect('#topic',uniq(records.map(topicOf)),'All topics');fillSelect('#priority',['high','medium','low'],'All priorities');fillSelect('#review',uniq(records.map(r=>r.review_state)),'All review states');
['source','topic','priority','review'].forEach(k=>$('#'+k).onchange=e=>{state[k]=e.target.value;state.selected=null;render()});$('#confidence').oninput=e=>{state.confidence=Number(e.target.value);$('#confLabel').textContent=state.confidence.toFixed(2);state.selected=null;render()};$('#search').oninput=e=>{state.search=e.target.value;state.selected=null;render()};$('#reset').onclick=()=>{Object.assign(state,{source:'all',topic:'all',priority:'all',review:'all',confidence:0,search:'',selected:null});['source','topic','priority','review'].forEach(k=>$('#'+k).value='all');$('#confidence').value=0;$('#confLabel').textContent='0.00';$('#search').value='';render()};$('#highRisk').onclick=()=>{$('#priority').value='high';$('#review').value='needs_review';state.priority='high';state.review='needs_review';state.selected=null;render()};document.querySelectorAll('[data-action]').forEach(btn=>btn.onclick=()=>{const r=records.find(x=>x.record_id===state.selected);if(!r)return;state.log.push(`${btn.textContent} action noted for ${r.record_id}`);if(btn.dataset.action==='approved')r.review_state='reviewed';if(btn.dataset.action==='dismissed')r.review_state='archived';render()});
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
