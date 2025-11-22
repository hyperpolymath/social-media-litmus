"""
NUJ Social Media Ethics Monitor - Analyzer Service
Purpose: NLP-powered analysis of policy changes
Tech: Python + FastAPI + OpenAI + spaCy
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.config import settings
from app.database import init_db
from app.routers import health, analysis, guidance
from app.workers import start_workers
from app.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    logger.info("Starting NUJ Analyzer Service")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Start background workers
    workers = await start_workers()
    logger.info("Background workers started")

    yield

    # Shutdown
    logger.info("Shutting down workers")
    for worker in workers:
        worker.cancel()

    logger.info("Analyzer service shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="NUJ Analyzer Service",
    description="NLP-powered policy change analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(guidance.router, prefix="/api/guidance", tags=["guidance"])

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "nuj-analyzer",
        "version": "0.1.0",
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.debug,
    )
