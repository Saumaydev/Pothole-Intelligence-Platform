import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RoadAnalysis, RoadSegment
from app.services.report_service import generate_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])


# -------------------- PDF DOWNLOAD --------------------
@router.get("/download/{analysis_id}")
async def download_report(analysis_id: int, db: Session = Depends(get_db)):

    db_analysis = (
        db.query(RoadAnalysis)
        .filter(RoadAnalysis.id == analysis_id)
        .first()
    )

    if not db_analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if db_analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet complete")

    segments = (
        db.query(RoadSegment)
        .filter(RoadSegment.analysis_id == analysis_id)
        .order_by(RoadSegment.segment_index)
        .all()
    )

    meta = db_analysis.analysis_metadata or {}

    report_data = {
        "road_name": db_analysis.road_name,
        "city": db_analysis.city,
        "state": db_analysis.state,
        "center_lat": db_analysis.center_lat,
        "center_lng": db_analysis.center_lng,
        "road_length_km": db_analysis.road_length_km,
        "road_type": db_analysis.road_type,
        "total_points_sampled": db_analysis.total_points_sampled,
        "total_images_analyzed": db_analysis.total_images_analyzed,
        "total_potholes_detected": db_analysis.total_potholes_detected,
        "avg_pothole_density": db_analysis.avg_pothole_density,
        "max_pothole_density": db_analysis.max_pothole_density,
        "overall_risk_level": db_analysis.overall_risk_level,
        "speed_analysis": meta.get("speed_analysis", {}),
        "segments": [
            {
                "segment_index": s.segment_index,
                "pothole_count": s.pothole_count,
                "pothole_density": s.pothole_density,
                "avg_severity": s.avg_severity,
                "risk_level": s.risk_level,
                "predicted_speed": s.predicted_speed or 0,
                "speed_reduction": s.speed_reduction or 0,
            }
            for s in segments
        ],
    }

    filepath = generate_pdf_report(report_data)

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=os.path.basename(filepath),
    )


# -------------------- CSV DOWNLOAD --------------------
@router.get("/download-csv/{analysis_id}")
async def download_csv(analysis_id: int, db: Session = Depends(get_db)):

    db_analysis = (
        db.query(RoadAnalysis)
        .filter(RoadAnalysis.id == analysis_id)
        .first()
    )

    if not db_analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if db_analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet complete")

    segments = (
        db.query(RoadSegment)
        .filter(RoadSegment.analysis_id == analysis_id)
        .order_by(RoadSegment.segment_index)
        .all()
    )

    # Build CSV rows (one row per segment)
    rows = []

    for s in segments:
        rows.append({
            "analysis_id": analysis_id,
            "road_name": db_analysis.road_name,
            "city": db_analysis.city,
            "state": db_analysis.state,
            "road_length_km": db_analysis.road_length_km,
            "segment_index": s.segment_index,
            "pothole_count": s.pothole_count,
            "pothole_density_per_km": s.pothole_density,
            "avg_severity": s.avg_severity,
            "risk_level": s.risk_level,
            "predicted_speed_kmh": s.predicted_speed or 0,
            "speed_reduction_percent": s.speed_reduction or 0,
            "total_potholes_detected": db_analysis.total_potholes_detected,
            "overall_risk_level": db_analysis.overall_risk_level,
        })

    if not rows:
        raise HTTPException(status_code=400, detail="No segment data available")

    df = pd.DataFrame(rows)

    file_path = f"analysis_{analysis_id}_report.csv"
    df.to_csv(file_path, index=False)

    return FileResponse(
        file_path,
        media_type="text/csv",
        filename=file_path,
    )