/**
 * ChainSentinel Visualizations: Map, Gauges, SHAP Feature Attribution
 */

let mapInstance = null;
let routeLine = null;
let originMarker = null;
let destMarker = null;

// Coordinates for key fulfillment nodes
const COORDINATES = {
  "EE. UU.": [37.7749, -122.4194],
  "United States": [38.9072, -77.0369],
  "Puerto Rico": [18.2208, -66.5901],
  "Canada": [45.4215, -75.6972],
  "Mexico": [19.4326, -99.1332],
  "France": [48.8566, 2.3522],
  "Germany": [50.1109, 8.6821],
  "United Kingdom": [51.5074, -0.1278],
  "Japan": [35.6762, 139.6503],
  "India": [28.6139, 77.2090],
  "Australia": [-33.8688, 151.2093]
};

function initRouteMap() {
  const mapElement = document.getElementById('leaflet-map');
  if (!mapElement || typeof L === 'undefined') return;

  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
  }

  // Dark Map Tiles
  mapInstance = L.map('leaflet-map', {
    center: [30, 0],
    zoom: 2,
    zoomControl: false,
    attributionControl: false
  });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 18,
    subdomains: 'abcd'
  }).addTo(mapInstance);

  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
}

function updateRouteMap(originCountry, destCountry, isDisrupted = true) {
  if (!mapInstance || typeof L === 'undefined') return;

  const originCoords = COORDINATES[originCountry] || [37.7749, -122.4194];
  const destCoords = COORDINATES[destCountry] || [48.8566, 2.3522];

  if (routeLine) mapInstance.removeLayer(routeLine);
  if (originMarker) mapInstance.removeLayer(originMarker);
  if (destMarker) mapInstance.removeLayer(destMarker);

  const routeColor = isDisrupted ? '#f43f5e' : '#10b981';

  // Origin Icon
  const originIcon = L.divIcon({
    className: 'custom-map-pin',
    html: `<div style="width: 14px; height: 14px; background: #00d8ff; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 0 12px #00d8ff;"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7]
  });

  // Destination Icon
  const destIcon = L.divIcon({
    className: 'custom-map-pin',
    html: `<div style="width: 16px; height: 16px; background: ${routeColor}; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 0 15px ${routeColor};" class="pulse-red"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  });

  originMarker = L.marker(originCoords, { icon: originIcon }).addTo(mapInstance)
    .bindPopup(`<b>Origin Hub:</b> ${originCountry}`);

  destMarker = L.marker(destCoords, { icon: destIcon }).addTo(mapInstance)
    .bindPopup(`<b>Destination:</b> ${destCountry} (${isDisrupted ? 'CRITICAL DISRUPTION' : 'NORMAL'})`);

  // Curved Route Line
  const latlngs = [originCoords, destCoords];
  routeLine = L.polyline(latlngs, {
    color: routeColor,
    weight: 3,
    opacity: 0.85,
    dashArray: isDisrupted ? '6, 8' : null
  }).addTo(mapInstance);

  mapInstance.fitBounds(L.latLngBounds([originCoords, destCoords]).pad(0.35));
}

function renderShapRiskDrivers(drivers) {
  const container = document.getElementById('shap-drivers-list');
  if (!container) return;

  if (!drivers || drivers.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted); font-size: 12px;">No active risk drivers flagged.</div>';
    return;
  }

  let html = '';
  drivers.forEach(d => {
    const isIncrease = d.direction === 'INCREASES_RISK';
    const fillClass = isIncrease ? 'increase' : 'reduce';
    const sign = isIncrease ? '+' : '-';
    const color = isIncrease ? 'var(--accent-red)' : 'var(--accent-green)';

    html += `
      <div class="driver-bar-item" title="${d.description || ''}">
        <div class="driver-info">
          <span style="font-weight: 500;">${d.feature}</span>
          <span class="mono" style="color: ${color}; font-weight: 700;">${sign}${d.impact_pct.toFixed(1)}%</span>
        </div>
        <div class="driver-bar-track">
          <div class="driver-bar-fill ${fillClass}" style="width: ${Math.min(100, d.impact_pct * 2.5)}%;"></div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function renderDurationGauge(fastestDays, scheduledDays, normalDays) {
  const container = document.getElementById('duration-gauge-box');
  if (!container) return;

  const maxDays = Math.max(7, normalDays + 1);
  const fastestPct = Math.round((fastestDays / maxDays) * 100);
  const scheduledPct = Math.round((scheduledDays / maxDays) * 100);
  const normalPct = Math.round((normalDays / maxDays) * 100);

  container.innerHTML = `
    <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px; display: flex; justify-content: space-between;">
      <span>Fastest Expedited: <strong style="color: var(--accent-cyan);">${fastestDays}d</strong></span>
      <span>Contractual SLA: <strong style="color: #fff;">${scheduledDays}d</strong></span>
      <span>Standard Predicted: <strong style="color: var(--accent-red);">${normalDays}d</strong></span>
    </div>
    <div style="position: relative; height: 10px; background: rgba(255, 255, 255, 0.08); border-radius: 999px; overflow: hidden; margin-bottom: 6px;">
      <div style="position: absolute; left: 0; top: 0; bottom: 0; width: ${fastestPct}%; background: var(--accent-cyan); opacity: 0.9;"></div>
      <div style="position: absolute; left: 0; top: 0; bottom: 0; width: ${normalPct}%; background: var(--accent-red); opacity: 0.45;"></div>
      <div style="position: absolute; left: ${scheduledPct}%; top: -2px; bottom: -2px; width: 3px; background: #fff; box-shadow: 0 0 8px #fff; z-index: 5;" title="SLA: ${scheduledDays}d"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 10px; color: var(--text-muted);">
      <span>0d</span>
      <span>Air Courier Velocity</span>
      <span>SLA Breach (+${Math.max(0, normalDays - scheduledDays)}d)</span>
    </div>
  `;
}
