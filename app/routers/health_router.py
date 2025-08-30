from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime

from app.database import test_connection
from app.services.ml_service import ml_service
from app.repositories.customer_repository import CustomerRepository
from app.repositories.loan_repository import LoanApplicationRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Basic health check endpoint
    
    Returns the overall health status of the system
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "credit-risk-loan-approval",
            "version": "1.0.0"
        }
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=health_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """
    Detailed health check endpoint
    
    Returns comprehensive health information about all system components
    """
    try:
        health_info = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "credit-risk-loan-approval",
            "version": "1.0.0",
            "components": {}
        }
        
        # Check database connectivity
        try:
            db_healthy = test_connection()
            health_info["components"]["database"] = {
                "status": "healthy" if db_healthy else "unhealthy",
                "type": "MySQL",
                "connection_test": db_healthy
            }
        except Exception as e:
            health_info["components"]["database"] = {
                "status": "unhealthy",
                "type": "MySQL",
                "error": str(e)
            }
        
        # Check ML service
        try:
            ml_ready = ml_service.is_ready()
            ml_info = ml_service.get_model_info() if ml_ready else {}
            
            health_info["components"]["ml_service"] = {
                "status": "healthy" if ml_ready else "unhealthy",
                "models_loaded": ml_info.get("models_loaded", []),
                "ready": ml_ready
            }
        except Exception as e:
            health_info["components"]["ml_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check repositories
        try:
            customer_repo = CustomerRepository()
            loan_repo = LoanApplicationRepository()
            
            # Test basic repository operations
            customer_count = customer_repo.count()
            loan_count = loan_repo.count()
            
            health_info["components"]["repositories"] = {
                "status": "healthy",
                "customer_count": customer_count,
                "loan_application_count": loan_count
            }
        except Exception as e:
            health_info["components"]["repositories"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Determine overall status
        component_statuses = [comp["status"] for comp in health_info["components"].values()]
        if all(status == "healthy" for status in component_statuses):
            overall_status = "healthy"
            http_status = status.HTTP_200_OK
        elif any(status == "healthy" for status in component_statuses):
            overall_status = "degraded"
            http_status = status.HTTP_200_OK
        else:
            overall_status = "unhealthy"
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        health_info["status"] = overall_status
        
        return JSONResponse(
            status_code=http_status,
            content=health_info
        )
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/health/database", response_model=Dict[str, Any])
async def database_health_check():
    """
    Database-specific health check
    
    Tests database connectivity and returns connection information
    """
    try:
        db_healthy = test_connection()
        
        if db_healthy:
            # Get some basic statistics
            customer_repo = CustomerRepository()
            loan_repo = LoanApplicationRepository()
            
            stats = {
                "status": "healthy",
                "connection": "active",
                "statistics": {
                    "total_customers": customer_repo.count(),
                    "total_applications": loan_repo.count(),
                    "customer_stats": customer_repo.get_customer_statistics(),
                    "application_stats": loan_repo.get_application_statistics()
                }
            }
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=stats
            )
        else:
            raise Exception("Database connection test failed")
            
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e)
            }
        )

@router.get("/health/ml", response_model=Dict[str, Any])
async def ml_service_health_check():
    """
    ML service-specific health check
    
    Tests ML model availability and returns model information
    """
    try:
        ml_ready = ml_service.is_ready()
        
        if ml_ready:
            ml_info = ml_service.get_model_info()
            
            health_status = {
                "status": "healthy",
                "ready": True,
                "models": ml_info
            }
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=health_status
            )
        else:
            raise Exception("ML service not ready")
            
    except Exception as e:
        logger.error(f"ML service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "ready": False,
                "error": str(e)
            }
        )