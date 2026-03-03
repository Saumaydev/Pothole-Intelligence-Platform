import httpx
import asyncio
from typing import List, Tuple, Dict, Any, Optional
from app.utils.geo_utils import haversine_distance, sample_points_along_line
import logging

logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"


async def get_road_geometry(
    road_name: str,
    center_lat: float,
    center_lng: float,
    search_radius: int = 5000,
) -> Dict[str, Any]:
    query = f"""
    [out:json][timeout:60];
    (
      way["name"~"{road_name}",i]
        (around:{search_radius},{center_lat},{center_lng});
      way["name:en"~"{road_name}",i]
        (around:{search_radius},{center_lat},{center_lng});
    );
    (._;>;);
    out body;
    """

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            OVERPASS_URL, data={"data": query}
        )
        response.raise_for_status()
        data = response.json()

    elements = data.get("elements", [])
    nodes = {
        e["id"]: (e["lat"], e["lon"])
        for e in elements
        if e["type"] == "node"
    }
    ways = [e for e in elements if e["type"] == "way"]

    if not ways:
        logger.warning(
            f"No ways found for '{road_name}', generating synthetic road"
        )
        return _generate_synthetic_road(center_lat, center_lng)

    road_type = "urban"
    for way in ways:
        tags = way.get("tags", {})
        highway = tags.get("highway", "")
        if highway in ("motorway", "trunk", "primary"):
            road_type = "highway"
        elif highway in ("residential", "living_street"):
            road_type = "residential"
        elif highway in ("unclassified", "track"):
            road_type = "rural"

    all_coordinates = []
    for way in ways:
        way_coords = []
        for node_id in way.get("nodes", []):
            if node_id in nodes:
                way_coords.append(nodes[node_id])
        if way_coords:
            all_coordinates.extend(way_coords)

    if len(all_coordinates) < 2:
        return _generate_synthetic_road(center_lat, center_lng)

    # Remove duplicates while preserving order
    seen = set()
    unique_coords = []
    for c in all_coordinates:
        key = (round(c[0], 7), round(c[1], 7))
        if key not in seen:
            seen.add(key)
            unique_coords.append(c)

    total_length = sum(
        haversine_distance(
            unique_coords[i][0], unique_coords[i][1],
            unique_coords[i + 1][0], unique_coords[i + 1][1],
        )
        for i in range(len(unique_coords) - 1)
    )

    logger.info(
        f"Road '{road_name}': {len(unique_coords)} nodes, "
        f"{total_length:.0f}m, type={road_type}"
    )

    return {
        "coordinates": unique_coords,
        "total_length_m": total_length,
        "total_length_km": round(total_length / 1000, 3),
        "node_count": len(unique_coords),
        "way_count": len(ways),
        "road_type": road_type,
    }


def _generate_synthetic_road(
    center_lat: float, center_lng: float, length_km: float = 2.0
) -> Dict[str, Any]:
    import numpy as np

    num_points = int(length_km * 20)
    coords = []
    lat, lng = center_lat, center_lng

    for i in range(num_points):
        lat += np.random.normal(0, 0.0002)
        lng += 0.0001 + np.random.normal(0, 0.00005)
        coords.append((round(lat, 7), round(lng, 7)))

    total_length = sum(
        haversine_distance(
            coords[i][0], coords[i][1],
            coords[i + 1][0], coords[i + 1][1],
        )
        for i in range(len(coords) - 1)
    )

    return {
        "coordinates": coords,
        "total_length_m": total_length,
        "total_length_km": round(total_length / 1000, 3),
        "node_count": len(coords),
        "way_count": 1,
        "road_type": "urban",
        "synthetic": True,
    }
