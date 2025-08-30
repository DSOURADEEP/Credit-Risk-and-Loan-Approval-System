from typing import Dict, List, Any, Tuple
import logging
from dataclasses import dataclass
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class RuleResult:
    """Result of a rule evaluation"""
    rule_name: str
    passed: bool
    message: str
    value: Any = None
    threshold: Any = None

@dataclass
class RuleEngineResult:
    """Overall result of rule engine evaluation"""
    passed: bool
    failed_rules: List[RuleResult]
    passed_rules: List[RuleResult]
    decision: str  # 'approved', 'rejected', 'proceed_to_ml'
    reason: str

class LoanRuleEngine:
    """Rule-based validation engine for loan applications"""
    
    def __init__(self):
        self.min_salary = settings.MIN_SALARY
        self.min_credit_score = settings.MIN_CREDIT_SCORE
        self.max_debt_to_income_ratio = settings.MAX_DEBT_TO_INCOME_RATIO
        
        # Additional configurable thresholds
        self.min_age = 18
        self.max_age = 75
        self.min_employment_years = 0.5  # 6 months
        self.max_loan_to_income_ratio = 5.0
        self.min_loan_amount = 1000
        self.max_loan_amount = 2000000
    
    def evaluate_application(self, application_data: Dict[str, Any]) -> RuleEngineResult:
        """Evaluate loan application against all rules"""
        try:
            passed_rules = []
            failed_rules = []
            
            # Extract application data
            salary = application_data.get('salary', 0)
            credit_score = application_data.get('credit_score', 0)
            age = application_data.get('age', 0)
            loan_amount = application_data.get('loan_amount', 0)
            monthly_income = application_data.get('monthly_income', 0)
            employment_years = application_data.get('employment_years', 0)
            existing_loans = application_data.get('existing_loans', 0)
            
            # Rule 1: Minimum salary requirement
            salary_result = self._check_minimum_salary(salary)
            if salary_result.passed:
                passed_rules.append(salary_result)
            else:
                failed_rules.append(salary_result)
            
            # Rule 2: Minimum credit score requirement
            credit_result = self._check_minimum_credit_score(credit_score)
            if credit_result.passed:
                passed_rules.append(credit_result)
            else:
                failed_rules.append(credit_result)
            
            # Rule 3: Debt-to-income ratio
            debt_ratio_result = self._check_debt_to_income_ratio(
                loan_amount, monthly_income, existing_loans
            )
            if debt_ratio_result.passed:
                passed_rules.append(debt_ratio_result)
            else:
                failed_rules.append(debt_ratio_result)
            
            # Rule 4: Age requirements
            age_result = self._check_age_requirements(age)
            if age_result.passed:
                passed_rules.append(age_result)
            else:
                failed_rules.append(age_result)
            
            # Rule 5: Employment history
            employment_result = self._check_employment_history(employment_years)
            if employment_result.passed:
                passed_rules.append(employment_result)
            else:
                failed_rules.append(employment_result)
            
            # Rule 6: Loan amount limits
            loan_amount_result = self._check_loan_amount_limits(loan_amount)
            if loan_amount_result.passed:
                passed_rules.append(loan_amount_result)
            else:
                failed_rules.append(loan_amount_result)
            
            # Rule 7: Loan-to-income ratio
            loan_income_result = self._check_loan_to_income_ratio(loan_amount, salary)
            if loan_income_result.passed:
                passed_rules.append(loan_income_result)
            else:
                failed_rules.append(loan_income_result)
            
            # Determine overall result
            all_passed = len(failed_rules) == 0
            
            if all_passed:
                decision = "proceed_to_ml"
                reason = "All rule-based checks passed. Proceeding to ML evaluation."
            else:
                # Check if any critical rules failed
                critical_failures = [rule for rule in failed_rules 
                                   if rule.rule_name in ['minimum_salary', 'minimum_credit_score', 'debt_to_income_ratio']]
                
                if critical_failures:
                    decision = "rejected"
                    reason = f"Critical rule failures: {', '.join([rule.message for rule in critical_failures])}"
                else:
                    decision = "proceed_to_ml"
                    reason = "Non-critical rule failures. Proceeding to ML evaluation with caution."
            
            result = RuleEngineResult(
                passed=all_passed,
                failed_rules=failed_rules,
                passed_rules=passed_rules,
                decision=decision,
                reason=reason
            )
            
            logger.info(f"Rule engine evaluation completed. Decision: {decision}")
            return result
            
        except Exception as e:
            logger.error(f"Error in rule engine evaluation: {e}")
            raise
    
    def _check_minimum_salary(self, salary: float) -> RuleResult:
        """Check minimum salary requirement"""
        passed = salary >= self.min_salary
        return RuleResult(
            rule_name="minimum_salary",
            passed=passed,
            message=f"Salary ${salary:,.2f} {'meets' if passed else 'below'} minimum requirement of ${self.min_salary:,.2f}",
            value=salary,
            threshold=self.min_salary
        )
    
    def _check_minimum_credit_score(self, credit_score: int) -> RuleResult:
        """Check minimum credit score requirement"""
        passed = credit_score >= self.min_credit_score
        return RuleResult(
            rule_name="minimum_credit_score",
            passed=passed,
            message=f"Credit score {credit_score} {'meets' if passed else 'below'} minimum requirement of {self.min_credit_score}",
            value=credit_score,
            threshold=self.min_credit_score
        )
    
    def _check_debt_to_income_ratio(self, loan_amount: float, monthly_income: float, existing_loans: int) -> RuleResult:
        """Check debt-to-income ratio"""
        if monthly_income <= 0:
            return RuleResult(
                rule_name="debt_to_income_ratio",
                passed=False,
                message="Invalid monthly income",
                value=0,
                threshold=self.max_debt_to_income_ratio
            )
        
        # Estimate monthly payment (assuming 30-year loan at 5% interest)
        monthly_payment = self._estimate_monthly_payment(loan_amount)
        
        # Estimate existing debt payments (rough estimate)
        estimated_existing_debt = existing_loans * 500  # Assume $500 per existing loan
        
        total_monthly_debt = monthly_payment + estimated_existing_debt
        debt_to_income_ratio = total_monthly_debt / monthly_income
        
        passed = debt_to_income_ratio <= self.max_debt_to_income_ratio
        
        return RuleResult(
            rule_name="debt_to_income_ratio",
            passed=passed,
            message=f"Debt-to-income ratio {debt_to_income_ratio:.2%} {'within' if passed else 'exceeds'} maximum of {self.max_debt_to_income_ratio:.2%}",
            value=debt_to_income_ratio,
            threshold=self.max_debt_to_income_ratio
        )
    
    def _check_age_requirements(self, age: int) -> RuleResult:
        """Check age requirements"""
        passed = self.min_age <= age <= self.max_age
        return RuleResult(
            rule_name="age_requirements",
            passed=passed,
            message=f"Age {age} {'within' if passed else 'outside'} acceptable range of {self.min_age}-{self.max_age}",
            value=age,
            threshold=(self.min_age, self.max_age)
        )
    
    def _check_employment_history(self, employment_years: float) -> RuleResult:
        """Check employment history requirements"""
        passed = employment_years >= self.min_employment_years
        return RuleResult(
            rule_name="employment_history",
            passed=passed,
            message=f"Employment history {employment_years} years {'meets' if passed else 'below'} minimum of {self.min_employment_years} years",
            value=employment_years,
            threshold=self.min_employment_years
        )
    
    def _check_loan_amount_limits(self, loan_amount: float) -> RuleResult:
        """Check loan amount limits"""
        passed = self.min_loan_amount <= loan_amount <= self.max_loan_amount
        return RuleResult(
            rule_name="loan_amount_limits",
            passed=passed,
            message=f"Loan amount ${loan_amount:,.2f} {'within' if passed else 'outside'} acceptable range of ${self.min_loan_amount:,.2f}-${self.max_loan_amount:,.2f}",
            value=loan_amount,
            threshold=(self.min_loan_amount, self.max_loan_amount)
        )
    
    def _check_loan_to_income_ratio(self, loan_amount: float, annual_salary: float) -> RuleResult:
        """Check loan-to-income ratio"""
        if annual_salary <= 0:
            return RuleResult(
                rule_name="loan_to_income_ratio",
                passed=False,
                message="Invalid annual salary",
                value=0,
                threshold=self.max_loan_to_income_ratio
            )
        
        ratio = loan_amount / annual_salary
        passed = ratio <= self.max_loan_to_income_ratio
        
        return RuleResult(
            rule_name="loan_to_income_ratio",
            passed=passed,
            message=f"Loan-to-income ratio {ratio:.1f} {'within' if passed else 'exceeds'} maximum of {self.max_loan_to_income_ratio:.1f}",
            value=ratio,
            threshold=self.max_loan_to_income_ratio
        )
    
    def _estimate_monthly_payment(self, loan_amount: float, annual_rate: float = 0.05, years: int = 30) -> float:
        """Estimate monthly payment for a loan"""
        if loan_amount <= 0:
            return 0
        
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        if monthly_rate == 0:
            return loan_amount / num_payments
        
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                         ((1 + monthly_rate) ** num_payments - 1)
        
        return monthly_payment
    
    def get_rule_configuration(self) -> Dict[str, Any]:
        """Get current rule configuration"""
        return {
            'min_salary': self.min_salary,
            'min_credit_score': self.min_credit_score,
            'max_debt_to_income_ratio': self.max_debt_to_income_ratio,
            'min_age': self.min_age,
            'max_age': self.max_age,
            'min_employment_years': self.min_employment_years,
            'max_loan_to_income_ratio': self.max_loan_to_income_ratio,
            'min_loan_amount': self.min_loan_amount,
            'max_loan_amount': self.max_loan_amount
        }