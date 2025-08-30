from typing import Dict, Any, Tuple, Optional
import logging
from dataclasses import dataclass
from app.models.loan_terms import LoanTermsResponse
from app.config import settings
import math

logger = logging.getLogger(__name__)

@dataclass
class RiskFactors:
    """Risk factors used in assessment"""
    credit_score_factor: float
    income_stability_factor: float
    debt_burden_factor: float
    employment_factor: float
    loan_size_factor: float
    age_factor: float
    overall_score: float

@dataclass
class LoanTermsCalculation:
    """Loan terms calculation result"""
    approved_amount: float
    interest_rate: float
    tenure_months: int
    monthly_payment: float
    debt_to_income_ratio: float
    risk_category: str
    risk_factors: RiskFactors

class RiskAssessmentService:
    """Service for risk assessment and loan terms calculation"""
    
    def __init__(self):
        # Base interest rates by risk category (more realistic rates)
        self.base_rates = {
            'low': 8.5,      # Best rate for low-risk customers
            'medium': 10.5,  # Standard rate for medium-risk customers  
            'high': 13.5     # Higher rate for high-risk customers
        }
        
        # Risk premium adjustments
        self.risk_premiums = {
            'low': 0.5,      # Small premium for excellent credit
            'medium': 2.0,   # Moderate premium for average credit
            'high': 4.5      # Higher premium for poor credit
        }
        
        # Loan amount adjustment factors by risk
        self.amount_adjustments = {
            'low': 1.0,      # No reduction
            'medium': 0.9,   # 10% reduction
            'high': 0.75     # 25% reduction
        }
        
        # Maximum tenure by risk category (in months)
        self.max_tenure = {
            'low': 360,      # 30 years
            'medium': 300,   # 25 years
            'high': 240      # 20 years
        }
        
        # Debt-to-income ratio limits
        self.max_dti_ratios = {
            'low': 0.35,
            'medium': 0.40,
            'high': 0.45
        }
    
    def assess_risk_category(self, application_data: Dict[str, Any], 
                           ml_prediction_data: Dict[str, Any] = None) -> Tuple[str, RiskFactors]:
        """Assess risk category based on application data and ML predictions"""
        try:
            # Extract application data
            credit_score = application_data.get('credit_score', 0)
            salary = application_data.get('salary', 0)
            age = application_data.get('age', 0)
            loan_amount = application_data.get('loan_amount', 0)
            existing_loans = application_data.get('existing_loans', 0)
            employment_years = application_data.get('employment_years', 0)
            monthly_income = application_data.get('monthly_income', salary / 12)
            
            # Calculate individual risk factors
            credit_factor = self._calculate_credit_score_factor(credit_score)
            income_factor = self._calculate_income_stability_factor(salary, employment_years)
            debt_factor = self._calculate_debt_burden_factor(existing_loans, monthly_income)
            employment_factor = self._calculate_employment_factor(employment_years)
            loan_size_factor = self._calculate_loan_size_factor(loan_amount, salary)
            age_factor = self._calculate_age_factor(age)
            
            # Calculate overall risk score (0-100, higher is better)
            risk_weights = {
                'credit_score': 0.30,
                'income_stability': 0.20,
                'debt_burden': 0.20,
                'employment': 0.15,
                'loan_size': 0.10,
                'age': 0.05
            }
            
            overall_score = (
                credit_factor * risk_weights['credit_score'] +
                income_factor * risk_weights['income_stability'] +
                debt_factor * risk_weights['debt_burden'] +
                employment_factor * risk_weights['employment'] +
                loan_size_factor * risk_weights['loan_size'] +
                age_factor * risk_weights['age']
            )
            
            # Adjust score based on ML prediction if available
            if ml_prediction_data:
                ml_adjustment = self._calculate_ml_adjustment(ml_prediction_data)
                overall_score = overall_score * ml_adjustment
            
            # Determine risk category
            if overall_score >= settings.LOW_RISK_THRESHOLD * 100:
                risk_category = 'low'
            elif overall_score >= settings.HIGH_RISK_THRESHOLD * 100:
                risk_category = 'medium'
            else:
                risk_category = 'high'
            
            risk_factors = RiskFactors(
                credit_score_factor=credit_factor,
                income_stability_factor=income_factor,
                debt_burden_factor=debt_factor,
                employment_factor=employment_factor,
                loan_size_factor=loan_size_factor,
                age_factor=age_factor,
                overall_score=overall_score
            )
            
            logger.info(f"Risk assessment completed. Category: {risk_category}, Score: {overall_score:.2f}")
            return risk_category, risk_factors
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            raise
    
    def calculate_loan_terms(self, application_data: Dict[str, Any], 
                           risk_category: str, application_id: int) -> LoanTermsCalculation:
        """Calculate loan terms based on risk assessment"""
        try:
            # Extract application data
            requested_amount = application_data.get('loan_amount', 0)
            monthly_income = application_data.get('monthly_income', 0)
            credit_score = application_data.get('credit_score', 0)
            
            # Calculate approved amount based on risk
            approved_amount = requested_amount * self.amount_adjustments[risk_category]
            
            # Calculate interest rate
            base_rate = self.base_rates[risk_category]
            risk_premium = self._calculate_risk_premium(credit_score, risk_category)
            interest_rate = base_rate + risk_premium
            
            # Calculate optimal tenure (considering user preference if provided)
            preferred_tenure_years = application_data.get('preferred_tenure_years')
            tenure_months = self._calculate_optimal_tenure(
                approved_amount, monthly_income, interest_rate, risk_category, preferred_tenure_years
            )
            
            # Calculate monthly payment
            monthly_payment = self._calculate_monthly_payment(
                approved_amount, interest_rate, tenure_months
            )
            
            # Calculate debt-to-income ratio
            debt_to_income_ratio = monthly_payment / monthly_income
            
            # Validate and adjust if necessary
            if debt_to_income_ratio > self.max_dti_ratios[risk_category]:
                # Adjust loan amount to meet DTI requirements
                max_payment = monthly_income * self.max_dti_ratios[risk_category]
                approved_amount = self._calculate_loan_amount_from_payment(
                    max_payment, interest_rate, tenure_months
                )
                monthly_payment = max_payment
                debt_to_income_ratio = monthly_payment / monthly_income
                
                logger.info(f"Adjusted loan amount to {approved_amount:.2f} to meet DTI requirements")
            
            # Create risk factors (simplified for terms calculation)
            risk_factors = RiskFactors(
                credit_score_factor=credit_score / 850 * 100,
                income_stability_factor=min(monthly_income / 5000 * 100, 100),
                debt_burden_factor=max(100 - debt_to_income_ratio * 200, 0),
                employment_factor=100,  # Simplified
                loan_size_factor=max(100 - (approved_amount / 500000) * 50, 50),
                age_factor=100,  # Simplified
                overall_score=0  # Will be calculated if needed
            )
            
            return LoanTermsCalculation(
                approved_amount=approved_amount,
                interest_rate=interest_rate,
                tenure_months=tenure_months,
                monthly_payment=monthly_payment,
                debt_to_income_ratio=debt_to_income_ratio,
                risk_category=risk_category,
                risk_factors=risk_factors
            )
            
        except Exception as e:
            logger.error(f"Error calculating loan terms: {e}")
            raise
    
    def _calculate_credit_score_factor(self, credit_score: int) -> float:
        """Calculate credit score risk factor (0-100)"""
        if credit_score >= 800:
            return 100
        elif credit_score >= 750:
            return 90
        elif credit_score >= 700:
            return 80
        elif credit_score >= 650:
            return 65
        elif credit_score >= 600:
            return 50
        else:
            return max(0, (credit_score - 300) / 300 * 30)
    
    def _calculate_income_stability_factor(self, salary: float, employment_years: float) -> float:
        """Calculate income stability factor (0-100)"""
        # Base score from salary level
        if salary >= 100000:
            salary_score = 100
        elif salary >= 75000:
            salary_score = 85
        elif salary >= 50000:
            salary_score = 70
        elif salary >= 35000:
            salary_score = 55
        else:
            salary_score = max(20, salary / 35000 * 55)
        
        # Employment stability bonus
        if employment_years >= 10:
            employment_bonus = 1.0
        elif employment_years >= 5:
            employment_bonus = 0.95
        elif employment_years >= 2:
            employment_bonus = 0.9
        else:
            employment_bonus = 0.8
        
        return min(100, salary_score * employment_bonus)
    
    def _calculate_debt_burden_factor(self, existing_loans: int, monthly_income: float) -> float:
        """Calculate debt burden factor (0-100, higher is better)"""
        if existing_loans == 0:
            return 100
        
        # Estimate existing debt payments
        estimated_debt_payment = existing_loans * 400  # Assume $400 per loan
        debt_ratio = estimated_debt_payment / monthly_income if monthly_income > 0 else 1
        
        # Convert to score (lower debt ratio = higher score)
        if debt_ratio <= 0.1:
            return 100
        elif debt_ratio <= 0.2:
            return 85
        elif debt_ratio <= 0.3:
            return 70
        elif debt_ratio <= 0.4:
            return 50
        else:
            return max(0, 50 - (debt_ratio - 0.4) * 100)
    
    def _calculate_employment_factor(self, employment_years: float) -> float:
        """Calculate employment factor (0-100)"""
        if employment_years >= 10:
            return 100
        elif employment_years >= 5:
            return 90
        elif employment_years >= 2:
            return 75
        elif employment_years >= 1:
            return 60
        else:
            return max(30, employment_years * 60)
    
    def _calculate_loan_size_factor(self, loan_amount: float, salary: float) -> float:
        """Calculate loan size factor (0-100)"""
        if salary <= 0:
            return 0
        
        loan_to_income = loan_amount / salary
        
        if loan_to_income <= 2:
            return 100
        elif loan_to_income <= 3:
            return 85
        elif loan_to_income <= 4:
            return 70
        elif loan_to_income <= 5:
            return 50
        else:
            return max(0, 50 - (loan_to_income - 5) * 10)
    
    def _calculate_age_factor(self, age: int) -> float:
        """Calculate age factor (0-100)"""
        if 30 <= age <= 50:
            return 100
        elif 25 <= age <= 60:
            return 90
        elif 22 <= age <= 65:
            return 80
        else:
            return 60
    
    def _calculate_ml_adjustment(self, ml_data: Dict[str, Any]) -> float:
        """Calculate adjustment factor based on ML predictions"""
        try:
            # Get average probability from ML models
            avg_probability = ml_data.get('average_probability', 0.5)
            consensus = ml_data.get('consensus', False)
            
            # Base adjustment on probability
            if avg_probability >= 0.8:
                adjustment = 1.1  # Boost score by 10%
            elif avg_probability >= 0.6:
                adjustment = 1.0  # No change
            elif avg_probability >= 0.4:
                adjustment = 0.9  # Reduce score by 10%
            else:
                adjustment = 0.8  # Reduce score by 20%
            
            # Additional adjustment for consensus
            if not consensus:
                adjustment *= 0.95  # Small penalty for disagreement
            
            return adjustment
            
        except Exception as e:
            logger.warning(f"Error calculating ML adjustment: {e}")
            return 1.0
    
    def _calculate_risk_premium(self, credit_score: int, risk_category: str) -> float:
        """Calculate risk premium for interest rate"""
        base_premium = self.risk_premiums[risk_category]
        
        # Fine-tune based on credit score within category
        if risk_category == 'low' and credit_score >= 780:
            return base_premium - 0.25
        elif risk_category == 'medium' and credit_score >= 720:
            return base_premium - 0.25
        elif risk_category == 'high' and credit_score < 600:
            return base_premium + 0.5
        
        return base_premium
    
    def _calculate_optimal_tenure(self, loan_amount: float, monthly_income: float, 
                                interest_rate: float, risk_category: str, 
                                preferred_tenure_years: Optional[int] = None) -> int:
        """Calculate optimal loan tenure"""
        max_tenure = self.max_tenure[risk_category]
        max_dti = self.max_dti_ratios[risk_category]
        
        # Calculate minimum tenure needed to meet DTI requirements
        max_payment = monthly_income * max_dti
        min_tenure = self._calculate_tenure_from_payment(loan_amount, interest_rate, max_payment)
        
        # If user specified a preferred tenure, try to use it
        if preferred_tenure_years:
            preferred_tenure_months = preferred_tenure_years * 12
            
            # Check if preferred tenure meets DTI requirements
            test_payment = self._calculate_monthly_payment(loan_amount, interest_rate, preferred_tenure_months)
            dti_ratio = test_payment / monthly_income
            
            # If preferred tenure is within limits and meets DTI requirements, use it
            if (preferred_tenure_months >= min_tenure and 
                preferred_tenure_months <= max_tenure and 
                dti_ratio <= max_dti):
                logger.info(f"Using user preferred tenure: {preferred_tenure_years} years")
                return preferred_tenure_months
            else:
                logger.info(f"User preferred tenure {preferred_tenure_years} years not feasible, calculating optimal")
        
        # Use the longer of minimum required tenure or standard tenure
        standard_tenure = 360 if loan_amount > 200000 else 240  # 30 years for large loans, 20 for smaller
        
        optimal_tenure = max(min_tenure, standard_tenure)
        return min(optimal_tenure, max_tenure)
    
    def _calculate_monthly_payment(self, principal: float, annual_rate: float, months: int) -> float:
        """Calculate monthly payment using loan formula"""
        if principal <= 0 or months <= 0:
            return 0
        
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate == 0:
            return principal / months
        
        payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                 ((1 + monthly_rate) ** months - 1)
        
        # Cap the payment at database maximum to prevent overflow
        max_payment = 9999999999.99  # Maximum value for DECIMAL(12,2)
        if payment > max_payment:
            logger.warning(f"Monthly payment {payment:.2f} exceeds database maximum, capping at {max_payment}")
            payment = max_payment
        
        return round(payment, 2)
    
    def _calculate_loan_amount_from_payment(self, payment: float, annual_rate: float, months: int) -> float:
        """Calculate loan amount from desired payment"""
        if payment <= 0 or months <= 0:
            return 0
        
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate == 0:
            return payment * months
        
        principal = payment * ((1 + monthly_rate) ** months - 1) / \
                   (monthly_rate * (1 + monthly_rate) ** months)
        
        return principal
    
    def _calculate_tenure_from_payment(self, principal: float, annual_rate: float, payment: float) -> int:
        """Calculate required tenure from loan amount and payment"""
        if principal <= 0 or payment <= 0:
            return 360  # Default to 30 years
        
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate == 0:
            return int(principal / payment)
        
        if payment <= principal * monthly_rate:
            return 360  # Payment too small, return maximum
        
        months = -math.log(1 - (principal * monthly_rate) / payment) / math.log(1 + monthly_rate)
        return max(12, int(math.ceil(months)))  # Minimum 1 year

# Global risk assessment service instance
risk_service = RiskAssessmentService()