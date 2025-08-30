from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator

@dataclass
class MLPrediction:
    """ML prediction data model"""
    id: Optional[int] = None
    application_id: int = 0
    model_name: str = ""
    prediction: str = ""
    probability_score: float = 0.0
    feature_vector: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class MLPredictionRequest(BaseModel):
    """Pydantic model for ML prediction requests"""
    salary: float = Field(..., gt=0)
    age: int = Field(..., ge=18, le=100)
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., gt=0)
    existing_loans: int = Field(..., ge=0)
    employment_years: int = Field(..., ge=0)
    monthly_income: float = Field(..., gt=0)
    
    @validator('salary', 'loan_amount', 'monthly_income')
    def validate_amounts(cls, v):
        return round(v, 2)

class MLPredictionResponse(BaseModel):
    """Pydantic model for ML prediction responses"""
    model_name: str
    prediction: str
    probability_score: float = Field(..., ge=0.0, le=1.0)
    confidence: str
    feature_vector: Dict[str, Any]
    
    @validator('probability_score')
    def round_probability(cls, v):
        return round(v, 4)
    
    @validator('confidence')
    def set_confidence_level(cls, v, values):
        if 'probability_score' in values:
            score = values['probability_score']
            if score >= 0.8:
                return "high"
            elif score >= 0.6:
                return "medium"
            else:
                return "low"
        return "unknown"

class CombinedMLPrediction(BaseModel):
    """Combined prediction from multiple ML models"""
    random_forest: MLPredictionResponse
    logistic_regression: MLPredictionResponse
    final_decision: str
    consensus: bool
    average_probability: float
    
    @validator('average_probability')
    def calculate_average(cls, v, values):
        if 'random_forest' in values and 'logistic_regression' in values:
            rf_prob = values['random_forest'].probability_score
            lr_prob = values['logistic_regression'].probability_score
            return round((rf_prob + lr_prob) / 2, 4)
        return v
    
    @validator('consensus')
    def check_consensus(cls, v, values):
        if 'random_forest' in values and 'logistic_regression' in values:
            rf_pred = values['random_forest'].prediction
            lr_pred = values['logistic_regression'].prediction
            return rf_pred == lr_pred
        return False