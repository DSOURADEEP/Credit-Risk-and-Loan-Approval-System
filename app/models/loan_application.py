from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, validator

class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"

class RiskCategory(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class LoanApplication:
    """Loan application data model"""
    id: Optional[int] = None
    customer_id: int = 0
    loan_amount: float = 0.0
    existing_loans: int = 0
    monthly_income: float = 0.0
    employment_years: int = 0
    application_date: Optional[datetime] = None
    status: str = LoanStatus.PENDING
    risk_category: Optional[str] = None
    decision_reason: Optional[str] = None

class LoanApplicationRequest(BaseModel):
    """Pydantic model for loan application requests"""
    customer_name: str = Field(..., min_length=2, max_length=255)
    customer_age: int = Field(..., ge=18, le=100)
    customer_salary: float = Field(..., gt=0)
    customer_credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., gt=0, le=10000000, description="Requested loan amount")
    existing_loans: int = Field(default=0, ge=0, le=50, description="Number of existing loans")
    monthly_income: float = Field(..., gt=0, description="Monthly income")
    employment_years: int = Field(..., ge=0, le=50, description="Years of employment")
    preferred_tenure_years: Optional[int] = Field(default=None, ge=1, le=30, description="Preferred loan tenure in years")
    
    @validator('customer_name')
    def validate_customer_name(cls, v):
        if not v.strip():
            raise ValueError('Customer name cannot be empty')
        return v.strip().title()
    
    @validator('loan_amount', 'monthly_income', 'customer_salary')
    def validate_amounts(cls, v):
        return round(v, 2)
    
    @validator('monthly_income')
    def validate_monthly_income_vs_salary(cls, v, values):
        if 'customer_salary' in values:
            annual_from_monthly = v * 12
            salary = values['customer_salary']
            # Allow some variance between monthly income and salary
            if abs(annual_from_monthly - salary) > salary * 0.2:
                raise ValueError('Monthly income should be consistent with annual salary')
        return v

class LoanApplicationResponse(BaseModel):
    """Pydantic model for loan application responses"""
    id: int
    customer_id: int
    loan_amount: float
    existing_loans: int
    monthly_income: float
    employment_years: int
    application_date: datetime
    status: LoanStatus
    risk_category: Optional[RiskCategory]
    decision_reason: Optional[str]
    
    class Config:
        from_attributes = True