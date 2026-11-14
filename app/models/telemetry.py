from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import time

class PhysiologicalVitals(BaseModel):
    astronaut_id: str
    timestamp: float = Field(default_factory=time.time)
    heart_rate_bpm: float = 68.0
    hrv_rmssd_ms: float = 48.5  # Heart Rate Variability (Root Mean Square of Successive Differences)
    systolic_bp_mmhg: float = 118.0
    diastolic_bp_mmhg: float = 76.0
    spo2_percent: float = 98.2
    respiration_rate_bpm: float = 14.5
    core_temp_celsius: float = 36.8
    perfusion_index: float = 2.4
    stress_index: float = 24.0  # 0-100 scale based on sympathovagal balance
    cardiac_status: str = "NOMINAL"  # NOMINAL, ELEVATED, ARRHYTHMIA_RISK

class EnvironmentalTelemetry(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    cabin_co2_mmhg: float = 2.1
    cabin_o2_percent: float = 21.2
    cabin_pressure_psi: float = 14.65
    cabin_temp_celsius: float = 22.4
    cabin_humidity_percent: float = 44.0
    radiation_dose_rate_ugy_hr: float = 19.2  # microGray per hour
    cumulative_mission_dose_msv: float = 38.6
    acoustic_noise_db: float = 58.0
    air_quality_status: str = "OPTIMAL"  # OPTIMAL, ELEVATED_CO2, CRITICAL
    radiation_storm_active: bool = False

class TelemetrySnapshot(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    crew_vitals: Dict[str, PhysiologicalVitals]
    environment: EnvironmentalTelemetry
    system_status: str = "AUTONOMOUS_OPERATIONAL"

