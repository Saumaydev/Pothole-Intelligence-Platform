import numpy as np
from typing import List, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def predict_speed_impact(
    segment_results: List[Dict[str, Any]],
    road_type: str = "urban",
) -> Dict[str, Any]:
    base_speed = settings.BASE_SPEEDS.get(road_type, 50)

    segments_speed = []
    predicted_speeds = []

    for seg in segment_results:
        density = seg["pothole_density"]
        avg_severity = seg["avg_severity"]
        pothole_count = seg["pothole_count"]

        predicted = _calculate_segment_speed(
            base_speed, density, avg_severity, pothole_count
        )

        speed_reduction = round(
            ((base_speed - predicted) / base_speed) * 100, 2
        )

        factors = _compute_speed_factors(density, avg_severity, pothole_count)

        segments_speed.append(
            {
                "segment_index": seg["segment_index"],
                "start_distance": seg.get("start_distance", 0),
                "base_speed": base_speed,
                "predicted_speed": predicted,
                "speed_reduction_pct": speed_reduction,
                "pothole_density": density,
                "avg_severity": avg_severity,
                "risk_level": seg["risk_level"],
                "factors": factors,
            }
        )
        predicted_speeds.append(predicted)

    avg_predicted = round(np.mean(predicted_speeds), 2) if predicted_speeds else base_speed
    min_predicted = round(min(predicted_speeds), 2) if predicted_speeds else base_speed
    max_predicted = round(max(predicted_speeds), 2) if predicted_speeds else base_speed

    overall_reduction = round(
        ((base_speed - avg_predicted) / base_speed) * 100, 2
    )

    overall_factors = {
        "density_impact": round(
            np.mean([s["factors"]["density_factor"] for s in segments_speed]), 4
        ),
        "severity_impact": round(
            np.mean([s["factors"]["severity_factor"] for s in segments_speed]), 4
        ),
        "avoidance_impact": round(
            np.mean([s["factors"]["avoidance_factor"] for s in segments_speed]), 4
        ),
    }

    # Time impact calculation
    if predicted_speeds and segment_results:
        total_distance_km = sum(s["length_meters"] for s in segment_results) / 1000
        normal_time_min = (total_distance_km / base_speed) * 60
        actual_time_min = sum(
            (seg["length_meters"] / 1000) / max(sp, 5) * 60
            for seg, sp in zip(segment_results, predicted_speeds)
        )
        time_delay_min = round(actual_time_min - normal_time_min, 2)
    else:
        normal_time_min = 0
        actual_time_min = 0
        time_delay_min = 0

    result = {
        "base_speed": base_speed,
        "avg_predicted_speed": avg_predicted,
        "min_predicted_speed": min_predicted,
        "max_predicted_speed": max_predicted,
        "speed_reduction_pct": overall_reduction,
        "segments_speed": segments_speed,
        "speed_factors": overall_factors,
        "normal_travel_time_min": round(normal_time_min, 2),
        "actual_travel_time_min": round(actual_time_min, 2),
        "time_delay_min": time_delay_min,
        "road_type": road_type,
    }

    logger.info(
        f"Speed analysis: base={base_speed} → avg={avg_predicted} km/h "
        f"({overall_reduction}% reduction), delay={time_delay_min} min"
    )

    return result


def _calculate_segment_speed(
    base_speed: float,
    density: float,
    avg_severity: float,
    pothole_count: int,
) -> float:
    # Factor 1: Density impact (more potholes → slower)
    # Research-based: ~6-8% speed reduction per pothole/km
    density_factor = max(0.25, 1 - 0.07 * density)

    # Factor 2: Severity impact (worse potholes → much slower)
    # Severe potholes cause up to 40% speed reduction
    severity_factor = max(0.35, 1 - 0.45 * avg_severity)

    # Factor 3: Driver avoidance behavior
    # Drivers swerve/brake more with many potholes
    if pothole_count == 0:
        avoidance_factor = 1.0
    elif pothole_count <= 2:
        avoidance_factor = 0.92
    elif pothole_count <= 5:
        avoidance_factor = 0.82
    else:
        avoidance_factor = max(0.55, 0.82 - 0.04 * (pothole_count - 5))

    # Combine all factors
    combined = density_factor * severity_factor * avoidance_factor
    predicted = base_speed * combined

    # Clamp to realistic bounds
    predicted = max(8, min(predicted, base_speed))

    return round(predicted, 2)


def _compute_speed_factors(
    density: float, avg_severity: float, pothole_count: int
) -> Dict[str, float]:
    density_factor = max(0.25, 1 - 0.07 * density)
    severity_factor = max(0.35, 1 - 0.45 * avg_severity)

    if pothole_count == 0:
        avoidance_factor = 1.0
    elif pothole_count <= 2:
        avoidance_factor = 0.92
    elif pothole_count <= 5:
        avoidance_factor = 0.82
    else:
        avoidance_factor = max(0.55, 0.82 - 0.04 * (pothole_count - 5))

    return {
        "density_factor": round(density_factor, 4),
        "severity_factor": round(severity_factor, 4),
        "avoidance_factor": round(avoidance_factor, 4),
        "combined_factor": round(
            density_factor * severity_factor * avoidance_factor, 4
        ),
    }