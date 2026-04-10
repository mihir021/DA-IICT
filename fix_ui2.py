import re

with open("frontend/admin.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Redundant Headings
redundant = [
    '<div class="eyebrow">Revenue Over Time</div><h3>Revenue Over Time</h3>',
    '<div class="eyebrow">Price Adjustment Reasons</div><h3>Price Adjustment Reasons</h3>',
    '<div class="eyebrow">Recent Price Changes</div><h3>Recent Price Changes</h3>',
    '<div class="eyebrow">Pricing Model Status</div><h3>Pricing Model Status</h3>',
    '<div class="eyebrow">Guardrail Rules</div><h3>Guardrail Rules</h3>',
    '<div class="eyebrow">Live Demand Signals</div><h3>Live Demand Signals</h3>',
    '<div class="eyebrow">Session Model Performance</div><h3>Session Model Performance</h3>',
    '<div class="eyebrow">Top Recommended Categories Today</div><h3>Top Recommended Categories Today</h3>',
    '<div class="eyebrow">Cold Start Signals Used</div><h3>Cold Start Signals Used</h3>',
    '<div class="eyebrow">Active Experiments</div><h3>Active Experiments</h3>',
    '<div class="eyebrow">Top Price Movement</div><h3>Top 10 Most Price-Changed Products Today</h3>',
    '<div class="eyebrow">Price Distribution</div><h3>Price Distribution</h3>',
    '<div class="eyebrow">Catalog Controls</div><h3>Products</h3>'
]
for item in redundant:
    if item == '<div class="eyebrow">Top Price Movement</div><h3>Top 10 Most Price-Changed Products Today</h3>':
        html = html.replace(item, '<h3>Top 10 Most Price-Changed Products Today</h3>')
    elif item == '<div class="eyebrow">Catalog Controls</div><h3>Products</h3>':
         html = html.replace(item, '<h3>Products</h3>')
    else:
        # Keep just the h3
        h3_match = re.search(r'<h3>(.*?)</h3>', item)
        if h3_match:
            h3 = h3_match.group(0)
            html = html.replace(item, h3)

# 2 & 3. Icon Monotony and KPI Padding (CSS overlay)
css_update = """
.icon { font-size: 20px; color: var(--accent-rose); display: flex; align-items: center; justify-content: center; width:44px; height:44px; background: rgba(183, 110, 121, 0.08); border-radius: 12px; border: 1px solid rgba(183, 110, 121, 0.15); margin-left: 12px; }
.search { min-width: 250px; }
th { color: var(--accent-gold); font-weight: 600; opacity: 0.9; }
"""

html = html.replace('.icon { font-size: 18px; color: var(--accent-rose); display: flex; align-items: center; justify-content: center; width:40px; height:40px; background: transparent;}', css_update.strip())

# Replacing the 4 ❖ with actual SVG icons.
# Revenue
icon1 = '<svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
# Sessions
icon2 = '<svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
# Prices Updated
icon3 = '<svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>'
# AOV
icon4 = '<svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>'

icons = [icon1, icon2, icon3, icon4] 

count = 0
while '❖' in html and count < 4:
    html = html.replace('❖', icons[count], 1)
    count += 1

# 4. Search UI Proportions => Applied in CSS (.search { min-width: 250px; })

# 5. Throughput Visual Crowding
html = html.replace('x="432" y="252">now</text>', 'x="456" y="252">now</text>')
html = html.replace('x="54" y="252">-60m</text>', 'x="62" y="252">-60m</text>') 

# 6. Table header contrast
html = html.replace('th { background: rgba(201, 169, 110, 0.06); border-bottom: 1px solid var(--border-subtle); padding: 12px 16px; text-align: left; font-family: \'DM Sans\', sans-serif; font-size: 11px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.08em; text-transform: uppercase; }', 
'th { background: rgba(201, 169, 110, 0.06); border-bottom: 1px solid var(--border-subtle); padding: 12px 16px; text-align: left; font-family: \'DM Sans\', sans-serif; font-size: 11px; font-weight: 600; color: var(--accent-gold); letter-spacing: 0.08em; text-transform: uppercase; }')


with open("frontend/admin.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Applied final UI polish.")
