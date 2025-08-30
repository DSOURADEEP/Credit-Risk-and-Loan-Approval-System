from typing import Dict, Any, Optional, Tuple, List
import logging
from datetime import datetime
from dataclasses import dataclass

from app.models.loan_application import LoanApplicationRequest, LoanApplicationResponse, LoanStatus
from app.models.customer import Customer, CustomerRequest
from app.models.ml_prediction import MLPredictionRequest
from app.repositories.customer_repository import CustomerRepository
from app.repositories.loan_repository import LoanApplicationRepository
from app.repositories.ml_prediction_repository import MLPredictionRepository
from app.repositories.loan_terms_repository import LoanTermsRepository
from app.services.rule_engine import LoanRuleEngine, RuleEngineResult
from app.services.ml_service import ml_service
from app.services.risk_assessment import risk_service

logger = logging.getLogger(__name__)

@dataclass
class LoanProcessingResult:
    """Result of loan processing workflow"""
    application_id: int
    customer_id: int
    status: str
    risk_category: Optional[str]
    decision_reason: str
    rule_engine_result: Optional[RuleEngineResult]
    ml_prediction_result: Optional[Dict[str, Any]]
    loan_terms: Optional[Dict[str, Any]]
    processing_time_ms: int

class LoanProcessingService:
    """Core service for processing loan applications"""
    
    def __init__(self):
        self.customer_repo = CustomerRepository()
        self.loan_repo = LoanApplicationRepository()
        self.ml_prediction_repo = MLPredictionRepository()
        self.loan_terms_repo = LoanTermsRepository()
        self.rule_engine = LoanRuleEngine()
    
    def process_loan_application(self, request: LoanApplicationRequest) -> LoanProcessingResult:
        """Process a complete loan application through the workflow"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting loan application processing for {request.customer_name}")
            
            # Step 1: Create or find customer
            customer_id = self._handle_customer(request)
            
            # Step 2: Create loan application record
            application_id = self._create_loan_application(customer_id, request)
            
            # Step 3: Run rule-based validation
            rule_result = self._run_rule_engine(request)
            
            # Step 4: Determine if we should proceed based on rules
            if rule_result.decision == "rejected":
                # Rules failed - reject immediately
                self._update_application_status(
                    application_id, LoanStatus.REJECTED, None, rule_result.reason
                )
                
                processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return LoanProcessingResult(
                    application_id=application_id,
                    customer_id=customer_id,
                    status=LoanStatus.REJECTED.value,
                    risk_category=None,
                    decision_reason=rule_result.reason,
                    rule_engine_result=rule_result,
                    ml_prediction_result=None,
                    loan_terms=None,
                    processing_time_ms=processing_time
                )
            
            # Step 5: Run ML models
            ml_result = self._run_ml_prediction(request, application_id)
            
            # Step 6: Combine rule and ML results for final decision
            final_status, risk_category, decision_reason = self._make_final_decision(
                rule_result, ml_result
            )
            
            # Step 7: Calculate loan terms if approved
            loan_terms = None
            if final_status == LoanStatus.APPROVED.value:
                loan_terms = self._calculate_and_store_loan_terms(
                    application_id, request, risk_category, ml_result
                )
            
            # Step 8: Update application with final decision
            self._update_application_status(
                application_id, final_status, risk_category, decision_reason
            )
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            logger.info(f"Loan application processing completed. Status: {final_status}, Time: {processing_time}ms")
            
            return LoanProcessingResult(
                application_id=application_id,
                customer_id=customer_id,
                status=final_status,
                risk_category=risk_category,
                decision_reason=decision_reason,
                rule_engine_result=rule_result,
                ml_prediction_result=ml_result,
                loan_terms=loan_terms,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing loan application: {e}")
            # Try to update application status to indicate error
            try:
                if 'application_id' in locals():
                    self._update_application_status(
                        application_id, LoanStatus.MANUAL_REVIEW.value, None, 
                        f"Processing error: {str(e)}"
                    )
            except:
                pass
            raise
    
    def _handle_customer(self, request: LoanApplicationRequest) -> int:
        """Create or find existing customer"""
        try:
            # Try to find existing customer
            existing_customer = self.customer_repo.find_customer_by_name_and_details(
                request.customer_name, request.customer_age, request.customer_credit_score
            )
            
            if existing_customer:
                logger.info(f"Found existing customer with ID: {existing_customer.id}")
                return existing_customer.id
            
            # Create new customer
            customer_data = {
                'name': request.customer_name,
                'age': request.customer_age,
                'salary': request.customer_salary,
                'credit_score': request.customer_credit_score
            }
            
            customer_id = self.customer_repo.create_customer(customer_data)
            logger.info(f"Created new customer with ID: {customer_id}")
            return customer_id
            
        except Exception as e:
            logger.error(f"Error handling customer: {e}")
            raise
    
    def _create_loan_application(self, customer_id: int, request: LoanApplicationRequest) -> int:
        """Create loan application record"""
        try:
            application_data = {
                'customer_id': customer_id,
                'loan_amount': request.loan_amount,
                'existing_loans': request.existing_loans,
                'monthly_income': request.monthly_income,
                'employment_years': request.employment_years,
                'status': LoanStatus.PENDING.value
            }
            
            application_id = self.loan_repo.create_loan_application(application_data)
            logger.info(f"Created loan application with ID: {application_id}")
            return application_id
            
        except Exception as e:
            logger.error(f"Error creating loan application: {e}")
            raise
    
    def _run_rule_engine(self, request: LoanApplicationRequest) -> RuleEngineResult:
        """Run rule-based validation"""
        try:
            application_data = {
                'salary': request.customer_salary,
                'credit_score': request.customer_credit_score,
                'age': request.customer_age,
                'loan_amount': request.loan_amount,
                'monthly_income': request.monthly_income,
                'employment_years': request.employment_years,
                'existing_loans': request.existing_loans
            }
            
            result = self.rule_engine.evaluate_application(application_data)
            logger.info(f"Rule engine result: {result.decision}")
            return result
            
        except Exception as e:
            logger.error(f"Error running rule engine: {e}")
            raise
    
    def _run_ml_prediction(self, request: LoanApplicationRequest, application_id: int) -> Dict[str, Any]:
        """Run ML model predictions"""
        try:
            if not ml_service.is_ready():
                logger.warning("ML service not ready, skipping ML prediction")
                return {'error': 'ML service not available'}
            
            # Create ML prediction request
            ml_request = MLPredictionRequest(
                salary=request.customer_salary,
                age=request.customer_age,
                credit_score=request.customer_credit_score,
                loan_amount=request.loan_amount,
                existing_loans=request.existing_loans,
                employment_years=request.employment_years,
                monthly_income=request.monthly_income
            )
            
            # Validate request
            ml_service.validate_request(ml_request)
            
            # Get combined prediction
            combined_result = ml_service.predict_combined(ml_request)
            
            # Store individual predictions in database
            self._store_ml_predictions(application_id, combined_result)
            
            # Convert to dict for easier handling
            result = {
                'final_decision': combined_result.final_decision,
                'consensus': combined_result.consensus,
                'average_probability': combined_result.average_probability,
                'random_forest': {
                    'prediction': combined_result.random_forest.prediction,
                    'probability_score': combined_result.random_forest.probability_score,
                    'confidence': combined_result.random_forest.confidence
                },
                'logistic_regression': {
                    'prediction': combined_result.logistic_regression.prediction,
                    'probability_score': combined_result.logistic_regression.probability_score,
                    'confidence': combined_result.logistic_regression.confidence
                }
            }
            
            logger.info(f"ML prediction result: {result['final_decision']}, consensus: {result['consensus']}")
            return result
            
        except Exception as e:
            logger.error(f"Error running ML prediction: {e}")
            return {'error': str(e)}
    
    def _store_ml_predictions(self, application_id: int, combined_result) -> None:
        """Store ML predictions in database"""
        try:
            # Store Random Forest prediction
            rf_data = {
                'application_id': application_id,
                'model_name': 'RandomForest',
                'prediction': combined_result.random_forest.prediction,
                'probability_score': combined_result.random_forest.probability_score,
                'feature_vector': combined_result.random_forest.feature_vector
            }
            self.ml_prediction_repo.create_prediction(rf_data)
            
            # Store Logistic Regression prediction
            lr_data = {
                'application_id': application_id,
                'model_name': 'LogisticRegression',
                'prediction': combined_result.logistic_regression.prediction,
                'probability_score': combined_result.logistic_regression.probability_score,
                'feature_vector': combined_result.logistic_regression.feature_vector
            }
            self.ml_prediction_repo.create_prediction(lr_data)
            
            logger.info(f"Stored ML predictions for application {application_id}")
            
        except Exception as e:
            logger.error(f"Error storing ML predictions: {e}")
            # Don't raise - this is not critical for the main workflow
    
    def _make_final_decision(self, rule_result: RuleEngineResult, 
                           ml_result: Dict[str, Any]) -> Tuple[str, Optional[str], str]:
        """Make final decision combining rule and ML results"""
        try:
            # If rules rejected, that's final
            if rule_result.decision == "rejected":
                return LoanStatus.REJECTED.value, None, rule_result.reason
            
            # If ML service had an error, fall back to rules
            if 'error' in ml_result:
                if rule_result.passed:
                    return LoanStatus.MANUAL_REVIEW.value, 'medium', "ML service unavailable - requires manual review"
                else:
                    return LoanStatus.REJECTED.value, None, "Rule failures and ML service unavailable"
            
            # Get ML decision
            ml_decision = ml_result.get('final_decision', 'manual_review')
            consensus = ml_result.get('consensus', False)
            avg_probability = ml_result.get('average_probability', 0.5)
            
            # Decision logic
            if ml_decision == 'approved' and consensus and avg_probability >= 0.7:
                # Strong approval from ML
                if avg_probability >= 0.85:
                    risk_category = 'low'
                elif avg_probability >= 0.75:
                    risk_category = 'medium'
                else:
                    risk_category = 'medium'
                
                return LoanStatus.APPROVED.value, risk_category, f"Approved by ML models (confidence: {avg_probability:.2%})"
            
            elif ml_decision == 'rejected' and consensus and avg_probability <= 0.3:
                # Strong rejection from ML
                return LoanStatus.REJECTED.value, 'high', f"Rejected by ML models (confidence: {1-avg_probability:.2%})"
            
            else:
                # Uncertain cases go to manual review
                risk_category = 'medium' if avg_probability >= 0.5 else 'high'
                reason = f"ML models uncertain (consensus: {consensus}, probability: {avg_probability:.2%})"
                return LoanStatus.MANUAL_REVIEW.value, risk_category, reason
            
        except Exception as e:
            logger.error(f"Error making final decision: {e}")
            return LoanStatus.MANUAL_REVIEW.value, 'medium', f"Decision error: {str(e)}"
    
    def _calculate_and_store_loan_terms(self, application_id: int, request: LoanApplicationRequest,
                                      risk_category: str, ml_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate and store loan terms"""
        try:
            # Prepare application data for risk assessment
            application_data = {
                'salary': request.customer_salary,
                'credit_score': request.customer_credit_score,
                'age': request.customer_age,
                'loan_amount': request.loan_amount,
                'monthly_income': request.monthly_income,
                'employment_years': request.employment_years,
                'existing_loans': request.existing_loans,
                'preferred_tenure_years': request.preferred_tenure_years
            }
            
            # Calculate loan terms
            terms_calc = risk_service.calculate_loan_terms(
                application_data, risk_category, application_id
            )
            
            # Store in database
            terms_data = {
                'application_id': application_id,
                'approved_amount': terms_calc.approved_amount,
                'interest_rate': terms_calc.interest_rate,
                'tenure_months': terms_calc.tenure_months,
                'monthly_payment': terms_calc.monthly_payment
            }
            
            terms_id = self.loan_terms_repo.create_loan_terms(terms_data)
            
            # Return terms for response
            loan_terms = {
                'id': terms_id,
                'approved_amount': terms_calc.approved_amount,
                'interest_rate': terms_calc.interest_rate,
                'tenure_months': terms_calc.tenure_months,
                'monthly_payment': terms_calc.monthly_payment,
                'debt_to_income_ratio': terms_calc.debt_to_income_ratio
            }
            
            logger.info(f"Calculated and stored loan terms for application {application_id}")
            return loan_terms
            
        except Exception as e:
            logger.error(f"Error calculating loan terms: {e}")
            raise
    
    def _update_application_status(self, application_id: int, status: str, 
                                 risk_category: Optional[str], reason: str) -> None:
        """Update loan application status"""
        try:
            success = self.loan_repo.update_application_status(
                application_id, status, risk_category, reason
            )
            
            if not success:
                logger.warning(f"Failed to update application {application_id} status")
            
        except Exception as e:
            logger.error(f"Error updating application status: {e}")
            raise
    
    def get_application_decision(self, application_id: int) -> Dict[str, Any]:
        """Get complete decision information for an application"""
        try:
            # Get application details
            application = self.loan_repo.get_loan_application_by_id(application_id)
            if not application:
                raise ValueError(f"Application {application_id} not found")
            
            # Get customer details
            customer = self.customer_repo.get_customer_by_id(application.customer_id)
            
            # Get loan terms if approved
            loan_terms = None
            if application.status == LoanStatus.APPROVED.value:
                terms = self.loan_terms_repo.get_terms_by_application_id(application_id)
                if terms:
                    loan_terms = {
                        'approved_amount': terms.approved_amount,
                        'interest_rate': terms.interest_rate,
                        'tenure_months': terms.tenure_months,
                        'monthly_payment': terms.monthly_payment
                    }
            
            # Get ML predictions
            ml_predictions = self.ml_prediction_repo.get_predictions_by_application_id(application_id)
            
            return {
                'application_id': application_id,
                'customer': {
                    'id': customer.id if customer else None,
                    'name': customer.name if customer else 'Unknown',
                    'credit_score': customer.credit_score if customer else None
                },
                'application': {
                    'loan_amount': application.loan_amount,
                    'status': application.status,
                    'risk_category': application.risk_category,
                    'decision_reason': application.decision_reason,
                    'application_date': application.application_date
                },
                'loan_terms': loan_terms,
                'ml_predictions': [
                    {
                        'model_name': pred.model_name,
                        'prediction': pred.prediction,
                        'probability_score': pred.probability_score
                    } for pred in ml_predictions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting application decision: {e}")
            raise
    
    def get_customer_loan_history(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get loan history for a customer"""
        try:
            applications = self.loan_repo.get_applications_by_customer_id(customer_id)
            
            history = []
            for app in applications:
                # Get loan terms if approved
                loan_terms = None
                if app.status == LoanStatus.APPROVED.value:
                    terms = self.loan_terms_repo.get_terms_by_application_id(app.id)
                    if terms:
                        loan_terms = {
                            'approved_amount': terms.approved_amount,
                            'interest_rate': terms.interest_rate,
                            'tenure_months': terms.tenure_months,
                            'monthly_payment': terms.monthly_payment
                        }
                
                history.append({
                    'application_id': app.id,
                    'loan_amount': app.loan_amount,
                    'status': app.status,
                    'risk_category': app.risk_category,
                    'decision_reason': app.decision_reason,
                    'application_date': app.application_date.isoformat() if app.application_date else None,
                    'loan_terms': loan_terms
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting customer loan history: {e}")
            raise

# Global loan processing service instance
loan_service = LoanProcessingService()