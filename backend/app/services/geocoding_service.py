import httpx
import asyncio
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


async def geocode_road(
    road_name: str,
    city: Optional[str] = None,
    state: Optional[str] = None,
) -> Dict[str, Any]:
    query_parts = [road_name]
    if city:
        query_parts.append(city)
    if state:
        query_parts.append(state)
    query_parts.append("India")
    query = ", ".join(query_parts)

    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "countrycodes": "in",
    }

    headers = {"User-Agent": settings.NOMINATIM_USER_AGENT}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            NOMINATIM_URL, params=params, headers=headers
        )
        response.raise_for_status()
        results = response.json()

    if not results:
        query_simple = f"{road_name}, India"
        params["q"] = query_simple
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                NOMINATIM_URL, params=params, headers=headers
            )
            results = response.json()

    if not results:
        raise ValueError(f"Could not find road: {road_name}")

    best = results[0]
    address = best.get("address", {})

    logger.info(f"Geocoded '{road_name}' → ({best['lat']}, {best['lon']})")

    return {
        "lat": float(best["lat"]),
        "lng": float(best["lon"]),
        "display_name": best.get("display_name", road_name),
        "osm_id": best.get("osm_id"),
        "osm_type": best.get("osm_type"),
        "city": address.get("city") or address.get("town") or address.get("village") or city,
        "state": address.get("state", state),
        "boundingbox": best.get("boundingbox"),
    }