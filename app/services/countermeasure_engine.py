"""
Autonomous Clinical Countermeasure Generation Engine.
Synthesizes NASA space medicine protocols into tailored, executable action checklists
allowing astronauts to actively mitigate detected physiological and environmental hazards.
"""

import time
import uuid
from typing import List, Dict, Any
from app.models.countermeasure import CountermeasurePlan, ProtocolActionItem

class CountermeasureEngine:
    @staticmethod
    def generate_plan(
        astronaut_id: str,
        astronaut_name: str,
        evaluation: Dict[str, Any],
        radiation_storm: bool = False
    ) -> CountermeasurePlan:
        scores = evaluation["hazard_scores"]
        alerts = evaluation["alerts"]
        actions: List[ProtocolActionItem] = []
        focus_areas: List[str] = []

        # 1. EMERGENCY RADIATION PROTOCOL
        if radiation_storm or scores["radiation"] < 50.0:
            focus_areas.append("SPE Radiation Storm Shelter")
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Immediate Shelter Ingress: Storm Haven",
                description="Cease all extravehicular or perimeter activities. Relocate to high-density water-wall storm shelter module.",
                category="RADIATION",
                priority="EMERGENCY",
                duration_minutes=180,
                dosage_or_intensity="Class 1 Storm Haven Lockdown"
            ))
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Administer Radioprotectant Antioxidant Regimen",
                description="Ingest oral radioprotective cocktail (N-acetylcysteine 600mg + Vitamin E 400IU + Selenium 200mcg) to scavenge free radicals.",
                category="RADIATION",
                priority="EMERGENCY",
                duration_minutes=5,
                dosage_or_intensity="1 Oral Sachet with 250ml H2O"
            ))

        # 2. SANS & INTRACRANIAL PRESSURE INTERVENTION
        if scores["sans_ocular"] < 80.0:
            focus_areas.append("SANS Ocular Decongestion")
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Lower Body Negative Pressure (LBNP) Session",
                description="Conduct 45-minute LBNP chamber suction at -25 mmHg to draw pooled cephalad venous blood back into lower limbs and relieve optic nerve pressure.",
                category="OCULAR_SANS",
                priority="URGENT" if scores["sans_ocular"] < 65.0 else "ROUTINE",
                duration_minutes=45,
                dosage_or_intensity="-25 mmHg negative pressure"
            ))
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Adjust Sleep Ergonomics / Head-Up Sleep Protocol",
                description="Engage 10-degree head-up sleep tether inclination and wear mild thigh cuffs during high-workload periods.",
                category="OCULAR_SANS",
                priority="ROUTINE",
                duration_minutes=15,
                dosage_or_intensity="10° inclination / Mechanical Cuffs"
            ))

        # 3. MUSCULOSKELETAL & BONE PRESERVATION (ARED)
        if scores["musculoskeletal"] < 85.0:
            focus_areas.append("ARED High-Load Bone Remodeling")
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="ARED High-Axial-Load Protocol (Squats & Deadlifts)",
                description="Increase axial resistance loading to 1.8x 1g-equivalent. Execute 4 sets x 8 reps of squats and stiff-legged deadlifts with 2.5kN heel-strike impact force.",
                category="EXERCISE",
                priority="URGENT" if scores["musculoskeletal"] < 70.0 else "ROUTINE",
                duration_minutes=60,
                dosage_or_intensity="4x8 Reps @ 1.8x Earth BW Equivalent"
            ))
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Oral Calcium Citrate & Vitamin D3 Supplementation",
                description="Take 1000mg Calcium Citrate with 2000 IU Vitamin D3 to counteract microgravity bone demineralization and suppress PTH surge.",
                category="NUTRITION",
                priority="ROUTINE",
                duration_minutes=5,
                dosage_or_intensity="1 Tab Daily with Meal"
            ))

        # 4. CARDIOVASCULAR & ORTHOSTATIC DECONDITIONING
        if scores["cardiovascular"] < 80.0:
            focus_areas.append("Cardiovascular Autonomic Conditioning")
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="T2 Treadmill High-Intensity Interval Protocol",
                description="Perform 6 x 2-minute high-load running intervals at 85-90% VO2 max with harness bungee tension at 75% body weight.",
                category="EXERCISE",
                priority="ROUTINE",
                duration_minutes=35,
                dosage_or_intensity="Intervals: 85% Max HR"
            ))
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Plasma Volume Expansion (Electrolyte Salt Loading)",
                description="Consume 8 salt tablets (8g NaCl) dissolved in 1.0L water to expand intravascular volume and prevent orthostatic dysregulation.",
                category="NUTRITION",
                priority="ROUTINE",
                duration_minutes=10,
                dosage_or_intensity="1.0L Isotonic Saline"
            ))

        # 5. NEUROCOGNITIVE FATIGUE & CIRCADIAN DESYNCHRONIZATION
        if scores["cognitive_behavioral"] < 80.0:
            focus_areas.append("Circadian Resynchronization & Cognitive Reset")
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Blue-Enriched 480nm Phototherapy",
                description="Position workspace lighting to blue-enriched spectrum (480 nm, 10,000 lux equivalent) for 45 minutes to stimulate intrinsically photosensitive retinal ganglion cells and suppress daytime melatonin.",
                category="PSYCH_CIRCADIAN",
                priority="ROUTINE",
                duration_minutes=45,
                dosage_or_intensity="480nm Spectrum @ 10,000 Lux"
            ))
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Mandatory 30-Minute Micro-Rest & Task Re-delegation",
                description="Log off non-critical payload operations. Rest in acoustic dampening cabin with eye mask. Do not conduct docking or EVA maneuvers.",
                category="PSYCH_CIRCADIAN",
                priority="URGENT" if scores["cognitive_behavioral"] < 60.0 else "ROUTINE",
                duration_minutes=30,
                dosage_or_intensity="Complete Sensory Attenuation"
            ))

        # 6. CLOSED CABIN CO2 EMERGENCY
        if scores["cabin_environment"] < 75.0:
            focus_areas.append("Cabin Scrubber Maintenance")
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="ECLSS Secondary Scrubber Canister Changeout",
                description="Manually replace exhausted Amine/Metox CO2 removal bed with fresh regenerative sorbent canister in Module 3.",
                category="RADIATION",  # life-support category
                priority="EMERGENCY" if scores["cabin_environment"] < 50.0 else "URGENT",
                duration_minutes=25,
                dosage_or_intensity="ECLSS Bed B-2 Swap"
            ))

        # Default routine maintenance if everything is nominal
        if not actions:
            focus_areas.append("Routine Deep Space Maintenance")
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Nominal Daily ARED Resistance Conditioning",
                description="Maintain baseline skeletal loading with scheduled 45-min resistance workout.",
                category="EXERCISE",
                priority="ROUTINE",
                duration_minutes=45,
                dosage_or_intensity="Nominal Load Matrix"
            ))
            actions.append(ProtocolActionItem(
                id=str(uuid.uuid4())[:8],
                title="Standard Hydration & Micronutrient Intake",
                description="Consume scheduled 2.5L electrolyte-balanced water with daily space multivitamin.",
                category="NUTRITION",
                priority="ROUTINE",
                duration_minutes=5,
                dosage_or_intensity="2.5L Water + Vitamin D"
            ))

        focus_str = ", ".join(focus_areas)
        summary = (
            f"Autonomous clinical protocol generated for {astronaut_name}. "
            f"Focus: {focus_str}. "
            f"{len(actions)} specific action items assigned to counteract detected spaceflight hazards."
        )

        return CountermeasurePlan(
            plan_id=str(uuid.uuid4())[:12],
            astronaut_id=astronaut_id,
            generated_at=time.time(),
            hazard_focus=focus_str,
            severity_level=evaluation["status"],
            summary=summary,
            action_items=actions,
            re_evaluation_in_hours=8 if evaluation["status"] == "CRITICAL" else 12
        )
