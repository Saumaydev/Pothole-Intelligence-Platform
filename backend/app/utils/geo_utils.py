import math
from typing import List, Tuple
from shapely.geometry import LineString, Point
import numpy as np


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sample_points_along_line(
    coordinates: List[Tuple[float, float]], interval_meters: float
) -> List[dict]:
    if len(coordinates) < 2:
        return [
            {"lat": coordinates[0][0], "lng": coordinates[0][1], "distance": 0}
        ]

    line = LineString([(lng, lat) for lat, lng in coordinates])
    total_length_deg = line.length

    total_length_m = 0
    for i in range(len(coordinates) - 1):
        total_length_m += haversine_distance(
            coordinates[i][0], coordinates[i][1],
            coordinates[i + 1][0], coordinates[i + 1][1],
        )

    if total_length_m == 0:
        return [
            {"lat": coordinates[0][0], "lng": coordinates[0][1], "distance": 0}
        ]

    scale = total_length_deg / total_length_m
    interval_deg = interval_meters * scale

    sampled_points = []
    distance_covered = 0.0
    current_offset = 0.0

    while current_offset <= total_length_deg:
        point = line.interpolate(current_offset)
        sampled_points.append(
            {
                "lat": point.y,
                "lng": point.x,
                "distance": round(distance_covered, 2),
            }
        )
        current_offset += interval_deg
        distance_covered += interval_meters

    return sampled_points


def create_segments(
    sampled_points: List[dict], segment_length_points: int = 5
) -> List[dict]:
    segments = []
    for i in range(0, len(sampled_points) - 1, segment_length_points):
        end_idx = min(i + segment_length_points, len(sampled_points) - 1)
        start_pt = sampled_points[i]
        end_pt = sampled_points[end_idx]

        length = haversine_distance(
            start_pt["lat"], start_pt["lng"],
            end_pt["lat"], end_pt["lng"],
        )

        segments.append(
            {
                "segment_index": len(segments),
                "start_lat": start_pt["lat"],
                "start_lng": start_pt["lng"],
                "end_lat": end_pt["lat"],
                "end_lng": end_pt["lng"],
                "start_distance": start_pt["distance"],
                "end_distance": end_pt["distance"],
                "length_meters": round(length, 2),
                "point_indices": list(range(i, end_idx + 1)),
            }
        )

    return segments


def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
        lat2
    ) * math.cos(dlon)
    bearing = math.atan2(x, y)
    return (math.degrees(bearing) + 360) % 360