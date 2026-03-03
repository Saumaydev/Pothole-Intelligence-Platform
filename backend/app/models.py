from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class RoadAnalysis(Base):
    __tablename__ = "road_analyses"

    id = Column(Integer, primary_key=True, index=True)
    road_name = Column(String(500), index=True, nullable=False)
    city = Column(String(200), nullable=True)
    state = Column(String(200), nullable=True)
    country = Column(String(100), default="India")

    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    road_length_km = Column(Float, nullable=False)
    road_type = Column(String(50), default="urban")

    total_points_sampled = Column(Integer, default=0)
    total_images_analyzed = Column(Integer, default=0)
    total_potholes_detected = Column(Integer, default=0)

    avg_pothole_density = Column(Float, default=0.0)
    max_pothole_density = Column(Float, default=0.0)
    overall_risk_level = Column(String(20), default="safe")

    avg_predicted_speed = Column(Float, nullable=True)
    min_predicted_speed = Column(Float, nullable=True)
    speed_reduction_pct = Column(Float, nullable=True)
    base_speed = Column(Float, nullable=True)

    road_polyline = Column(JSON, nullable=True)
    heatmap_data = Column(JSON, nullable=True)
    analysis_metadata = Column(JSON, nullable=True)

    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    segments = relationship(
        "RoadSegment", back_populates="analysis", cascade="all, delete-orphan"
    )
    detections = relationship(
        "PotholeDetection", back_populates="analysis", cascade="all, delete-orphan"
    )


class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("road_analyses.id"), nullable=False)
    segment_index = Column(Integer, nullable=False)

    start_lat = Column(Float, nullable=False)
    start_lng = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lng = Column(Float, nullable=False)
    length_meters = Column(Float, nullable=False)

    pothole_count = Column(Integer, default=0)
    pothole_density = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    avg_severity = Column(Float, default=0.0)

    risk_level = Column(String(20), default="safe")
    predicted_speed = Column(Float, nullable=True)
    speed_reduction = Column(Float, nullable=True)

    analysis = relationship("RoadAnalysis", back_populates="segments")


class PotholeDetection(Base):
    __tablename__ = "pothole_detections"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("road_analyses.id"), nullable=False)
    segment_index = Column(Integer, nullable=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    distance_along_road_m = Column(Float, nullable=True)

    confidence = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)
    bbox_x1 = Column(Float, nullable=True)
    bbox_y1 = Column(Float, nullable=True)
    bbox_x2 = Column(Float, nullable=True)
    bbox_y2 = Column(Float, nullable=True)
    bbox_area = Column(Float, nullable=True)

    image_path = Column(String(500), nullable=True)
    image_source = Column(String(50), default="mapillary")

    analysis = relationship("RoadAnalysis", back_populates="detections")