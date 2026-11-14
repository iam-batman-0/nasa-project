"""
Autonomous NASA Health Analyzer & Clinical Risk Engine.
Evaluates the 5 Hazards of Spaceflight and provides clinical triage
without requiring real-time Ground Support.
"""

from typing import Dict, Any, List
import math
from app.config import config
from app.models.telemetry import PhysiologicalVitals, EnvironmentalTelemetry
from app.models.assessment import PVTTestResult, SANSOcularExam, BiomarkerLog

class HealthAnalyzer:
    @staticmethod
    def evaluate_crew_member(
        vitals: PhysiologicalVitals,
        env: EnvironmentalTelemetry,
        latest_pvt: PVTTestResult = None,
        latest_ocular: SANSOcularExam = None,
        latest_biomarkers: BiomarkerLog = None,
        career_radiation_msv: float = 142.0,
        baseline_bmd_t_score: float = 0.5,
        current_bmd_t_score: float = 0.2
    ) -> Dict[str, Any]:
        """
        Produces multi-hazard scoring (0-100, where 0 is extreme danger and 100 is optimal)
        and diagnostic findings for a specific astronaut.
        """
        findings: List[str] = []
        alerts: List[Dict[str, str]] = []

        # -------------------------------------------------------------
        # 1. RADIATION HAZARD EVALUATION
        # -------------------------------------------------------------
        rad_score = 100.0
        # Instantaneous rate penalty
        if env.radiation_storm_active or env.radiation_dose_rate_ugy_hr > config.SPE_STORM_ALERT_UGY_HR:
            rad_score -= 65.0
            alerts.append({
                "type": "CRITICAL",
                "hazard": "RADIATION",
                "message": f"CRITICAL: Solar Particle Event detected! Dose rate at {env.radiation_dose_rate_ugy_hr} µGy/hr. Immediate storm shelter entry mandatory."
            })
            findings.append("Active high-energy particle shower exceeds bio-safety envelope.")
        elif env.radiation_dose_rate_ugy_hr > 50.0:
            rad_score -= 25.0
            findings.append("Elevated cosmic ray background observed.")

        # Cumulative career exposure check
        career_pct = (career_radiation_msv / config.CREW_COUNT) / 600.0 * 100.0
        if career_radiation_msv > 450.0:
            rad_score -= 20.0
            findings.append(f"Cumulative career radiation high: {career_radiation_msv:.1f} mSv.")

        rad_score = max(5.0, min(100.0, rad_score))

        # -------------------------------------------------------------
        # 2. CARDIOVASCULAR & ORTHOSTATIC RISK
        # -------------------------------------------------------------
        cardio_score = 100.0
        if vitals.cardiac_status == "TACHYARRHYTHMIA_ALERT" or vitals.heart_rate_bpm > 105.0:
            cardio_score -= 40.0
            alerts.append({
                "type": "CRITICAL",
                "hazard": "CARDIOVASCULAR",
                "message": f"Cardiac anomaly detected: Resting HR {vitals.heart_rate_bpm:.1f} bpm with autonomic tachycardia pattern."
            })
            findings.append("Autonomic tachycardia indicates cardiovascular deconditioning or acute stress.")
        elif vitals.heart_rate_bpm > config.RESTING_HR_MAX:
            cardio_score -= 15.0
            findings.append(f"Resting HR slightly elevated at {vitals.heart_rate_bpm:.1f} bpm.")

        # HRV analysis (Parasympathetic tone)
        if vitals.hrv_rmssd_ms < 20.0:
            cardio_score -= 25.0
            findings.append(f"Severely depressed HRV RMSSD ({vitals.hrv_rmssd_ms:.1f} ms) indicates autonomic exhaustion.")
        elif vitals.hrv_rmssd_ms < config.HRV_RMSSD_MIN_MS:
            cardio_score -= 10.0
            findings.append(f"Sub-optimal HRV RMSSD ({vitals.hrv_rmssd_ms:.1f} ms).")

        cardio_score = max(10.0, min(100.0, cardio_score))

        # -------------------------------------------------------------
        # 3. ALTERED GRAVITY: BONE MINERAL & MUSCLE ATROPHY
        # -------------------------------------------------------------
        bmd_score = 100.0
        bmd_delta = baseline_bmd_t_score - current_bmd_t_score
        # Space bone resorption is roughly 1-1.5% per month in microgravity
        monthly_loss_rate = bmd_delta / (184.0 / 30.0) * 100.0  # approximate % per month
        
        if current_bmd_t_score < -0.5:
            bmd_score -= 35.0
            alerts.append({
                "type": "CAUTION",
                "hazard": "MUSCULOSKELETAL",
                "message": f"Accelerated osteopenia: BMD T-score down to {current_bmd_t_score:.2f}."
            })
            findings.append("Trabecular bone loss exceeding nominal countermeasure threshold.")
        elif monthly_loss_rate > config.BMD_LOSS_CAUTION_RATE_PCT_MONTH:
            bmd_score -= 20.0
            findings.append(f"Projected bone mineral density loss rate ({monthly_loss_rate:.1f}%/mo) requires ARED load adjustment.")

        if latest_biomarkers and latest_biomarkers.urinary_ntx_nmol_bce_mmol_cr > 65.0:
            bmd_score -= 15.0
            findings.append(f"Urinary NTx resorption marker high ({latest_biomarkers.urinary_ntx_nmol_bce_mmol_cr:.1f} nmol BCE/mmol Cr).")

        bmd_score = max(15.0, min(100.0, bmd_score))

        # -------------------------------------------------------------
        # 4. SANS (SPACEFLIGHT-ASSOCIATED NEURO-OCULAR SYNDROME)
        # -------------------------------------------------------------
        sans_score = 100.0
        if latest_ocular:
            if latest_ocular.amsler_distortion:
                sans_score -= 30.0
                alerts.append({
                    "type": "CRITICAL",
                    "hazard": "SANS_OCULAR",
                    "message": "Amsler Grid exam reveals metamorphopsia / visual scotoma. Suspected posterior globe flattening."
                })
                findings.append("Positive Amsler grid distortion detected in ocular self-exam.")

            if latest_ocular.intraocular_pressure_est_mmhg > config.SANS_INTRAOCULAR_PRESSURE_MAX_MMHG:
                sans_score -= 25.0
                findings.append(f"Intraocular pressure elevated ({latest_ocular.intraocular_pressure_est_mmhg:.1f} mmHg) from cephalad fluid shift.")

            if latest_ocular.blurred_vision_score >= 5:
                sans_score -= 20.0
                findings.append(f"Subjective blurred vision score {latest_ocular.blurred_vision_score}/10.")
        else:
            # Baseline estimation from vitals & BP
            if vitals.systolic_bp_mmhg > 130.0:
                sans_score -= 10.0
                findings.append("Cephalad venous pressure likely elevated based on systemic blood pressure.")

        sans_score = max(10.0, min(100.0, sans_score))

        # -------------------------------------------------------------
        # 5. ISOLATION & NEUROCOGNITIVE PERFORMANCE (PVT)
        # -------------------------------------------------------------
        cog_score = 100.0
        if latest_pvt:
            if latest_pvt.lapse_count >= 4 or latest_pvt.mean_reaction_time_ms > 380.0:
                cog_score -= 40.0
                alerts.append({
                    "type": "CAUTION",
                    "hazard": "BEHAVIORAL_COGNITIVE",
                    "message": f"Cognitive degradation detected: {latest_pvt.lapse_count} PVT lapses with mean RT {latest_pvt.mean_reaction_time_ms:.0f} ms."
                })
                findings.append("High attentional lapse frequency indicates neurobehavioral fatigue or sleep debt.")
            elif latest_pvt.lapse_count >= 2:
                cog_score -= 15.0
                findings.append(f"Mild attentional drift: {latest_pvt.lapse_count} PVT lapses logged.")

            cog_score = min(cog_score, latest_pvt.cognitive_readiness_score)
        else:
            if vitals.stress_index > 70.0:
                cog_score -= 20.0
                findings.append(f"Sympathovagal stress index high ({vitals.stress_index:.1f}/100).")

        cog_score = max(10.0, min(100.0, cog_score))

        # -------------------------------------------------------------
        # 6. CLOSED CABIN ENVIRONMENT & CO2
        # -------------------------------------------------------------
        env_score = 100.0
        if env.cabin_co2_mmhg > config.CABIN_CO2_CRITICAL_MMHG:
            env_score -= 60.0
            alerts.append({
                "type": "CRITICAL",
                "hazard": "CABIN_ENVIRONMENT",
                "message": f"SEVERE HYPERCAPNIA RISK: Cabin CO2 at {env.cabin_co2_mmhg} mmHg. Acidosis and severe headaches imminent."
            })
            findings.append("Environmental CO2 above life-support safety threshold.")
        elif env.cabin_co2_mmhg > config.CABIN_CO2_CAUTION_MMHG:
            env_score -= 25.0
            alerts.append({
                "type": "CAUTION",
                "hazard": "CABIN_ENVIRONMENT",
                "message": f"Elevated Cabin CO2 ({env.cabin_co2_mmhg} mmHg). Scrubber efficiency degradation suspected."
            })
            findings.append("Mild cabin CO2 elevation; monitor for astronaut lethargy and frontal headaches.")

        env_score = max(10.0, min(100.0, env_score))

        # Overall Composite Health Score (Weighted)
        overall_health = (
            rad_score * 0.20 +
            cardio_score * 0.20 +
            bmd_score * 0.15 +
            sans_score * 0.15 +
            cog_score * 0.15 +
            env_score * 0.15
        )

        overall_health = round(overall_health, 1)

        # Status categorization
        if any(a["type"] == "CRITICAL" for a in alerts) or overall_health < 70.0:
            status = "CRITICAL"
        elif any(a["type"] == "CAUTION" for a in alerts) or overall_health < 85.0:
            status = "CAUTION"
        else:
            status = "NOMINAL"

        return {
            "overall_health_score": overall_health,
            "status": status,
            "hazard_scores": {
                "radiation": round(rad_score, 1),
                "cardiovascular": round(cardio_score, 1),
                "musculoskeletal": round(bmd_score, 1),
                "sans_ocular": round(sans_score, 1),
                "cognitive_behavioral": round(cog_score, 1),
                "cabin_environment": round(env_score, 1)
            },
            "alerts": alerts,
            "findings": findings
        }
