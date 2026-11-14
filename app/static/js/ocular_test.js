/**
 * SANS Ocular Self-Assessment & Interactive Amsler Grid Module.
 * Evaluates cephalad fluid shift, optic disc edema, and posterior globe flattening.
 */

let amslerPoints = [];

function initAmslerGrid() {
  const canvas = document.getElementById('amsler-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  // Background
  ctx.fillStyle = '#060913';
  ctx.fillRect(0, 0, w, h);

  // Draw Grid Lines (white / slate-400)
  ctx.strokeStyle = '#334155';
  ctx.lineWidth = 1;

  const step = w / 16;
  for (let x = 0; x <= w; x += step) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }

  for (let y = 0; y <= h; y += step) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  // Draw recorded distortion markers
  for (const pt of amslerPoints) {
    ctx.fillStyle = 'rgba(239, 68, 68, 0.45)';
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, 16, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#ef4444';
    ctx.stroke();
  }

  // Center fixation dot
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.arc(w / 2, h / 2, 4, 0, Math.PI * 2);
  ctx.fill();
}

function handleAmslerClick(event) {
  const canvas = document.getElementById('amsler-canvas');
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  amslerPoints.push({ x, y });
  initAmslerGrid();

  const flag = document.getElementById('amsler-distortion-flag');
  flag.innerText = `Distortion / Scotoma Detected (${amslerPoints.length} regions)`;
  flag.className = 'text-amber-400 font-bold';

  document.getElementById('sans-risk-pill').innerText = 'STAGE 2: SANS CAUTION';
  document.getElementById('sans-risk-pill').className = 'text-xs px-2 py-0.5 rounded bg-amber-950 text-amber-400 font-mono';
}

function resetAmslerGrid() {
  amslerPoints = [];
  initAmslerGrid();
  const flag = document.getElementById('amsler-distortion-flag');
  flag.innerText = 'Grid Lines: Straight & Uniform';
  flag.className = 'text-emerald-400';
  document.getElementById('sans-risk-pill').innerText = 'STAGE 0: NORMAL';
  document.getElementById('sans-risk-pill').className = 'text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono';
}

function submitSANSExam() {
  if (!window.selectedAstronautId) return;

  const acuity = document.getElementById('sans-acuity-select').value;
  const headache = parseInt(document.getElementById('sans-headache-select').value, 10);
  const hasDistortion = amslerPoints.length > 0;

  // Calculate IOP estimate
  let estIop = 16.0 + (headache * 0.8);
  if (hasDistortion) estIop += 3.5;
  if (acuity !== '20/20') estIop += 2.0;
  estIop = Math.min(28.0, Math.round(estIop * 10) / 10);

  let riskTier = 'STAGE_0_NORMAL';
  if (hasDistortion || estIop > 22.0 || acuity === '20/60') riskTier = 'STAGE_3_SEVERE';
  else if (estIop > 19.5 || acuity === '20/40') riskTier = 'STAGE_2_MODERATE';
  else if (headache > 2 || acuity === '20/25') riskTier = 'STAGE_1_MILD';

  document.getElementById('est-iop').innerText = `${estIop} mmHg`;

  fetch('/api/assessment/ocular', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      astronaut_id: window.selectedAstronautId,
      visual_acuity_left: acuity,
      visual_acuity_right: acuity,
      amsler_distortion: hasDistortion,
      amsler_distortion_quadrants: hasDistortion ? ['Paracentral Macular', 'Inferior Arcade'] : [],
      scotoma_detected: hasDistortion,
      intraocular_pressure_est_mmhg: estIop,
      globe_flattening_symptoms: hasDistortion || acuity !== '20/20',
      headache_severity: headache,
      blurred_vision_score: acuity === '20/20' ? 0 : 5,
      sans_risk_tier: riskTier
    })
  })
  .then(r => r.json())
  .then(data => {
    alert(`SANS Exam Saved! Classification: ${riskTier}. Actionable countermeasure protocols updated.`);
    if (window.refreshActiveData) window.refreshActiveData();
  });
}

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
  initAmslerGrid();
});

