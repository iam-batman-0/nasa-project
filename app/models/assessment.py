from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import time

class PVTTestResult(BaseModel):
    astronaut_id: str
    timestamp: float = Field(default_factory=time.time)
    test_duration_sec: int = 60
    total_stimuli: int
    mean_reaction_time_ms: float
    median_reaction_time_ms: float
    fastest_10pct_rt_ms: float
    slowest_10pct_rt_ms: float
    lapse_count: int = Field(description="Reactions taking >500 ms")
    false_starts: int = 0
    fatigue_level: str = "LOW"  # LOW, MODERATE, HIGH, CRITICAL
    cognitive_readiness_score: float = Field(default=95.0, ge=0.0, le=100.0)

class SANSOcularExam(BaseModel):
    astronaut_id: str
    timestamp: float = Field(default_factory=time.time)
    visual_acuity_left: str = "20/20"  # Snellen rating
    visual_acuity_right: str = "20/20"
    amsler_grid_distortion: bool = False
    amsler_distortion_quadrants: List[str] = []
    scotoma_detected: bool = False
    intraocular_pressure_est_mmhg: float = 17.5
    globe_flattening_symptoms: bool = False
    headache_severity: int = Field(default=0, ge=0, le=10)
    blurred_vision_score: int = Field(default=0, ge=0, le=10)
    sans_risk_tier: str = "STAGE_0_NORMAL"  # STAGE_0_NORMAL, STAGE_1_MILD, STAGE_2_MODERATE, STAGE_3_SEVERE

class BiomarkerLog(BaseModel):
    astronaut_id: str
    timestamp: float = Field(default_factory=time.time)
    urine_specific_gravity: float = 1.018  # 1.002 - 1.030 (hydration)
    urinary_ntx_nmol_bce_mmol_cr: float = 45.0  # Bone resorption rate (normal 20-65)
    salivary_cortisol_ug_dl: float = 0.28  # Stress biomarker (0.1 - 0.4)
    inflammatory_cytokine_il6_pg_ml: float = 1.8  # Immune dysregulation (<3.0 normal)
    muscle_soreness_rating: int = Field(default=2, ge=0, le=10)
    sleep_hours: float = 7.2
    rem_sleep_percentage: float = 22.0
    deep_sleep_percentage: float = 18.0
    sleep_quality_score: int = Field(default=84, ge=0, le=100)
    notes: Optional[str] = None

