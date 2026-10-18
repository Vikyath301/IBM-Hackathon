/**
 * ChainSentinel Multi-Agent Visualizer & Node State Controller
 */

const AGENT_NODES = [
  { id: 'node-detection', name: 'Detection Agent', role: 'Anomaly Triage', latency: '2.1ms' },
  { id: 'node-risk', name: 'Risk Agent', role: 'XGBoost & Duration ML', latency: '3.4ms' },
  { id: 'node-recommendation', name: 'Recommendation Agent', role: 'Pareto Action Ranking', latency: '2.8ms' },
  { id: 'node-explanation', name: 'Explanation Agent', role: 'IBM Granite Synthesis', latency: '2.9ms' },
  { id: 'node-commit', name: 'z/OS Connect Commit', role: 'Db2 ACID Protocol', latency: '1.2ms' }
];

async function animateAgentPipeline(totalLatencyMs = 11.4) {
  const nodes = document.querySelectorAll('.agent-node');
  
  // Reset all
  nodes.forEach(n => {
    n.classList.remove('active-stage', 'active-critical', 'node-animating');
  });

  // Step through nodes sequentially
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    node.classList.add('node-animating', 'active-stage');
    
    // Quick micro-pause to show execution step
    await new Promise(r => setTimeout(r, 60));
    node.classList.remove('node-animating');
  }

  // Final highlight for critical state if alert
  const riskNode = document.getElementById('node-risk');
  if (riskNode) {
    riskNode.classList.add('active-stage');
  }
}

function updateAgentDetails(data) {
  // Detection Agent Node
  const detectionStatus = document.getElementById('det-agent-status');
  if (detectionStatus && data.detection) {
    detectionStatus.textContent = data.detection.is_anomaly ? 'ANOMALY DETECTED' : 'NORMAL';
    detectionStatus.style.color = data.detection.is_anomaly ? 'var(--accent-red)' : 'var(--accent-green)';
  }

  // Risk Agent Node
  const riskStatus = document.getElementById('risk-agent-status');
  if (riskStatus && data.risk) {
    riskStatus.textContent = `${(data.risk.late_delivery_probability * 100).toFixed(1)}% (${data.risk.alert_level})`;
    riskStatus.style.color = data.risk.is_high_risk ? 'var(--accent-red)' : 'var(--accent-green)';
  }

  // Overall Latency
  const latencyBadge = document.getElementById('pipeline-latency-val');
  if (latencyBadge && data.latency_ms) {
    latencyBadge.textContent = `${data.latency_ms} ms`;
  }
}
