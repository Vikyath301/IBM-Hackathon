/**
 * ChainSentinel IBM Z / Db2 Real-Time Stream Simulator
 */

let streamInterval = null;
let isStreaming = false;
let streamCount = 15482;
let totalDollarExposure = 2295243;
let disruptionsCount = 42;

const SAMPLE_PRODUCTS = [
  { name: "Tier-1 Enterprise Server Modules", cat: "Electronics", val: 1900000, origin: "EE. UU.", dest: "France", region: "Western Europe", mode: "Standard Class" },
  { name: "High-Performance MCU-8 Blades", cat: "Electronics", val: 24500, origin: "EE. UU.", dest: "Germany", region: "Western Europe", mode: "First Class" },
  { name: "ASML Lithography Optic Spares", cat: "Semiconductors", val: 185000, origin: "Canada", dest: "Japan", region: "Eastern Asia", mode: "Second Class" },
  { name: "Automotive Radar Transceivers", cat: "Automotive", val: 89000, origin: "EE. UU.", dest: "United Kingdom", region: "Western Europe", mode: "Standard Class" },
  { name: "Cryogenic Cooling Manifolds", cat: "Cloud Systems", val: 340000, origin: "Puerto Rico", dest: "India", region: "South Asia", mode: "Standard Class" },
  { name: "Industrial Micro-Inverters", cat: "Electronics", val: 12000, origin: "EE. UU.", dest: "United States", region: "North America", mode: "Same Day" }
];

function toggleLiveStream() {
  const btn = document.getElementById('btn-toggle-stream');
  if (isStreaming) {
    clearInterval(streamInterval);
    isStreaming = false;
    if (btn) {
      btn.innerHTML = '▶ Start Live IBM Z Stream';
      btn.classList.remove('btn-critical');
      btn.classList.add('btn-primary');
    }
  } else {
    isStreaming = true;
    if (btn) {
      btn.innerHTML = '⏸ Pause Stream';
      btn.classList.remove('btn-primary');
      btn.classList.add('btn-critical');
    }
    // Ingest first immediately, then interval
    simulateIngestEvent();
    streamInterval = setInterval(simulateIngestEvent, 2500);
  }
}

function simulateIngestEvent() {
  streamCount += 1;
  const item = SAMPLE_PRODUCTS[Math.floor(Math.random() * SAMPLE_PRODUCTS.length)];
  const orderId = 10000 + Math.floor(Math.random() * 90000);
  
  // Decide risk probability
  const isDelayed = Math.random() < 0.28 || item.val > 500000;
  const prob = isDelayed ? (0.75 + Math.random() * 0.20) : (0.05 + Math.random() * 0.35);
  const dollarAtRisk = Math.round(prob * item.val);
  
  if (isDelayed) {
    disruptionsCount += 1;
    totalDollarExposure += dollarAtRisk;
  }

  // Update counters
  updateMetricCounters();

  // Add Row to Live Stream Table
  prependStreamTableRow({
    orderId: orderId,
    product: item.name,
    route: `${item.origin} -> ${item.dest}`,
    mode: item.mode,
    value: item.val,
    prob: prob,
    isDelayed: isDelayed,
    alertLevel: prob >= 0.75 ? 'CRITICAL' : (prob >= 0.5 ? 'WARNING' : 'NORMAL')
  });
}

function updateMetricCounters() {
  const totalEl = document.getElementById('kpi-total-ingested');
  const disEl = document.getElementById('kpi-disruptions-count');
  const dollarEl = document.getElementById('kpi-dollar-risk');

  if (totalEl) totalEl.textContent = streamCount.toLocaleString();
  if (disEl) disEl.textContent = disruptionsCount.toLocaleString();
  if (dollarEl) dollarEl.textContent = `$${totalDollarExposure.toLocaleString()}`;
}

function prependStreamTableRow(txn) {
  const tbody = document.getElementById('stream-table-body');
  if (!tbody) return;

  const row = document.createElement('tr');
  const alertColor = txn.alertLevel === 'CRITICAL' ? 'var(--accent-red)' : (txn.alertLevel === 'WARNING' ? 'var(--accent-amber)' : 'var(--accent-green)');
  const alertBadgeClass = txn.alertLevel === 'CRITICAL' ? 'kpi-pill red' : (txn.alertLevel === 'WARNING' ? 'kpi-pill cyan' : 'kpi-pill green');

  row.innerHTML = `
    <td class="mono" style="font-weight: 700; color: #fff;">#${txn.orderId}</td>
    <td>${txn.product}</td>
    <td style="color: var(--text-secondary);">${txn.route}</td>
    <td>${txn.mode}</td>
    <td class="mono">$${txn.value.toLocaleString()}</td>
    <td class="mono" style="color: ${alertColor}; font-weight: 700;">${(txn.prob * 100).toFixed(1)}%</td>
    <td><span class="${alertBadgeClass}">${txn.alertLevel}</span></td>
  `;

  // Clicking row loads into inspector
  row.addEventListener('click', () => {
    loadTransactionIntoInspector(txn);
  });

  tbody.insertBefore(row, tbody.firstChild);

  // Keep max 25 rows
  if (tbody.children.length > 25) {
    tbody.removeChild(tbody.lastChild);
  }
}

function loadTransactionIntoInspector(txn) {
  const orderIdEl = document.getElementById('inspect-order-id');
  const prodNameEl = document.getElementById('inspect-product-name');
  const riskProbEl = document.getElementById('inspect-risk-prob');
  const dollarRiskEl = document.getElementById('inspect-dollar-risk');

  if (orderIdEl) orderIdEl.textContent = `#${txn.orderId}`;
  if (prodNameEl) prodNameEl.textContent = txn.product;
  if (riskProbEl) {
    riskProbEl.textContent = `${(txn.prob * 100).toFixed(1)}%`;
    riskProbEl.style.color = txn.isDelayed ? 'var(--accent-red)' : 'var(--accent-green)';
  }
  if (dollarRiskEl) {
    dollarRiskEl.textContent = `$${(txn.prob * txn.value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  }

  // Parse origin and destination
  const parts = txn.route.split(' -> ');
  if (parts.length === 2) {
    updateRouteMap(parts[0], parts[1], txn.isDelayed);
  }
}
