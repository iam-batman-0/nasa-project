from pydantic import BaseModel, Field
from typing import Optional, List

class AstronautProfile(BaseModel):
    id: str
    name: str
    callsign: str
    role: str
    age: int
    blood_type: str
    mission_day: int = 184
    overall_health_score: float = Field(default=92.0, ge=0.0, le=100.0)
    health_status: str = "NOMINAL"  # NOMINAL, CAUTION, CRITICAL
    career_radiation_msv: float = Field(default=142.5, description="Cumulative mSv dose")
    career_radiation_limit_msv: float = 600.0
    baseline_bmd_t_score: float = 0.5  # Bone Mineral Density T-score
    current_bmd_t_score: float = 0.2
    active_countermeasures_count: int = 3
    avatar_url: Optional[str] = None

