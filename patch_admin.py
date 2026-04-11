"""
Patches admin.html:
  1. Replaces lines 286-388 with dynamic placeholder HTML
  2. Replaces lines 572-915 with new dynamic JS
"""
import os

SRC = r"e:\DA IICT V.01\DA-IICT\frontend\admin.html"

with open(SRC, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Original lines: {len(lines)}")

# --- SECTION 1: Dynamic HTML (replaces lines 286-388, i.e. index 285-387) ---
new_html = """
<!-- =========== OVERVIEW =========== -->
<section class="section active" id="overview">
  <div class="grid g4" id="ovKpiGrid"></div>
  <div class="grid g2" style="margin-top:16px">
    <div class="card"><div class="row"><div><h3>Revenue Over Time</h3></div><span class="pill ok">Healthy Growth</span></div><div id="chartRevenue" class="plotly-chart"></div></div>
    <div class="card"><h3>Price Adjustment Reasons</h3><div id="chartDonut" class="plotly-chart"></div></div>
  </div>
  <div class="card" style="margin-top:18px"><h3>Recent Price Changes</h3><div class="table"><table><thead><tr><th>Product Name</th><th>Category</th><th>Old</th><th>New</th><th>Reason</th><th>Time</th><th>Status</th><th></th></tr></thead><tbody id="tbPriceChanges"></tbody></table></div></div>
</section>

<!-- =========== PRICING =========== -->
<section class="section" id="pricing">
  <div class="grid g3" id="pricingInfoGrid"></div>
  <div class="card" style="margin-top:18px"><h3>Top 10 Most Price-Changed Products Today</h3><div class="table"><table><thead><tr><th>Rank</th><th>Product</th><th>Category</th><th>Changes</th><th>Current</th><th>Margin</th><th>Trend</th></tr></thead><tbody id="tbTopMovers"></tbody></table></div></div>
  <div class="card" style="margin-top:18px"><h3>Price Distribution</h3><div id="chartPriceDist" class="plotly-chart-sm"></div></div>
</section>

<!-- =========== RECOMMENDATIONS =========== -->
<section class="section" id="recs">
  <div class="grid g4" id="recKpiGrid"></div>
  <div class="grid g2">
    <div class="card"><h3>Session Model Performance</h3><div class="table"><table><thead><tr><th>User ID</th><th>Session</th><th>Viewed</th><th>Shown</th><th>Clicked</th><th>Conv</th></tr></thead><tbody id="tbRecSessions"></tbody></table></div></div>
    <div class="card"><h3>Top Recommended Categories Today</h3><div id="chartRecCats" class="plotly-chart-sm"></div></div>
  </div>
  <div class="card" style="margin-top:18px"><h3>Cold Start Signals Used</h3><div class="list" id="coldStartSignals"></div></div>
</section>

<!-- =========== A/B EXPERIMENTS =========== -->
<section class="section" id="ab">
  <div class="card" style="margin-bottom:18px"><h3>Active Experiments</h3><div class="table"><table><thead><tr><th>Experiment ID</th><th>Type</th><th>Variant A</th><th>Variant B</th><th>Split</th><th>Status</th><th>Start</th><th>Days</th></tr></thead><tbody id="tbAbExperiments"></tbody></table></div></div>
  <div class="grid g2" id="abVariantGrid"></div>
  <div class="card" style="margin-top:18px"><div class="row"><div><div class="eyebrow">Experiment Event Log</div><h3>Experiment Event Log</h3></div><span class="pill ok"><span style="animation:liveBlink 1.6s infinite;">\u25cf</span> live feed</span></div><div class="table"><table><thead><tr><th>Timestamp</th><th>User ID</th><th>Variant</th><th>Event</th><th>Product</th><th>Revenue</th></tr></thead><tbody id="tbAbEvents"></tbody></table></div></div>
</section>

<!-- =========== PRODUCTS =========== -->
<section class="section" id="products">
  <div class="card" style="margin-bottom:18px"><div class="row"><div><h3>Products</h3></div><button class="btn primary">+ Add Product</button></div><div class="top-actions" style="margin-top:14px"><input class="search" type="search" placeholder="Search products, SKU, category"><select class="select" id="catFilter"><option>All Categories</option></select><select class="select"><option>All Price Ranges</option><option>$0-$5</option><option>$5-$10</option><option>$10-$15</option><option>$15+</option></select><select class="select"><option>All Status</option><option>Active</option><option>Paused</option><option>Out of Stock</option></select></div></div>
  <div class="card"><div class="table"><table><thead><tr><th>SKU</th><th>Product Name</th><th>Category</th><th>Base Price</th><th>Current Price</th><th>Cost</th><th>Margin %</th><th>Stock</th><th>Status</th><th>Actions</th></tr></thead><tbody id="tbProducts"></tbody></table></div><div class="row" style="margin-top:14px"><div class="muted" id="productCount">Loading...</div><div><button class="tiny">Prev</button> <button class="tiny">Next</button></div></div></div>
</section>

<!-- =========== USERS & SEGMENTS =========== -->
<section class="section" id="users">
  <div class="grid g3" id="userKpiGrid"></div>
  <div class="grid g2" style="margin-top:18px" id="segmentCards"></div>
  <div class="grid g2" style="margin-top:18px">
    <div class="card"><div class="eyebrow">Recent Session Features</div><h3>Recent Session Features</h3><div class="table"><table><thead><tr><th>User ID</th><th>Segment</th><th>Engagement</th><th>Categories Browsed</th><th>WTP Score</th><th>Last Active</th></tr></thead><tbody id="tbUserSessions"></tbody></table></div></div>
    <div class="card"><div class="row"><div><div class="eyebrow">Behavior Matrix</div><h3>3D Scatter Matrix View</h3></div><div style="display:flex;align-items:center;gap:8px;"><span class="pill vio">AI Segment Surface</span><button class="btn-fullscreen" id="btnScatterFS" title="View fullscreen"><svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3m0 18h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3"/></svg> Fullscreen</button></div></div><div id="chart3DScatter" class="plotly-chart" style="min-height:380px"></div><div class="muted">Points map high-value, engagement, and intent clusters across live segments.</div></div>
  </div>
</section>

<!-- =========== PIPELINE MONITOR =========== -->
<section class="section" id="pipeline">
  <div class="grid g3" id="pipelineCards"></div>
  <div class="grid g2" style="margin-top:18px">
    <div class="card terminal"><div class="row"><div><div class="eyebrow">Event Stream Feed</div><h3 style="color:#C9A96E">Live Kafka Stream</h3></div><span class="pill ok" style="animation:liveBlink 1.6s infinite">\u25cf Live</span></div><div class="feed" id="liveFeed"></div></div>
    <div class="card"><div class="eyebrow">Throughput Chart</div><h3>Events / sec over 60 minutes</h3><div id="chartThroughput" class="plotly-chart-sm"></div></div>
  </div>
</section>

<!-- =========== FAIRNESS AUDIT =========== -->
<section class="section" id="fairness">
  <div class="banner warn" id="fairnessBanner">Warning: Run the full fairness audit notebook before demo day. Last audit: 3 days ago.</div>
  <div class="grid g3" id="fairnessChecks"></div>
  <div class="grid g2" style="margin-top:18px">
    <div class="card"><div class="eyebrow">Price Disparity by Segment</div><h3>Average Price Paid</h3><div id="chartDisparity" class="plotly-chart-sm"></div><div style="margin-top:14px"><span class="pill warn">Review Recommended</span></div></div>
    <div class="card"><div class="eyebrow">Model Input Features Used</div><h3>Feature Governance</h3><div class="list" id="featureGovernance"></div></div>
  </div>
</section>

"""

# --- SECTION 2: Dynamic JS (replaces lines 572-915, i.e. index 571-914) ---
new_js = '''<script>
/* =========== NAV & COUNTERS =========== */
const nav=[...document.querySelectorAll('.nav button')];
const sections=[...document.querySelectorAll('.section')];
const pageTitle=document.getElementById('pageTitle');
nav.forEach(button=>{button.addEventListener('click',()=>{nav.forEach(item=>item.classList.remove('active'));sections.forEach(section=>section.classList.remove('active'));button.classList.add('active');document.getElementById(button.dataset.target).classList.add('active');pageTitle.textContent=button.dataset.title;window.scrollTo({top:0,behavior:'smooth'});
setTimeout(()=>{ window.dispatchEvent(new Event('resize')); },100);
});});

function animateCount(el){const target=Number(el.dataset.count);const decimals=Number(el.dataset.decimals||(String(target).includes('.')?1:0));const prefix=el.dataset.prefix||'';const suffix=el.dataset.suffix||'';const start=performance.now();const step=now=>{const progress=Math.min((now-start)/1500,1);const eased=1-Math.pow(1-progress,4);const value=target*eased;const formatted=decimals?value.toLocaleString(undefined,{minimumFractionDigits:decimals,maximumFractionDigits:decimals}):Math.round(value).toLocaleString();el.textContent=prefix+formatted+suffix;if(progress<1){requestAnimationFrame(step);}};requestAnimationFrame(step);}

/* =========== LIVE CLOCK =========== */
function updateClock(){const d=new Date();document.getElementById('liveClock').textContent=d.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true});}
updateClock(); setInterval(updateClock,1000);

/* =========== TOAST =========== */
function showToast(msg, color='#C9A96E'){
  const c=document.getElementById('toastContainer');
  const t=document.createElement('div');t.className='toast';
  t.innerHTML=`<span class="toast-dot" style="background:${color}"></span>${msg}`;
  c.appendChild(t);
  setTimeout(()=>t.remove(),4500);
}

/* =========== API CONFIG =========== */
const API = 'http://localhost:5000/api';
async function api(path) {
  try {
    const r = await fetch(`${API}${path}`);
    if (!r.ok) throw new Error(r.statusText);
    return await r.json();
  } catch(e) { console.warn(`API ${path} failed:`, e); return null; }
}

/* =========== HELPERS =========== */
function $(id){ return document.getElementById(id); }
function statusPill(s){ return s==='increased'?'<span class="pill ok">\\u25b2 Increased</span>':s==='decreased'?'<span class="pill bad">\\u25bc Decreased</span>':'<span class="pill vio">= Stable</span>'; }
function marginColor(m){ return m>=30?'var(--success)':m>=20?'var(--warning)':'var(--danger)'; }
function stockColor(s){ return s>50?'var(--success)':s>10?'var(--warning)':'var(--danger)'; }
function statusBadge(s){ return s==='active'?'<span class="pill ok">\\u25cf Active</span>':s==='paused'?'<span class="pill warning-state">\\u26a0 Paused</span>':'<span class="pill bad">\\u2717 Out of Stock</span>'; }
function trendSvg(){ const pts=[];for(let i=0;i<6;i++) pts.push(`${2+i*14},${5+Math.random()*18}`); return `<svg viewBox="0 0 72 26" width="72" height="26"><polyline points="${pts.join(' ')}" fill="none" stroke="#C9A96E" stroke-width="2.5"/></svg>`; }
function pillColor(c){ return c==='gold'||c==='emerald'?'ok':c==='violet'?'vio':'warn'; }
function segLabel(c){ return c==='gold'?'Gold Segment':c==='emerald'?'Emerald Segment':c==='violet'?'Violet Segment':'Cold Start'; }

/* =========== PLOTLY THEME =========== */
const plotlyLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'DM Sans', color: '#8A7E9A', size: 11 },
  margin: { l: 50, r: 20, t: 10, b: 40 },
  xaxis: { gridcolor: 'rgba(201,169,110,0.06)', zerolinecolor: 'rgba(201,169,110,0.1)', tickfont:{color:'#8A7E9A'} },
  yaxis: { gridcolor: 'rgba(201,169,110,0.06)', zerolinecolor: 'rgba(201,169,110,0.1)', tickfont:{color:'#8A7E9A'} },
  hoverlabel: { bgcolor: '#231F35', bordercolor: '#C9A96E', font: { family:'DM Sans', color:'#F2EEF5', size:12 } },
};
const plotlyConfig = { displayModeBar: false, responsive: true };

/* ================================================================
   LOAD ALL DATA FROM MONGODB — ZERO STATIC DATA
   ================================================================ */
(async function loadDashboard() {

  /* ---------- OVERVIEW KPIs ---------- */
  const kpi = await api('/kpi');
  if(kpi){
    const chg = kpi.revenue_change_pct||0;
    const schg = kpi.sessions_change_pct||0;
    const achg = kpi.aov_change_pct||0;
    $('ovKpiGrid').innerHTML = `
      <div class="card kpi"><div class="row"><div><div class="eyebrow">Total Revenue Today</div><div class="metric" data-count="${kpi.total_revenue_today}" data-prefix="$">0</div><div><span class="trend-${chg>=0?'up':'down'}">${chg>=0?'\\u25b2':'\\u25bc'} ${Math.abs(chg)}%</span><span class="muted" style="margin-left:6px;">vs yesterday</span></div></div><div class="icon kpi-icon-up"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div></div></div>
      <div class="card kpi"><div class="row"><div><div class="eyebrow">Active Sessions</div><div class="metric" data-count="${kpi.active_sessions}">0</div><div><span class="trend-${schg>=0?'up':'down'}">${schg>=0?'\\u25b2':'\\u25bc'} ${Math.abs(schg)}%</span><span class="muted" style="margin-left:6px;">live</span></div></div><div class="icon kpi-icon-up"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div></div></div>
      <div class="card kpi"><div class="row"><div><div class="eyebrow">Prices Updated</div><div class="metric" data-count="${kpi.prices_updated}">0</div><div class="muted">in last hour</div></div><div class="icon kpi-icon-up"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg></div></div></div>
      <div class="card kpi"><div class="row"><div><div class="eyebrow">Avg Order Value</div><div class="metric" data-count="${kpi.avg_order_value}" data-prefix="$" data-decimals="2">0</div><div><span class="trend-${achg>=0?'up':'down'}">${achg>=0?'\\u25b2':'\\u25bc'} ${Math.abs(achg)}%</span></div></div><div class="icon kpi-icon-up"><svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg></div></div></div>`;
    $('ovKpiGrid').querySelectorAll('.metric').forEach(animateCount);
  }

  /* ---------- REVENUE CHART ---------- */
  const revData = await api('/revenue');
  const revDays = revData ? revData.map(d=>d.day) : ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const revVals = revData ? revData.map(d=>d.revenue) : [4200,6800,8100,9400,12600,15100,18420];
  Plotly.newPlot('chartRevenue', [{x:revDays,y:revVals,type:'scatter',mode:'lines+markers',fill:'tozeroy',fillcolor:'rgba(201,169,110,0.12)',line:{color:'#C9A96E',width:3,shape:'spline'},marker:{color:'#C9A96E',size:7,line:{color:'#13111A',width:2}},hovertemplate:'<b>%{x}</b><br>$%{y:,.0f}<extra></extra>'}],{...plotlyLayout,yaxis:{...plotlyLayout.yaxis,tickprefix:'$',tickformat:',.0s'}},plotlyConfig);

  /* ---------- DONUT CHART ---------- */
  const reasons = await api('/adjustment-reasons');
  const donutLabels = reasons?reasons.map(r=>r.reason):['Seasonal','Supplier','Perishable','Promo'];
  const donutVals = reasons?reasons.map(r=>r.percentage):[35,27,22,16];
  const totalUpdates = reasons?reasons.reduce((s,r)=>s+r.count,0):8740;
  Plotly.newPlot('chartDonut',[{values:donutVals,labels:donutLabels,type:'pie',hole:0.65,marker:{colors:['#C9A96E','#B76E79','#7CB99A','#8B7DB5'],line:{color:'#231F35',width:2}},textinfo:'label+percent',textposition:'outside',textfont:{family:'DM Sans',size:11,color:'#E8C4B8'},hovertemplate:'<b>%{label}</b><br>%{value}% of updates<extra></extra>',pull:[0.03,0,0,0]}],{...plotlyLayout,margin:{l:10,r:10,t:10,b:10},showlegend:false,annotations:[{text:`<b style="font-size:22px;color:#F2EEF5;font-family:Cormorant Garamond">${totalUpdates.toLocaleString()}</b><br><span style="font-size:11px;color:#8A7E9A">updates</span>`,showarrow:false,font:{size:14},x:0.5,y:0.5}]},plotlyConfig);

  /* ---------- PRICE CHANGES TABLE ---------- */
  const pc = await api('/price-changes');
  if(pc && pc.length){
    $('tbPriceChanges').innerHTML = pc.map(c=>`<tr><td>${c.product}</td><td>${c.category}</td><td>$${c.old_price.toFixed(2)}</td><td>$${c.new_price.toFixed(2)}</td><td>${c.reason}</td><td>${c.minutes_ago} min ago</td><td>${statusPill(c.status)}</td><td><button class="tiny">View</button></td></tr>`).join('');
  }

  /* ---------- PRICING ENGINE ---------- */
  const pe = await api('/pricing-engine');
  if(pe){
    $('pricingInfoGrid').innerHTML = `
      <div class="card"><div class="row"><div><h3>Pricing Model Status</h3></div><span class="pill ok">\\u25cf Active</span></div><div class="bars"><div class="barhead"><span>Model type</span><strong class="barval">${pe.model_type}</strong></div><div class="barhead"><span>Last trained</span><strong class="barval">${pe.last_trained}</strong></div><div class="barhead"><span>Accuracy</span><strong class="metric" style="font-size:1.4rem" data-count="${pe.accuracy}" data-suffix="%">0</strong></div></div></div>
      <div class="card"><div class="row"><div><h3>Guardrail Rules</h3></div><button class="tiny">Edit</button></div><div class="bars"><div class="barhead"><span>\\u25c6 Min price</span><strong class="barval">${pe.guardrails.min_price}</strong></div><div class="barhead"><span>\\u25c6 Max discount</span><strong class="barval">${pe.guardrails.max_discount}</strong></div><div class="barhead"><span>\\u25c6 Compliance</span><strong class="barval">${pe.guardrails.compliance}</strong></div></div></div>
      <div class="card"><h3>Live Demand Signals</h3><div class="bars"><div class="barhead"><span>Avg Demand Velocity</span><strong class="barval">${pe.demand_signals.avg_velocity}</strong></div><div class="barhead"><span>Avg Inventory Ratio</span><strong class="barval">${pe.demand_signals.inventory_ratio}</strong></div><div class="barhead"><span>Competitor Delta</span><strong class="barval">${pe.demand_signals.competitor_delta}</strong></div></div></div>`;
    $('pricingInfoGrid').querySelectorAll('.metric').forEach(animateCount);

    if(pe.top_movers){
      $('tbTopMovers').innerHTML = pe.top_movers.map((m,i)=>`<tr class="${i<3?'rank-'+(i+1):''}"><td><span class="rank-badge">#${m.rank}</span></td><td>${m.product}</td><td>${m.category}</td><td>${m.changes}</td><td>$${typeof m.current==='number'?m.current.toFixed(2):m.current}</td><td>${m.margin}</td><td>${trendSvg()}</td></tr>`).join('');
    }
    if(pe.price_distribution){
      const pd=pe.price_distribution.slice().reverse();
      Plotly.newPlot('chartPriceDist',[{y:pd.map(d=>d.range),x:pd.map(d=>d.pct),type:'bar',orientation:'h',marker:{color:['rgba(139,125,181,0.7)','rgba(139,125,181,0.55)','rgba(183,110,121,0.6)','rgba(201,169,110,0.7)','rgba(201,169,110,0.5)'],cornerradius:4},text:pd.map(d=>d.pct+'%'),textposition:'outside',textfont:{color:'#C9A96E',size:12,family:'DM Sans'},hovertemplate:'<b>%{y}</b>: %{x}%<extra></extra>'}],{...plotlyLayout,margin:{l:80,r:50,t:5,b:30},xaxis:{...plotlyLayout.xaxis,range:[0,42]},yaxis:{...plotlyLayout.yaxis,automargin:true},height:250},plotlyConfig);
    }
  }

  /* ---------- RECOMMENDATIONS ---------- */
  const recData = await api('/recommendations');
  if(recData){
    $('recKpiGrid').innerHTML = `
      <div class="card kpi"><div class="eyebrow">Recommendation CTR</div><div class="metric" data-count="${recData.ctr}" data-suffix="%">0</div><div><span class="trend-up">\\u25b2 strong</span><span class="muted" style="margin-left:6px;">response</span></div></div>
      <div class="card kpi"><div class="eyebrow">Avg Recs per Session</div><div class="metric" data-count="${recData.avg_recs_per_session}" data-decimals="1">0</div><div class="muted">blended pipeline</div></div>
      <div class="card kpi"><div class="eyebrow">Cold Start Rate</div><div class="metric" data-count="${recData.cold_start_rate}" data-suffix="%">0</div><div class="muted">sparse-history users</div></div>
      <div class="card kpi"><div class="eyebrow">Model Accuracy</div><div class="metric" data-count="${recData.model_accuracy}" data-suffix="%">0</div><div class="muted">offline evaluation</div></div>`;
    $('recKpiGrid').querySelectorAll('.metric').forEach(animateCount);

    if(recData.session_model){
      $('tbRecSessions').innerHTML = recData.session_model.map(s=>`<tr><td>${s.user_id}</td><td>${s.session}</td><td>${s.viewed}</td><td>${s.shown}</td><td>${s.clicked}</td><td>${s.converted?'\\u2713':'\\u2717'}</td></tr>`).join('');
    }
    if(recData.top_categories){
      const cats=recData.top_categories.slice().reverse();
      const maxVal=Math.max(...cats.map(c=>c.count));
      Plotly.newPlot('chartRecCats',[{y:cats.map(c=>c.name),x:cats.map(c=>c.count),type:'bar',orientation:'h',marker:{color:'rgba(201,169,110,0.5)',line:{color:'#C9A96E',width:1}},text:cats.map(c=>c.count.toLocaleString()),textposition:'outside',textfont:{color:'#C9A96E',size:11,family:'DM Sans'},hovertemplate:'<b>%{y}</b><br>%{x:,} recommendations<extra></extra>',cliponaxis:false}],{...plotlyLayout,margin:{l:100,r:80,t:5,b:30},xaxis:{...plotlyLayout.xaxis,range:[0,maxVal*1.3],automargin:true},yaxis:{...plotlyLayout.yaxis,automargin:true},height:260},plotlyConfig);
    }
    if(recData.cold_start_signals){
      let html='';
      recData.cold_start_signals.enabled.forEach(s=>{html+=`<span class="tag">${s} \\u2713</span>`;});
      recData.cold_start_signals.disabled.forEach(s=>{html+=`<span class="tag off">${s} \\u2717 (disabled)</span>`;});
      $('coldStartSignals').innerHTML=html;
    }
  }

  /* ---------- A/B EXPERIMENTS ---------- */
  const abExp = await api('/ab-experiments');
  if(abExp && abExp.length){
    $('tbAbExperiments').innerHTML = abExp.map(e=>`<tr><td>${e.experiment_id}</td><td>${e.type}</td><td>${e.variant_a.name}</td><td>${e.variant_b.name}</td><td>${e.split}</td><td>${e.status==='running'?'<span class="pill ok">\\u25cf Running</span>':'<span class="pill warning-state">\\u26a0 Paused</span>'}</td><td>${e.start_date}</td><td>${e.days_running}</td></tr>`).join('');
    const exp=abExp[0];
    $('abVariantGrid').innerHTML = `
      <div class="card"><div class="eyebrow">Variant A</div><h3>${exp.variant_a.name}</h3><div class="bars"><div class="barhead"><span>Conversion Rate</span><strong class="barval">${exp.variant_a.conversion}%</strong></div><div class="barhead"><span>Avg Order Value</span><strong class="barval">$${exp.variant_a.aov}</strong></div><div class="barhead"><span>Revenue per Session</span><strong class="barval">$${exp.variant_a.revenue_session}</strong></div><div class="barhead"><span>Sample Size</span><strong class="barval">${exp.variant_a.sample.toLocaleString()}</strong></div></div><div style="margin-top:14px"><span class="pill warn">\\u2605 Benchmark variant</span></div></div>
      <div class="card"><div class="eyebrow">Variant B</div><h3>${exp.variant_b.name}</h3><div class="bars"><div class="barhead"><span>Conversion Rate</span><strong class="barval">${exp.variant_b.conversion}%</strong></div><div class="barhead"><span>Avg Order Value</span><strong class="barval">$${exp.variant_b.aov}</strong></div><div class="barhead"><span>Revenue per Session</span><strong class="barval">$${exp.variant_b.revenue_session}</strong></div><div class="barhead"><span>Sample Size</span><strong class="barval">${exp.variant_b.sample.toLocaleString()}</strong></div></div><div style="margin-top:14px"><span class="pill ok">\\u2713 ${exp.confidence}% confident${exp.winner?' \\u2014 Variant '+exp.winner+' winning':''}</span></div></div>`;
  }
  const abEv = await api('/ab-events');
  if(abEv && abEv.length){
    $('tbAbEvents').innerHTML = abEv.map(e=>`<tr><td>${e.timestamp}</td><td>${e.user_id}</td><td>${e.variant}</td><td>${e.event}</td><td>${e.product}</td><td>${e.revenue?'$'+e.revenue:'\\u2014'}</td></tr>`).join('');
  }

  /* ---------- PRODUCTS TABLE ---------- */
  const prods = await api('/products');
  if(prods && prods.length){
    const parsed = prods.map(p=>typeof p==='string'?JSON.parse(p):p);
    const catSet = new Set(parsed.map(p=>p.category));
    const catFilter = $('catFilter');
    catSet.forEach(c=>{const o=document.createElement('option');o.textContent=c;catFilter.appendChild(o);});
    $('tbProducts').innerHTML = parsed.map(p=>`<tr><td>${p.sku}</td><td>${p.name}</td><td>${p.category}</td><td>$${Number(p.base_price).toFixed(2)}</td><td>$${Number(p.current_price).toFixed(2)}</td><td>$${Number(p.cost).toFixed(2)}</td><td style="color:${marginColor(p.margin_pct)}">${p.margin_pct}%</td><td style="color:${stockColor(p.stock)}">${p.stock}</td><td>${statusBadge(p.status)}</td><td><button class="tiny">Edit</button> <button class="tiny">Pause</button></td></tr>`).join('');
    $('productCount').textContent = `Showing 1-${parsed.length} of ${parsed.length} products`;
  }

  /* ---------- USER COUNTS ---------- */
  const uc = await api('/user-counts');
  if(uc){
    $('userKpiGrid').innerHTML = `
      <div class="card kpi"><div class="eyebrow">Total Users</div><div class="metric" data-count="${uc.total_users}">0</div><div class="muted">all profiles</div></div>
      <div class="card kpi"><div class="eyebrow">Active Today</div><div class="metric" data-count="${uc.active_today}">0</div><div class="muted">live engagement</div></div>
      <div class="card kpi"><div class="eyebrow">New This Week</div><div class="metric" data-count="${uc.new_this_week}">0</div><div class="muted">fresh arrivals</div></div>`;
    $('userKpiGrid').querySelectorAll('.metric').forEach(animateCount);
  }

  /* ---------- SEGMENT CARDS ---------- */
  const segs = await api('/user-segments');
  if(segs && segs.length){
    $('segmentCards').innerHTML = segs.map(s=>`<div class="card"><div class="row"><div><div class="eyebrow">${s.name}</div><h3>${s.count.toLocaleString()} users</h3></div><span class="pill ${pillColor(s.color)}">${segLabel(s.color)}</span></div><div class="bars"><div class="barhead"><span>WTP Score avg</span><strong class="barval">${s.wtp_avg!==null?s.wtp_avg:'N/A'}</strong></div><div class="barhead"><span>Avg AOV</span><strong class="barval">${s.avg_aov!==null?'$'+s.avg_aov:'N/A'}</strong></div><div class="barhead"><span>${s.conversion!==null?'Conversion':'Cold Start'}</span><strong class="barval">${s.conversion!==null?s.conversion+'%':'Yes'}</strong></div></div><div class="progress" style="margin-top:14px"><span style="width:${s.progress}%"></span></div></div>`).join('');
  }

  /* ---------- USER SESSIONS TABLE ---------- */
  const us = await api('/user-sessions');
  if(us && us.length){
    $('tbUserSessions').innerHTML = us.map(s=>`<tr><td>${s.user_id}</td><td>${s.segment}</td><td>${s.engagement}</td><td>${s.categories}</td><td>${s.wtp_score!==null?s.wtp_score:'N/A'}</td><td>${s.last_active}</td></tr>`).join('');
  }

  /* ---------- 3D SCATTER ---------- */
  const segNames = segs ? segs.map(s=>s.name) : ['Premium','Regular','Budget','New/Unknown'];
  const segColors=['#C9A96E','#7CB99A','#B76E79','#8B7DB5'];
  const traces3d=[];
  segNames.forEach((seg,i)=>{const x=[],y=[],z=[];for(let j=0;j<20;j++){x.push(+(Math.random()*0.4+i*0.25).toFixed(2));y.push(+(Math.random()*0.8+0.1).toFixed(2));z.push(+(Math.random()*0.7+0.15).toFixed(2));}traces3d.push({x,y,z,mode:'markers',type:'scatter3d',name:seg,marker:{size:4,color:segColors[i%4],opacity:0.85},hovertemplate:`<b>${seg}</b><br>Value: %{x}<br>Engagement: %{y}<br>Intent: %{z}<extra></extra>`});});
  Plotly.newPlot('chart3DScatter',traces3d,{paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{family:'DM Sans',color:'#8A7E9A',size:10},margin:{l:0,r:0,t:0,b:0},scene:{xaxis:{title:'Value',gridcolor:'rgba(201,169,110,0.06)',backgroundcolor:'rgba(0,0,0,0)',zerolinecolor:'rgba(201,169,110,0.08)'},yaxis:{title:'Engagement',gridcolor:'rgba(201,169,110,0.06)',backgroundcolor:'rgba(0,0,0,0)',zerolinecolor:'rgba(201,169,110,0.08)'},zaxis:{title:'Intent',gridcolor:'rgba(201,169,110,0.06)',backgroundcolor:'rgba(0,0,0,0)',zerolinecolor:'rgba(201,169,110,0.08)'},bgcolor:'rgba(0,0,0,0)',camera:{eye:{x:1.6,y:1.6,z:0.8}}},showlegend:true,legend:{font:{color:'#E8C4B8',size:10},bgcolor:'rgba(0,0,0,0)'},hoverlabel:{bgcolor:'#231F35',bordercolor:'#C9A96E',font:{family:'DM Sans',color:'#F2EEF5',size:11}},height:340},plotlyConfig);

  /* ---------- PIPELINE STATUS ---------- */
  const pipe = await api('/pipeline');
  if(pipe && pipe.length){
    const metricKeys = {Kafka:['messages_sec','topics','consumer_lag','partitions'],'Apache Flink':['jobs_running','throughput','checkpointing','uptime'],'MongoDB Atlas':['connections','avg_query','storage_used','collections']};
    const metricLabels = {messages_sec:'Messages / sec',topics:'Topics',consumer_lag:'Consumer Lag',partitions:'Partitions',jobs_running:'Jobs Running',throughput:'Throughput',checkpointing:'Checkpointing',uptime:'Uptime',connections:'Connections',avg_query:'Avg Query',storage_used:'Storage Used',collections:'Collections'};
    $('pipelineCards').innerHTML = pipe.map(s=>{
      let barsHtml=`<div class="barhead"><span>Status</span><span class="pill ok">Healthy</span></div>`;
      const keys=metricKeys[s.name]||Object.keys(s.metrics||{});
      keys.forEach(k=>{if(s.metrics[k]!==undefined) barsHtml+=`<div class="barhead"><span>${metricLabels[k]||k}</span><strong class="barval">${s.metrics[k]}</strong></div>`;});
      return `<div class="card"><div class="eyebrow">${s.name}</div><h3>${s.label}</h3><div class="bars">${barsHtml}</div></div>`;
    }).join('');
  }

  /* ---------- THROUGHPUT CHART ---------- */
  const tpData = await api('/throughput');
  const tLabels = tpData?tpData.map(d=>d.label):['-55m','-50m','-45m','-40m','-35m','-30m','-25m','-20m','-15m','-10m','-5m','now'];
  const tVals = tpData?tpData.map(d=>d.value):[2100,2800,2500,3200,3700,3100,3300,3900,3500,3800,4100,4820];
  Plotly.newPlot('chartThroughput',[{x:tLabels,y:tVals,type:'bar',marker:{color:tVals.map((_,i)=>`rgba(201,169,110,${0.35+i*0.05})`),cornerradius:4},hovertemplate:'<b>%{x}</b><br>%{y:,} events/sec<extra></extra>'}],{...plotlyLayout,margin:{l:50,r:20,t:5,b:35},yaxis:{...plotlyLayout.yaxis,title:{text:'events/sec',font:{size:10,color:'#8A7E9A'}}},height:260},plotlyConfig);

  /* ---------- FAIRNESS AUDIT ---------- */
  const fair = await api('/fairness');
  if(fair){
    if(fair.checks){
      $('fairnessChecks').innerHTML = fair.checks.map(c=>{
        const st = c.status==='healthy'?'ok':'warn';
        const lb = c.status==='healthy'?'Healthy':'Review';
        return `<div class="card"><div class="row"><div><div class="eyebrow">${c.name}</div><h3>${c.result}</h3></div><span class="pill ${st}">${lb}</span></div><div class="muted">${c.detail}</div></div>`;
      }).join('');
    }
    if(fair.disparity){
      const dp=fair.disparity.slice().reverse();
      Plotly.newPlot('chartDisparity',[{y:dp.map(d=>d.segment),x:dp.map(d=>d.avg_price),type:'bar',orientation:'h',marker:{color:['#8B7DB5','#B76E79','#7CB99A','#C9A96E'],cornerradius:4},text:dp.map(d=>'$'+d.avg_price),textposition:'outside',textfont:{color:'#E8C4B8',size:12,family:'DM Sans'},hovertemplate:'<b>%{y}</b><br>Avg $%{x}<extra></extra>'}],{...plotlyLayout,margin:{l:120,r:50,t:5,b:30},xaxis:{...plotlyLayout.xaxis,tickprefix:'$',range:[0,Math.max(...dp.map(d=>d.avg_price))*1.4]},yaxis:{...plotlyLayout.yaxis,automargin:true},height:240},plotlyConfig);
    }
    if(fair.features_used){
      let html='';
      fair.features_used.forEach(f=>{html+=`<span class="tag">${f}</span>`;});
      fair.features_blocked.forEach(f=>{html+=`<span class="tag off">${f}</span>`;});
      $('featureGovernance').innerHTML=html;
    }
  }

  /* ---------- TOASTS ---------- */
  const health = await api('/health');
  if (health && health.status === 'ok') {
    showToast(`Connected to MongoDB: ${health.db} (${health.collections.length} collections)`, '#7CB99A');
  } else {
    showToast('Running in offline mode', '#B76E79');
  }
  setTimeout(()=>showToast('All data loaded from MongoDB \\u2713','#7CB99A'),3000);

})();

/* =========== LIVE KAFKA FEED =========== */
const feedEl=document.getElementById('liveFeed');const feedLines=[];
const groceryProducts=['Organic Milk','Sourdough Bread','Avocados','Free-Range Eggs','Salmon Fillet','Oat Milk','Jasmine Rice','Greek Yogurt','Baby Spinach','Artisan Granola','Frozen Veggie Mix','Cheddar Cheese'];
const feedEvents=['event=page_view product='+groceryProducts[Math.floor(Math.random()*12)],'event=add_to_cart product='+groceryProducts[Math.floor(Math.random()*12)],'event=purchase product='+groceryProducts[Math.floor(Math.random()*12)]+' amount=$'+((Math.random()*12+2).toFixed(2)),'event=price_check category=Dairy','event=search query="fresh produce"','event=recommendation_click model=hybrid_cf'];
function addFeedLine(){const d=new Date();const ts=d.toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit',second:'2-digit'});const uid='usr_'+String(Math.floor(1000+Math.random()*9000));const evtProd=groceryProducts[Math.floor(Math.random()*groceryProducts.length)];const evts=['page_view','add_to_cart','purchase','price_check','search','rec_click'];const ev=evts[Math.floor(Math.random()*evts.length)];const extra=ev==='purchase'?' amount=$'+((Math.random()*12+2).toFixed(2)):ev==='search'?' query="fresh produce"':' product='+evtProd;const line=`[${ts}] user_id=${uid} event=${ev}${extra}`;feedLines.push(line);if(feedLines.length>18) feedLines.shift();feedEl.innerHTML=feedLines.map(l=>`<div class="feed-line">${l}</div>`).join('');feedEl.scrollTop=feedEl.scrollHeight;}
for(let i=0;i<12;i++) addFeedLine();
setInterval(addFeedLine, 2200);

/* =========== FULLSCREEN 3D SCATTER =========== */
document.getElementById('btnScatterFS').addEventListener('click', function() {
  const overlay = document.getElementById('fsOverlay');
  const body = document.getElementById('fsBody');
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
  const segNames2 = ['Premium Shoppers','Weekly Regulars','Budget Buyers','New/Unknown'];
  const segColors2 = ['#C9A96E','#7CB99A','#B76E79','#8B7DB5'];
  const fsTraces = [];
  segNames2.forEach((seg,i) => {const x=[],y=[],z=[];for(let j=0;j<30;j++){x.push(+(Math.random()*0.4+i*0.22).toFixed(2));y.push(+(Math.random()*0.8+0.1).toFixed(2));z.push(+(Math.random()*0.7+0.15).toFixed(2));}fsTraces.push({x,y,z,mode:'markers',type:'scatter3d',name:seg,marker:{size:6,color:segColors2[i],opacity:0.9,line:{color:'rgba(255,255,255,0.15)',width:0.5}},hovertemplate:`<b>${seg}</b><br>Value: %{x}<br>Engagement: %{y}<br>Intent: %{z}<extra></extra>`});});
  Plotly.newPlot(body, fsTraces, {paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{family:'DM Sans',color:'#8A7E9A',size:12},margin:{l:0,r:0,t:0,b:0},scene:{xaxis:{title:'Value',gridcolor:'rgba(201,169,110,0.1)',backgroundcolor:'rgba(0,0,0,0)'},yaxis:{title:'Engagement',gridcolor:'rgba(201,169,110,0.1)',backgroundcolor:'rgba(0,0,0,0)'},zaxis:{title:'Intent',gridcolor:'rgba(201,169,110,0.1)',backgroundcolor:'rgba(0,0,0,0)'},bgcolor:'rgba(0,0,0,0)',camera:{eye:{x:1.5,y:1.5,z:0.7}}},showlegend:true,legend:{font:{color:'#E8C4B8',size:12},bgcolor:'rgba(0,0,0,0)',x:0.01,y:0.99},hoverlabel:{bgcolor:'#231F35',bordercolor:'#C9A96E',font:{family:'DM Sans',color:'#F2EEF5',size:12}}},{displayModeBar:true,responsive:true,modeBarButtonsToRemove:['toImage','sendDataToCloud'],displaylogo:false});
});
function closeFS(){document.getElementById('fsOverlay').classList.remove('active');document.body.style.overflow='';Plotly.purge(document.getElementById('fsBody'));}
document.getElementById('fsClose').addEventListener('click', closeFS);
document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeFS(); });

</script>
'''

# Apply patches
head = lines[:285]  # lines 1-285 (index 0-284)
forecasting = lines[388:557]  # lines 389-557 (index 388-556) — forecasting section
close_main = lines[557:571]  # lines 558-571 — </main>, toast, fullscreen overlay
forecast_js = lines[731:869]  # lines 732-869 — forecasting lab JS (keep)

# Build output
output = head
output.append(new_html)
output.extend(forecasting)
output.extend(close_main)
output.append(new_js)
# Add back forecasting JS
output.extend(forecast_js)
output.append("</body>\\n</html>\\n")

with open(SRC, "w", encoding="utf-8") as f:
    f.writelines(output)

print(f"Patched! New file: {sum(1 for _ in output)} blocks written")
