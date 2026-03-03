import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    PROJECT_NAME: str = "Pothole Intelligence Platform"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR}/pothole_platform.db"
    )

    MAPILLARY_CLIENT_TOKEN: str = os.getenv("MAPILLARY_CLIENT_TOKEN", "")
    NOMINATIM_USER_AGENT: str = os.getenv(
        "NOMINATIM_USER_AGENT", "pothole-platform-v1"
    )

    SAMPLING_DISTANCE_METERS: int = int(
        os.getenv("SAMPLING_DISTANCE_METERS", "50")
    )
    CONFIDENCE_THRESHOLD: float = float(
        os.getenv("CONFIDENCE_THRESHOLD", "0.25")
    )

    YOLO_MODEL_PATH: str = os.getenv(
        "YOLO_MODEL_PATH", str(BASE_DIR / "trained_models" / "best.pt")
    )
    TEMP_IMAGE_DIR: str = os.getenv(
        "TEMP_IMAGE_DIR", str(BASE_DIR / "temp_images")
    )
    REPORTS_DIR: str = os.getenv(
        "REPORTS_DIR", str(BASE_DIR / "reports")
    )

    # Speed Prediction Constants
    BASE_SPEEDS = {
        "highway": 80,
        "urban": 50,
        "rural": 60,
        "residential": 30,
        "default": 50,
    }

    SEVERITY_THRESHOLDS = {
        "low": 0.35,
        "medium": 0.55,
        "high": 0.75,
        "critical": 1.0,
    }

    RISK_DENSITY_THRESHOLDS = {
        "safe": 2,
        "moderate": 5,
        "dangerous": 10,
        "critical": float("inf"),
    }


settings = Settings()
os.makedirs(settings.TEMP_IMAGE_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)