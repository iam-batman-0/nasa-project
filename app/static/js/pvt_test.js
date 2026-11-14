/**
 * NASA Psychomotor Vigilance Task (PVT) Module.
 * Measures reaction time and attentional lapses to assess neurocognitive readiness and fatigue.
 */

let pvtActive = false;
let pvtStimulusActive = false;
let pvtStartTime = 0;
let pvtTimerInterval = null;
let pvtTimeoutId = null;
let pvtStimuliCompleted = 0;
const pvtTotalStimuli = 5; // Rapid 5-trial assessment for demo (or 8)
let pvtReactionTimes = [];
let pvtLapses = 0;
let pvtFalseStarts = 0;

function startPVTTest() {
  if (pvtActive) return;

  pvtActive = true;
  pvtStimuliCompleted = 0;
  pvtReactionTimes = [];
  pvtLapses = 0;
  pvtFalseStarts = 0;

  document.getElementById('pvt-start-btn').disabled = true;
  document.getElementById('pvt-start-btn').classList.add('opacity-50');
  document.getElementById('pvt-status-pill').innerText = 'TEST IN PROGRESS';
  document.getElementById('pvt-status-pill').className = 'text-xs px-2 py-0.5 rounded bg-amber-950 text-amber-400 font-mono';

  document.getElementById('pvt-stimuli-count').innerText = `0/${pvtTotalStimuli}`;
  document.getElementById('pvt-lapse-count').innerText = '0';
  document.getElementById('pvt-false-starts').innerText = '0';

  scheduleNextStimulus();
}

function scheduleNextStimulus() {
  if (pvtStimuliCompleted >= pvtTotalStimuli) {
    completePVTTest();
    return;
  }

  pvtStimulusActive = false;
  document.getElementById('pvt-idle-screen').classList.add('hidden');
  document.getElementById('pvt-active-screen').classList.add('hidden');
  document.getElementById('pvt-waiting-screen').classList.remove('hidden');

  // Random delay between 1.5s and 4.5s
  const delay = Math.floor(Math.random() * 3000) + 1500;

  pvtTimeoutId = setTimeout(() => {
    triggerStimulus();
  }, delay);
}

function triggerStimulus() {
  pvtStimulusActive = true;
  pvtStartTime = performance.now();

  document.getElementById('pvt-waiting-screen').classList.add('hidden');
  document.getElementById('pvt-active-screen').classList.remove('hidden');

  const timerEl = document.getElementById('pvt-timer-display');
  timerEl.innerText = '000';

  pvtTimerInterval = setInterval(() => {
    const elapsed = Math.floor(performance.now() - pvtStartTime);
    timerEl.innerText = String(elapsed).padStart(3, '0');
    if (elapsed > 500) {
      timerEl.classList.remove('text-rose-500');
      timerEl.classList.add('text-amber-400');
    }
  }, 10);
}

function handlePVTInteraction() {
  if (!pvtActive) return;

  if (!pvtStimulusActive) {
    // False start!
    clearTimeout(pvtTimeoutId);
    pvtFalseStarts++;
    document.getElementById('pvt-false-starts').innerText = pvtFalseStarts;
    showPVTNotice('FALSE START DETECTED (-5s penalty)');
    scheduleNextStimulus();
    return;
  }

  // Valid response
  clearInterval(pvtTimerInterval);
  const rt = Math.round(performance.now() - pvtStartTime);
  pvtReactionTimes.push(rt);
  pvtStimuliCompleted++;

  if (rt > 500) {
    pvtLapses++;
    document.getElementById('pvt-lapse-count').innerText = pvtLapses;
  }

  document.getElementById('pvt-stimuli-count').innerText = `${pvtStimuliCompleted}/${pvtTotalStimuli}`;

  const timerEl = document.getElementById('pvt-timer-display');
  timerEl.innerText = `${rt} ms`;

  setTimeout(() => {
    scheduleNextStimulus();
  }, 800);
}

// Support Spacebar for tactile reaction
window.addEventListener('keydown', (e) => {
  if (e.code === 'Space' && pvtActive) {
    e.preventDefault();
    handlePVTInteraction();
  }
});

function completePVTTest() {
  pvtActive = false;
  pvtStimulusActive = false;
  clearInterval(pvtTimerInterval);
  clearTimeout(pvtTimeoutId);

  document.getElementById('pvt-start-btn').disabled = false;
  document.getElementById('pvt-start-btn').classList.remove('opacity-50');
  document.getElementById('pvt-status-pill').innerText = 'COMPLETED';
  document.getElementById('pvt-status-pill').className = 'text-xs px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono';

  document.getElementById('pvt-active-screen').classList.add('hidden');
  document.getElementById('pvt-waiting-screen').classList.add('hidden');
  document.getElementById('pvt-idle-screen').classList.remove('hidden');

  // Compute metrics
  const meanRt = Math.round(pvtReactionTimes.reduce((a, b) => a + b, 0) / pvtReactionTimes.length);
  pvtReactionTimes.sort((a, b) => a - b);
  const medianRt = pvtReactionTimes[Math.floor(pvtReactionTimes.length / 2)];

  // Readiness score formula
  let readiness = 100 - (meanRt - 220) * 0.2 - (pvtLapses * 12) - (pvtFalseStarts * 8);
  readiness = Math.max(20, Math.min(100, Math.round(readiness)));

  let fatigue = "LOW";
  if (readiness < 65 || pvtLapses >= 3) fatigue = "HIGH";
  else if (readiness < 82 || pvtLapses >= 1) fatigue = "MODERATE";

  document.getElementById('pvt-mean-rt').innerText = `${meanRt} ms`;
  document.getElementById('pvt-readiness').innerText = `${readiness}%`;
  document.getElementById('pvt-fatigue').innerText = fatigue;

  // Send result to backend
  if (window.selectedAstronautId) {
    fetch('/api/assessment/pvt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        astronaut_id: window.selectedAstronautId,
        total_stimuli: pvtTotalStimuli,
        mean_reaction_time_ms: meanRt,
        median_reaction_time_ms: medianRt,
        fastest_10pct_rt_ms: pvtReactionTimes[0] || meanRt,
        slowest_10pct_rt_ms: pvtReactionTimes[pvtReactionTimes.length - 1] || meanRt,
        lapse_count: pvtLapses,
        false_starts: pvtFalseStarts,
        fatigue_level: fatigue,
        cognitive_readiness_score: readiness
      })
    })
    .then(r => r.json())
    .then(() => {
      if (window.refreshActiveData) window.refreshActiveData();
    });
  }
}

function showPVTNotice(msg) {
  const arena = document.getElementById('pvt-arena');
  const banner = document.createElement('div');
  banner.className = 'absolute top-2 inset-x-4 bg-red-900/80 text-red-200 text-xs py-1 px-3 rounded text-center font-mono animate-bounce';
  banner.innerText = msg;
  arena.appendChild(banner);
  setTimeout(() => banner.remove(), 1200);
}
