import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def generate_pdf_report(analysis_data: Dict[str, Any]) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    road_safe = analysis_data["road_name"].replace(" ", "_")[:30]
    filename = f"pothole_report_{road_safe}_{timestamp}.pdf"
    filepath = os.path.join(settings.REPORTS_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title style
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=22, textColor=colors.HexColor("#1a237e"),
        spaceAfter=20,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle", parent=styles["Heading2"],
        fontSize=14, textColor=colors.HexColor("#283593"),
        spaceBefore=15, spaceAfter=10,
    )
    body_style = styles["Normal"]

    # Title
    elements.append(Paragraph("🛣️ POTHOLE INTELLIGENCE REPORT", title_style))
    elements.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}",
            body_style,
        )
    )
    elements.append(Spacer(1, 20))

    # Road Information
    elements.append(Paragraph("📍 Road Information", subtitle_style))
    road_info = [
        ["Road Name", analysis_data["road_name"]],
        ["City", analysis_data.get("city", "N/A")],
        ["State", analysis_data.get("state", "N/A")],
        ["Road Length", f"{analysis_data['road_length_km']} km"],
        ["Road Type", analysis_data.get("road_type", "urban").title()],
        ["GPS Center", f"{analysis_data['center_lat']:.5f}, {analysis_data['center_lng']:.5f}"],
    ]
    t = Table(road_info, colWidths=[3 * inch, 4 * inch])
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e3f2fd")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(t)
    elements.append(Spacer(1, 15))

    # Pothole Summary
    elements.append(Paragraph("🕳️ Pothole Detection Summary", subtitle_style))
    speed = analysis_data.get("speed_analysis", {})
    risk_color = {
        "safe": "#4caf50", "moderate": "#ff9800",
        "dangerous": "#f44336", "critical": "#b71c1c",
    }
    risk = analysis_data.get("overall_risk_level", "safe")

    summary = [
        ["Total Potholes Detected", str(analysis_data["total_potholes_detected"])],
        ["Points Sampled", str(analysis_data["total_points_sampled"])],
        ["Images Analyzed", str(analysis_data["total_images_analyzed"])],
        ["Average Density", f"{analysis_data['avg_pothole_density']} potholes/km"],
        ["Maximum Density", f"{analysis_data['max_pothole_density']} potholes/km"],
        ["Overall Risk Level", risk.upper()],
    ]
    t2 = Table(summary, colWidths=[3 * inch, 4 * inch])
    t2.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#fff3e0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(t2)
    elements.append(Spacer(1, 15))

    # Speed Impact
    elements.append(Paragraph("🚗 Speed Impact Analysis", subtitle_style))
    speed_data = [
        ["Base Speed (No Potholes)", f"{speed.get('base_speed', 'N/A')} km/h"],
        ["Average Predicted Speed", f"{speed.get('avg_predicted_speed', 'N/A')} km/h"],
        ["Minimum Predicted Speed", f"{speed.get('min_predicted_speed', 'N/A')} km/h"],
        ["Speed Reduction", f"{speed.get('speed_reduction_pct', 0)}%"],
        ["Normal Travel Time", f"{speed.get('normal_travel_time_min', 0)} min"],
        ["Actual Travel Time", f"{speed.get('actual_travel_time_min', 0)} min"],
        ["Time Delay", f"{speed.get('time_delay_min', 0)} min"],
    ]
    t3 = Table(speed_data, colWidths=[3 * inch, 4 * inch])
    t3.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8f5e9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(t3)
    elements.append(Spacer(1, 15))

    # Segment Details
    elements.append(Paragraph("📊 Segment-wise Analysis", subtitle_style))
    seg_header = [
        "Seg #", "Potholes", "Density\n(/km)",
        "Severity", "Risk", "Speed\n(km/h)", "Reduction"
    ]
    seg_rows = [seg_header]
    for seg in analysis_data.get("segments", [])[:20]:
        seg_rows.append([
            str(seg["segment_index"] + 1),
            str(seg["pothole_count"]),
            f"{seg['pothole_density']:.1f}",
            f"{seg['avg_severity']:.2f}",
            seg["risk_level"].title(),
            f"{seg['predicted_speed']:.1f}",
            f"{seg['speed_reduction']:.1f}%",
        ])

    t4 = Table(seg_rows, colWidths=[0.6*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 0.8*inch, 0.9*inch])
    t4.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ])
    )
    elements.append(t4)

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(
        Paragraph(
            "This report was auto-generated by the Pothole Intelligence Platform. "
            "Data is based on AI-powered analysis and should be verified for official use.",
            ParagraphStyle("Footer", parent=body_style, fontSize=8, textColor=colors.grey),
        )
    )

    doc.build(elements)
    logger.info(f"Report generated: {filepath}")
    return filepath