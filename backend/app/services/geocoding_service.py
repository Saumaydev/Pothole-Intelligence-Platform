import asyncio
import logging
from typing import Optional, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

cache = {}


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

    if query in cache:
        logger.info(f"Nominatim cache hit: {query}")
        return cache[query]

    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
        "countrycodes": "in",
    }

    headers = {
        "User-Agent": settings.NOMINATIM_USER_AGENT,
        "Accept": "application/json",
    }

    timeout = httpx.Timeout(
        connect=15.0,
        read=30.0,
        write=30.0,
        pool=30.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        headers=headers,
        follow_redirects=True,
    ) as client:

        for attempt in range(1, settings.GEOCODING_MAX_RETRIES + 1):

            try:
                if attempt > 1:
                    await asyncio.sleep(settings.GEOCODING_DELAY_SECONDS)

                logger.info(
                    f"Nominatim request attempt {attempt}/{settings.GEOCODING_MAX_RETRIES}: {query}"
                )

                response = await client.get(
                    NOMINATIM_URL,
                    params=params,
                )

                logger.info(
                    f"Nominatim response: {response.status_code}"
                )

                if response.status_code == 429:
                    logger.warning("Nominatim rate limit reached")
                    await asyncio.sleep(2 * attempt)
                    continue

                response.raise_for_status()

                results = response.json()

                if results:
                    result = _build_result(
                        results[0],
                        road_name,
                        city,
                        state,
                    )

                    cache[query] = result

                    logger.info(
                        f"Geocoded '{road_name}' -> "
                        f"{result['lat']}, {result['lng']}"
                    )

                    return result

                break

            except (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.NetworkError,
            ) as e:

                logger.warning(
                    f"Nominatim network error on attempt {attempt}: {e}"
                )

                if attempt == settings.GEOCODING_MAX_RETRIES:
                    raise RuntimeError(
                        f"Unable to connect to Nominatim after "
                        f"{settings.GEOCODING_MAX_RETRIES} attempts"
                    ) from e

            except httpx.HTTPStatusError as e:

                logger.error(
                    f"Nominatim HTTP error: "
                    f"{e.response.status_code}"
                )

                raise

            except Exception:
                logger.exception(
                    "Unexpected Nominatim error"
                )
                raise

    raise ValueError(
        f"Could not find road: {road_name}"
    )


def _build_result(
    best: Dict[str, Any],
    road_name: str,
    city: Optional[str],
    state: Optional[str],
) -> Dict[str, Any]:

    address = best.get("address", {})

    return {
        "lat": float(best["lat"]),
        "lng": float(best["lon"]),
        "display_name": best.get(
            "display_name",
            road_name
        ),
        "osm_id": best.get("osm_id"),
        "osm_type": best.get("osm_type"),
        "city": (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or city
        ),
        "state": address.get("state", state),
        "boundingbox": best.get("boundingbox"),
    }
