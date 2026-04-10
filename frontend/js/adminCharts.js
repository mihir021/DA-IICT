function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value);
}


export function renderSalesChart(host, data) {
  if (!data.length) {
    host.innerHTML = "<p class='muted-label'>No sales data available.</p>";
    return;
  }

  const maxRevenue = Math.max(...data.map((item) => item.revenue), 1);
  const width = 620;
  const height = 260;
  const stepX = width / Math.max(data.length - 1, 1);
  const points = data.map((item, index) => {
    const x = index * stepX;
    const y = height - (item.revenue / maxRevenue) * 210 - 20;
    return `${x},${y}`;
  }).join(" ");

  const labels = data.map((item, index) => `<text x="${index * stepX}" y="252" fill="#5c6b61" font-size="11">${item.label}</text>`).join("");
  host.innerHTML = `
    <svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Sales trend chart">
      <defs>
        <linearGradient id="sales-gradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#2e8b57" stop-opacity="0.34"></stop>
          <stop offset="100%" stop-color="#2e8b57" stop-opacity="0"></stop>
        </linearGradient>
      </defs>
      <polyline fill="none" stroke="#2e8b57" stroke-width="4" points="${points}"></polyline>
      <polygon fill="url(#sales-gradient)" points="0,240 ${points} ${width},240"></polygon>
      ${labels}
    </svg>
    <p class="muted-label">Range revenue: ${formatCurrency(data.reduce((sum, item) => sum + item.revenue, 0))}</p>
  `;
}


export function renderDonutChart(host, data) {
  const total = data.reduce((sum, item) => sum + item.value, 0) || 1;
  const colors = ["#2e8b57", "#ff8f3d", "#f2b541"];
  const radius = 68;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;
  const segments = data.map((item, index) => {
    const segmentLength = (item.value / total) * circumference;
    const circle = `<circle cx="90" cy="90" r="${radius}" fill="none" stroke="${colors[index % colors.length]}" stroke-width="18" stroke-dasharray="${segmentLength} ${circumference - segmentLength}" stroke-dashoffset="${-offset}" transform="rotate(-90 90 90)"></circle>`;
    offset += segmentLength;
    return circle;
  }).join("");

  host.innerHTML = `
    <div class="donut-wrap">
      <svg class="line-chart" viewBox="0 0 180 180" role="img" aria-label="Inventory mix chart">
        <circle cx="90" cy="90" r="${radius}" fill="none" stroke="#e4ebe4" stroke-width="18"></circle>
        ${segments}
      </svg>
      <div class="legend-list">
        ${data.map((item, index) => `
          <div class="legend-item">
            <span><span class="legend-dot legend-dot-${index + 1}">●</span>${item.label}</span>
            <strong>${item.value}</strong>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}


export function renderCategoryBars(host, data) {
  const maxValue = Math.max(...data.map((item) => item.revenue), 1);
  host.innerHTML = data.map((item) => {
    const width = Math.max((item.revenue / maxValue) * 260, 8);
    return `
      <div class="bar-row">
        <div>
          <strong>${item.label}</strong>
          <svg width="280" height="18" viewBox="0 0 280 18" role="img" aria-label="${item.label} revenue">
            <rect x="0" y="4" width="280" height="10" rx="5" fill="#e4ebe4"></rect>
            <rect x="0" y="4" width="${width}" height="10" rx="5" fill="#2e8b57"></rect>
          </svg>
        </div>
        <strong>${formatCurrency(item.revenue)}</strong>
      </div>
    `;
  }).join("");
}


export function renderInventory3D(host, data) {
  const maxValue = Math.max(...data.map((item) => item.stock), 1);
  const barWidth = 34;
  const gap = 24;
  const depth = 14;
  const svgBars = data.map((item, index) => {
    const height = Math.max((item.stock / maxValue) * 150, 14);
    const x = index * (barWidth + gap) + 10;
    const baseY = 220;
    const frontY = baseY - height;
    const top = `${x},${frontY} ${x + depth},${frontY - depth} ${x + barWidth + depth},${frontY - depth} ${x + barWidth},${frontY}`;
    const side = `${x + barWidth},${frontY} ${x + barWidth + depth},${frontY - depth} ${x + barWidth + depth},${baseY - depth} ${x + barWidth},${baseY}`;
    return `
      <polygon points="${top}" fill="#63b77e"></polygon>
      <polygon points="${side}" fill="#1f6a42"></polygon>
      <rect x="${x}" y="${frontY}" width="${barWidth}" height="${height}" rx="4" fill="#2e8b57"></rect>
      <text x="${x}" y="244" fill="#5c6b61" font-size="10">${item.label.slice(0, 8)}</text>
      <text x="${x}" y="${frontY - 10}" fill="#132017" font-size="10">${item.stock}</text>
    `;
  }).join("");

  host.innerHTML = `<svg class="line-chart" viewBox="0 0 400 260" role="img" aria-label="3D inventory depth chart">${svgBars}</svg>`;
}


export function renderMetricList(host, items, formatter = (value) => value) {
  host.innerHTML = items.map((item) => `
    <div class="premium-tile">
      <strong>${item.label}</strong>
      <div class="table-inline">
        <span>${item.note || ""}</span>
        <span>${formatter(item.value)}</span>
      </div>
    </div>
  `).join("");
}


export function renderRecords(host, records, fields) {
  host.innerHTML = records.map((record) => `
    <div class="data-table">
      ${fields.map((field) => `<div class="table-inline"><span>${field.label}</span><strong>${record[field.key] ?? "-"}</strong></div>`).join("")}
    </div>
  `).join("");
}


export function renderScatterMatrix3D(host, points) {
  const maxX = Math.max(...points.map((point) => point.x), 1);
  const maxY = Math.max(...points.map((point) => point.y), 1);
  const maxZ = Math.max(...points.map((point) => point.z), 1);
  const colors = ["#2e8b57", "#ff8f3d", "#3f88ff", "#b66cff", "#f2b541", "#ff5f6d"];
  const bubbles = points.map((point, index) => {
    const x = 50 + (point.x / maxX) * 260;
    const y = 220 - (point.y / maxY) * 150;
    const depth = (point.z / maxZ) * 18;
    const radius = 7 + depth / 4;
    return `
      <ellipse cx="${x + depth}" cy="${y - depth}" rx="${radius}" ry="${radius * 0.55}" fill="rgba(19,32,23,0.12)"></ellipse>
      <circle cx="${x}" cy="${y}" r="${radius}" fill="${colors[index % colors.length]}" opacity="0.82"></circle>
      <text x="${x + 12}" y="${y - 10}" fill="#132017" font-size="10">${point.label.split(" ")[0]}</text>
    `;
  }).join("");

  host.innerHTML = `
    <svg class="line-chart" viewBox="0 0 380 260" role="img" aria-label="3D scatter matrix">
      <line x1="40" y1="220" x2="330" y2="220" stroke="#8da094" stroke-width="1.2"></line>
      <line x1="40" y1="220" x2="40" y2="40" stroke="#8da094" stroke-width="1.2"></line>
      <line x1="40" y1="220" x2="80" y2="180" stroke="#8da094" stroke-width="1.2"></line>
      <text x="300" y="240" fill="#5c6b61" font-size="10">Order frequency</text>
      <text x="12" y="34" fill="#5c6b61" font-size="10">Basket value</text>
      <text x="84" y="176" fill="#5c6b61" font-size="10">LTV depth</text>
      ${bubbles}
    </svg>
  `;
}
