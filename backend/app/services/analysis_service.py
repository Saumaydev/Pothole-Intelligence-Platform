import numpy as np
from typing import List, Dict, Any
from app.utils.geo_utils import create_segments, haversine_distance
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def aggregate_results(
    detection_results: List[Dict[str, Any]],
    sampled_points: List[dict],
    road_data: Dict[str, Any],
) -> Dict[str, Any]:
    segments = create_segments(sampled_points, segment_length_points=5)

    all_detections = []
    for dr in detection_results:
        for det in dr.get("detections", []):
            all_detections.append(
                {
                    **det,
                    "latitude": dr["lat"],
                    "longitude": dr["lng"],
                    "distance_along_road": dr.get("distance", 0),
                    "point_index": dr["point_index"],
                }
            )

    segment_results = []
    for seg in segments:
        seg_detections = [
            d
            for d in all_detections
            if d["point_index"] in seg["point_indices"]
        ]

        pothole_count = len(seg_detections)
        length_km = seg["length_meters"] / 1000 if seg["length_meters"] > 0 else 0.001
        density = round(pothole_count / length_km, 2)

        avg_conf = (
            round(np.mean([d["confidence"] for d in seg_detections]), 4)
            if seg_detections else 0.0
        )

        severity_scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        avg_severity = (
            round(
                np.mean(
                    [severity_scores.get(d["severity"], 0.5) for d in seg_detections]
                ),
                4,
            )
            if seg_detections else 0.0
        )

        risk_level = _classify_risk(density, avg_severity)

        segment_results.append(
            {
                **seg,
                "pothole_count": pothole_count,
                "pothole_density": density,
                "avg_confidence": avg_conf,
                "avg_severity": avg_severity,
                "risk_level": risk_level,
            }
        )

    # Heatmap data
    heatmap_data = []
    for d in all_detections:
        severity_weight = {"low": 0.3, "medium": 0.6, "high": 0.85, "critical": 1.0}
        intensity = d["confidence"] * severity_weight.get(d["severity"], 0.5)
        heatmap_data.append(
            {
                "lat": d["latitude"],
                "lng": d["longitude"],
                "intensity": round(intensity, 4),
            }
        )

    # Severity distribution
    severity_dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for d in all_detections:
        severity_dist[d["severity"]] = severity_dist.get(d["severity"], 0) + 1

    # Confidence list
    confidence_scores = [d["confidence"] for d in all_detections]

    # Density along road
    density_along = [
        {
            "distance": seg["start_distance"],
            "density": seg_r["pothole_density"],
            "segment_index": seg_r["segment_index"],
        }
        for seg, seg_r in zip(segments, segment_results)
    ]

    # Cumulative potholes
    cumulative = []
    running_total = 0
    for seg_r in segment_results:
        running_total += seg_r["pothole_count"]
        cumulative.append(
            {
                "distance": seg_r["start_distance"],
                "cumulative_count": running_total,
                "segment_index": seg_r["segment_index"],
            }
        )

    total_potholes = len(all_detections)
    road_length_km = road_data["total_length_km"]
    avg_density = round(total_potholes / max(road_length_km, 0.01), 2)
    max_density = max(
        (s["pothole_density"] for s in segment_results), default=0
    )
    overall_risk = _classify_risk(avg_density, np.mean(
        [s["avg_severity"] for s in segment_results if s["avg_severity"] > 0]
    ) if segment_results else 0)

    return {
        "segments": segment_results,
        "all_detections": all_detections,
        "heatmap_data": heatmap_data,
        "severity_distribution": severity_dist,
        "confidence_scores": confidence_scores,
        "density_along_road": density_along,
        "cumulative_potholes": cumulative,
        "total_potholes": total_potholes,
        "avg_density": avg_density,
        "max_density": max_density,
        "overall_risk": overall_risk,
    }


def _classify_risk(density: float, avg_severity: float) -> str:
    score = 0.6 * min(density / 15, 1.0) + 0.4 * avg_severity

    if score < 0.2:
        return "safe"
    elif score < 0.45:
        return "moderate"
    elif score < 0.7:
        return "dangerous"
    else:
        return "critical"