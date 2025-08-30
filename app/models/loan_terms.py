from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

@dataclass
class LoanTerms:
    """Loan terms data model"""
    id: Optional[int] = None
    application_id: int = 0
    approved_amount: float = 0.0
    interest_rate: float = 0.0
    tenure_months: int = 0
    monthly_payment: float = 0.0
    created_at: Optional[datetime] = None

class LoanTermsRequest(BaseModel):
    """Pydantic model for loan terms calculation requests"""
    loan_amount: float = Field(..., gt=0)
    risk_category: str = Field(..., pattern="^(low|medium|high)$")
    credit_score: int = Field(..., ge=300, le=850)
    monthly_income: float = Field(..., gt=0)
    
    @validator('loan_amount', 'monthly_income')
    def validate_amounts(cls, v):
        return round(v, 2)

class LoanTermsResponse(BaseModel):
    """Pydantic model for loan terms responses"""
    application_id: int
    approved_amount: float
    interest_rate: float
    tenure_months: int
    monthly_payment: float
    debt_to_income_ratio: float
    
    @validator('approved_amount', 'monthly_payment')
    def round_amounts(cls, v):
        return round(v, 2)
    
    @validator('interest_rate')
    def round_interest_rate(cls, v):
        return round(v, 2)
    
    @validator('debt_to_income_ratio')
    def round_ratio(cls, v):
        return round(v, 4)
    
    class Config:
        from_attributes = True

class LoanTermsCalculation(BaseModel):
    """Model for loan terms calculation parameters"""
    base_rate: float = Field(default=3.5, ge=0, le=20)
    risk_premium_low: float = Field(default=0.5, ge=0, le=5)
    risk_premium_medium: float = Field(default=1.5, ge=0, le=5)
    risk_premium_high: float = Field(default=3.0, ge=0, le=5)
    max_tenure_months: int = Field(default=360, ge=12, le=480)
    max_debt_to_income: float = Field(default=0.4, ge=0.1, le=0.6)