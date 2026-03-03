import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routes.analysis_routes import router as analysis_router
from app.routes.report_routes import router as report_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered road pothole detection and speed impact analysis platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix=settings.API_PREFIX)
app.include_router(report_router, prefix=settings.API_PREFIX)

# Serve temp images if needed
app.mount(
    "/images",
    StaticFiles(directory=settings.TEMP_IMAGE_DIR),
    name="images",
)


@app.on_event("startup")
async def startup():
    init_db()
    logging.getLogger(__name__).info(
        f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} started"
    )


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}