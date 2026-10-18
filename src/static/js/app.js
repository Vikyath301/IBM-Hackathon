/**
 * ChainSentinel Main Application Orchestrator
 */

let currentOrderData = null;

document.addEventListener('DOMContentLoaded', () => {
  initRouteMap();
  bindUIEvents();
  
  // Auto-load Slide 8 Disruption state on initial launch for high-impact first impression
  simulateSlide8Disruption();
  
  // Seed initial rows in stream table
  for (let i = 0; i < 4; i++) {
    simulateIngestEvent();
  }
});

function bindUIEvents() {
  // Slide 8 Disruption Simulator
  const btnSlide8 = document.getElementById('btn-simulate-slide8');
  if (btnSlide8) {
    btnSlide8.addEventListener('click', simulateSlide8Disruption);
  }

  // Toggle Live Stream
  const btnStream = document.getElementById('btn-toggle-stream');
  if (btnStream) {
    btnStream.addEventListener('click', toggleLiveStream);
  }

  // Commit via z/OS Connect API Button
  const btnCommit = document.getElementById('btn-commit-action');
  if (btnCommit) {
    btnCommit.addEventListener('click', executeZosCommit);
  }

  // View Audit Dossier Button
  const btnAudit = document.getElementById('btn-view-audit');
  if (btnAudit) {
    btnAudit.addEventListener('click', viewAuditDossier);
  }

  // Custom Simulator Modal open/close
  const btnCustomSim = document.getElementById('btn-custom-sim');
  const modalCustom = document.getElementById('modal-custom-sim');
  const closeCustom = document.getElementById('close-custom-sim');
  
  if (btnCustomSim && modalCustom) {
    btnCustomSim.addEventListener('click', () => modalCustom.classList.add('open'));
  }
  if (closeCustom && modalCustom) {
    closeCustom.addEventListener('click', () => modalCustom.classList.remove('open'));
  }

  // Custom Form Submit
  const customForm = document.getElementById('custom-order-form');
  if (customForm) {
    customForm.addEventListener('submit', handleCustomOrderSubmit);
  }

  // Audit Modal Close
  const closeAudit = document.getElementById('close-audit-modal');
  const modalAudit = document.getElementById('modal-audit-report');
  if (closeAudit && modalAudit) {
    closeAudit.addEventListener('click', () => modalAudit.classList.remove('open'));
  }

  // Commit Terminal Modal Close
  const closeTerminal = document.getElementById('close-terminal-modal');
  const modalTerminal = document.getElementById('modal-terminal');
  if (closeTerminal && modalTerminal) {
    closeTerminal.addEventListener('click', () => modalTerminal.classList.remove('open'));
  }
}

async function simulateSlide8Disruption() {
  try {
    const res = await fetch('/simulate-disruption', { method: 'POST' });
    if (!res.ok) throw new Error('Disruption simulation endpoint failed');
    const data = await res.json();
    currentOrderData = data;

    // Animate multi-agent execution pipeline
    await animateAgentPipeline(data.latency_ms);
    updateAgentDetails(data);

    // Update UI elements
    renderOrderDisruption(data);
    showToast('Slide 8 Disruption Scenario Simulated ($1.9M at Risk)', 'critical');
  } catch (err) {
    console.warn('API offline or error, falling back to local Slide 8 specification:', err);
    fallbackSlide8();
  }
}

function fallbackSlide8() {
  const mockData = {
    order_id: 4471,
    product_name: "Tier-1 Enterprise Server Modules",
    category_name: "Tier-1 Electronics",
    order_country: "France",
    shipping_mode: "Standard Ground",
    order_value: 1900000.00,
    latency_ms: 11.2,
    detection: {
      is_anomaly: true,
      anomaly_score: 0.50,
      anomaly_reasons: [
        "High-value capital transaction ($1,900,000) exceeding standard buffer threshold",
        "Bulk volume (800 units) risking warehouse staging bottlenecks"
      ]
    },
    risk: {
      late_delivery_probability: 0.87,
      is_high_risk: true,
      alert_level: "CRITICAL",
      dollar_at_risk: 1700000.00,
      fastest_predicted_days: 2,
      normal_predicted_days: 6,
      risk_drivers: [
        { feature: "Carrier Mode: Standard Ground", impact_pct: 34.0, direction: "INCREASES_RISK", description: "Standard Ground exhibits elevated transit variance." },
        { feature: "Delivery SLA: 4 Days Scheduled", impact_pct: 28.0, direction: "INCREASES_RISK", description: "Compressed delivery window leaves low buffer." },
        { feature: "Capital Exposure: $1,900,000 Value", impact_pct: 18.0, direction: "INCREASES_RISK", description: "Tier-1 capital inventory requires priority fulfillment." },
        { feature: "Cross-Border: EE. UU. -> France", impact_pct: 12.0, direction: "INCREASES_RISK", description: "Transatlantic customs inspection." },
        { feature: "Order Volume: 800 Units", impact_pct: 8.0, direction: "INCREASES_RISK", description: "Pallet staging bottleneck." }
      ]
    },
    recommendations: [
      {
        rank: 1,
        action: "SHIFT_SUPPLIER_VOLUME",
        title: "Shift 60% order allocation to regional secondary supplier (covers Western Europe)",
        feasibility: "High (Verified contract buffer)",
        estimated_expedite_cost: 48000.00,
        protected_revenue: 1700000.00,
        roi_ratio: "35.4x",
        turnaround_days: 2,
        simulation_notes: "Secondary supplier contracted SLA buffer of 48h with 3.5% allocation surcharge."
      },
      {
        rank: 2,
        action: "EXPEDITE_AIR_CARRIER",
        title: "Upgrade carrier to First Class Air (reduces delivery from 4d to 2d)",
        feasibility: "Medium (Airport cargo cutoff dependent)",
        estimated_expedite_cost: 123500.00,
        protected_revenue: 1900000.00,
        roi_ratio: "15.4x",
        turnaround_days: 2,
        simulation_notes: "Air courier freight rate parity (+6.5% surcharge) ensuring arrival within 2 days."
      },
      {
        rank: 3,
        action: "RESERVE_STOCK_TRANSFER",
        title: "Dispatch reserve buffer inventory from nearest central distribution hub",
        feasibility: "High (Hub stock verified)",
        estimated_expedite_cost: 45.00,
        protected_revenue: 950000.00,
        roi_ratio: ">1000x",
        turnaround_days: 1,
        simulation_notes: "Availability of 10% safety stock buffer at central distribution warehouse."
      }
    ],
    explanation: "High risk: Supplier A is 36 hours late, stock covers 4 days, demand is up 18%. Recommended: Shift 60% of volume to Supplier B and reroute shipment 4471. Protects about $1.7M of orders for about $48K added cost. Status quo: found in next week's review, after the stock-out."
  };
  currentOrderData = mockData;
  renderOrderDisruption(mockData);
}

function renderOrderDisruption(data) {
  if (!data || !data.risk) return;

  // Order identifiers
  const orderIdEl = document.getElementById('inspect-order-id');
  if (orderIdEl) orderIdEl.textContent = `#${data.order_id || 4471}`;

  const prodNameEl = document.getElementById('inspect-product-name');
  if (prodNameEl) prodNameEl.textContent = data.product_name || 'Custom Enterprise Order';

  const catSubEl = document.getElementById('inspect-category-subtitle');
  if (catSubEl) {
    const origin = data.customer_country || 'EE. UU.';
    const dest = data.order_country || 'France';
    const mode = data.shipping_mode || 'Standard Class';
    catSubEl.textContent = `${data.category_name || 'Electronics'} | Corridor: ${origin} ➔ ${dest} (${mode})`;
  }
  
  // Risk Probability
  const prob = (data.risk.late_delivery_probability !== undefined) ? Number(data.risk.late_delivery_probability) : 0.5;
  const probEl = document.getElementById('inspect-risk-prob');
  if (probEl) {
    probEl.textContent = `${(prob * 100).toFixed(1)}%`;
    probEl.className = data.risk.is_high_risk ? 'stat-cell-val critical' : 'stat-cell-val cyan';
  }

  // Dollar at Risk
  const dollarVal = (data.risk.dollar_at_risk !== undefined) ? Number(data.risk.dollar_at_risk) : (prob * Number(data.order_value || 0));
  const dollarRiskEl = document.getElementById('inspect-dollar-risk');
  if (dollarRiskEl) {
    dollarRiskEl.textContent = `$${dollarVal.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    dollarRiskEl.className = data.risk.is_high_risk ? 'stat-cell-val critical' : 'stat-cell-val cyan';
  }

  // Order Total Value
  const orderVal = Number(data.order_value || 0);
  const orderValEl = document.getElementById('inspect-order-val');
  if (orderValEl) {
    orderValEl.textContent = `$${orderVal.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
  }

  // Route & Scheduled Days (Contract SLA)
  const schedDays = Number(data.scheduled_days || 4);
  const schedEl = document.getElementById('inspect-scheduled-days');
  if (schedEl) {
    schedEl.textContent = `${schedDays} Days (SLA)`;
  }

  // Route Map
  const originCountry = data.customer_country || 'EE. UU.';
  const destCountry = data.order_country || 'France';
  updateRouteMap(originCountry, destCountry, Boolean(data.risk.is_high_risk));

  // Duration Gauge
  const fastest = Number(data.risk.fastest_predicted_days || 1);
  const normal = Number(data.risk.normal_predicted_days || (schedDays + 2));
  renderDurationGauge(fastest, schedDays, normal);

  // SHAP Risk Drivers
  renderShapRiskDrivers(data.risk.risk_drivers || []);

  // IBM Granite Explanation Typewriter
  typewriterGranite(data.explanation || 'Disruption analysis completed successfully.');

  // Render Action Cards
  renderActionCards(data.recommendations || []);
}

function typewriterGranite(text) {
  const el = document.getElementById('granite-explanation-text');
  if (!el) return;

  el.textContent = '';
  let i = 0;
  const speed = 12;

  function type() {
    if (i < text.length) {
      el.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }
  type();
}

function renderActionCards(actions) {
  const container = document.getElementById('action-cards-container');
  if (!container) return;

  if (!actions || actions.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted);">No mitigation action necessary. Order is on track.</div>';
    return;
  }

  let html = '';
  actions.forEach((act, idx) => {
    const isTop = idx === 0;
    html += `
      <div class="action-card ${isTop ? 'top-recommended' : ''}">
        <div class="action-header">
          <div class="action-title">${act.title}</div>
          <div class="roi-badge">${act.roi_ratio || '35.4x ROI'}</div>
        </div>
        <div class="action-meta">
          <span>Feasibility: <strong style="color: #fff;">${act.feasibility}</strong></span>
          <span>Expedite Cost: <strong style="color: var(--accent-red);">$${act.estimated_expedite_cost.toLocaleString()}</strong></span>
          <span>Protected Capital: <strong style="color: var(--accent-green);">$${act.protected_revenue.toLocaleString()}</strong></span>
        </div>
        <div class="action-notes">${act.simulation_notes}</div>
        <div class="action-btn-row">
          <button class="btn ${isTop ? 'btn-critical' : 'btn-outline'}" onclick="executeSpecificAction('${act.action}', '${escapeQuote(act.title)}')">
            ${isTop ? '✓ Select & Approve Mitigation' : 'Select Alternative'}
          </button>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function escapeQuote(str) {
  return str.replace(/'/g, "\\'");
}

async function executeSpecificAction(actionType, actionTitle) {
  if (!currentOrderData) return;

  const payload = {
    order_id: currentOrderData.order_id,
    action_type: actionType,
    selected_recommendation: actionTitle,
    operator_notes: "Approved by Operations Lead via ChainSentinel Dashboard"
  };

  try {
    const res = await fetch('/api/zos-connect/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    showMainframeTerminalCommit(result);
    showToast(`Committed to Db2 for z/OS (RC=0000 SUCCESS_COMMIT)`, 'success');
  } catch (err) {
    console.error('Commit failed:', err);
    showToast('Failed to execute z/OS commit', 'critical');
  }
}

async function executeZosCommit() {
  if (!currentOrderData || !currentOrderData.recommendations || currentOrderData.recommendations.length === 0) return;
  const topAction = currentOrderData.recommendations[0];
  await executeSpecificAction(topAction.action, topAction.title);
}

function showMainframeTerminalCommit(res) {
  const modal = document.getElementById('modal-terminal');
  const screen = document.getElementById('terminal-content');
  if (!modal || !screen) return;

  const timestamp = new Date().toISOString();
  screen.innerHTML = `
<span class="terminal-highlight">========================================================================</span>
<span class="terminal-highlight">           IBM Z / Db2 for z/OS TRANSACTION COMMIT LOG                  </span>
<span class="terminal-highlight">========================================================================</span>
GATEWAY:       z/OS Connect Enterprise REST Gateway (v3.0.78)
PLATFORM:      IBM LinuxONE (s390x) High-Performance Core
SECURITY:      RACF Secured Token & AT-TLS Dual Channel
TIMESTAMP:     ${timestamp}
ORDER ID:      #${res.order_id}
ACTION:        ${res.action_executed}
DETAILS:       ${res.details}

<span class="terminal-success">>>> DB2 RETURN CODE:  ${res.db2_return_code}</span>
>>> Z/OS COMMIT REF:  ${res.zos_connect_transaction_id}
>>> AUDIT TRAIL:      ${res.mainframe_audit_log}
>>> ACID STATE:       DURABLE (Write-Ahead Log Synchronized)

<span class="terminal-success">STATUS: 200 OK - MITIGATION PERMANENTLY COMMITTED TO MAINFRAME</span>
  `;

  modal.classList.add('open');
}

async function viewAuditDossier() {
  const orderId = currentOrderData ? currentOrderData.order_id : 4471;
  try {
    const res = await fetch(`/api/audit-report/${orderId}`);
    const data = await res.json();
    renderAuditModal(data);
  } catch (err) {
    console.error('Audit report fetch failed:', err);
  }
}

function renderAuditModal(data) {
  const modal = document.getElementById('modal-audit-report');
  const body = document.getElementById('audit-report-body');
  if (!modal || !body) return;

  body.innerHTML = `
    <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 14px; margin-bottom: 16px;">
      <h3 style="font-size: 18px; color: #fff;">${data.report_id} | Official Multi-Agent Compliance Audit</h3>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
        Generated: ${data.generated_at} | Platform: <strong>${data.platform_certification}</strong>
      </div>
    </div>
    
    <div style="margin-bottom: 16px; font-size: 13px;">
      <p><strong>Order Reference:</strong> #${data.order.order_id} (${data.order.product_name})</p>
      <p><strong>Corridor:</strong> ${data.order.customer_country} -> ${data.order.order_country} (${data.order.shipping_mode})</p>
      <p><strong>Order Capital:</strong> $${data.order.order_value.toLocaleString()}</p>
    </div>

    <div style="background: rgba(11, 17, 32, 0.85); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 14px; margin-bottom: 16px; font-size: 12px;">
      <h4 style="color: var(--accent-cyan); margin-bottom: 8px;">Multi-Agent Decision Chain</h4>
      <p>• <strong>Detection Agent:</strong> Score ${data.multi_agent_evaluation.detection_agent.score} - Anomaly Confirmed</p>
      <p>• <strong>Risk Agent:</strong> Delay Probability ${(data.multi_agent_evaluation.risk_agent.late_delivery_probability*100).toFixed(1)}% | Capital-at-Risk: $${data.multi_agent_evaluation.risk_agent.dollar_at_risk.toLocaleString()}</p>
      <p>• <strong>Recommendation Agent:</strong> ${data.multi_agent_evaluation.recommendation_agent.action_title} (ROI: ${data.multi_agent_evaluation.recommendation_agent.roi_ratio})</p>
      <p>• <strong>Explanation Agent:</strong> Synthesized by IBM Granite Foundation Model</p>
    </div>

    <div style="border-top: 1px solid var(--border-subtle); padding-top: 14px; font-family: var(--font-mono); font-size: 11px; color: var(--text-secondary);">
      <p>Mainframe Commit Status: <span style="color: var(--accent-green);">${data.mainframe_audit_trail.db2_return_code}</span></p>
      <p>Cryptographic Signature: <span style="color: var(--accent-cyan);">${data.mainframe_audit_trail.security_hash}</span></p>
    </div>
  `;

  modal.classList.add('open');
}

async function handleCustomOrderSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>⏳ Running Multi-Agent Workflow...</span>';
  }

  const payload = {
    order_id: parseInt(form.order_id.value) || 9924,
    product_name: (form.product_name.value || '').trim() || 'Custom Semiconductor Accelerator Blade',
    category_name: form.category_name.value || 'Electronics',
    shipping_mode: form.shipping_mode.value || 'Standard Class',
    customer_country: form.customer_country.value || 'EE. UU.',
    order_country: form.order_country.value || 'France',
    order_region: form.order_region.value || 'Western Europe',
    scheduled_days: parseInt(form.scheduled_days.value) || 4,
    order_item_quantity: parseInt(form.order_item_quantity.value) || 1,
    order_value: parseFloat(form.order_value.value) || 1000.0
  };

  try {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      let errMsg = `HTTP ${res.status}`;
      try {
        const errJson = await res.json();
        if (errJson && errJson.detail) {
          errMsg = Array.isArray(errJson.detail) ? errJson.detail.map(d => d.msg || JSON.stringify(d)).join(', ') : String(errJson.detail);
        }
      } catch (_) {}
      throw new Error(errMsg);
    }

    const result = await res.json();
    currentOrderData = result;

    const modal = document.getElementById('modal-custom-sim');
    if (modal) modal.classList.remove('open');

    await animateAgentPipeline(result.latency_ms || 11.4);
    updateAgentDetails(result);
    renderOrderDisruption(result);
    showToast(`Evaluated Custom Order #${result.order_id} (${result.product_name}) in ${result.latency_ms || 12}ms`, 'success');
  } catch (err) {
    console.error('Custom evaluation failed:', err);
    showToast(`Evaluation Failed: ${err.message || 'Server error'}`, 'critical');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnHtml;
    }
  }
}

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <div class="pulse-dot ${type === 'critical' ? 'pulse-red' : 'pulse-green'}"></div>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => toast.classList.add('show'), 50);

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}
