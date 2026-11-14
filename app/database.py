"""
Local SQLite Database for BioSentinel Space Health Software.
Autonomous offline persistence for crew records, vitals, assessments, and countermeasure plans.
"""

import sqlite3
import json
import os
import time
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "biosentinel.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Astronaut Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS astronauts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        callsign TEXT NOT NULL,
        role TEXT NOT NULL,
        age INTEGER NOT NULL,
        blood_type TEXT NOT NULL,
        mission_day INTEGER NOT NULL,
        overall_health_score REAL NOT NULL,
        health_status TEXT NOT NULL,
        career_radiation_msv REAL NOT NULL,
        baseline_bmd_t_score REAL NOT NULL,
        current_bmd_t_score REAL NOT NULL,
        updated_at REAL NOT NULL
    )
    """)

    # Telemetry Log (Time-series buffer)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        astronaut_id TEXT NOT NULL,
        heart_rate REAL NOT NULL,
        hrv_rmssd REAL NOT NULL,
        systolic_bp REAL NOT NULL,
        diastolic_bp REAL NOT NULL,
        spo2 REAL NOT NULL,
        stress_index REAL NOT NULL,
        respiration_rate REAL NOT NULL
    )
    """)

    # Environmental Telemetry
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS environmental_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        cabin_co2 REAL NOT NULL,
        radiation_dose_rate REAL NOT NULL,
        cabin_pressure REAL NOT NULL,
        cumulative_mission_dose REAL NOT NULL
    )
    """)

    # PVT Cognitive Tests
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pvt_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        astronaut_id TEXT NOT NULL,
        timestamp REAL NOT NULL,
        mean_rt REAL NOT NULL,
        median_rt REAL NOT NULL,
        lapse_count INTEGER NOT NULL,
        false_starts INTEGER NOT NULL,
        fatigue_level TEXT NOT NULL,
        cognitive_readiness REAL NOT NULL
    )
    """)

    # SANS Ocular Exams
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ocular_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        astronaut_id TEXT NOT NULL,
        timestamp REAL NOT NULL,
        visual_acuity_left TEXT NOT NULL,
        visual_acuity_right TEXT NOT NULL,
        amsler_distortion INTEGER NOT NULL,
        intraocular_pressure REAL NOT NULL,
        sans_risk_tier TEXT NOT NULL
    )
    """)

    # Biomarkers & Daily Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS biomarker_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        astronaut_id TEXT NOT NULL,
        timestamp REAL NOT NULL,
        urine_specific_gravity REAL NOT NULL,
        urinary_ntx REAL NOT NULL,
        salivary_cortisol REAL NOT NULL,
        sleep_hours REAL NOT NULL,
        sleep_quality_score INTEGER NOT NULL,
        muscle_soreness INTEGER NOT NULL
    )
    """)

    # Countermeasure Plans & Action Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS countermeasure_plans (
        plan_id TEXT PRIMARY KEY,
        astronaut_id TEXT NOT NULL,
        generated_at REAL NOT NULL,
        hazard_focus TEXT NOT NULL,
        severity_level TEXT NOT NULL,
        summary TEXT NOT NULL,
        action_items_json TEXT NOT NULL
    )
    """)

    # Seed initial crew if empty
    cursor.execute("SELECT COUNT(*) FROM astronauts")
    if cursor.fetchone()[0] == 0:
        initial_crew = [
            ("ASTRO-01", "Dr. Sarah Vance", "Valkyrie", "Commander & Flight Surgeon", 42, "O+", 184, 94.0, "NOMINAL", 142.5, 0.6, 0.4, time.time()),
            ("ASTRO-02", "Alexei Romanov", "Cosmo", "Lead Flight Engineer", 38, "A+", 184, 88.0, "NOMINAL", 148.0, 0.4, 0.1, time.time()),
            ("ASTRO-03", "Maya Lin", "Nova", "Science Payload Specialist", 34, "B+", 184, 76.0, "CAUTION", 136.2, 0.3, -0.2, time.time()),
            ("ASTRO-04", "Marcus Brody", "Titan", "Systems Operations Officer", 45, "O-", 184, 83.0, "NOMINAL", 155.8, 0.5, 0.15, time.time()),
        ]
        cursor.executemany("""
        INSERT INTO astronauts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_crew)

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
