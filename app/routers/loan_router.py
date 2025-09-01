from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from pydantic import ValidationError

from app.models.loan_application import LoanApplicationRequest, LoanApplicationResponse
from app.models.validation import ErrorFormatter
from app.services.simple_loan_service import simple_loan_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/loans", tags=["loans"])

@router.post("/apply", response_model=Dict[str, Any])
async def apply_for_loan(request: LoanApplicationRequest):
    """
    Submit a new loan application
    
    This endpoint processes a complete loan application through:
    1. Customer creation/lookup
    2. Rule-based validation
    3. ML model evaluation
    4. Risk assessment
    5. Loan terms calculation (if approved)
    """
    try:
        logger.info(f"Received loan application for {request.customer_name}")
        
        # Process the loan application
        result = simple_loan_service.process_loan_application(request)
        
        # Prepare response
        response = {
            "application_id": result.application_id,
            "customer_id": result.customer_id,
            "status": result.status,
            "risk_category": result.risk_category,
            "decision_reason": result.decision_reason,
            "processing_time_ms": result.processing_time_ms
        }
        
        # Add loan terms if approved
        if result.loan_terms:
            response["loan_terms"] = result.loan_terms
        
        # Add simplified evaluation info
        response["evaluation_method"] = "rule_based_assessment"
        response["assessment_type"] = "automated_decision_engine"
        
        logger.info(f"Loan application processed successfully. ID: {result.application_id}, Status: {result.status}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error in loan application: {e}")
        error_response = ErrorFormatter.format_pydantic_error(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_response
        )
    
    except ValueError as e:
        logger.warning(f"Business rule error in loan application: {e}")
        error_response = ErrorFormatter.format_business_rule_error("application", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response
        )
    
    except Exception as e:
        logger.error(f"Unexpected error processing loan application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PROCESSING_ERROR",
                "message": "An error occurred while processing your loan application",
                "details": "Please try again later or contact support"
            }
        )

@router.get("/{application_id}/decision", response_model=Dict[str, Any])
async def get_loan_decision(application_id: int):
    """
    Get loan decision and terms for a specific application
    
    Returns complete information about the loan decision including:
    - Application status and risk category
    - Loan terms (if approved)
    - ML model predictions
    - Decision reasoning
    """
    try:
        logger.info(f"Retrieving loan decision for application {application_id}")
        
        # Get application decision
        decision_info = simple_loan_service.get_application_decision(application_id)
        
        logger.info(f"Retrieved loan decision for application {application_id}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=decision_info
        )
        
    except ValueError as e:
        logger.warning(f"Application not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "APPLICATION_NOT_FOUND",
                "message": f"Loan application {application_id} not found",
                "application_id": application_id
            }
        )
    
    except Exception as e:
        logger.error(f"Error retrieving loan decision: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "RETRIEVAL_ERROR",
                "message": "An error occurred while retrieving the loan decision",
                "application_id": application_id
            }
        )

@router.get("/applications/{application_id}", response_model=Dict[str, Any])
async def get_application_details(application_id: int):
    """
    Get detailed information about a specific loan application
    
    This is an alias for the decision endpoint for consistency
    """
    return await get_loan_decision(application_id)

@router.get("/status/{application_id}", response_model=Dict[str, Any])
async def get_application_status(application_id: int):
    """
    Get basic status information for a loan application
    
    Returns a simplified view with just the essential status information
    """
    try:
        logger.info(f"Retrieving application status for {application_id}")
        
        # Get full decision info
        decision_info = simple_loan_service.get_application_decision(application_id)
        
        # Return simplified status
        status_info = {
            "application_id": application_id,
            "status": decision_info["application"]["status"],
            "risk_category": decision_info["application"]["risk_category"],
            "application_date": decision_info["application"]["application_date"],
            "decision_reason": decision_info["application"]["decision_reason"]
        }
        
        # Add basic loan terms if approved
        if decision_info.get("loan_terms"):
            status_info["approved_amount"] = decision_info["loan_terms"]["approved_amount"]
            status_info["interest_rate"] = decision_info["loan_terms"]["interest_rate"]
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=status_info
        )
        
    except ValueError as e:
        logger.warning(f"Application not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "APPLICATION_NOT_FOUND",
                "message": f"Loan application {application_id} not found"
            }
        )
    
    except Exception as e:
        logger.error(f"Error retrieving application status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "STATUS_ERROR",
                "message": "An error occurred while retrieving the application status"
            }
        )