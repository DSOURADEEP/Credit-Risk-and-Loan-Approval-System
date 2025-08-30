from typing import Optional, List, Dict, Any
from mysql.connector import Error
import logging
from app.repositories.base_repository import BaseRepository
from app.models.customer import Customer
from app.database import execute_query

logger = logging.getLogger(__name__)

class CustomerRepository(BaseRepository):
    """Repository for customer data operations"""
    
    def __init__(self):
        super().__init__("customers")
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Optional[int]:
        """Create a new customer record"""
        try:
            # Validate required fields
            required_fields = ['name', 'age', 'salary', 'credit_score']
            for field in required_fields:
                if field not in customer_data:
                    raise ValueError(f"Missing required field: {field}")
            
            customer_id = self.create(customer_data)
            logger.info(f"Created customer: {customer_data['name']} with ID: {customer_id}")
            return customer_id
            
        except Error as e:
            logger.error(f"Error creating customer: {e}")
            raise
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID and return Customer object"""
        try:
            result = self.get_by_id(customer_id)
            if result:
                return Customer(
                    id=result['id'],
                    name=result['name'],
                    age=result['age'],
                    salary=float(result['salary']),
                    credit_score=result['credit_score'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
            return None
            
        except Error as e:
            logger.error(f"Error retrieving customer {customer_id}: {e}")
            raise
    
    def find_customer_by_name_and_details(self, name: str, age: int, credit_score: int) -> Optional[Customer]:
        """Find customer by name and basic details"""
        try:
            query = """
                SELECT * FROM customers 
                WHERE name = %s AND age = %s AND credit_score = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            result = execute_query(query, (name, age, credit_score), fetch_one=True)
            
            if result:
                return Customer(
                    id=result['id'],
                    name=result['name'],
                    age=result['age'],
                    salary=float(result['salary']),
                    credit_score=result['credit_score'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                )
            return None
            
        except Error as e:
            logger.error(f"Error finding customer by details: {e}")
            raise
    
    def get_customers_by_credit_score_range(self, min_score: int, max_score: int) -> List[Customer]:
        """Get customers within a credit score range"""
        try:
            query = """
                SELECT * FROM customers 
                WHERE credit_score BETWEEN %s AND %s 
                ORDER BY credit_score DESC
            """
            results = execute_query(query, (min_score, max_score), fetch_all=True)
            
            customers = []
            for result in results:
                customers.append(Customer(
                    id=result['id'],
                    name=result['name'],
                    age=result['age'],
                    salary=float(result['salary']),
                    credit_score=result['credit_score'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                ))
            
            return customers
            
        except Error as e:
            logger.error(f"Error retrieving customers by credit score range: {e}")
            raise
    
    def get_customers_by_salary_range(self, min_salary: float, max_salary: float) -> List[Customer]:
        """Get customers within a salary range"""
        try:
            query = """
                SELECT * FROM customers 
                WHERE salary BETWEEN %s AND %s 
                ORDER BY salary DESC
            """
            results = execute_query(query, (min_salary, max_salary), fetch_all=True)
            
            customers = []
            for result in results:
                customers.append(Customer(
                    id=result['id'],
                    name=result['name'],
                    age=result['age'],
                    salary=float(result['salary']),
                    credit_score=result['credit_score'],
                    created_at=result['created_at'],
                    updated_at=result['updated_at']
                ))
            
            return customers
            
        except Error as e:
            logger.error(f"Error retrieving customers by salary range: {e}")
            raise
    
    def update_customer(self, customer_id: int, update_data: Dict[str, Any]) -> bool:
        """Update customer information"""
        try:
            # Remove None values and empty strings
            clean_data = {k: v for k, v in update_data.items() if v is not None and v != ''}
            
            if not clean_data:
                logger.warning(f"No valid data to update for customer {customer_id}")
                return False
            
            success = self.update(customer_id, clean_data)
            if success:
                logger.info(f"Updated customer {customer_id} with data: {clean_data}")
            
            return success
            
        except Error as e:
            logger.error(f"Error updating customer {customer_id}: {e}")
            raise
    
    def get_customer_statistics(self) -> Dict[str, Any]:
        """Get customer statistics"""
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total_customers,
                    AVG(age) as avg_age,
                    AVG(salary) as avg_salary,
                    AVG(credit_score) as avg_credit_score,
                    MIN(credit_score) as min_credit_score,
                    MAX(credit_score) as max_credit_score
                FROM customers
            """
            result = execute_query(stats_query, fetch_one=True)
            
            if result:
                return {
                    'total_customers': result['total_customers'],
                    'average_age': round(float(result['avg_age']), 1) if result['avg_age'] else 0,
                    'average_salary': round(float(result['avg_salary']), 2) if result['avg_salary'] else 0,
                    'average_credit_score': round(float(result['avg_credit_score']), 1) if result['avg_credit_score'] else 0,
                    'min_credit_score': result['min_credit_score'],
                    'max_credit_score': result['max_credit_score']
                }
            
            return {}
            
        except Error as e:
            logger.error(f"Error retrieving customer statistics: {e}")
            raise