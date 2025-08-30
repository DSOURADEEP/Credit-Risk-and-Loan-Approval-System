from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import logging

from app.services.loan_service import loan_service
from app.repositories.customer_repository import CustomerRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])

@router.get("/{customer_id}/history", response_model=List[Dict[str, Any]])
async def get_customer_loan_history(customer_id: int):
    """
    Retrieve loan application history for a specific customer
    
    Returns all loan applications for the customer, sorted by application date (newest first)
    """
    try:
        logger.info(f"Retrieving loan history for customer {customer_id}")
        
        # Get customer loan history
        history = loan_service.get_customer_loan_history(customer_id)
        
        logger.info(f"Retrieved {len(history)} loan applications for customer {customer_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=history
        )
        
    except ValueError as e:
        logger.warning(f"Customer not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "CUSTOMER_NOT_FOUND",
                "message": f"Customer {customer_id} not found or has no loan history",
                "customer_id": customer_id
            }
        )
    
    except Exception as e:
        logger.error(f"Error retrieving customer loan history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "HISTORY_ERROR",
                "message": "An error occurred while retrieving loan history",
                "customer_id": customer_id
            }
        )

@router.get("/{customer_id}/profile", response_model=Dict[str, Any])
async def get_customer_profile(customer_id: int):
    """
    Get customer profile information
    
    Returns basic customer information and summary statistics
    """
    try:
        logger.info(f"Retrieving profile for customer {customer_id}")
        
        customer_repo = CustomerRepository()
        
        # Get customer details
        customer = customer_repo.get_customer_by_id(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Get loan history for statistics
        history = loan_service.get_customer_loan_history(customer_id)
        
        # Calculate summary statistics
        total_applications = len(history)
        approved_count = sum(1 for app in history if app['status'] == 'approved')
        rejected_count = sum(1 for app in history if app['status'] == 'rejected')
        pending_count = sum(1 for app in history if app['status'] == 'pending')
        manual_review_count = sum(1 for app in history if app['status'] == 'manual_review')
        
        total_approved_amount = sum(
            app['loan_terms']['approved_amount'] 
            for app in history 
            if app['status'] == 'approved' and app['loan_terms']
        )
        
        profile = {
            "customer_id": customer.id,
            "name": customer.name,
            "age": customer.age,
            "salary": customer.salary,
            "credit_score": customer.credit_score,
            "member_since": customer.created_at.isoformat() if customer.created_at else None,
            "loan_history_summary": {
                "total_applications": total_applications,
                "approved_applications": approved_count,
                "rejected_applications": rejected_count,
                "pending_applications": pending_count,
                "manual_review_applications": manual_review_count,
                "approval_rate": round((approved_count / total_applications * 100), 2) if total_applications > 0 else 0,
                "total_approved_amount": total_approved_amount
            }
        }
        
        logger.info(f"Retrieved profile for customer {customer_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=profile
        )
        
    except ValueError as e:
        logger.warning(f"Customer not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "CUSTOMER_NOT_FOUND",
                "message": f"Customer {customer_id} not found"
            }
        )
    
    except Exception as e:
        logger.error(f"Error retrieving customer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PROFILE_ERROR",
                "message": "An error occurred while retrieving customer profile"
            }
        )

@router.get("/{customer_id}/summary", response_model=Dict[str, Any])
async def get_customer_summary(customer_id: int):
    """
    Get a quick summary of customer information
    
    Returns essential customer info without detailed history
    """
    try:
        logger.info(f"Retrieving summary for customer {customer_id}")
        
        customer_repo = CustomerRepository()
        
        # Get customer details
        customer = customer_repo.get_customer_by_id(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Get basic loan statistics
        history = loan_service.get_customer_loan_history(customer_id)
        
        summary = {
            "customer_id": customer.id,
            "name": customer.name,
            "credit_score": customer.credit_score,
            "total_applications": len(history),
            "latest_application": history[0] if history else None
        }
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=summary
        )
        
    except ValueError as e:
        logger.warning(f"Customer not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "CUSTOMER_NOT_FOUND",
                "message": f"Customer {customer_id} not found"
            }
        )
    
    except Exception as e:
        logger.error(f"Error retrieving customer summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SUMMARY_ERROR",
                "message": "An error occurred while retrieving customer summary"
            }
        )