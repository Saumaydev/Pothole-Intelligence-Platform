import os
import numpy as np
from typing import List, Dict, Any, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

_model = None


def load_model():
    global _model
    if _model is not None:
        return _model

    model_path = settings.YOLO_MODEL_PATH

    if os.path.exists(model_path):
        from ultralytics import YOLO
        _model = YOLO(model_path)
        logger.info(f"Loaded YOLO model from {model_path}")
    else:
        logger.warning(
            f"No trained model at {model_path}. Using simulation mode."
        )
        _model = "simulation"

    return _model


def detect_potholes_batch(
    image_data_list: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    model = load_model()
    results = []

    for img_data in image_data_list:
        img_path = img_data.get("image_path")
        if not img_path or not os.path.exists(img_path):
            results.append({**img_data, "detections": [], "pothole_count": 0})
            continue

        if model == "simulation":
            detections = _simulate_detection(img_data)
        else:
            detections = _run_yolo_detection(model, img_path)

        results.append(
            {
                **img_data,
                "detections": detections,
                "pothole_count": len(detections),
            }
        )

    total = sum(r["pothole_count"] for r in results)
    logger.info(
        f"Detection complete: {total} potholes in {len(results)} images"
    )
    return results


def _run_yolo_detection(model, image_path: str) -> List[Dict[str, Any]]:
    detections = []

    try:
        results = model(
            image_path,
            conf=settings.CONFIDENCE_THRESHOLD,
            imgsz=640,
            verbose=False,
        )

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])

                bbox_area = (x2 - x1) * (y2 - y1)
                img_area = 640 * 640
                relative_area = bbox_area / img_area

                severity = _classify_severity(conf, relative_area)

                detections.append(
                    {
                        "confidence": round(conf, 4),
                        "severity": severity,
                        "bbox": {
                            "x1": round(x1, 2),
                            "y1": round(y1, 2),
                            "x2": round(x2, 2),
                            "y2": round(y2, 2),
                        },
                        "bbox_area": round(bbox_area, 2),
                        "relative_area": round(relative_area, 6),
                        "class_id": cls,
                    }
                )
    except Exception as e:
        logger.error(f"YOLO detection error: {e}")

    return detections


def _simulate_detection(img_data: Dict) -> List[Dict[str, Any]]:
    import random

    num_potholes = random.choices(
        [0, 1, 2, 3, 4, 5, 6],
        weights=[15, 20, 25, 18, 12, 7, 3],
    )[0]

    detections = []
    for _ in range(num_potholes):
        conf = round(random.uniform(0.30, 0.95), 4)
        w = random.uniform(20, 120)
        h = random.uniform(15, 90)
        x1 = random.uniform(100, 520)
        y1 = random.uniform(50, 550)
        bbox_area = w * h
        relative_area = bbox_area / (640 * 640)

        severity = _classify_severity(conf, relative_area)

        detections.append(
            {
                "confidence": conf,
                "severity": severity,
                "bbox": {
                    "x1": round(x1, 2),
                    "y1": round(y1, 2),
                    "x2": round(x1 + w, 2),
                    "y2": round(y1 + h, 2),
                },
                "bbox_area": round(bbox_area, 2),
                "relative_area": round(relative_area, 6),
                "class_id": 0,
            }
        )

    return detections


def _classify_severity(confidence: float, relative_area: float) -> str:
    score = 0.6 * confidence + 0.4 * min(relative_area * 50, 1.0)

    if score < settings.SEVERITY_THRESHOLDS["low"]:
        return "low"
    elif score < settings.SEVERITY_THRESHOLDS["medium"]:
        return "medium"
    elif score < settings.SEVERITY_THRESHOLDS["high"]:
        return "high"
    else:
        return "critical"