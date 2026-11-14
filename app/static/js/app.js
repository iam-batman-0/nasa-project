/**
 * Main Flight Deck Application Script.
 * Orchestrates WebSockets, Chart.js telemetry visualization,
 * crew profile management, and autonomous countermeasure execution.
 */

window.selectedAstronautId = "ASTRO-01";
let cardioChart = null;
let bmdChart = null;
let radChart = null;
let audioEnabled = true;
let socket = null;
let activePlan = null;
let crewList = [];

// Mission Clock Ticker
setInterval(() => {
  const now = new Date();
  const timeStr = now.toTimeString().split(' ')[0];
  const clockEl = document.getElementById('mission-clock');
  if (clockEl) clockEl.innerText = `DAY 184 ${timeStr}`;
}, 1000);

// Tab Switching
function switchTab(tabId) {
  const views = ['dashboard', 'diagnostics', 'countermeasures', 'biomarkers', 'simulator'];
  views.forEach(v => {
    const el = document.getElementById(`view-${v}`);
    const tab = document.getElementById(`tab-${v}`);
    if (el) el.classList.toggle('hidden', v !== tabId);
    if (tab) {
      if (v === tabId) {
        tab.classList.add('active', 'text-space-cyan');
        tab.classList.remove('text-slate-400');
      } else {
        tab.classList.remove('active', 'text-space-cyan');
        tab.classList.add('text-slate-400');
      }
    }
  });

  if (tabId === 'diagnostics') {
    setTimeout(() => { if (typeof initAmslerGrid === 'function') initAmslerGrid(); }, 100);
  } else if (tabId === 'biomarkers') {
    setTimeout(renderHistoricalCharts, 100);
  }
}

// Web Audio API Chimes (No external sound files required)
function playChime(type = 'alert') {
  if (!audioEnabled) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    if (type === 'critical') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      osc.frequency.setValueAtTime(440, ctx.currentTime + 0.15);
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
      osc.start();
      osc.stop(ctx.currentTime + 0.4);
    } else {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.setValueAtTime(880, ctx.currentTime + 0.08); // A5
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
      osc.start();
      osc.stop(ctx.currentTime + 0.3);
    }
  } catch (e) {
    // AudioContext might require user gesture first
  }
}

function toggleAudioAlerts() {
  audioEnabled = !audioEnabled;
  const icon = document.getElementById('audio-icon');
  if (icon) {
    icon.setAttribute('data-lucide', audioEnabled ? 'volume-2' : 'volume-x');
    lucide.createIcons();
  }
}

// Initialize Charts
function initCharts() {
  const ctx = document.getElementById('cardio-chart').getContext('2d');
  
  const initialLabels = Array.from({ length: 25 }, (_, i) => `-${25 - i}s`);
  const initialHR = Array.from({ length: 25 }, () => 68);
  const initialHRV = Array.from({ length: 25 }, () => 48);

  cardioChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: initialLabels,
      datasets: [
        {
          label: 'Heart Rate (BPM)',
          data: initialHR,
          borderColor: '#00e5ff',
          backgroundColor: 'rgba(0, 229, 255, 0.08)',
          fill: true,
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 0,
          yAxisID: 'y'
        },
        {
          label: 'HRV RMSSD (ms)',
          data: initialHRV,
          borderColor: '#00f5a0',
          backgroundColor: 'transparent',
          tension: 0.35,
          borderWidth: 2,
          borderDash: [4, 4],
          pointRadius: 0,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#64748b', font: { family: 'monospace', size: 10 } }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          min: 40,
          max: 130,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#00e5ff', font: { family: 'monospace', size: 10 } },
          title: { display: true, text: 'BPM', color: '#00e5ff', font: { size: 10 } }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          min: 10,
          max: 90,
          grid: { drawOnChartArea: false },
          ticks: { color: '#00f5a0', font: { family: 'monospace', size: 10 } },
          title: { display: true, text: 'RMSSD (ms)', color: '#00f5a0', font: { size: 10 } }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#94a3b8', font: { family: 'monospace', size: 11 } }
        }
      }
    }
  });
}

function renderHistoricalCharts() {
  // BMD Loss Trajectory Chart
  const bmdEl = document.getElementById('bmd-chart');
  if (bmdEl && !bmdChart) {
    const ctx = bmdEl.getContext('2d');
    bmdChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Day 0', 'Day 30', 'Day 60', 'Day 90', 'Day 120', 'Day 150', 'Day 184 (Now)', 'Day 210 (Proj)', 'Day 240 (Proj)'],
        datasets: [
          {
            label: 'Actual / Proj with ARED Protocol',
            data: [0.6, 0.58, 0.55, 0.51, 0.47, 0.43, 0.40, 0.37, 0.34],
            borderColor: '#00f5a0',
            backgroundColor: 'rgba(0, 245, 160, 0.1)',
            fill: true,
            borderWidth: 2,
            tension: 0.3
          },
          {
            label: 'Unmitigated Microgravity Loss (-1.2%/mo)',
            data: [0.6, 0.48, 0.35, 0.21, 0.06, -0.09, -0.25, -0.40, -0.55],
            borderColor: '#ff3366',
            borderDash: [5, 5],
            borderWidth: 2,
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: '#64748b', font: { size: 10 } } },
          y: {
            title: { display: true, text: 'BMD T-Score', color: '#94a3b8' },
            ticks: { color: '#94a3b8', font: { size: 10 } }
          }
        },
        plugins: {
          legend: { labels: { color: '#cbd5e1', font: { size: 11 } } }
        }
      }
    });
  }

  // Cumulative Radiation vs Career Limit Chart
  const radEl = document.getElementById('radiation-chart');
  if (radEl && !radChart) {
    const ctx = radEl.getContext('2d');
    radChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Dr. Vance', 'Alexei', 'Maya Lin', 'Marcus', 'Career Limit'],
        datasets: [{
          label: 'Cumulative Radiation (mSv)',
          data: [142.5, 148.0, 136.2, 155.8, 600.0],
          backgroundColor: [
            'rgba(0, 229, 255, 0.6)',
            'rgba(0, 229, 255, 0.6)',
            'rgba(0, 229, 255, 0.6)',
            'rgba(0, 229, 255, 0.6)',
            'rgba(255, 51, 102, 0.7)'
          ],
          borderColor: [
            '#00e5ff',
            '#00e5ff',
            '#00e5ff',
            '#00e5ff',
            '#ff3366'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: '#94a3b8', font: { size: 11 } } },
          y: {
            max: 700,
            title: { display: true, text: 'mSv', color: '#94a3b8' },
            ticks: { color: '#94a3b8', font: { size: 10 } }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

// Fetch Initial Crew List
function fetchCrew() {
  fetch('/api/crew')
    .then(r => r.json())
    .then(data => {
      crewList = data;
      renderCrewCards();
      selectAstronaut(window.selectedAstronautId);
    });
}

function renderCrewCards() {
  const container = document.getElementById('crew-cards-container');
  if (!container) return;

  container.innerHTML = crewList.map(a => {
    const isSelected = a.id === window.selectedAstronautId;
    let badgeColor = "bg-emerald-950 text-emerald-400 border-emerald-500/30";
    if (a.health_status === "CAUTION") badgeColor = "bg-amber-950 text-amber-400 border-amber-500/30";
    if (a.health_status === "CRITICAL") badgeColor = "bg-red-950 text-red-400 border-red-500/30";

    return `
      <div onclick="selectAstronaut('${a.id}')" class="cursor-pointer bg-space-900 border ${isSelected ? 'border-space-cyan ring-1 ring-space-cyan/50 shadow-lg shadow-space-cyan/10' : 'border-space-800 hover:border-space-700'} rounded-xl p-3 transition-all">
        <div class="flex items-start justify-between">
          <div>
            <h4 class="font-bold text-sm text-white">${a.name}</h4>
            <span class="text-[11px] text-slate-400 font-mono">${a.callsign} • ${a.role}</span>
          </div>
          <span class="text-[10px] font-mono px-1.5 py-0.5 rounded border ${badgeColor}">${a.health_status}</span>
        </div>
        <div class="mt-3 flex items-center justify-between text-xs font-mono">
          <span class="text-slate-400">SCORE: <b class="text-white">${a.overall_health_score}</b></span>
          <span class="text-slate-400">RAD: <b class="text-slate-300">${a.career_radiation_msv} mSv</b></span>
          <span class="text-slate-400">BMD T: <b class="text-slate-300">${a.current_bmd_t_score}</b></span>
        </div>
      </div>
    `;
  }).join('');
}

function selectAstronaut(astroId) {
  window.selectedAstronautId = astroId;
  renderCrewCards();
  loadAstronautEvaluation(astroId);
  loadCountermeasures(astroId);
}

// Load Evaluation from Backend
function loadAstronautEvaluation(astroId) {
  fetch(`/api/evaluate/${astroId}`)
    .then(r => r.json())
    .then(data => {
      updateEvaluationHUD(data);
    });
}

function updateEvaluationHUD(evalData) {
  const badge = document.getElementById('overall-health-badge');
  if (badge) {
    badge.innerText = evalData.overall_health_score;
    if (evalData.status === 'NOMINAL') {
      badge.className = 'font-mono text-2xl font-black text-space-emerald';
    } else if (evalData.status === 'CAUTION') {
      badge.className = 'font-mono text-2xl font-black text-amber-400';
    } else {
      badge.className = 'font-mono text-2xl font-black text-rose-500 animate-pulse';
    }
  }

  // Render 5-Hazard Bars
  const barsContainer = document.getElementById('hazard-bars-container');
  if (barsContainer && evalData.hazard_scores) {
    const hazards = [
      { key: 'radiation', label: 'Radiation Risk Envelope', icon: 'shield-alert' },
      { key: 'cardiovascular', label: 'Cardiovascular / Orthostatic', icon: 'heart-pulse' },
      { key: 'musculoskeletal', label: 'Musculoskeletal & Bone Loss', icon: 'bone' },
      { key: 'sans_ocular', label: 'SANS Neuro-Ocular Decongestion', icon: 'eye' },
      { key: 'cognitive_behavioral', label: 'Cognitive & Behavioral Health', icon: 'brain' },
      { key: 'cabin_environment', label: 'Closed Cabin Atmosphere', icon: 'wind' },
    ];

    barsContainer.innerHTML = hazards.map(h => {
      const score = evalData.hazard_scores[h.key] || 90;
      let barColor = 'bg-space-emerald';
      if (score < 60) barColor = 'bg-rose-500';
      else if (score < 80) barColor = 'bg-amber-400';

      return `
        <div>
          <div class="flex justify-between text-xs mb-1 font-mono">
            <span class="text-slate-300">${h.label}</span>
            <span class="font-bold text-white">${score}%</span>
          </div>
          <div class="w-full bg-space-850 h-2 rounded-full overflow-hidden">
            <div class="${barColor} h-full hazard-bar-fill rounded-full" style="width: ${score}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Clinical findings list
  const findingsList = document.getElementById('clinical-findings-list');
  if (findingsList) {
    if (evalData.findings && evalData.findings.length > 0) {
      findingsList.innerHTML = evalData.findings.map(f => `
        <li class="text-slate-300">• ${f}</li>
      `).join('');
    } else {
      findingsList.innerHTML = `<li class="text-emerald-400">• All biometrics tracking within nominal spaceflight baseline.</li>`;
    }
  }

  // Alerts Banner
  const alertBanner = document.getElementById('critical-alert-banner');
  if (evalData.alerts && evalData.alerts.length > 0) {
    const alert = evalData.alerts[0];
    document.getElementById('alert-title').innerText = `${alert.type}: ${alert.hazard} HAZARD`;
    document.getElementById('alert-desc').innerText = alert.message;
    alertBanner.classList.remove('hidden');
    if (alert.type === 'CRITICAL') playChime('critical');
  } else {
    alertBanner.classList.add('hidden');
  }
}

// Countermeasures Management
function loadCountermeasures(astroId) {
  fetch(`/api/countermeasures/${astroId}`)
    .then(r => r.json())
    .then(plan => {
      activePlan = plan;
      renderCountermeasures(plan);
    });
}

function renderCountermeasures(plan) {
  if (!plan) return;

  const nameEl = document.getElementById('plan-astro-name');
  if (nameEl) {
    const astro = crewList.find(a => a.id === plan.astronaut_id);
    nameEl.innerText = astro ? astro.name : plan.astronaut_id;
  }

  const badgeEl = document.getElementById('plan-severity-badge');
  if (badgeEl) {
    badgeEl.innerText = `${plan.severity_level} PROTOCOL`;
    if (plan.severity_level === 'CRITICAL') {
      badgeEl.className = 'px-2 py-0.5 rounded text-xs font-mono bg-red-950 text-red-400 border border-red-500/30';
    } else if (plan.severity_level === 'CAUTION') {
      badgeEl.className = 'px-2 py-0.5 rounded text-xs font-mono bg-amber-950 text-amber-400 border border-amber-500/30';
    } else {
      badgeEl.className = 'px-2 py-0.5 rounded text-xs font-mono bg-emerald-950 text-emerald-400 border border-emerald-500/30';
    }
  }

  const summaryEl = document.getElementById('plan-summary-text');
  if (summaryEl) summaryEl.innerText = plan.summary;

  const countBadge = document.getElementById('badge-actions-count');
  if (countBadge) countBadge.innerText = plan.action_items.filter(a => !a.is_completed).length;

  const container = document.getElementById('action-items-container');
  if (!container) return;

  container.innerHTML = plan.action_items.map(item => {
    let priColor = 'bg-blue-950 text-blue-400 border-blue-500/30';
    if (item.priority === 'EMERGENCY') priColor = 'bg-red-950 text-red-400 border-red-500/30 animate-pulse';
    else if (item.priority === 'URGENT') priColor = 'bg-amber-950 text-amber-400 border-amber-500/30';

    return `
      <div class="bg-space-900 border ${item.is_completed ? 'border-emerald-500/30 bg-emerald-950/10' : 'border-space-800'} rounded-xl p-4 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between text-[11px] font-mono">
            <span class="px-2 py-0.5 rounded border ${priColor}">${item.priority}</span>
            <span class="text-slate-400">${item.category} • ${item.duration_minutes} MIN</span>
          </div>
          <h4 class="font-bold text-sm text-white mt-2 ${item.is_completed ? 'line-through text-slate-400' : ''}">${item.title}</h4>
          <p class="text-xs text-slate-300/90 mt-1">${item.description}</p>
          <div class="mt-2 text-[11px] font-mono text-space-cyan">
            DOSAGE/INTENSITY: ${item.dosage_or_intensity}
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-space-800 flex items-center justify-between">
          <span class="text-xs text-slate-400 font-mono">${item.is_completed ? 'COMPLETED' : 'STATUS: PENDING'}</span>
          <button onclick="toggleActionItem('${item.id}')" class="px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition ${item.is_completed ? 'bg-space-850 text-slate-400 hover:text-white' : 'bg-space-cyan hover:bg-cyan-300 text-space-950 shadow'}">
            ${item.is_completed ? 'RE-OPEN' : 'MARK EXECUTED'}
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function toggleActionItem(itemId) {
  if (!activePlan) return;
  const item = activePlan.action_items.find(a => a.id === itemId);
  if (item) {
    item.is_completed = !item.is_completed;
    item.completed_at = item.is_completed ? Date.now() / 1000 : null;
    playChime(item.is_completed ? 'nominal' : 'alert');
    renderCountermeasures(activePlan);
  }
}

function regenerateCountermeasures() {
  loadCountermeasures(window.selectedAstronautId);
  playChime('nominal');
}

// Biomarker Submissions
function submitBiomarkers(e) {
  e.preventDefault();
  if (!window.selectedAstronautId) return;

  const hydration = parseFloat(document.getElementById('input-hydration').value);
  const ntx = parseFloat(document.getElementById('input-ntx').value);
  const sleep = parseFloat(document.getElementById('input-sleep').value);
  const soreness = parseInt(document.getElementById('input-soreness').value, 10);

  fetch('/api/assessment/biomarkers', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      astronaut_id: window.selectedAstronautId,
      urine_specific_gravity: hydration,
      urinary_ntx_nmol_bce_mmol_cr: ntx,
      sleep_hours: sleep,
      muscle_soreness_rating: soreness,
      sleep_quality_score: Math.min(100, Math.round(sleep * 12))
    })
  })
  .then(r => r.json())
  .then(() => {
    alert('Biomarker and bone resorption lab record successfully logged!');
    loadAstronautEvaluation(window.selectedAstronautId);
  });
}

// Crisis Injection
function triggerCrisis(scenarioName) {
  fetch('/api/simulator/scenario', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario: scenarioName })
  })
  .then(r => r.json())
  .then(res => {
    alert(`MISSION EVENT APPLIED: ${scenarioName}. Autonomous decision engine actively processing telemetry...`);
    switchTab('dashboard');
    refreshActiveData();
  });
}

// Telemetry Streaming (Polling / WebSocket)
function connectTelemetryStream() {
  // We use reliable 1.5s interval polling which works seamlessly in all sandboxes/browsers
  setInterval(() => {
    fetch('/api/telemetry/snapshot')
      .then(r => r.json())
      .then(snapshot => {
        updateTelemetryHUD(snapshot);
      })
      .catch(() => {});
  }, 1500);
}

function updateTelemetryHUD(snapshot) {
  // Update Environmental HUD
  const env = snapshot.environment;
  if (env) {
    document.getElementById('env-co2').innerText = env.cabin_co2_mmhg.toFixed(2);
    document.getElementById('env-rad-rate').innerText = env.radiation_dose_rate_ugy_hr.toFixed(1);
    document.getElementById('env-cum-dose').innerText = env.cumulative_mission_dose_msv.toFixed(2);
    document.getElementById('env-pressure').innerText = env.cabin_pressure_psi.toFixed(2);
    document.getElementById('env-temp').innerText = `${env.cabin_temp_celsius}°C / ${env.cabin_o2_percent}%`;
    document.getElementById('env-noise').innerText = env.acoustic_noise_db.toFixed(1);

    const co2Status = document.getElementById('env-co2-status');
    if (env.cabin_co2_mmhg > 3.5) {
      co2Status.innerText = 'HIGH (>3.5 mmHg)';
      co2Status.className = 'inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-red-950 text-red-400 font-mono animate-pulse';
    } else {
      co2Status.innerText = 'NOMINAL (<3.5)';
      co2Status.className = 'inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono';
    }

    const radStatus = document.getElementById('env-rad-status');
    if (env.radiation_storm_active) {
      radStatus.innerText = 'SOLAR STORM ALERT';
      radStatus.className = 'inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-red-950 text-red-400 font-mono animate-pulse';
    } else {
      radStatus.innerText = 'GCR BACKGROUND';
      radStatus.className = 'inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono';
    }
  }

  // Update selected astronaut live vitals
  const vitals = snapshot.crew_vitals[window.selectedAstronautId];
  if (vitals) {
    document.getElementById('detail-hr').innerText = Math.round(vitals.heart_rate_bpm);
    document.getElementById('detail-hrv').innerText = Math.round(vitals.hrv_rmssd_ms);
    document.getElementById('detail-stress').innerText = Math.round(vitals.stress_index);
    document.getElementById('detail-bp').innerText = `${Math.round(vitals.systolic_bp_mmhg)}/${Math.round(vitals.diastolic_bp_mmhg)}`;
    document.getElementById('detail-spo2').innerText = vitals.spo2_percent.toFixed(1);
    document.getElementById('detail-resp').innerText = vitals.respiration_rate_bpm.toFixed(1);
    document.getElementById('detail-temp').innerText = vitals.core_temp_celsius.toFixed(1);

    // Push into Chart.js
    if (cardioChart) {
      cardioChart.data.datasets[0].data.shift();
      cardioChart.data.datasets[0].data.push(vitals.heart_rate_bpm);
      cardioChart.data.datasets[1].data.shift();
      cardioChart.data.datasets[1].data.push(vitals.hrv_rmssd_ms);
      cardioChart.update('none');
    }
  }
}

window.refreshActiveData = function() {
  fetchCrew();
  loadAstronautEvaluation(window.selectedAstronautId);
  loadCountermeasures(window.selectedAstronautId);
};

// Application Startup
window.addEventListener('DOMContentLoaded', () => {
  initCharts();
  fetchCrew();
  connectTelemetryStream();
  // Poll evaluations periodically
  setInterval(() => {
    if (window.selectedAstronautId) {
      loadAstronautEvaluation(window.selectedAstronautId);
    }
  }, 4000);
});
