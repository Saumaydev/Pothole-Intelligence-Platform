from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    road_name: str = Field(..., min_length=3, description="Name of the road in India")
    city: Optional[str] = Field(None, description="City name for better geocoding")
    state: Optional[str] = Field(None, description="State name")
    road_type: Optional[str] = Field("urban", description="highway|urban|rural|residential")
    sampling_distance: Optional[int] = Field(50, description="Distance between sample points in meters")


class CoordinatePoint(BaseModel):
    lat: float
    lng: float
    distance_along_road: Optional[float] = None


class DetectionResult(BaseModel):
    latitude: float
    longitude: float
    confidence: float
    severity: str
    bbox: Optional[Dict[str, float]] = None
    bbox_area: Optional[float] = None
    distance_along_road: Optional[float] = None


class SegmentResult(BaseModel):
    segment_index: int
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    length_meters: float
    pothole_count: int
    pothole_density: float
    avg_confidence: float
    avg_severity: float
    risk_level: str
    predicted_speed: float
    speed_reduction: float


class SpeedAnalysis(BaseModel):
    base_speed: float
    avg_predicted_speed: float
    min_predicted_speed: float
    max_predicted_speed: float
    speed_reduction_pct: float
    segments_speed: List[Dict[str, Any]]
    speed_factors: Dict[str, float]


class HeatmapPoint(BaseModel):
    lat: float
    lng: float
    intensity: float


class AnalysisResponse(BaseModel):
    id: int
    road_name: str
    city: Optional[str]
    state: Optional[str]
    center_lat: float
    center_lng: float
    road_length_km: float
    road_type: str

    total_points_sampled: int
    total_images_analyzed: int
    total_potholes_detected: int
    avg_pothole_density: float
    max_pothole_density: float
    overall_risk_level: str

    speed_analysis: SpeedAnalysis
    segments: List[SegmentResult]
    detections: List[DetectionResult]
    heatmap_data: List[HeatmapPoint]
    road_polyline: List[List[float]]

    severity_distribution: Dict[str, int]
    confidence_scores: List[float]
    density_along_road: List[Dict[str, float]]
    cumulative_potholes: List[Dict[str, float]]

    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AnalysisListItem(BaseModel):
    id: int
    road_name: str
    city: Optional[str]
    total_potholes_detected: int
    overall_risk_level: str
    avg_predicted_speed: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True