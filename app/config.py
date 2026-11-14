"""
Configuration and Medical Baselines for BioSentinel NASA Health Monitoring System.
Based on NASA Human Research Program (HRP) standards for deep space transit.
"""

from pydantic import BaseModel
from typing import Dict, Any

class MissionConfig(BaseModel):
    MISSION_NAME: str = "ARES-V Deep Space Exploration"
    MISSION_DESTINATION: str = "Mars Transit (Interplanetary Transfer)"
    MISSION_DAY: int = 184
    CREW_COUNT: int = 4
    ONE_WAY_COMMS_DELAY_SEC: int = 862  # ~14 min 22 sec communication lag to Earth
    AUTONOMOUS_MODE: bool = True

    # Environmental Safety Thresholds (NASA Flight Standards)
    CABIN_CO2_NOMINAL_MMHG: float = 2.0
    CABIN_CO2_CAUTION_MMHG: float = 3.5
    CABIN_CO2_CRITICAL_MMHG: float = 5.0

    CABIN_PRESSURE_NOMINAL_PSI: float = 14.7
    CABIN_RADIATION_NOMINAL_UGY_HR: float = 18.5  # Typical background GCR in deep space
    SPE_STORM_ALERT_UGY_HR: float = 250.0  # Solar Particle Event threshold

    # Physiological Nominal Baselines
    RESTING_HR_MIN: int = 50
    RESTING_HR_MAX: int = 90
    HRV_RMSSD_MIN_MS: float = 30.0  # Parasympathetic tone threshold
    SPO2_MIN_PERCENT: float = 94.0
    SYSTOLIC_BP_MAX: int = 135
    DIASTOLIC_BP_MAX: int = 88
    CORE_TEMP_MIN_C: float = 36.2
    CORE_TEMP_MAX_C: float = 37.8

    # SANS (Spaceflight-Associated Neuro-ocular Syndrome) Thresholds
    SANS_INTRAOCULAR_PRESSURE_MAX_MMHG: float = 21.0
    SANS_REFRACTIVE_SHIFT_MAX_DIOPTERS: float = 0.75

    # Bone & Muscle Degradation Limits
    BMD_LOSS_CAUTION_RATE_PCT_MONTH: float = 1.0  # Greater than 1% loss per month triggers intervention
    EXERCISE_ARED_MIN_HOURS_PER_DAY: float = 1.5

config = MissionConfig()

