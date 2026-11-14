"""
NASA BioSentinel Autonomous Health System.
FastAPI Backend providing real-time telemetry streaming, autonomous diagnostic triage,
and clinical countermeasure execution for deep-space missions.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
from typing import List, Dict, Any

from app.database import init_db, get_db
from app.models.astronaut import AstronautProfile
from app.models.telemetry import TelemetrySnapshot
from app.models.assessment import PVTTestResult, SANSOcularExam, BiomarkerLog
from app.models.countermeasure import CountermeasurePlan
from app.services.telemetry_simulator import simulator
from app.services.health_analyzer import HealthAnalyzer
from app.services.countermeasure_engine import CountermeasureEngine

app = FastAPI(
    title="NASA BioSentinel",
    description="Autonomous Spaceflight Health Decision & Countermeasure System",
    version="2.4.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Cache of latest assessment logs in memory for fast autonomous evaluation
latest_pvt_cache: Dict[str, PVTTestResult] = {}
latest_ocular_cache: Dict[str, SANSOcularExam] = {}
latest_biomarkers_cache: Dict[str, BiomarkerLog] = {}

@app.on_event("startup")
def startup_event():
    init_db()

# --- WEB DASHBOARD ROUTE ---
@app.get("/")
def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- CREW ROSTER ENDPOINTS ---
@app.get("/api/crew", response_model=List[AstronautProfile])
def get_crew():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM astronauts ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    crew = []
    for r in rows:
        crew.append(AstronautProfile(
            id=r["id"],
            name=r["name"],
            callsign=r["callsign"],
            role=r["role"],
            age=r["age"],
            blood_type=r["blood_type"],
            mission_day=r["mission_day"],
            overall_health_score=r["overall_health_score"],
            health_status=r["health_status"],
            career_radiation_msv=r["career_radiation_msv"],
            baseline_bmd_t_score=r["baseline_bmd_t_score"],
            current_bmd_t_score=r["current_bmd_t_score"]
        ))
    return crew

# --- REAL-TIME TELEMETRY STREAM SNAPSHOT ---
@app.get("/api/telemetry/snapshot", response_model=TelemetrySnapshot)
def get_telemetry_snapshot():
    snapshot = simulator.generate_tick()
    return snapshot

# --- AUTONOMOUS CLINICAL EVALUATION ENGINE ---
@app.get("/api/evaluate/{astronaut_id}")
def evaluate_astronaut(astronaut_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM astronauts WHERE id = ?", (astronaut_id,))
    astro = cursor.fetchone()
    conn.close()

    if not astro:
        raise HTTPException(status_code=404, detail="Astronaut not found")

    snapshot = simulator.generate_tick()
    vitals = snapshot.crew_vitals.get(astronaut_id)
    if not vitals:
        raise HTTPException(status_code=404, detail="Astronaut telemetry offline")

    # Run multi-hazard analyzer
    evaluation = HealthAnalyzer.evaluate_crew_member(
        vitals=vitals,
        env=snapshot.environment,
        latest_pvt=latest_pvt_cache.get(astronaut_id),
        latest_ocular=latest_ocular_cache.get(astronaut_id),
        latest_biomarkers=latest_biomarkers_cache.get(astronaut_id),
        career_radiation_msv=astro["career_radiation_msv"],
        baseline_bmd_t_score=astro["baseline_bmd_t_score"],
        current_bmd_t_score=astro["current_bmd_t_score"]
    )

    # Sync overall health score back to DB
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE astronauts SET overall_health_score = ?, health_status = ?, updated_at = ? WHERE id = ?",
        (evaluation["overall_health_score"], evaluation["status"], time.time(), astronaut_id)
    )
    conn.commit()
    conn.close()

    return evaluation

# --- CLINICAL COUNTERMEASURE GENERATION ---
@app.get("/api/countermeasures/{astronaut_id}", response_model=CountermeasurePlan)
def get_countermeasure_plan(astronaut_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM astronauts WHERE id = ?", (astronaut_id,))
    astro = cursor.fetchone()
    conn.close()

    if not astro:
        raise HTTPException(status_code=404, detail="Astronaut not found")

    snapshot = simulator.generate_tick()
    vitals = snapshot.crew_vitals.get(astronaut_id)

    evaluation = HealthAnalyzer.evaluate_crew_member(
        vitals=vitals,
        env=snapshot.environment,
        latest_pvt=latest_pvt_cache.get(astronaut_id),
        latest_ocular=latest_ocular_cache.get(astronaut_id),
        latest_biomarkers=latest_biomarkers_cache.get(astronaut_id),
        career_radiation_msv=astro["career_radiation_msv"],
        baseline_bmd_t_score=astro["baseline_bmd_t_score"],
        current_bmd_t_score=astro["current_bmd_t_score"]
    )

    plan = CountermeasureEngine.generate_plan(
        astronaut_id=astronaut_id,
        astronaut_name=astro["name"],
        evaluation=evaluation,
        radiation_storm=snapshot.environment.radiation_storm_active
    )

    return plan

# --- SELF-ASSESSMENT SUBMISSION HANDLERS ---
@app.post("/api/assessment/pvt")
def submit_pvt_assessment(result: PVTTestResult):
    latest_pvt_cache[result.astronaut_id] = result
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pvt_assessments (astronaut_id, timestamp, mean_rt, median_rt, lapse_count, false_starts, fatigue_level, cognitive_readiness)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        result.astronaut_id,
        result.timestamp,
        result.mean_reaction_time_ms,
        result.median_reaction_time_ms,
        result.lapse_count,
        result.false_starts,
        result.fatigue_level,
        result.cognitive_readiness_score
    ))
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "message": "PVT Cognitive Assessment Logged"}

@app.post("/api/assessment/ocular")
def submit_ocular_assessment(exam: SANSOcularExam):
    latest_ocular_cache[exam.astronaut_id] = exam
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO ocular_assessments (astronaut_id, timestamp, visual_acuity_left, visual_acuity_right, amsler_distortion, intraocular_pressure, sans_risk_tier)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        exam.astronaut_id,
        exam.timestamp,
        exam.visual_acuity_left,
        exam.visual_acuity_right,
        1 if exam.amsler_distortion else 0,
        exam.intraocular_pressure_est_mmhg,
        exam.sans_risk_tier
    ))
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "message": "SANS Ocular Self-Assessment Logged"}

@app.post("/api/assessment/biomarkers")
def submit_biomarkers(log: BiomarkerLog):
    latest_biomarkers_cache[log.astronaut_id] = log
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO biomarker_logs (astronaut_id, timestamp, urine_specific_gravity, urinary_ntx, salivary_cortisol, sleep_hours, sleep_quality_score, muscle_soreness)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log.astronaut_id,
        log.timestamp,
        log.urine_specific_gravity,
        log.urinary_ntx_nmol_bce_mmol_cr,
        log.salivary_cortisol_ug_dl,
        log.sleep_hours,
        log.sleep_quality_score,
        log.muscle_soreness_rating
    ))
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "message": "Biomarker and Bone Lab Record Saved"}

# --- CRISIS SCENARIO INJECTOR ---
class ScenarioPayload(BaseModel):
    scenario: str

@app.post("/api/simulator/scenario")
def set_simulator_scenario(payload: ScenarioPayload):
    simulator.set_scenario(payload.scenario)
    return {
        "status": "SUCCESS",
        "active_scenario": payload.scenario,
        "message": f"Mission event {payload.scenario} injected into telemetry bus."
    }
