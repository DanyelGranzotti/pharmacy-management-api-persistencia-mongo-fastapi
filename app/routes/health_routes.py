from fastapi import APIRouter, status
from app.config.database import check_database_connection

router = APIRouter()

@router.get("/health", 
    response_description="Check API and database health",
    tags=["Health"])
async def health_check():
    db_health = await check_database_connection()
    
    response = {
        "api": "healthy",
        "database": db_health
    }
    
    if db_health["status"] == "unhealthy":
        return response, status.HTTP_503_SERVICE_UNAVAILABLE
        
    return response
