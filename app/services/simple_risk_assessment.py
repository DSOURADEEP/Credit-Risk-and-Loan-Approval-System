"""
Simplified Risk Assessment Service - Rule-based approach
No ML dependencies required for deployment
"""
import random
import time
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class LoanApplication:
    customer_name: str
    customer_age: int
    customer_salary: float
    customer_credit_score: int
    loan_amount: float
    existing_loans: int
    monthly_income: float
    employment_years: float
    preferred_tenure_years: int = None

class SimpleRiskAssessment:
    def __init__(self):
        self.min_salary = 30000
        self.min_credit_score = 600
        self.max_debt_to_income_ratio = 0.4
        self.low_risk_threshold = 0.8
        self.high_risk_threshold = 0.4
        
    def assess_risk(self, application: LoanApplication) -> Dict[str, Any]:
        """
        Rule-based risk assessment without ML dependencies
        """
        start_time = time.time()
        
        # Calculate basic metrics
        debt_to_income = application.loan_amount / (application.customer_salary * 12)
        loan_to_income = application.loan_amount / application.customer_salary
        
        # Rule-based scoring
        score = 0.0
        reasons = []
        
        # Credit Score Assessment (40% weight)
        if application.customer_credit_score >= 750:
            score += 0.4
            reasons.append("Excellent credit score")
        elif application.customer_credit_score >= 700:
            score += 0.32
            reasons.append("Good credit score")
        elif application.customer_credit_score >= 650:
            score += 0.24
            reasons.append("Fair credit score")
        elif application.customer_credit_score >= 600:
            score += 0.16
            reasons.append("Acceptable credit score")
        else:
            score += 0.0
            reasons.append("Poor credit score")
            
        # Income Assessment (30% weight)
        if application.customer_salary >= 100000:
            score += 0.3
            reasons.append("High income")
        elif application.customer_salary >= 60000:
            score += 0.24
            reasons.append("Good income")
        elif application.customer_salary >= 40000:
            score += 0.18
            reasons.append("Moderate income")
        elif application.customer_salary >= 30000:
            score += 0.12
            reasons.append("Minimum acceptable income")
        else:
            score += 0.0
            reasons.append("Income below minimum threshold")
            
        # Debt-to-Income Ratio (20% weight)
        if debt_to_income <= 0.2:
            score += 0.2
            reasons.append("Low debt-to-income ratio")
        elif debt_to_income <= 0.3:
            score += 0.15
            reasons.append("Acceptable debt-to-income ratio")
        elif debt_to_income <= 0.4:
            score += 0.1
            reasons.append("High debt-to-income ratio")
        else:
            score += 0.0
            reasons.append("Debt-to-income ratio too high")
            
        # Employment Stability (10% weight)
        if application.employment_years >= 5:
            score += 0.1
            reasons.append("Stable employment history")
        elif application.employment_years >= 2:
            score += 0.07
            reasons.append("Good employment history")
        elif application.employment_years >= 1:
            score += 0.05
            reasons.append("Acceptable employment history")
        else:
            score += 0.02
            reasons.append("Limited employment history")
            
        # Existing Loans Penalty
        if application.existing_loans > 3:
            score -= 0.1
            reasons.append("Multiple existing loans")
        elif application.existing_loans > 1:
            score -= 0.05
            reasons.append("Some existing loans")
            
        # Age factor
        if 25 <= application.customer_age <= 55:
            score += 0.05
            reasons.append("Prime age group")
        elif application.customer_age > 60:
            score -= 0.05
            reasons.append("Advanced age consideration")
            
        # Determine risk category and decision
        if score >= self.low_risk_threshold:
            risk_category = "low"
            decision = "approved"
            decision_reason = f"Low risk profile. {', '.join(reasons[:3])}"
        elif score >= self.high_risk_threshold:
            risk_category = "medium"
            decision = "manual_review"
            decision_reason = f"Medium risk profile requires review. {', '.join(reasons[:2])}"
        else:
            risk_category = "high"
            decision = "rejected"
            decision_reason = f"High risk profile. {', '.join(reasons[:2])}"
            
        # Calculate loan terms if approved
        loan_terms = None
        if decision == "approved":
            loan_terms = self._calculate_loan_terms(application, score)
            
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "decision": decision,
            "risk_category": risk_category,
            "decision_reason": decision_reason,
            "confidence_score": round(score, 3),
            "loan_terms": loan_terms,
            "processing_time_ms": processing_time,
            "assessment_details": {
                "debt_to_income_ratio": round(debt_to_income, 3),
                "loan_to_income_ratio": round(loan_to_income, 3),
                "risk_factors": reasons
            }
        }
        
    def _calculate_loan_terms(self, application: LoanApplication, score: float) -> Dict[str, Any]:
        """Calculate loan terms based on risk assessment"""
        
        # Base interest rate based on risk score
        if score >= 0.8:
            base_rate = 8.5  # Excellent
        elif score >= 0.7:
            base_rate = 10.5  # Good
        elif score >= 0.6:
            base_rate = 12.5  # Fair
        else:
            base_rate = 15.5  # Higher risk
            
        # Adjust rate based on credit score
        if application.customer_credit_score >= 750:
            interest_rate = base_rate - 1.0
        elif application.customer_credit_score >= 700:
            interest_rate = base_rate - 0.5
        elif application.customer_credit_score < 650:
            interest_rate = base_rate + 1.0
        else:
            interest_rate = base_rate
            
        # Determine tenure
        if application.preferred_tenure_years:
            tenure_years = application.preferred_tenure_years
        else:
            # Auto-calculate optimal tenure
            if application.loan_amount <= 100000:
                tenure_years = 5
            elif application.loan_amount <= 500000:
                tenure_years = 10
            elif application.loan_amount <= 1000000:
                tenure_years = 15
            else:
                tenure_years = 20
                
        tenure_months = tenure_years * 12
        
        # Calculate approved amount (might be less than requested)
        max_affordable = application.monthly_income * 0.4 * tenure_months
        approved_amount = min(application.loan_amount, max_affordable)
        
        # Calculate EMI using simple interest formula
        monthly_rate = interest_rate / 100 / 12
        if monthly_rate > 0:
            emi = approved_amount * monthly_rate * (1 + monthly_rate) ** tenure_months / ((1 + monthly_rate) ** tenure_months - 1)
        else:
            emi = approved_amount / tenure_months
            
        return {
            "approved_amount": round(approved_amount, 2),
            "interest_rate": round(interest_rate, 2),
            "tenure_months": tenure_months,
            "monthly_payment": round(emi, 2),
            "total_amount": round(emi * tenure_months, 2),
            "total_interest": round((emi * tenure_months) - approved_amount, 2)
        }

# Create global instance
risk_assessor = SimpleRiskAssessment()