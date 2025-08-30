from typing import Optional, List, Dict, Any
from mysql.connector import Error
import logging
from app.repositories.base_repository import BaseRepository
from app.models.loan_terms import LoanTerms
from app.database import execute_query

logger = logging.getLogger(__name__)

class LoanTermsRepository(BaseRepository):
    """Repository for loan terms data operations"""
    
    def __init__(self):
        super().__init__("loan_terms")
    
    def create_loan_terms(self, terms_data: Dict[str, Any]) -> Optional[int]:
        """Create new loan terms record"""
        try:
            # Validate required fields
            required_fields = ['application_id', 'approved_amount', 'interest_rate', 'tenure_months', 'monthly_payment']
            for field in required_fields:
                if field not in terms_data:
                    raise ValueError(f"Missing required field: {field}")
            
            terms_id = self.create(terms_data)
            logger.info(f"Created loan terms with ID: {terms_id}")
            return terms_id
            
        except Error as e:
            logger.error(f"Error creating loan terms: {e}")
            raise
    
    def get_terms_by_id(self, terms_id: int) -> Optional[LoanTerms]:
        """Get loan terms by ID and return LoanTerms object"""
        try:
            result = self.get_by_id(terms_id)
            if result:
                return LoanTerms(
                    id=result['id'],
                    application_id=result['application_id'],
                    approved_amount=float(result['approved_amount']),
                    interest_rate=float(result['interest_rate']),
                    tenure_months=result['tenure_months'],
                    monthly_payment=float(result['monthly_payment']),
                    created_at=result['created_at']
                )
            return None
            
        except Error as e:
            logger.error(f"Error retrieving loan terms {terms_id}: {e}")
            raise
    
    def get_terms_by_application_id(self, application_id: int) -> Optional[LoanTerms]:
        """Get loan terms for a specific application"""
        try:
            query = """
                SELECT * FROM loan_terms 
                WHERE application_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            result = execute_query(query, (application_id,), fetch_one=True)
            
            if result:
                return LoanTerms(
                    id=result['id'],
                    application_id=result['application_id'],
                    approved_amount=float(result['approved_amount']),
                    interest_rate=float(result['interest_rate']),
                    tenure_months=result['tenure_months'],
                    monthly_payment=float(result['monthly_payment']),
                    created_at=result['created_at']
                )
            return None
            
        except Error as e:
            logger.error(f"Error retrieving terms for application {application_id}: {e}")
            raise
    
    def update_loan_terms(self, terms_id: int, update_data: Dict[str, Any]) -> bool:
        """Update loan terms"""
        try:
            # Remove None values and empty strings
            clean_data = {k: v for k, v in update_data.items() if v is not None and v != ''}
            
            if not clean_data:
                logger.warning(f"No valid data to update for loan terms {terms_id}")
                return False
            
            success = self.update(terms_id, clean_data)
            if success:
                logger.info(f"Updated loan terms {terms_id} with data: {clean_data}")
            
            return success
            
        except Error as e:
            logger.error(f"Error updating loan terms {terms_id}: {e}")
            raise
    
    def delete_terms_by_application_id(self, application_id: int) -> bool:
        """Delete loan terms for a specific application"""
        try:
            query = "DELETE FROM loan_terms WHERE application_id = %s"
            rows_affected = execute_query(query, (application_id,))
            success = rows_affected > 0
            
            if success:
                logger.info(f"Deleted loan terms for application {application_id}")
            
            return success
            
        except Error as e:
            logger.error(f"Error deleting terms for application {application_id}: {e}")
            raise
    
    def get_terms_statistics(self) -> Dict[str, Any]:
        """Get loan terms statistics"""
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total_terms,
                    AVG(approved_amount) as avg_approved_amount,
                    AVG(interest_rate) as avg_interest_rate,
                    AVG(tenure_months) as avg_tenure_months,
                    AVG(monthly_payment) as avg_monthly_payment,
                    MIN(interest_rate) as min_interest_rate,
                    MAX(interest_rate) as max_interest_rate,
                    SUM(approved_amount) as total_approved_amount
                FROM loan_terms
            """
            result = execute_query(stats_query, fetch_one=True)
            
            if result:
                return {
                    'total_terms': result['total_terms'],
                    'average_approved_amount': round(float(result['avg_approved_amount']), 2) if result['avg_approved_amount'] else 0,
                    'average_interest_rate': round(float(result['avg_interest_rate']), 2) if result['avg_interest_rate'] else 0,
                    'average_tenure_months': round(float(result['avg_tenure_months']), 1) if result['avg_tenure_months'] else 0,
                    'average_monthly_payment': round(float(result['avg_monthly_payment']), 2) if result['avg_monthly_payment'] else 0,
                    'min_interest_rate': float(result['min_interest_rate']) if result['min_interest_rate'] else 0,
                    'max_interest_rate': float(result['max_interest_rate']) if result['max_interest_rate'] else 0,
                    'total_approved_amount': round(float(result['total_approved_amount']), 2) if result['total_approved_amount'] else 0
                }
            
            return {}
            
        except Error as e:
            logger.error(f"Error retrieving loan terms statistics: {e}")
            raise