"""
Physiological and Environmental Telemetry Simulator.
Generates realistic multi-modal telemetry for deep space transit crew,
supporting injected clinical crises and autonomous mission anomaly testing.
"""

import time
import math
import random
from typing import Dict, Any, List
from app.models.telemetry import PhysiologicalVitals, EnvironmentalTelemetry, TelemetrySnapshot

class TelemetrySimulator:
    def __init__(self):
        self.active_scenario: str = "NORMAL"
        self.scenario_start_time: float = 0.0
        self.tick_count: int = 0
        
        # Crew baseline settings
        self.crew_baselines = {
            "ASTRO-01": {"name": "Dr. Sarah Vance", "resting_hr": 64.0, "hrv_base": 55.0, "bp_sys": 116.0, "bp_dia": 74.0},
            "ASTRO-02": {"name": "Alexei Romanov", "resting_hr": 70.0, "hrv_base": 48.0, "bp_sys": 122.0, "bp_dia": 78.0},
            "ASTRO-03": {"name": "Maya Lin", "resting_hr": 74.0, "hrv_base": 36.0, "bp_sys": 128.0, "bp_dia": 82.0},  # Mild SANS / fatigue candidate
            "ASTRO-04": {"name": "Marcus Brody", "resting_hr": 68.0, "hrv_base": 50.0, "bp_sys": 120.0, "bp_dia": 76.0},
        }

        # Environmental baselines
        self.env_co2 = 2.1
        self.env_radiation = 19.2
        self.cumulative_dose = 38.65
        self.cabin_pressure = 14.65

    def set_scenario(self, scenario_name: str):
        self.active_scenario = scenario_name
        self.scenario_start_time = time.time()

    def generate_tick(self) -> TelemetrySnapshot:
        self.tick_count += 1
        now = time.time()
        circadian_phase = math.sin(self.tick_count * 0.05)

        # Environmental Telemetry Generation
        co2 = self.env_co2 + random.uniform(-0.05, 0.05)
        radiation = self.env_radiation + random.uniform(-0.5, 0.5)
        pressure = self.cabin_pressure + random.uniform(-0.01, 0.01)
        radiation_storm = False
        air_status = "OPTIMAL"

        # Apply Scenarios to Environment
        if self.active_scenario == "SOLAR_PARTICLE_EVENT":
            radiation = 320.0 + random.uniform(-15.0, 30.0)  # Severe SPE alert
            radiation_storm = True
            self.cumulative_dose += (radiation / 1000.0) * 0.01

        elif self.active_scenario == "CO2_SCRUBBER_MALFUNCTION":
            elapsed = min(120, now - self.scenario_start_time)
            co2 = 2.0 + (elapsed / 120.0) * 2.4 + random.uniform(-0.05, 0.05)  # Climbs past 4.0 mmHg
            if co2 > 3.5:
                air_status = "CRITICAL_CO2"
            else:
                air_status = "ELEVATED_CO2"

        env = EnvironmentalTelemetry(
            timestamp=now,
            cabin_co2_mmhg=round(co2, 2),
            cabin_o2_percent=round(21.2 + random.uniform(-0.1, 0.1), 1),
            cabin_pressure_psi=round(pressure, 2),
            cabin_temp_celsius=round(22.2 + random.uniform(-0.2, 0.2), 1),
            cabin_humidity_percent=round(44.0 + random.uniform(-1.0, 1.0), 1),
            radiation_dose_rate_ugy_hr=round(radiation, 1),
            cumulative_mission_dose_msv=round(self.cumulative_dose, 3),
            acoustic_noise_db=round(58.5 + random.uniform(-1.5, 1.5), 1),
            air_quality_status=air_status,
            radiation_storm_active=radiation_storm
        )

        # Crew Physiological Vitals Generation
        crew_vitals: Dict[str, PhysiologicalVitals] = {}

        for astro_id, base in self.crew_baselines.items():
            hr_noise = random.uniform(-1.5, 1.5)
            hr = base["resting_hr"] + circadian_phase * 3.0 + hr_noise
            hrv = base["hrv_base"] - circadian_phase * 4.0 + random.uniform(-2.0, 2.0)
            sys_bp = base["bp_sys"] + random.uniform(-2.0, 2.0)
            dia_bp = base["bp_dia"] + random.uniform(-1.5, 1.5)
            spo2 = 98.4 + random.uniform(-0.4, 0.3)
            stress = max(10.0, min(95.0, 30.0 - (hrv - 45.0) * 0.8 + random.uniform(-3.0, 3.0)))
            cardiac_status = "NOMINAL"
            resp_rate = 14.0 + random.uniform(-0.5, 0.5)

            # Scenario modifications for specific astronauts
            if self.active_scenario == "CO2_SCRUBBER_MALFUNCTION":
                # Everyone experiences elevated HR and mild hypercapnia tachypnea
                hr += 12.0
                resp_rate += 4.5
                sys_bp += 8.0
                stress += 25.0

            elif self.active_scenario == "SANS_OCULAR_CRISIS" and astro_id == "ASTRO-03":
                # Maya Lin experiences elevated cephalad arterial/venous pressure
                sys_bp += 18.0
                dia_bp += 10.0
                stress = 78.0

            elif self.active_scenario == "FATIGUE_EXHAUSTION" and astro_id in ("ASTRO-02", "ASTRO-03"):
                hrv = max(14.0, hrv - 22.0)
                stress = 84.0
                hr += 9.0

            elif self.active_scenario == "CARDIAC_ARRHYTHMIA_RISK" and astro_id == "ASTRO-04":
                hr = 108.0 + random.uniform(-8.0, 15.0)
                hrv = 18.0 + random.uniform(-3.0, 3.0)
                cardiac_status = "TACHYARRHYTHMIA_ALERT"
                stress = 88.0

            crew_vitals[astro_id] = PhysiologicalVitals(
                astronaut_id=astro_id,
                timestamp=now,
                heart_rate_bpm=round(hr, 1),
                hrv_rmssd_ms=round(hrv, 1),
                systolic_bp_mmhg=round(sys_bp, 1),
                diastolic_bp_mmhg=round(dia_bp, 1),
                spo2_percent=round(min(100.0, spo2), 1),
                respiration_rate_bpm=round(resp_rate, 1),
                core_temp_celsius=round(36.8 + random.uniform(-0.15, 0.15), 2),
                perfusion_index=round(2.5 + random.uniform(-0.3, 0.3), 1),
                stress_index=round(stress, 1),
                cardiac_status=cardiac_status
            )

        return TelemetrySnapshot(
            timestamp=now,
            crew_vitals=crew_vitals,
            environment=env,
            system_status="AUTONOMOUS_OPERATIONAL"
        )

# Global simulator instance
simulator = TelemetrySimulator()

