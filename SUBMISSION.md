# NASA Space Apps Challenge Submission Details
## Project Name: BioSentinel (Aegis-Astro)
### Challenge: Health Monitoring Software for Astronauts on Space Missions

---

### 1. High-Level Project Summary (Elevator Pitch)
BioSentinel is an offline-first autonomous clinical software designed for astronauts during long-duration deep space missions (such as Mars transit). Due to communication latencies of up to 22 minutes to Earth, astronauts must autonomously track cross-system physiological drift. BioSentinel ingests biometric telemetry (heart rate, HRV, continuous blood pressure, SpO2), environmental life-support sensors (ambient CO2, radiation dosimeters), and interactive self-assessments (Psychomotor Vigilance Task for cognitive fatigue and Amsler Grid for Spaceflight-Associated Neuro-ocular Syndrome). Using a rule-based clinical engine modeled on NASA Human Research Program (HRP) standards, BioSentinel detects early health risks and generates immediate, actionable countermeasures—including adapted ARED resistance exercise, Lower Body Negative Pressure (LBNP) sessions, solar storm sheltering, and circadian phototherapy.

---

### 2. Detailed Description: What Does It Do?
On missions beyond low Earth orbit, astronauts face the 5 Hazards of Spaceflight: space radiation, altered gravity, isolation and confinement, hostile closed environments, and distance from Earth. BioSentinel serves as an onboard digital flight surgeon by providing:
1. **Command Flight Deck HUD**: Live visual streaming of crew vitals, atmospheric conditions, and an Earth communication latency indicator (+14m 22s).
2. **5-Hazard Diagnostic Engine**: Calculates a composite health score (0–100) and multi-hazard risk envelopes based on NASA clinical limits.
3. **Interactive Self-Assessment Suite**:
   - In-browser Psychomotor Vigilance Task (PVT) quantifying reaction times and attentional lapses (>500ms).
   - SANS Ocular Self-Exam with an interactive Amsler grid for mapping visual distortions caused by cephalad fluid shifts.
   - Biomarker and bone resorption lab tracker (urinary NTx, hydration, sleep quality).
4. **Actionable Clinical Countermeasures**: Generates tailored, prioritized checklists for astronauts to execute and log countermeasure compliance.
5. **Mission Crisis Simulator**: Allows real-time injection of simulated anomalies (solar radiation storms, CO2 scrubber malfunctions, acute SANS spikes) to verify autonomous triage.

---

### 3. Space Agency Data & Research Sources Used
- **NASA Human Research Program (HRP)**: Clinical evidence on SANS, space radiation biodosimetry, and microgravity bone demineralization.
- **NASA-STD-3001**: Space Flight Human-System Standards for environmental life-support and crew health envelopes.
- **Basner & Dinges (2011)**: Psychomotor Vigilance Test sensitivity metrics for spaceflight sleep debt and attentional lapse detection.
- **NASA Open Science Data Repository (OSDR)**: Space biology parameters for microgravity fluid redistribution and trabecular bone loss rates.

---

### 4. Hardware, Software & Tools Used
- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic, NumPy, SciPy, Scikit-learn.
- **Persistence**: Embedded SQLite (zero internet or cloud dependency).
- **Frontend**: HTML5, Tailwind CSS, Chart.js, Lucide Icons, HTML5 Canvas API, Web Audio API.
- **Version Control**: Git and GitHub.

---

### 5. Links for Direct Submission
- **Project Repository URL**: https://github.com/iam-batman-0/nasa-project
- **7-Slide Project Demonstration (Full URL)**: https://github.com/iam-batman-0/nasa-project/blob/main/demo/SLIDES.md
- **30-Second Video Script & Storyboard**: https://github.com/iam-batman-0/nasa-project/blob/main/demo/30_SECOND_VIDEO_SCRIPT.md
