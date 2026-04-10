import re

with open("frontend/admin.html", "r", encoding="utf-8") as f:
    html = f.read()

new_head = """<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>PulsePrice Admin</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg-primary: #13111A;
  --bg-secondary: #1E1B2E;
  --bg-card: #231F35;
  --bg-card-hover: #2A2640;
  --bg-input: #1A1728;
  --accent-gold: #C9A96E;
  --accent-rose: #B76E79;
  --accent-blush: #E8C4B8;
  --accent-mist: #F2EEF5;
  --success: #7CB99A;
  --warning: #C9A96E;
  --danger: #B76E79;
  --info: #8B7DB5;
  --border-subtle: rgba(201, 169, 110, 0.10);
  --border-medium: rgba(201, 169, 110, 0.22);
  --border-strong: rgba(201, 169, 110, 0.45);
  --border-rose: rgba(183, 110, 121, 0.25);
  --text-primary: #F2EEF5;
  --text-secondary: #E8C4B8;
  --text-muted: #8A7E9A;
  --text-gold: #C9A96E;
  --text-rose: #B76E79;
  --sidebar-width: 240px;
  --sidebar-bg: #0F0D18;
  --sidebar-border: rgba(201, 169, 110, 0.12);
  --glow-gold: 0 0 24px rgba(201, 169, 110, 0.18);
  --glow-rose: 0 0 24px rgba(183, 110, 121, 0.18);
  --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.35);
}

* { box-sizing: border-box; }
body { margin: 0; background: var(--bg-primary); color: var(--text-secondary); font-family: 'DM Sans', sans-serif; font-weight: 300; }

h1,h2,h3,h4,.metric,#pageTitle,.logo-text { font-family: "Cormorant Garamond", serif; font-weight: 500; color: var(--text-primary); }

#pageTitle { font-size: 20px; font-weight: 500; margin: 0; }
.section > h2, .section > h3 { font-size: 22px; margin-bottom: 24px; position: relative; }
.section > h2::after, .section > h3::after { content: ''; display: block; width: 40px; height: 2px; background: var(--accent-gold); margin-top: 6px; }

.card h3 { font-size: 16px; margin: 0 0 4px 0; }
.card > .eyebrow + h3 { margin-bottom: 14px; }
.card > .row > div > h3 { margin-top: 4px; }

.app { display: flex; min-height: 100vh; }
.side { position: fixed; inset: 0 auto 0 0; width: var(--sidebar-width); background: var(--sidebar-bg); border-right: 1px solid var(--sidebar-border); display: flex; flex-direction: column; z-index: 2; }
.main { margin-left: var(--sidebar-width); flex: 1; padding: 18px; }

.logo { padding: 22px 16px 12px; display: flex; align-items: center; gap: 12px; }
.pulse-wrap { position: relative; width: 12px; height: 12px; display: grid; place-items: center; }
.pulse { width: 8px; height: 8px; background: var(--accent-rose); transform: rotate(45deg); animation: goldPulse 2s ease-in-out infinite; }
.logo-text { font-size: 20px; font-weight: 600; color: var(--accent-gold); }

.meta { padding: 0 16px 20px; font-family: 'DM Sans', sans-serif; display: flex; flex-direction: column; gap: 4px; }
.meta .text { font-size: 11px; font-weight: 300; color: var(--text-muted); }
.meta-user { display: flex; align-items: center; gap: 12px; margin-top: 12px; }
.avatar { width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center; background: linear-gradient(135deg, #B76E79, #C9A96E); color: #13111A; font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 500; }
.user-info { display: flex; flex-direction: column; }
.user-info .name { font-size: 12px; color: var(--text-secondary); font-weight: 400; }
.live { font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; margin-top: 2px;}
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--success); animation: liveBlink 2.5s ease-in-out infinite; }

.nav { display: flex; flex-direction: column; gap: 4px; padding: 0 0 20px 0; flex: 1; }
.nav button { height: 40px; padding: 0 16px; display: flex; align-items: center; gap: 10px; background: transparent; border: none; border-left: 2px solid transparent; color: var(--text-muted); font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 400; cursor: pointer; transition: all 200ms ease; width: 100%; text-align: left; }
.nav button:hover { background: rgba(201, 169, 110, 0.06); color: var(--text-secondary); }
.nav button.active { background: rgba(201, 169, 110, 0.10); color: var(--accent-gold); border-left-color: var(--accent-gold); padding-left: 14px; }
.nav-icon { width: 15px; font-style: normal; text-align: center; color: inherit; font-size: 15px; }
.nav button .label { display: block; }

.status { background: rgba(201, 169, 110, 0.05); border-top: 1px solid var(--border-subtle); padding: 12px 16px; }
.status h4 { font-family: 'DM Sans', sans-serif; font-size: 10px; color: var(--text-muted); font-weight: 400; margin: 0 0 8px 0; text-transform:none;}
.status .muted { display: flex; flex-direction: column; gap: 4px; }
.status-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text-secondary); font-family: 'DM Sans', sans-serif; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--success); }

.topbar { background: var(--bg-secondary); border-bottom: 1px solid var(--border-subtle); height: 56px; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 1; margin: -18px -18px 18px -18px; }
.top-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.search, .select { background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 8px 14px; font-family: 'DM Sans', sans-serif; font-size: 13px; color: var(--text-secondary); transition: all 200ms ease; min-height: 40px; }
.search::placeholder { color: var(--text-muted); }
.search:focus, .select:focus { border-color: var(--border-strong); box-shadow: 0 0 0 3px rgba(201, 169, 110, 0.12); outline: none; }
.select { appearance: none; -webkit-appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23C9A96E'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 10px center; background-size: 14px; padding-right: 32px; }

.btn { background: transparent; border: 1px solid var(--border-medium); border-radius: 8px; padding: 9px 16px; color: var(--text-secondary); font-family: 'DM Sans', sans-serif; font-size: 12px; font-weight: 400; cursor: pointer; transition: all 200ms ease; min-height: 40px; text-decoration:none; display:inline-flex; align-items:center;}
.btn:hover { border-color: var(--accent-gold); color: var(--accent-gold); }
.btn.out { padding: 7px 14px; }
.btn.primary { background: linear-gradient(135deg, #B76E79 0%, #C9A96E 100%); color: #13111A; border: none; border-radius: 10px; padding: 13px 24px; font-size: 13px; font-weight: 500; letter-spacing: 0.02em; box-shadow: 0 4px 16px rgba(183, 110, 121, 0.30); }
.btn.primary:hover { box-shadow: 0 6px 24px rgba(201, 169, 110, 0.40); transform: translateY(-1px); border-color: transparent;}
.btn.primary:active { transform: translateY(0); box-shadow: 0 2px 8px rgba(183, 110, 121, 0.30); }
.btn.daterange { background: var(--bg-input); border-color: var(--border-subtle); padding: 7px 14px; }
.btn.daterange:hover { color: var(--text-secondary); border-color: var(--border-medium); cursor: default; }

.notif { background: transparent; border: none; position: relative; cursor: pointer; width: 40px; height: 40px; border-radius: 8px; transition: all 200ms ease; display: grid; place-items: center; color: var(--text-secondary); }
.notif:hover { background: rgba(201, 169, 110, 0.08); }
.notif i { font-size: 18px; font-style: normal; }
.badge { position: absolute; top: 0; right: 0; width: 16px; height: 16px; background: var(--accent-rose); border-radius: 50%; color: white; display: grid; place-items: center; font-family: 'DM Sans', sans-serif; font-size: 9px; font-weight: 500; }

.section { display: none; animation: fade .28s ease; }
.section.active { display: block; }

.grid { display: grid; gap: 16px; }
.g4 { grid-template-columns: repeat(4, 1fr); }
.g3 { grid-template-columns: repeat(3, 1fr); }
.g2 { grid-template-columns: repeat(2, 1fr); }

.card { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 14px; padding: 20px 22px; box-shadow: var(--shadow-card); transition: border-color 250ms ease, box-shadow 250ms ease, transform 200ms ease; }
.card:hover { border-color: var(--border-medium); box-shadow: var(--glow-gold); transform: translateY(-2px); }

.eyebrow { font-family: 'DM Sans', sans-serif; font-size: 11px; font-weight: 400; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.metric { font-size: 32px; font-weight: 600; color: var(--text-primary); margin: 6px 0; }
.muted { color: var(--text-muted); font-size: 11px; font-family: 'DM Sans', sans-serif; }

.row { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.row > div { flex: 1; }
.icon { font-size: 18px; color: var(--accent-rose); display: flex; align-items: center; justify-content: center; width:40px; height:40px; background: transparent;}

.pill { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 20px; font-family: 'DM Sans', sans-serif; font-weight: 500; font-size: 11px; }
.pill.ok { background: rgba(124, 185, 154, 0.15); color: var(--success); }
.pill.warn { background: rgba(183, 110, 121, 0.15); color: var(--accent-rose); }
.pill.vio { background: rgba(138, 126, 154, 0.15); color: var(--text-muted); }
.pill.warning-state { background: rgba(201, 169, 110, 0.15); color: var(--accent-gold); }
.pill.bad { background: rgba(183, 110, 121, 0.15); color: var(--accent-rose); }

.table { overflow: auto; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 14px; margin-top: 14px; }
table { width: 100%; border-collapse: collapse; min-width: 760px; }
th { background: rgba(201, 169, 110, 0.06); border-bottom: 1px solid var(--border-subtle); padding: 12px 16px; text-align: left; font-family: 'DM Sans', sans-serif; font-size: 11px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.08em; text-transform: uppercase; }
td { border-bottom: 1px solid var(--border-subtle); padding: 13px 16px; font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 400; color: var(--text-secondary); }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: rgba(201, 169, 110, 0.04); }

.tiny { background: transparent; border: 1px solid var(--border-medium); border-radius: 6px; padding: 4px 10px; font-family: 'DM Sans', sans-serif; font-size: 11px; font-weight: 400; color: var(--text-secondary); cursor: pointer; transition: all 200ms ease; }
.tiny:hover { border-color: var(--accent-gold); color: var(--accent-gold); }

.bars { display: grid; gap: 12px; margin-top: 14px; }
.barhead { display: flex; justify-content: space-between; font-family: 'DM Sans', sans-serif; font-size: 12px; color: var(--text-secondary); gap:12px;}
.barval { font-weight: 500; font-size: 12px; color: var(--accent-gold); }
.track { height: 6px; border-radius: 4px; background: rgba(201, 169, 110, 0.08); overflow: hidden; margin-top: 6px; border: none; }
.fill { height: 100%; background: linear-gradient(90deg, #B76E79, #C9A96E); border-radius: 4px; box-shadow:none;}
.viofill { background: linear-gradient(90deg, #B76E79, #C9A96E); border-radius: 4px; }

.progress { height: 6px; border-radius: 4px; background: rgba(201, 169, 110, 0.10); overflow: hidden; margin-top: 6px; }
.progress > span { display: block; height: 100%; background: linear-gradient(90deg, #B76E79, #C9A96E); width:auto;}

.terminal { background: #0A0812; border: 1px solid var(--border-subtle); border-radius: 10px; padding: 16px; font-family: Consolas, monospace; font-size: 12px; color: #C9A96E; line-height: 1.8; }
.feed { height: 220px; overflow: hidden; margin-top: 16px; }
.scroll { display: grid; gap: 8px; animation: streamScroll 12s linear infinite; }

.banner { background: rgba(201, 169, 110, 0.06); border:none; border-left: 3px solid var(--accent-gold); border-radius: 0 10px 10px 0; padding: 16px 20px; color: var(--text-secondary); font-family: 'DM Sans', sans-serif; font-size: 13px; margin-bottom: 24px; }
.banner.warn { background: rgba(183, 110, 121, 0.08); border-left-color: var(--accent-rose); }

.list { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
.tag { padding: 6px 12px; border-radius: 20px; background: rgba(201, 169, 110, 0.08); border: 1px solid var(--border-subtle); font-family: 'DM Sans', sans-serif; font-size: 11px; font-weight: 500; color: var(--accent-gold); }
.tag.off { background: rgba(183, 110, 121, 0.08); border-color: rgba(183, 110, 121, 0.25); color: var(--accent-rose); text-decoration: none; }

.hide-sm { display: inline; }

.trend-up { display:inline-flex; align-items:center;  padding: 3px 10px; border-radius:20px; font-size: 11px; font-weight:500; font-family:'DM Sans'; background: rgba(124, 185, 154, 0.15); color: var(--success); }
.trend-down { display:inline-flex; align-items:center; padding: 3px 10px; border-radius:20px; font-size: 11px; font-weight:500; font-family:'DM Sans'; background: rgba(183, 110, 121, 0.15); color: var(--accent-rose); }
.kpi-icon-up { color: var(--accent-rose); }

.rank-1 { border: 1px solid rgba(201, 169, 110, 0.50); box-shadow: 0 0 32px rgba(201, 169, 110, 0.15); }
.rank-1 .rank-badge { background: #C9A96E; color: #13111A; }
.rank-2 { border: 1px solid rgba(183, 110, 121, 0.40); box-shadow: 0 0 24px rgba(183, 110, 121, 0.12); }
.rank-2 .rank-badge { background: #B76E79; color: #13111A; }
.rank-3 { border: 1px solid rgba(139, 125, 181, 0.35); }
.rank-3 .rank-badge { background: #8B7DB5; color: #F2EEF5; }
.rank-badge { border-radius: 20px; padding: 3px 10px; font-family: 'DM Sans', sans-serif; font-size: 11px; font-weight: 500; }

@keyframes goldPulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.15); opacity: 0.7; } }
@keyframes liveBlink { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
@keyframes fade { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
@keyframes streamScroll { 0% { transform: translateY(0); } 100% { transform: translateY(-50%); } }

@media (max-width:1180px){.g4,.g3{grid-template-columns:repeat(2,minmax(0,1fr))}.g2{grid-template-columns:1fr}}
@media (max-width:860px){.side{width:84px;padding:18px 10px}.main{margin-left:84px}.logo-text,.meta .text,.nav .label,.status .text,.status h4,.user-info,.nav button span {display:none}.nav button{justify-content:center;padding:0}.search{width:100%}.topbar{flex-direction:column;align-items:flex-start}.top-actions{width:100%;justify-content:flex-start}.g4,.g3,.g2{grid-template-columns:1fr}}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: rgba(201, 169, 110, 0.25); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(201, 169, 110, 0.45); }
</style>
</head>"""

# Replace in body
html = re.sub(r'<head>.*?</head>', new_head, html, flags=re.DOTALL)

# Sidebar structural changes
html = html.replace('<div class="logo"><span class="pulse"></span><span class="logo-text">PulsePrice</span></div>',
                    '<div class="logo"><div class="pulse-wrap"><div class="pulse"></div></div><span class="logo-text">PulsePrice</span></div>')

html = html.replace('<div class="meta"><div class="avatar">AP</div><div class="text">Admin Panel</div><div class="live"><span style="animation:blink 1.8s infinite;">&#9679;</span> <span class="hide-sm">Live</span></div></div>',
                    '<div class="meta"><div class="text">Admin Panel</div><div class="meta-user"><div class="avatar">AD</div><div class="user-info"><span class="name">Administrator</span><span class="live"><div class="live-dot"></div> <span class="hide-sm">Live</span></span></div></div></div>')

# Change nav icons / active structural setup to support i and label span
html = html.replace('data-title="Overview">OV <span class="label">', 'data-title="Overview"><i class="nav-icon">OV</i> <span class="label">')
html = html.replace('data-title="Pricing Engine">PR <span class="label">', 'data-title="Pricing Engine"><i class="nav-icon">PR</i> <span class="label">')
html = html.replace('data-title="Recommendations">RC <span class="label">', 'data-title="Recommendations"><i class="nav-icon">RC</i> <span class="label">')
html = html.replace('data-title="A/B Experiments">AB <span class="label">', 'data-title="A/B Experiments"><i class="nav-icon">AB</i> <span class="label">')
html = html.replace('data-title="Products">PD <span class="label">', 'data-title="Products"><i class="nav-icon">PD</i> <span class="label">')
html = html.replace('data-title="Users & Segments">US <span class="label">', 'data-title="Users & Segments"><i class="nav-icon">US</i> <span class="label">')
html = html.replace('data-title="Pipeline Monitor">PL <span class="label">', 'data-title="Pipeline Monitor"><i class="nav-icon">PL</i> <span class="label">')
html = html.replace('data-title="Fairness Audit">FA <span class="label">', 'data-title="Fairness Audit"><i class="nav-icon">FA</i> <span class="label">')

html = html.replace('<span style="color:var(--success);animation:blink 2.1s infinite;">&#9679;</span> <span class="text">Kafka</span> | <span style="color:var(--success);animation:blink 2.1s infinite;">&#9679;</span> <span class="text">Flink</span> | <span style="color:var(--success);animation:blink 2.1s infinite;">&#9679;</span> <span class="text">MongoDB</span>',
                    '<div class="status-item"><div class="status-dot"></div> Kafka</div><div class="status-item"><div class="status-dot"></div> Flink</div><div class="status-item"><div class="status-dot"></div> MongoDB</div>')

# Topbar structural changes
html = html.replace('<div class="btn">Last 7 days &#9662;</div>', '<div class="btn daterange">Last 7 days &#9662;</div>')

# Table pills mapping
html = html.replace('<span class="pill ok">? Increased</span>', '<span class="pill ok">▲ Increased</span>')
html = html.replace('<span class="pill warn">? Decreased</span>', '<span class="pill bad">▼ Decreased</span>')
html = html.replace('<span class="pill vio">= Stable</span>', '<span class="pill vio">= Stable</span>')

html = html.replace('<span class="pill ok">Active</span>', '<span class="pill ok">● Active</span>')
html = html.replace('<span class="pill warn">Paused</span>', '<span class="pill warning-state">⚠ Paused</span>')
html = html.replace('<span class="pill bad">Out of Stock</span>', '<span class="pill bad">✗ Danger</span>')
# There is also "? Active" and "? Running" and "? Paused" inside pricing and AB experiments
html = html.replace('<span class="pill ok">? Active</span>', '<span class="pill ok">● Active</span>')
html = html.replace('<span class="pill ok">? Running</span>', '<span class="pill ok">● Running</span>')
html = html.replace('<span class="pill warn">? Paused</span>', '<span class="pill warning-state">⚠ Paused</span>')
html = html.replace('<span class="pill vio"><span style="animation:blink 1.6s infinite;">?</span> live feed</span>', '<span class="pill ok"><span style="animation:blink 1.6s infinite;">●</span> live feed</span>')
html = html.replace('<span class="pill ok" style="animation:blink 1.6s infinite">Live</span>', '<span class="pill ok" style="animation:blink 1.6s infinite">● Live</span>')

# Metrics and trend badging
html = html.replace('<div class="muted">? 12.4% vs yesterday</div>', '<div><span class="trend-up">▲ 12.4%</span><span class="muted" style="margin-left:6px;">vs yesterday</span></div>')
html = html.replace('<div class="muted">? 8.1% live</div>', '<div><span class="trend-up">▲ 8.1%</span><span class="muted" style="margin-left:6px;">live</span></div>')
html = html.replace('<div class="muted">? 3.2%</div>', '<div><span class="trend-down">▼ 3.2%</span></div>')
html = html.replace('<div class="muted">? strong response</div>', '<div><span class="trend-up">▲ strong</span><span class="muted" style="margin-left:6px;">response</span></div>')

html = html.replace('<div class="icon">??</div>', '<div class="icon kpi-icon-up"></div>')
html = html.replace('<div class="icon">?</div>', '<div class="icon kpi-icon-up"></div>')

# SVGs color tweaks
html = html.replace('rgba(0,245,255,.35)', 'rgba(201, 169, 110, 0.20)')
html = html.replace('rgba(0,245,255,.02)', 'rgba(201, 169, 110, 0.00)')
html = html.replace('stroke="rgba(255,255,255,.06)"', 'stroke="rgba(201, 169, 110, 0.08)" stroke-width="0.5"')

# Generic color mapping within svg elements
html = html.replace('stroke="#00f5ff"', 'stroke="#C9A96E"')
html = html.replace('fill="#00f5ff"', 'fill="#C9A96E"')
html = html.replace('stroke="#7c3aed"', 'stroke="#B76E79"')
html = html.replace('fill="#7c3aed"', 'fill="#B76E79"')
html = html.replace('stroke="#10b981"', 'stroke="#7CB99A"')
html = html.replace('fill="#10b981"', 'fill="#7CB99A"')
html = html.replace('stroke="#f59e0b"', 'stroke="#8B7DB5"')
html = html.replace('fill="#f59e0b"', 'fill="#8B7DB5"')
html = html.replace('fill="#ef4444"', 'fill="#B76E79"')

# SVG text
html = html.replace('fill="#6b7280"', 'fill="#8A7E9A" font-family="DM Sans"')
html = html.replace('fill="#f0f0f0" font-size="24" font-family="Space Grotesk"', 'fill="#F2EEF5" font-size="18" font-family="Cormorant Garamond"')
html = html.replace('font-size="24" font-family="Space Grotesk" font-weight="700">', 'font-size="18" font-family="Cormorant Garamond" font-weight="600">')

# Rank table rows
html = html.replace('<tr><td>#1</td>', '<tr class="rank-1"><td><span class="rank-badge">#1</span></td>')
html = html.replace('<tr><td>#2</td>', '<tr class="rank-2"><td><span class="rank-badge">#2</span></td>')
html = html.replace('<tr><td>#3</td>', '<tr class="rank-3"><td><span class="rank-badge">#3</span></td>')
html = html.replace('<tr><td>#4</td>', '<tr><td><span class="rank-badge">#4</span></td>')
html = html.replace('<tr><td>#5</td>', '<tr><td><span class="rank-badge">#5</span></td>')

# Buttons primary
html = html.replace('class="btn" style="background:var(--accent-cyan);color:#03141a;border-color:transparent"', 'class="btn primary"')

# Warning banner
html = html.replace('<div class="banner">', '<div class="banner warn">')

# Fix tags logic
html = html.replace('?</div>', '</div>') # removing random inline question marks

# Remove remaining text highlighting logic
html = html.replace('<strong>', '<strong class="barval">')

# Also fix the specific labels inside card tables! (Wait, regex for <strong> was done)
# Price Guardrail tags are `<strong> cost × 1.10</strong>`
# Just leave generic!

with open("e:/DA IICT V.01/DA-IICT/frontend/admin.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Done")
