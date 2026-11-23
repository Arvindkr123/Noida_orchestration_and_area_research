
import logging

from fastapi import FastAPI

from app.api.research import router
from app.config import get_settings
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )
)

# Load settings once so the app metadata and configuration share the same values.
settings = get_settings()

# FastAPI uses this object to serve the API routes and generated /docs page.
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered research agent for Noida, India"
    )
)

# CORS lets the browser-based frontend call this API from its dev-server origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add the research endpoints defined in app/api/research.py to this application.
app.include_router(router)


@app.get("/")
async def root():

    return {
        "message": "Noida Research Agent is running",
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }
