from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.db.base import engine
import os

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "agentic-dev-team"}

@router.get("/readyz")
async def readiness_check():
    """Readiness check with database connectivity"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "service": "agentic-dev-team",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not ready",
                "service": "agentic-dev-team",
                "database": "disconnected",
                "error": str(e)
            }
        )
