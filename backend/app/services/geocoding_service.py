import httpx
import asyncio
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# ✅ Simple in-memory cache
cache = {}


# ---------------- MAIN FUNCTION ----------------
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

    # ✅ CACHE CHECK
    if query in cache:
        logger.info(f"Cache hit for: {query}")
        return cache[query]

    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "countrycodes": "in",
    }

    headers = {
        "User-Agent": settings.NOMINATIM_USER_AGENT
    }

    # ✅ RETRY LOGIC
    results = None
    for attempt in range(settings.GEOCODING_MAX_RETRIES):

        try:
            await asyncio.sleep(settings.GEOCODING_DELAY_SECONDS)  # ✅ DELAY

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    NOMINATIM_URL, params=params, headers=headers
                )

                if response.status_code == 429:
                    logger.warning("429 Too Many Requests → retrying...")
                    await asyncio.sleep(2)
                    continue

                response.raise_for_status()
                results = response.json()

            if results:
                break

        except Exception as e:
            logger.error(f"Geocoding attempt {attempt+1} failed: {e}")
            await asyncio.sleep(2)

    # ✅ FALLBACK SIMPLE QUERY
    if not results:
        query_simple = f"{road_name}, India"
        params["q"] = query_simple

        await asyncio.sleep(settings.GEOCODING_DELAY_SECONDS)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                NOMINATIM_URL, params=params, headers=headers
            )
            if response.status_code == 429:
                logger.warning("Rate limited (429)")
                return None

            if response.status_code != 200:
                logger.error(f"Bad response: {response.status_code}")
                return None

            if not response.text.strip():
                logger.error("Empty response received")
                return None

            try:
                results = response.json()
            except Exception as e:
                logger.error(f"JSON parse error: {e}")
                return None

    if not results:
        raise ValueError(f"Could not find road: {road_name}")

    best = results[0]
    address = best.get("address", {})

    result = {
        "lat": float(best["lat"]),
        "lng": float(best["lon"]),
        "display_name": best.get("display_name", road_name),
        "osm_id": best.get("osm_id"),
        "osm_type": best.get("osm_type"),
        "city": address.get("city")
        or address.get("town")
        or address.get("village")
        or city,
        "state": address.get("state", state),
        "boundingbox": best.get("boundingbox"),
    }

    # ✅ SAVE TO CACHE
    cache[query] = result

    logger.info(f"Geocoded '{road_name}' → ({best['lat']}, {best['lon']})")

    return result
