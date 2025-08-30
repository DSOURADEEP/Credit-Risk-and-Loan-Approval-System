from typing import Optional, List, Dict, Any
from mysql.connector import Error
import logging
from app.repositories.base_repository import BaseRepository
from app.models.loan_application import LoanApplication, LoanStatus
from app.database import execute_query

logger = logging.getLogger(__name__)

class LoanApplicationRepository(BaseRepository):
    """Repository for loan application data operations"""
    
    def __init__(self):
        super().__init__("loan_applications")
    
    def create_loan_application(self, application_data: Dict[str, Any]) -> Optional[int]:
        """Create a new loan application record"""
        try:
            # Validate required fields
            required_fields = ['customer_id', 'loan_amount', 'monthly_income', 'employment_years']
            for field in required_fields:
                if field not in application_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Set default values
            application_data.setdefault('existing_loans', 0)
            application_data.setdefault('status', LoanStatus.PENDING.value)
            
            application_id = self.create(application_data)
            logger.info(f"Created loan application with ID: {application_id}")
            return application_id
            
        except Error as e:
            logger.error(f"Error creating loan application: {e}")
            raise
    
    def get_loan_application_by_id(self, application_id: int) -> Optional[LoanApplication]:
        """Get loan application by ID and return LoanApplication object"""
        try:
            result = self.get_by_id(application_id)
            if result:
                return LoanApplication(
                    id=result['id'],
                    customer_id=result['customer_id'],
                    loan_amount=float(result['loan_amount']),
                    existing_loans=result['existing_loans'],
                    monthly_income=float(result['monthly_income']),
                    employment_years=result['employment_years'],
                    application_date=result['application_date'],
                    status=result['status'],
                    risk_category=result['risk_category'],
                    decision_reason=result['decision_reason']
                )
            return None
            
        except Error as e:
            logger.error(f"Error retrieving loan application {application_id}: {e}")
            raise
    
    def get_applications_by_customer_id(self, customer_id: int) -> List[LoanApplication]:
        """Get all loan applications for a specific customer"""
        try:
            query = """
                SELECT * FROM loan_applications 
                WHERE customer_id = %s 
                ORDER BY application_date DESC
            """
            results = execute_query(query, (customer_id,), fetch_all=True)
            
            applications = []
            for result in results:
                applications.append(LoanApplication(
                    id=result['id'],
                    customer_id=result['customer_id'],
                    loan_amount=float(result['loan_amount']),
                    existing_loans=result['existing_loans'],
                    monthly_income=float(result['monthly_income']),
                    employment_years=result['employment_years'],
                    application_date=result['application_date'],
                    status=result['status'],
                    risk_category=result['risk_category'],
                    decision_reason=result['decision_reason']
                ))
            
            return applications
            
        except Error as e:
            logger.error(f"Error retrieving applications for customer {customer_id}: {e}")
            raise
    
    def get_applications_by_status(self, status: str) -> List[LoanApplication]:
        """Get all loan applications with a specific status"""
        try:
            query = """
                SELECT * FROM loan_applications 
                WHERE status = %s 
                ORDER BY application_date DESC
            """
            results = execute_query(query, (status,), fetch_all=True)
            
            applications = []
            for result in results:
                applications.append(LoanApplication(
                    id=result['id'],
                    customer_id=result['customer_id'],
                    loan_amount=float(result['loan_amount']),
                    existing_loans=result['existing_loans'],
                    monthly_income=float(result['monthly_income']),
                    employment_years=result['employment_years'],
                    application_date=result['application_date'],
                    status=result['status'],
                    risk_category=result['risk_category'],
                    decision_reason=result['decision_reason']
                ))
            
            return applications
            
        except Error as e:
            logger.error(f"Error retrieving applications by status {status}: {e}")
            raise
    
    def update_application_status(self, application_id: int, status: str, 
                                risk_category: Optional[str] = None, 
                                decision_reason: Optional[str] = None) -> bool:
        """Update loan application status and related fields"""
        try:
            update_data = {'status': status}
            
            if risk_category:
                update_data['risk_category'] = risk_category
            
            if decision_reason:
                update_data['decision_reason'] = decision_reason
            
            success = self.update(application_id, update_data)
            if success:
                logger.info(f"Updated application {application_id} status to {status}")
            
            return success
            
        except Error as e:
            logger.error(f"Error updating application status {application_id}: {e}")
            raise
    
    def get_application_statistics(self) -> Dict[str, Any]:
        """Get loan application statistics"""
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                    SUM(CASE WHEN status = 'manual_review' THEN 1 ELSE 0 END) as manual_review_count,
                    AVG(loan_amount) as avg_loan_amount,
                    SUM(CASE WHEN status = 'approved' THEN loan_amount ELSE 0 END) as total_approved_amount
                FROM loan_applications
            """
            result = execute_query(stats_query, fetch_one=True)
            
            if result:
                total = result['total_applications']
                return {
                    'total_applications': total,
                    'approved_count': result['approved_count'],
                    'rejected_count': result['rejected_count'],
                    'pending_count': result['pending_count'],
                    'manual_review_count': result['manual_review_count'],
                    'approval_rate': round((result['approved_count'] / total * 100), 2) if total > 0 else 0,
                    'average_loan_amount': round(float(result['avg_loan_amount']), 2) if result['avg_loan_amount'] else 0,
                    'total_approved_amount': round(float(result['total_approved_amount']), 2) if result['total_approved_amount'] else 0
                }
            
            return {}
            
        except Error as e:
            logger.error(f"Error retrieving application statistics: {e}")
            raise