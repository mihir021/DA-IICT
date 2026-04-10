with open("frontend/admin.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix donut chart track duplicate stroke-width
html = html.replace(
    'stroke="rgba(201, 169, 110, 0.08)" stroke-width="0.5" stroke-width="28"',
    'stroke="rgba(201, 169, 110, 0.08)" stroke-width="28"'
)

# Fix empty KPI icons by adding a decorative diamond symbol
html = html.replace(
    '<div class="icon kpi-icon-up"></div>',
    '<div class="icon kpi-icon-up">❖</div>'
)

# Fix random question marks from encoding issues in the original file
html = html.replace('<span>? Min price</span>', '<span>◆ Min price</span>')
html = html.replace('<span>? Max discount</span>', '<span>◆ Max discount</span>')
html = html.replace('<span>? Compliance</span>', '<span>◆ Compliance</span>')

html = html.replace('142 views/min ?', '142 views/min ↗')

html = html.replace('Device Type ?', 'Device Type ✓')
html = html.replace('Time of Day ?', 'Time of Day ✓')
html = html.replace('Referral Source ?', 'Referral Source ✓')
html = html.replace('Geo Region ? (disabled)', 'Geo Region ✗ (disabled)')

# Fix table columns with unknown '?' values (conversion checkmarks)
html = html.replace('<td>?</td>', '<td>✓</td>')
html = html.replace('<div class="muted">?</div>', '<div class="muted">✓</div>') # Just in case

# Fix the dummy danger text back to "Out of Stock"
html = html.replace('<span class="pill bad">✗ Danger</span>', '<span class="pill bad">✗ Out of Stock</span>')

# Any "Warn Benchmark" fixing
html = html.replace('<span class="pill warn">? Benchmark variant</span>', '<span class="pill warn">★ Benchmark variant</span>')
html = html.replace('<span class="pill ok">? 95% confident', '<span class="pill ok">✓ 95% confident')

# The pill Active and increased states inside tables (double check)
# It's currently: <span class="pill ok">▲ Increased</span> - that is correct.

with open("frontend/admin.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Fixed UI errors.")
