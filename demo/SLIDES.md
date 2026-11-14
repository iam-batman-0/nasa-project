# NASA BioSentinel (Aegis-Astro)
## Official 7-Slide Project Demonstration
**NASA International Space Apps Challenge**  
**Challenge:** Health Monitoring Software for Astronauts on Space Missions  
**Public Repository:** [https://github.com/iam-batman-0/nasa-project](https://github.com/iam-batman-0/nasa-project)  
**Live Slide Deck:** [https://github.com/iam-batman-0/nasa-project/blob/main/demo/SLIDES.md](https://github.com/iam-batman-0/nasa-project/blob/main/demo/SLIDES.md)

---

### Slide 1: Title & Mission Identity
- **Project Name:** BioSentinel (Aegis-Astro)
- **Subtitle:** Autonomous Health Decision & Clinical Countermeasure System for Deep-Space Exploration
- **Target Mission:** Long-Duration Mars Transit & Artemis Deep Space Gateway (Mission Day 184)
- **Challenge Statement:** Providing astronauts with autonomous capability to gather multi-modal health indicators, spot physiological changes, and execute evidence-based countermeasures without Earth ground-control dependency.

---

### Slide 2: The Challenge & The 5 Hazards of Spaceflight
- **The Problem:** Long-duration interplanetary missions expose astronauts to:
  1. **Space Radiation:** High-energy Galactic Cosmic Rays (GCR) and acute Solar Particle Events (SPE).
  2. **Altered Gravity:** Microgravity causes 1.0–1.5% monthly Bone Mineral Density (BMD) loss and Spaceflight-Associated Neuro-ocular Syndrome (SANS).
  3. **Isolation & Confinement:** Circadian dysregulation, sleep architecture loss, and cognitive performance degradation.
  4. **Hostile Closed Environment:** Elevated ambient $CO_2$ (>3.0 mmHg) and toxic life-support volatility.
  5. **Distance from Earth:** Up to 22-minute one-way communication latency prevents real-time telemedicine from Mission Control Houston.
- **The Need:** An onboard, offline-first autonomous system that turns raw biometrics into actionable clinical decisions.

---

### Slide 3: System Architecture & Offline Edge Autonomy
- **Zero Cloud Reliance:** Runs entirely on an embedded spacecraft edge server (Python 3.11 / FastAPI / SQLite) over local flight-deck networks.
- **Multi-Modal Data Ingestion:**
  - *Continuous Physiological Vitals:* HR, HRV (RMSSD), Continuous Blood Pressure, $SpO_2$, Respiration Rate, Core Temp.
  - *Environmental Telemetry:* Ambient $CO_2$, cabin pressure, radiation dosimeter ($\mu\text{Gy/hr}$ and cumulative $\text{mSv}$).
  - *Biomarkers & Labs:* Urinary NTx (bone resorption rate), urine hydration specific gravity, cortisol.
  - *Interactive Astronaut Self-Exams:* Psychomotor Vigilance Task (PVT) and SANS Amsler grid ocular mapping.

---

### Slide 4: Real-Time HUD & 5-Hazard Diagnostic Engine
- **Command HUD:** Real-time multi-crew telemetry visualizer with sub-second biometric graphing (Chart.js) and active mission clocks.
- **Autonomous Clinical Risk Engine:**
  - Continuously evaluates health against NASA Human Research Program (HRP) safety envelopes.
  - Generates composite health scores (0–100) and multi-hazard risk breakdowns (Radiation, Cardiovascular, Musculoskeletal, SANS, Cognitive/Behavioral, Closed Atmosphere).
  - Immediate autonomous triage categorizes status into **NOMINAL**, **CAUTION**, or **CRITICAL**.

---

### Slide 5: Interactive Self-Assessment Suite (PVT & SANS)
- **Interactive Psychomotor Vigilance Task (PVT):**
  - Standard NASA 60-second millisecond reaction test embedded directly in the browser.
  - Quantifies mean reaction time, false starts, and attentional lapses (>500 ms) to objectively score neurobehavioral readiness and sleep debt.
- **SANS Ocular & Amsler Grid Self-Exam:**
  - Clickable interactive Amsler Grid canvas for astronauts to map visual metamorphopsia, scotomas, and choroidal folds.
  - Near-point visual acuity and cephalad venous congestion estimator for early detection of optic disc edema.

---

### Slide 6: Actionable Clinical Countermeasure Generator
- **Autonomous Prescription Engine:** Synthesizes detected hazards into immediate, astronaut-executable action checklists:
  - **ARED Resistance Conditioning:** Dynamic axial-load scaling (1.8x bodyweight squats/deadlifts at 2.5 kN impact) to suppress bone resorption.
  - **Lower Body Negative Pressure (LBNP):** 45-minute negative pressure sessions (-25 mmHg) to pull pooled fluid from the head and reverse SANS ocular pressure.
  - **Solar Particle Event (SPE) Shelter:** Immediate storm-haven relocation and antioxidant radioprotectant cocktail administration.
  - **Circadian Phototherapy:** Blue-enriched 480 nm light therapy to align circadian rhythms.

---

### Slide 7: Mission Impact, Scalability & Terrestrial Spin-offs
- **Mission Impact:** Eliminates critical reliance on Earth telemedicine, ensuring crew survivability during deep-space exploration missions.
- **Readiness Level:** Architecture is edge-tested, modular, and containerizable for spaceflight avionics.
- **Terrestrial Dual-Use:**
  - Remote telemedicine in Arctic/Antarctic research stations, submarine crews, and isolated rural clinics.
  - Preventative monitoring of osteoporosis, bedrest deconditioning, and shift-work circadian fatigue.
- **Open Source:** Full code, data models, and simulator available at [https://github.com/iam-batman-0/nasa-project](https://github.com/iam-batman-0/nasa-project).

