"""Health check router"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "analyzer",
        "timestamp": datetime.utcnow().isoformat(),
    }
