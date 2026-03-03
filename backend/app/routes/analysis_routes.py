import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RoadAnalysis, RoadSegment, PotholeDetection
from app.schemas import AnalysisRequest, AnalysisResponse, AnalysisListItem
from app.config import settings
from app.services import (
    geocoding_service,
    road_service,
    image_service,
    detection_service,
    analysis_service,
    speed_service,
)
from app.utils.geo_utils import sample_points_along_line

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["Analysis"])

# In-memory progress store (use Redis in production)
analysis_progress = {}


@router.post("/start", response_model=dict)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Create initial DB record
    db_analysis = RoadAnalysis(
        road_name=request.road_name,
        city=request.city,
        state=request.state,
        center_lat=0,
        center_lng=0,
        road_length_km=0,
        road_type=request.road_type or "urban",
        status="processing",
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    analysis_progress[db_analysis.id] = {
        "status": "processing",
        "step": "geocoding",
        "progress": 0,
        "message": "Starting analysis...",
    }

    # Run analysis in background
    background_tasks.add_task(
        run_full_analysis, db_analysis.id, request
    )

    return {
        "analysis_id": db_analysis.id,
        "status": "processing",
        "message": f"Analysis started for '{request.road_name}'",
    }


@router.get("/progress/{analysis_id}")
async def get_progress(analysis_id: int):
    if analysis_id in analysis_progress:
        return analysis_progress[analysis_id]
    return {"status": "unknown", "progress": 0, "message": "Analysis not found"}


@router.get("/result/{analysis_id}", response_model=AnalysisResponse)
async def get_result(analysis_id: int, db: Session = Depends(get_db)):
    db_analysis = (
        db.query(RoadAnalysis).filter(RoadAnalysis.id == analysis_id).first()
    )
    if not db_analysis:
        raise HTTPException(404, "Analysis not found")

    if db_analysis.status != "completed":
        raise HTTPException(
            400, f"Analysis not yet complete. Status: {db_analysis.status}"
        )

    segments = (
        db.query(RoadSegment)
        .filter(RoadSegment.analysis_id == analysis_id)
        .order_by(RoadSegment.segment_index)
        .all()
    )
    detections = (
        db.query(PotholeDetection)
        .filter(PotholeDetection.analysis_id == analysis_id)
        .all()
    )

    meta = db_analysis.analysis_metadata or {}

    seg_results = [
        {
            "segment_index": s.segment_index,
            "start_lat": s.start_lat,
            "start_lng": s.start_lng,
            "end_lat": s.end_lat,
            "end_lng": s.end_lng,
            "length_meters": s.length_meters,
            "pothole_count": s.pothole_count,
            "pothole_density": s.pothole_density,
            "avg_confidence": s.avg_confidence,
            "avg_severity": s.avg_severity,
            "risk_level": s.risk_level,
            "predicted_speed": s.predicted_speed or 0,
            "speed_reduction": s.speed_reduction or 0,
        }
        for s in segments
    ]

    det_results = [
        {
            "latitude": d.latitude,
            "longitude": d.longitude,
            "confidence": d.confidence,
            "severity": d.severity,
            "bbox": (
                {"x1": d.bbox_x1, "y1": d.bbox_y1, "x2": d.bbox_x2, "y2": d.bbox_y2}
                if d.bbox_x1 else None
            ),
            "bbox_area": d.bbox_area,
            "distance_along_road": d.distance_along_road_m,
        }
        for d in detections
    ]

    return AnalysisResponse(
        id=db_analysis.id,
        road_name=db_analysis.road_name,
        city=db_analysis.city,
        state=db_analysis.state,
        center_lat=db_analysis.center_lat,
        center_lng=db_analysis.center_lng,
        road_length_km=db_analysis.road_length_km,
        road_type=db_analysis.road_type,
        total_points_sampled=db_analysis.total_points_sampled,
        total_images_analyzed=db_analysis.total_images_analyzed,
        total_potholes_detected=db_analysis.total_potholes_detected,
        avg_pothole_density=db_analysis.avg_pothole_density,
        max_pothole_density=db_analysis.max_pothole_density,
        overall_risk_level=db_analysis.overall_risk_level,
        speed_analysis=meta.get("speed_analysis", {}),
        segments=seg_results,
        detections=det_results,
        heatmap_data=db_analysis.heatmap_data or [],
        road_polyline=db_analysis.road_polyline or [],
        severity_distribution=meta.get("severity_distribution", {}),
        confidence_scores=meta.get("confidence_scores", []),
        density_along_road=meta.get("density_along_road", []),
        cumulative_potholes=meta.get("cumulative_potholes", []),
        status=db_analysis.status,
        created_at=db_analysis.created_at,
        completed_at=db_analysis.completed_at,
    )


@router.get("/history", response_model=List[AnalysisListItem])
async def get_history(
    limit: int = 20, offset: int = 0, db: Session = Depends(get_db)
):
    analyses = (
        db.query(RoadAnalysis)
        .order_by(RoadAnalysis.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return analyses


async def run_full_analysis(analysis_id: int, request: AnalysisRequest):
    from app.database import SessionLocal

    db = SessionLocal()

    try:
        db_analysis = db.query(RoadAnalysis).filter(
            RoadAnalysis.id == analysis_id
        ).first()

        # STEP 1: Geocoding
        _update_progress(analysis_id, "geocoding", 5, "Geocoding road name...")
        geo_data = await geocoding_service.geocode_road(
            request.road_name, request.city, request.state
        )
        db_analysis.center_lat = geo_data["lat"]
        db_analysis.center_lng = geo_data["lng"]
        db_analysis.city = geo_data.get("city", request.city)
        db_analysis.state = geo_data.get("state", request.state)
        db.commit()

        # STEP 2: Road Extraction
        _update_progress(analysis_id, "road_extraction", 15, "Extracting road geometry from OpenStreetMap...")
        road_data = await road_service.get_road_geometry(
            request.road_name, geo_data["lat"], geo_data["lng"]
        )
        db_analysis.road_length_km = road_data["total_length_km"]
        db_analysis.road_type = road_data.get("road_type", request.road_type or "urban")
        db_analysis.road_polyline = [
            [lat, lng] for lat, lng in road_data["coordinates"]
        ]
        db.commit()

        # STEP 3: Point Sampling
        _update_progress(analysis_id, "sampling", 25, "Sampling points along road...")
        sampling_dist = request.sampling_distance or settings.SAMPLING_DISTANCE_METERS
        sampled_points = sample_points_along_line(
            road_data["coordinates"], sampling_dist
        )
        db_analysis.total_points_sampled = len(sampled_points)
        db.commit()

        # STEP 4: Image Acquisition
        _update_progress(analysis_id, "image_acquisition", 35, f"Acquiring {len(sampled_points)} street-level images...")
        image_results = await image_service.acquire_images(sampled_points)
        images_acquired = sum(1 for r in image_results if r.get("image_path"))
        db_analysis.total_images_analyzed = images_acquired
        db.commit()

        # STEP 5: Pothole Detection
        _update_progress(analysis_id, "detection", 55, "Running YOLOv8 pothole detection...")
        detection_results = detection_service.detect_potholes_batch(image_results)

        # STEP 6: Analysis & Aggregation
        _update_progress(analysis_id, "analysis", 75, "Aggregating results and computing statistics...")
        agg_results = analysis_service.aggregate_results(
            detection_results, sampled_points, road_data
        )

        # STEP 7: Speed Prediction
        _update_progress(analysis_id, "speed_prediction", 85, "Predicting speed impact...")
        speed_results = speed_service.predict_speed_impact(
            agg_results["segments"], db_analysis.road_type
        )

        # Merge speed into segments
        speed_map = {s["segment_index"]: s for s in speed_results["segments_speed"]}
        for seg in agg_results["segments"]:
            sp = speed_map.get(seg["segment_index"], {})
            seg["predicted_speed"] = sp.get("predicted_speed", speed_results["base_speed"])
            seg["speed_reduction"] = sp.get("speed_reduction_pct", 0)

        # STEP 8: Save to Database
        _update_progress(analysis_id, "saving", 92, "Saving results to database...")

        db_analysis.total_potholes_detected = agg_results["total_potholes"]
        db_analysis.avg_pothole_density = agg_results["avg_density"]
        db_analysis.max_pothole_density = agg_results["max_density"]
        db_analysis.overall_risk_level = agg_results["overall_risk"]
        db_analysis.avg_predicted_speed = speed_results["avg_predicted_speed"]
        db_analysis.min_predicted_speed = speed_results["min_predicted_speed"]
        db_analysis.speed_reduction_pct = speed_results["speed_reduction_pct"]
        db_analysis.base_speed = speed_results["base_speed"]
        db_analysis.heatmap_data = agg_results["heatmap_data"]
        db_analysis.analysis_metadata = {
            "speed_analysis": speed_results,
            "severity_distribution": agg_results["severity_distribution"],
            "confidence_scores": agg_results["confidence_scores"],
            "density_along_road": agg_results["density_along_road"],
            "cumulative_potholes": agg_results["cumulative_potholes"],
        }

        # Save segments
        for seg in agg_results["segments"]:
            db_seg = RoadSegment(
                analysis_id=analysis_id,
                segment_index=seg["segment_index"],
                start_lat=seg["start_lat"],
                start_lng=seg["start_lng"],
                end_lat=seg["end_lat"],
                end_lng=seg["end_lng"],
                length_meters=seg["length_meters"],
                pothole_count=seg["pothole_count"],
                pothole_density=seg["pothole_density"],
                avg_confidence=seg["avg_confidence"],
                avg_severity=seg["avg_severity"],
                risk_level=seg["risk_level"],
                predicted_speed=seg.get("predicted_speed"),
                speed_reduction=seg.get("speed_reduction"),
            )
            db.add(db_seg)

        # Save detections
        for det in agg_results["all_detections"]:
            bbox = det.get("bbox", {})
            db_det = PotholeDetection(
                analysis_id=analysis_id,
                latitude=det["latitude"],
                longitude=det["longitude"],
                distance_along_road_m=det.get("distance_along_road"),
                confidence=det["confidence"],
                severity=det["severity"],
                bbox_x1=bbox.get("x1"),
                bbox_y1=bbox.get("y1"),
                bbox_x2=bbox.get("x2"),
                bbox_y2=bbox.get("y2"),
                bbox_area=det.get("bbox_area"),
                image_source=det.get("source", "simulated"),
            )
            db.add(db_det)

        db_analysis.status = "completed"
        db_analysis.completed_at = datetime.utcnow()
        db.commit()

        _update_progress(analysis_id, "completed", 100, "Analysis complete!")
        logger.info(f"Analysis {analysis_id} completed successfully")

    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {e}")
        db_analysis.status = "failed"
        db_analysis.analysis_metadata = {"error": str(e)}
        db.commit()
        _update_progress(analysis_id, "failed", 0, f"Error: {str(e)}")

    finally:
        db.close()


def _update_progress(analysis_id, step, progress, message):
    analysis_progress[analysis_id] = {
        "status": "processing" if progress < 100 else "completed",
        "step": step,
        "progress": progress,
        "message": message,
    }