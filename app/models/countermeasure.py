from pydantic import BaseModel, Field
from typing import List, Optional
import time

class ProtocolActionItem(BaseModel):
    id: str
    title: str
    description: str
    category: str  # EXERCISE, OCULAR_SANS, RADIATION, NUTRITION, PSYCH_CIRCADIAN
    priority: str  # ROUTINE, URGENT, EMERGENCY
    duration_minutes: int
    dosage_or_intensity: str
    is_completed: bool = False
    completed_at: Optional[float] = None

class CountermeasurePlan(BaseModel):
    plan_id: str
    astronaut_id: str
    generated_at: float = Field(default_factory=time.time)
    hazard_focus: str  # e.g., "SANS & Intracranial Pressure", "Solar Particle Shelter", "BMD Preservation"
    severity_level: str  # NOMINAL, ELEVATED_RISK, ACUTE_ALERT
    summary: str
    action_items: List[ProtocolActionItem]
    re_evaluation_in_hours: int = 12
