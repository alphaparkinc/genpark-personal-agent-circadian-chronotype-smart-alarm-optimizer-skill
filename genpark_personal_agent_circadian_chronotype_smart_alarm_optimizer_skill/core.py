# -*- coding: utf-8 -*-
"""Circadian Chronotype & Smart Alarm Optimizer Skill for GenPark Personal Health Agents."""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

def calculate_optimal_wake_window(bedtime_iso: str, target_cycles: int, chronotype: str, sleep_latency_minutes: int = 15) -> Dict[str, Any]:
    try:
        parts = bedtime_iso.split(":")
        b_hour = int(parts[0])
        b_min = int(parts[1])
    except Exception:
        return {"error": "Invalid bedtime_iso format, expected HH:MM"}

    now = datetime.now()
    bed_dt = now.replace(hour=b_hour, minute=b_min, second=0, microsecond=0)
    sleep_start = bed_dt + timedelta(minutes=sleep_latency_minutes)

    cycle_minutes = 90
    windows = []
    
    # Calculate for cycles (target - 1, target, target + 1)
    for c in range(max(3, target_cycles - 1), target_cycles + 2):
        wake_time = sleep_start + timedelta(minutes=c * cycle_minutes)
        total_hours = round((c * 90) / 60.0, 1)
        windows.append({
            "cycles": c,
            "total_sleep_hours": total_hours,
            "target_alarm_time": wake_time.strftime("%H:%M"),
            "recommended_smart_window": f"{(wake_time - timedelta(minutes=15)).strftime('%H:%M')} - {(wake_time + timedelta(minutes=10)).strftime('%H:%M')}",
            "is_preferred_target": (c == target_cycles)
        })

    # Morning Lux light schedule based on chronotype
    if chronotype == "wolf_night":
        lux_recommendation = "10,000 Lux light box for 20 mins within 45 mins of waking to advance circadian phase."
    elif chronotype == "lion_early":
        lux_recommendation = "Natural indirect sunlight within 10 mins of waking; delay heavy caffeine intake by 90 mins."
    else:
        lux_recommendation = "15-30 minutes outdoor natural sunlight exposure to trigger optimal Cortisol Awakening Response (CAR)."

    return {
        "chronotype": chronotype,
        "sleep_latency_allocated_minutes": sleep_latency_minutes,
        "calculated_wake_windows": windows,
        "morning_phototherapy_guidance": lux_recommendation,
        "circadian_engine": "GenPark Chronobiology Telemetry Service"
    }

def assess_sleep_inertia_mitigation(wake_state: str, sleep_debt_minutes: int) -> Dict[str, Any]:
    interventions = []
    
    if wake_state == "deep_slow_wave":
        severity = "HIGH"
        duration_est_minutes = 45
        interventions.append("Avoid immediate cognitive decision-making for 30 minutes.")
        interventions.append("Cold water facial splash or thermogenic temperature contrast.")
        interventions.append("Ingest 500ml water with electrolytes to reverse nocturnal dehydration.")
    elif wake_state == "rem_sleep":
        severity = "MODERATE"
        duration_est_minutes = 20
        interventions.append("Immediate blue-enriched ambient light exposure to suppress melatonin.")
        interventions.append("Light dynamic somatic stretching or zone-1 mobility flow.")
    else:
        severity = "MINIMAL"
        duration_est_minutes = 10
        interventions.append("Optimal awakening from light NREM sleep; proceed with planned morning routine.")

    if sleep_debt_minutes > 60:
        interventions.append(f"Cumulative sleep debt is {sleep_debt_minutes} mins; schedule a 20-minute restorative power nap between 13:00 and 15:00.")

    return {
        "wake_state": wake_state,
        "sleep_inertia_severity": severity,
        "estimated_inertia_clearance_minutes": duration_est_minutes,
        "evidence_based_protocols": interventions
    }
