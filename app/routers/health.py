from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Meeting Performance Analyzer",
        "version": "1.0.0"
    }
