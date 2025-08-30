from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

@dataclass
class Customer:
    """Customer data model"""
    id: Optional[int] = None
    name: str = ""
    age: int = 0
    salary: float = 0.0
    credit_score: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CustomerRequest(BaseModel):
    """Pydantic model for customer creation/update requests"""
    name: str = Field(..., min_length=2, max_length=255, description="Customer full name")
    age: int = Field(..., ge=18, le=100, description="Customer age")
    salary: float = Field(..., gt=0, description="Annual salary")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().title()
    
    @validator('salary')
    def validate_salary(cls, v):
        if v <= 0:
            raise ValueError('Salary must be positive')
        return round(v, 2)

class CustomerResponse(BaseModel):
    """Pydantic model for customer responses"""
    id: int
    name: str
    age: int
    salary: float
    credit_score: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True