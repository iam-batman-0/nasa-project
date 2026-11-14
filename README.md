# NASA BioSentinel (Aegis-Astro)
## Autonomous Health Monitoring & Countermeasure Software for Long-Duration Space Missions

[![NASA Space Apps](https://img.shields.io/badge/NASA-Human%20Research%20Program-blue.svg)](https://www.nasa.gov/hrp)
[![Architecture](https://img.shields.io/badge/Architecture-Edge%20Offline%20First-green.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-3.11-teal.svg)](https://fastapi.tiangolo.com)
[![Status](https://img.shields.io/badge/Status-Operational%20v2.4-cyan.svg)]()

---

## 📽️ Project Demonstration (NASA Space Apps Global Award Eligible)
- **7-Slide Presentation (Direct Public Link):**  
  👉 **[https://github.com/iam-batman-0/nasa-project/blob/main/demo/SLIDES.md](https://github.com/iam-batman-0/nasa-project/blob/main/demo/SLIDES.md)**  
  *(Compliant 7-slide presentation covering Problem, 5 Hazards, Edge Architecture, Real-Time HUD, Self-Assessments, Countermeasures & Impact)*

---

## 🚀 The Challenge
On long-duration exploration missions (e.g., Artemis deep-space gateways, Moon-to-Mars transits with 3- to 22-minute one-way communication delays to Earth), astronauts cannot rely on ground-based flight surgeons. The **5 Hazards of Human Spaceflight** impose compounding physiological damage:
1. **Space Radiation**: High-energy Galactic Cosmic Rays (GCR) and acute Solar Particle Events (SPE).
2. **Isolation and Confinement**: Circadian desynchronization, neurobehavioral fatigue, sleep loss.
3. **Distance from Earth**: Autonomous clinical self-reliance without real-time Mission Control Houston (MCH).
4. **Altered Gravity**: Spaceflight-Associated Neuro-ocular Syndrome (SANS), bone mineral density loss (1.0–1.5% per month), muscle atrophy, and orthostatic intolerance.
5. **Hostile Closed Environment**: Elevated ambient $CO_2$ (>3.0 mmHg), acoustic stress, toxic volatile compounds.

**BioSentinel** empowers astronauts to independently gather multi-modal health indicators, spot physiological drift in themselves, evaluate cross-system health risks with an autonomous clinical engine, and execute evidence-based countermeasures in real time.

---

## 🛰️ Key System Features

### 1. Flight Deck Command HUD & Real-Time Biometric Telemetry
- Real-time streaming telemetry for 4 expedition crew members (Heart Rate, HRV RMSSD, Continuous Blood Pressure, $SpO_2$, Respiration Rate, Core Temperature, Sympathovagal Stress Index).
- Closed cabin environmental life-support telemetry: Ambient $CO_2$, Cabin Pressure, Temperature, Humidity, and Active Radiation Dosimetry ($\mu\text{Gy/hr}$ and cumulative $\text{mSv}$).
- Live interactive charts powered by Chart.js.

### 2. Autonomous Multi-Hazard Clinical Evaluation Engine
- Calculates holistic health scores and 5-hazard safety envelopes based on NASA Human Research Program (HRP) thresholds.
- Detects early indicators of hypercapnia, cardiac deconditioning, bone resorption, SANS, and neurocognitive exhaustion.

### 3. Interactive Astronaut Self-Assessment Suite
- **Psychomotor Vigilance Task (PVT)**: An interactive 60-second reaction time test with millisecond precision, tracking attentional lapses (>500 ms) and false starts to calculate cognitive readiness and neurobehavioral fatigue.
- **SANS Ocular & Amsler Grid Self-Exam**: Astronauts map visual distortions, scotomas, and choroidal folds on an interactive canvas to track cephalad fluid shift and posterior globe flattening.
- **Biomarker & Bone Health Lab**: Tracks urinary NTx bone resorption markers, hydration (urine specific gravity), salivary cortisol, and sleep quality.

### 4. Actionable Clinical Countermeasure Generator
- Synthesizes detected hazards into customized, prioritizable action checklists:
  - **ARED Axial-Load Resistance Prescriptions**: High-impact heel-strike squats and deadlifts to preserve trabecular bone.
  - **Lower Body Negative Pressure (LBNP)**: Negative pressure suction to pull pooled fluid from the head and eyes to the lower limbs.
  - **SPE Radiation Storm Protocols**: Immediate shelter ingress and antioxidant radioprotectant administration.
  - **Circadian Phototherapy**: Blue-enriched 480 nm light exposure to align sleep-wake cycles.
  - **Plasma Volume Expansion**: Electrolyte and fluid loading for orthostatic stability.

### 5. Mission Crisis & Anomaly Injector
- One-click live simulation scenarios for evaluation and demonstration:
  - *Solar Particle Event (SPE) Radiation Storm*
  - *ECLSS $CO_2$ Scrubber Malfunction*
  - *Acute SANS Cephalad Pressure Spike*
  - *Circadian Desynchronization & Cognitive Exhaustion*
  - *Cardiac Tachyarrhythmia & Deconditioning*
  - *Nominal Operational Reset*

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic, NumPy, SciPy, Scikit-learn.
- **Database**: Local embedded SQLite (`data/biosentinel.db`) with zero external network or cloud dependencies.
- **Frontend**: Responsive NASA Flight Deck UI, Tailwind CSS, Chart.js, Lucide Icons, HTML5 Canvas API, Web Audio API synth chimes.
- **Offline Edge Resilience**: Completely self-contained; runs inside the spacecraft local area network.

---

## ⚡ Quick Start Guide

### 1. Clone & Navigate
```bash
git clone https://github.com/iam-batman-0/nasa-project.git
cd nasa-project
```

### 2. Set Up Virtual Environment & Install Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 3. Run the Application
```powershell
.\.venv\Scripts\python run.py
```

### 4. Open Flight Deck in Your Browser
Open the application on port `8000` (e.g., `http://127.0.0.1:8000` or via your machine's network IP).

---

## 📁 Repository Structure
```
├── app/
│   ├── config.py                 # NASA HRP clinical thresholds & constants
│   ├── database.py               # Embedded SQLite schema & crew records
│   ├── main.py                   # FastAPI application & API endpoints
│   ├── models/
│   │   ├── astronaut.py          # Crew profiles & health scores
│   │   ├── telemetry.py          # Biometric & environmental telemetry models
│   │   ├── assessment.py         # PVT test, SANS eye exam & biomarker models
│   │   └── countermeasure.py     # Clinical action plans & protocol items
│   ├── services/
│   │   ├── telemetry_simulator.py# Multi-modal real-time crew & cabin simulator
│   │   ├── health_analyzer.py    # 5-Hazard autonomous risk evaluation engine
│   │   └── countermeasure_engine.py # NASA clinical countermeasure generator
│   ├── static/
│   │   ├── css/styles.css        # Flight HUD styling & aerospace themes
│   │   └── js/
│   │       ├── app.js            # Main controller, Chart.js & WebSockets
│   │       ├── pvt_test.js       # Interactive Psychomotor Vigilance Task
│   │       └── ocular_test.js    # Interactive SANS Amsler grid self-exam
│   └── templates/
│       └── index.html            # Main Flight Operations dashboard
├── run.py                        # Server startup entry point
├── requirements.txt              # Production dependencies
└── README.md                     # Documentation
```

---

## 📜 Scientific References & NASA Standards
- **NASA Human Research Program (HRP)**: *Evidence Report: Risk of Spaceflight-Associated Neuro-ocular Syndrome (SANS)*.
- **NASA-STD-3001**: *NASA Space Flight Human-System Standard, Volume 1 (Crew Health)*.
- **Basner, M., & Dinges, D. F. (2011)**: *Maximizing Sensitivity of the Psychomotor Vigilance Test (PVT) to Sleep Loss*. SLEEP, 34(5), 581–591.
- **Sibonga, J. D. (2013)**: *Spaceflight-induced bone loss: Is there an osteoporosis risk?* Current Osteoporosis Reports, 11(2), 92–98.
