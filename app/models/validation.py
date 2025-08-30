from typing import Dict, List, Any, Optional
from pydantic import ValidationError
import re

class ValidationUtils:
    """Utility functions for data validation"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        """Validate SSN format (XXX-XX-XXXX)"""
        pattern = r'^\d{3}-\d{2}-\d{4}$'
        return bool(re.match(pattern, ssn))
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input to prevent XSS"""
        if not isinstance(value, str):
            return str(value)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
        sanitized = value
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_debt_to_income_ratio(monthly_debt: float, monthly_income: float) -> float:
        """Calculate and validate debt-to-income ratio"""
        if monthly_income <= 0:
            raise ValueError("Monthly income must be positive")
        
        ratio = monthly_debt / monthly_income
        return round(ratio, 4)
    
    @staticmethod
    def validate_loan_to_income_ratio(loan_amount: float, annual_income: float) -> float:
        """Calculate and validate loan-to-income ratio"""
        if annual_income <= 0:
            raise ValueError("Annual income must be positive")
        
        ratio = loan_amount / annual_income
        return round(ratio, 2)

class ErrorFormatter:
    """Format validation errors for API responses"""
    
    @staticmethod
    def format_pydantic_error(error: ValidationError) -> Dict[str, Any]:
        """Format Pydantic validation errors"""
        formatted_errors = []
        
        for err in error.errors():
            field = '.'.join(str(loc) for loc in err['loc'])
            formatted_errors.append({
                'field': field,
                'message': err['msg'],
                'type': err['type'],
                'input': err.get('input')
            })
        
        return {
            'error': 'VALIDATION_ERROR',
            'message': 'Input validation failed',
            'details': formatted_errors
        }
    
    @staticmethod
    def format_business_rule_error(field: str, message: str, value: Any = None) -> Dict[str, Any]:
        """Format business rule validation errors"""
        return {
            'error': 'BUSINESS_RULE_ERROR',
            'message': 'Business rule validation failed',
            'details': {
                'field': field,
                'message': message,
                'value': value
            }
        }
    
    @staticmethod
    def format_database_error(operation: str, message: str) -> Dict[str, Any]:
        """Format database operation errors"""
        return {
            'error': 'DATABASE_ERROR',
            'message': f'Database {operation} failed',
            'details': {
                'operation': operation,
                'message': message
            }
        }