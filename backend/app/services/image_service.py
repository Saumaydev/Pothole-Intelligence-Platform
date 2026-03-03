import httpx
import os
import asyncio
import random
import numpy as np
from PIL import Image, ImageDraw
from typing import List, Dict, Any, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def acquire_images(
    sampled_points: List[dict],
) -> List[Dict[str, Any]]:
    results = []

    if settings.MAPILLARY_CLIENT_TOKEN:
        results = await _fetch_mapillary_images(sampled_points)

    fetched_count = sum(1 for r in results if r.get("image_path"))

    # Fill remaining points with simulated images for demo
    if fetched_count < len(sampled_points):
        logger.info(
            f"Mapillary returned {fetched_count}/{len(sampled_points)} images. "
            f"Generating simulated images for remaining points."
        )
        results = await _generate_simulated_images(sampled_points, results)

    return results


async def _fetch_mapillary_images(
    points: List[dict],
) -> List[Dict[str, Any]]:
    results = []
    base_url = "https://graph.mapillary.com/images"

    async with httpx.AsyncClient(timeout=15.0) as client:
        for i, point in enumerate(points):
            try:
                params = {
                    "access_token": settings.MAPILLARY_CLIENT_TOKEN,
                    "fields": "id,thumb_1024_url,computed_geometry",
                    "limit": 1,
                    "closeto": f"{point['lng']},{point['lat']}",
                    "radius": 50,
                }
                resp = await client.get(base_url, params=params)
                data = resp.json()
                images = data.get("data", [])

                if images:
                    img_data = images[0]
                    img_url = img_data.get("thumb_1024_url", "")
                    if img_url:
                        img_resp = await client.get(img_url)
                        path = os.path.join(
                            settings.TEMP_IMAGE_DIR, f"point_{i}.jpg"
                        )
                        with open(path, "wb") as f:
                            f.write(img_resp.content)
                        results.append(
                            {
                                "point_index": i,
                                "lat": point["lat"],
                                "lng": point["lng"],
                                "distance": point["distance"],
                                "image_path": path,
                                "source": "mapillary",
                                "image_id": img_data["id"],
                            }
                        )
                        continue

            except Exception as e:
                logger.debug(f"Mapillary fetch failed for point {i}: {e}")

            results.append(
                {
                    "point_index": i,
                    "lat": point["lat"],
                    "lng": point["lng"],
                    "distance": point["distance"],
                    "image_path": None,
                    "source": "none",
                }
            )
            await asyncio.sleep(0.1)

    return results


async def _generate_simulated_images(
    points: List[dict], existing_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    existing_map = {r["point_index"]: r for r in existing_results if r.get("image_path")}
    results = []

    for i, point in enumerate(points):
        if i in existing_map:
            results.append(existing_map[i])
            continue

        # Generate a simulated road image with potential potholes
        img_path = _create_simulated_road_image(i)
        results.append(
            {
                "point_index": i,
                "lat": point["lat"],
                "lng": point["lng"],
                "distance": point["distance"],
                "image_path": img_path,
                "source": "simulated",
            }
        )

    return results


def _create_simulated_road_image(index: int) -> str:
    width, height = 640, 640
    img = Image.new("RGB", (width, height), color=(80, 80, 80))
    draw = ImageDraw.Draw(img)

    # Draw road surface
    draw.rectangle(
        [100, 0, 540, 640], fill=(60, 60, 60)
    )

    # Draw lane markings
    for y in range(0, 640, 40):
        draw.rectangle(
            [315, y, 325, y + 20], fill=(200, 200, 200)
        )

    # Randomly add potholes (dark ellipses with rough edges)
    num_potholes = random.choices(
        [0, 1, 2, 3, 4, 5], weights=[20, 25, 25, 15, 10, 5]
    )[0]

    for _ in range(num_potholes):
        px = random.randint(140, 500)
        py = random.randint(50, 590)
        pw = random.randint(20, 80)
        ph = random.randint(15, 60)

        # Pothole shadow
        draw.ellipse(
            [px - pw // 2, py - ph // 2, px + pw // 2, py + ph // 2],
            fill=(30 + random.randint(-10, 10), 25 + random.randint(-10, 10), 20),
            outline=(20, 15, 10),
            width=2,
        )
        # Inner darker area
        iw, ih = pw // 2, ph // 2
        draw.ellipse(
            [px - iw // 2, py - ih // 2, px + iw // 2, py + ih // 2],
            fill=(15, 10, 8),
        )

    # Add noise
    pixels = np.array(img)
    noise = np.random.normal(0, 8, pixels.shape).astype(np.int16)
    pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)

    path = os.path.join(settings.TEMP_IMAGE_DIR, f"sim_point_{index}.jpg")
    img.save(path, quality=90)
    return path