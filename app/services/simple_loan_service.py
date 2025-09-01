"""
Simplified Loan Service - No ML dependencies required
Uses rule-based risk assessment for deployment compatibility
"""
from typing import Dict, Any, Optional, List
import logging
import time
from datetime import datetime
from dataclasses import dataclass

from app.models.loan_application import LoanApplicationRequest, LoanStatus
from app.services.simple_risk_assessment import risk_assessor, LoanApplication

logger = logging.getLogger(__name__)

@dataclass
class SimpleLoanProcessingResult:
    """Result of simplified loan processing"""
    application_id: int
    customer_id: int
    status: str
    risk_category: Optional[str]
    decision_reason: str
    loan_terms: Optional[Dict[str, Any]]
    processing_time_ms: int

class SimpleLoanProcessingService:
    """Simplified loan processing service without ML dependencies"""
    
    def __init__(self):
        # In-memory storage for demo purposes
        self.customers = {}
        self.applications = {}
        self.next_customer_id = 1
        self.next_application_id = 1
    
    def process_loan_application(self, request: LoanApplicationRequest) -> SimpleLoanProcessingResult:
        """Process loan application using rule-based assessment"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing loan application for {request.customer_name}")
            
            # Create customer
            customer_id = self._create_customer(request)
            
            # Create application
            application_id = self._create_application(customer_id, request)
            
            # Create loan application object for assessment
            loan_app = LoanApplication(
                customer_name=request.customer_name,
                customer_age=request.customer_age,
                customer_salary=request.customer_salary,
                customer_credit_score=request.customer_credit_score,
                loan_amount=request.loan_amount,
                existing_loans=request.existing_loans,
                monthly_income=request.monthly_income,
                employment_years=request.employment_years,
                preferred_tenure_years=request.preferred_tenure_years
            )
            
            # Assess risk
            assessment = risk_assessor.assess_risk(loan_app)
            
            # Map decision to status
            status_mapping = {
                "approved": LoanStatus.APPROVED.value,
                "rejected": LoanStatus.REJECTED.value,
                "manual_review": LoanStatus.MANUAL_REVIEW.value
            }
            
            status = status_mapping.get(assessment["decision"], LoanStatus.MANUAL_REVIEW.value)
            
            # Update application
            self._update_application(
                application_id, 
                status, 
                assessment["risk_category"], 
                assessment["decision_reason"]
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.info(f"Loan application processed: {status} in {processing_time}ms")
            
            return SimpleLoanProcessingResult(
                application_id=application_id,
                customer_id=customer_id,
                status=status,
                risk_category=assessment["risk_category"],
                decision_reason=assessment["decision_reason"],
                loan_terms=assessment["loan_terms"],
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing loan application: {e}")
            raise
    
    def _create_customer(self, request: LoanApplicationRequest) -> int:
        """Create customer record"""
        customer_id = self.next_customer_id
        self.next_customer_id += 1
        
        self.customers[customer_id] = {
            'id': customer_id,
            'name': request.customer_name,
            'age': request.customer_age,
            'salary': request.customer_salary,
            'credit_score': request.customer_credit_score,
            'created_at': datetime.now()
        }
        
        return customer_id
    
    def _create_application(self, customer_id: int, request: LoanApplicationRequest) -> int:
        """Create application record"""
        application_id = self.next_application_id
        self.next_application_id += 1
        
        self.applications[application_id] = {
            'id': application_id,
            'customer_id': customer_id,
            'loan_amount': request.loan_amount,
            'existing_loans': request.existing_loans,
            'monthly_income': request.monthly_income,
            'employment_years': request.employment_years,
            'preferred_tenure_years': request.preferred_tenure_years,
            'status': LoanStatus.PENDING.value,
            'risk_category': None,
            'decision_reason': None,
            'application_date': datetime.now()
        }
        
        return application_id
    
    def _update_application(self, application_id: int, status: str, 
                          risk_category: Optional[str], decision_reason: str):
        """Update application with decision"""
        if application_id in self.applications:
            self.applications[application_id].update({
                'status': status,
                'risk_category': risk_category,
                'decision_reason': decision_reason,
                'updated_at': datetime.now()
            })
    
    def get_application_decision(self, application_id: int) -> Dict[str, Any]:
        """Get application decision details"""
        if application_id not in self.applications:
            raise ValueError(f"Application {application_id} not found")
        
        app = self.applications[application_id]
        customer = self.customers.get(app['customer_id'], {})
        
        # Get loan terms if approved
        loan_terms = None
        if app['status'] == LoanStatus.APPROVED.value:
            # Recalculate loan terms for display
            loan_app = LoanApplication(
                customer_name=customer.get('name', ''),
                customer_age=customer.get('age', 0),
                customer_salary=customer.get('salary', 0),
                customer_credit_score=customer.get('credit_score', 0),
                loan_amount=app['loan_amount'],
                existing_loans=app['existing_loans'],
                monthly_income=app['monthly_income'],
                employment_years=app['employment_years'],
                preferred_tenure_years=app['preferred_tenure_years']
            )
            assessment = risk_assessor.assess_risk(loan_app)
            loan_terms = assessment.get('loan_terms')
        
        return {
            'application_id': application_id,
            'customer': {
                'id': customer.get('id'),
                'name': customer.get('name', 'Unknown'),
                'credit_score': customer.get('credit_score')
            },
            'application': {
                'loan_amount': app['loan_amount'],
                'status': app['status'],
                'risk_category': app['risk_category'],
                'decision_reason': app['decision_reason'],
                'application_date': app['application_date'].isoformat() if app['application_date'] else None
            },
            'loan_terms': loan_terms
        }
    
    def get_customer_loan_history(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get customer's loan history"""
        history = []
        
        for app_id, app in self.applications.items():
            if app['customer_id'] == customer_id:
                # Get loan terms if approved
                loan_terms = None
                if app['status'] == LoanStatus.APPROVED.value:
                    customer = self.customers.get(customer_id, {})
                    loan_app = LoanApplication(
                        customer_name=customer.get('name', ''),
                        customer_age=customer.get('age', 0),
                        customer_salary=customer.get('salary', 0),
                        customer_credit_score=customer.get('credit_score', 0),
                        loan_amount=app['loan_amount'],
                        existing_loans=app['existing_loans'],
                        monthly_income=app['monthly_income'],
                        employment_years=app['employment_years'],
                        preferred_tenure_years=app['preferred_tenure_years']
                    )
                    assessment = risk_assessor.assess_risk(loan_app)
                    loan_terms = assessment.get('loan_terms')
                
                history.append({
                    'application_id': app_id,
                    'loan_amount': app['loan_amount'],
                    'status': app['status'],
                    'risk_category': app['risk_category'],
                    'decision_reason': app['decision_reason'],
                    'application_date': app['application_date'].isoformat() if app['application_date'] else None,
                    'loan_terms': loan_terms
                })
        
        return history

# Global service instance
simple_loan_service = SimpleLoanProcessingService()