#!/usr/bin/env python3
"""
Generate synthetic training data for ML models
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """Generate realistic synthetic loan application data"""
    
    def __init__(self, random_seed: int = 42):
        np.random.seed(random_seed)
        random.seed(random_seed)
        
        # Define realistic ranges and distributions
        self.age_range = (22, 65)
        self.salary_ranges = {
            'low': (25000, 45000),
            'medium': (45000, 85000),
            'high': (85000, 200000)
        }
        self.credit_score_ranges = {
            'poor': (300, 579),
            'fair': (580, 669),
            'good': (670, 739),
            'very_good': (740, 799),
            'excellent': (800, 850)
        }
        
    def generate_dataset(self, num_samples: int = 10000) -> pd.DataFrame:
        """Generate complete synthetic dataset"""
        logger.info(f"Generating {num_samples} synthetic loan applications...")
        
        data = []
        
        for i in range(num_samples):
            # Generate correlated features
            sample = self._generate_single_application()
            data.append(sample)
            
            if (i + 1) % 1000 == 0:
                logger.info(f"Generated {i + 1} samples...")
        
        df = pd.DataFrame(data)
        logger.info(f"Dataset generation complete. Shape: {df.shape}")
        
        return df
    
    def _generate_single_application(self) -> Dict:
        """Generate a single loan application with realistic correlations"""
        
        # Start with age - affects other variables
        age = np.random.randint(self.age_range[0], self.age_range[1] + 1)
        
        # Employment years based on age (can't work more years than age - 18)
        max_employment = min(age - 18, 40)
        employment_years = max(0, np.random.normal(max_employment * 0.6, max_employment * 0.2))
        employment_years = min(employment_years, max_employment)
        
        # Salary influenced by age and employment
        salary_category = self._determine_salary_category(age, employment_years)
        salary_range = self.salary_ranges[salary_category]
        salary = np.random.uniform(salary_range[0], salary_range[1])
        
        # Credit score influenced by age, employment, and salary
        credit_category = self._determine_credit_category(age, employment_years, salary)
        credit_range = self.credit_score_ranges[credit_category]
        credit_score = int(np.random.uniform(credit_range[0], credit_range[1]))
        
        # Monthly income (should be consistent with salary)
        monthly_income = salary / 12 * np.random.uniform(0.95, 1.05)  # Small variance
        
        # Existing loans based on age and credit score
        existing_loans = self._generate_existing_loans(age, credit_score)
        
        # Loan amount based on salary and credit score
        loan_amount = self._generate_loan_amount(salary, credit_score)
        
        # Generate repayment history score (0-100)
        repayment_history = self._generate_repayment_history(credit_score, existing_loans)
        
        # Generate target variable (approval decision)
        approval_decision = self._determine_approval(
            age, salary, credit_score, loan_amount, existing_loans, 
            employment_years, repayment_history
        )
        
        return {
            'age': age,
            'salary': round(salary, 2),
            'credit_score': credit_score,
            'loan_amount': round(loan_amount, 2),
            'existing_loans': existing_loans,
            'employment_years': round(employment_years, 1),
            'monthly_income': round(monthly_income, 2),
            'repayment_history': repayment_history,
            'approval_decision': approval_decision
        }
    
    def _determine_salary_category(self, age: int, employment_years: float) -> str:
        """Determine salary category based on age and employment"""
        # Younger people and those with less experience tend to earn less
        if age < 30 or employment_years < 3:
            return np.random.choice(['low', 'medium'], p=[0.6, 0.4])
        elif age < 45 and employment_years < 15:
            return np.random.choice(['low', 'medium', 'high'], p=[0.2, 0.6, 0.2])
        else:
            return np.random.choice(['medium', 'high'], p=[0.4, 0.6])
    
    def _determine_credit_category(self, age: int, employment_years: float, salary: float) -> str:
        """Determine credit score category based on other factors"""
        # Higher salary and more employment history generally mean better credit
        base_prob = [0.1, 0.2, 0.3, 0.25, 0.15]  # poor, fair, good, very_good, excellent
        
        # Adjust probabilities based on salary
        if salary > 80000:
            base_prob = [0.05, 0.1, 0.25, 0.35, 0.25]
        elif salary < 35000:
            base_prob = [0.2, 0.3, 0.3, 0.15, 0.05]
        
        # Adjust based on employment history
        if employment_years > 10:
            # Shift towards better credit
            base_prob = [max(0, base_prob[0] - 0.05), max(0, base_prob[1] - 0.05), 
                        base_prob[2], base_prob[3] + 0.05, base_prob[4] + 0.05]
        
        categories = ['poor', 'fair', 'good', 'very_good', 'excellent']
        return np.random.choice(categories, p=base_prob)
    
    def _generate_existing_loans(self, age: int, credit_score: int) -> int:
        """Generate number of existing loans"""
        if credit_score < 600:
            return np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1])
        elif credit_score < 700:
            return np.random.choice([0, 1, 2, 3, 4], p=[0.3, 0.3, 0.2, 0.15, 0.05])
        else:
            return np.random.choice([0, 1, 2, 3, 4, 5], p=[0.2, 0.3, 0.25, 0.15, 0.08, 0.02])
    
    def _generate_loan_amount(self, salary: float, credit_score: int) -> float:
        """Generate loan amount based on salary and credit score"""
        # Base loan amount on salary (typically 2-5x annual salary)
        base_multiplier = np.random.uniform(1.5, 4.5)
        
        # Adjust based on credit score
        if credit_score >= 750:
            multiplier = base_multiplier * np.random.uniform(1.0, 1.3)
        elif credit_score >= 650:
            multiplier = base_multiplier * np.random.uniform(0.8, 1.1)
        else:
            multiplier = base_multiplier * np.random.uniform(0.5, 0.9)
        
        loan_amount = salary * multiplier
        
        # Add some randomness and ensure reasonable bounds
        loan_amount *= np.random.uniform(0.8, 1.2)
        loan_amount = max(10000, min(loan_amount, 2000000))
        
        return loan_amount
    
    def _generate_repayment_history(self, credit_score: int, existing_loans: int) -> int:
        """Generate repayment history score (0-100)"""
        # Base score on credit score
        base_score = (credit_score - 300) / (850 - 300) * 100
        
        # Adjust based on existing loans (more loans might indicate some payment issues)
        if existing_loans > 2:
            base_score *= np.random.uniform(0.85, 0.95)
        
        # Add some noise
        score = base_score + np.random.normal(0, 10)
        
        return max(0, min(100, int(score)))
    
    def _determine_approval(self, age: int, salary: float, credit_score: int, 
                          loan_amount: float, existing_loans: int, 
                          employment_years: float, repayment_history: int) -> str:
        """Determine approval decision based on all factors"""
        
        # Calculate various ratios and scores
        loan_to_income = loan_amount / salary
        debt_burden_score = max(0, 100 - existing_loans * 15)
        
        # Create a composite score
        score = 0
        
        # Credit score component (40% weight)
        score += (credit_score - 300) / (850 - 300) * 40
        
        # Salary component (20% weight)
        if salary >= 75000:
            score += 20
        elif salary >= 50000:
            score += 15
        elif salary >= 35000:
            score += 10
        else:
            score += 5
        
        # Loan-to-income ratio component (20% weight)
        if loan_to_income <= 3:
            score += 20
        elif loan_to_income <= 4:
            score += 15
        elif loan_to_income <= 5:
            score += 10
        else:
            score += 5
        
        # Employment history component (10% weight)
        score += min(employment_years * 2, 10)
        
        # Repayment history component (10% weight)
        score += repayment_history * 0.1
        
        # Add some randomness to make it more realistic
        score += np.random.normal(0, 5)
        
        # Determine decision based on score
        if score >= 75:
            return 'approved'
        elif score >= 45:
            # Some randomness in the middle range
            return np.random.choice(['approved', 'manual_review'], p=[0.6, 0.4])
        elif score >= 25:
            return np.random.choice(['rejected', 'manual_review'], p=[0.7, 0.3])
        else:
            return 'rejected'

def main():
    """Main function to generate and save training data"""
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate training data
    generator = SyntheticDataGenerator()
    
    # Generate different sized datasets
    datasets = {
        'training_data_small.csv': 1000,
        'training_data_medium.csv': 5000,
        'training_data_large.csv': 10000
    }
    
    for filename, size in datasets.items():
        logger.info(f"Generating {filename} with {size} samples...")
        df = generator.generate_dataset(size)
        
        # Save to CSV
        filepath = data_dir / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {filename} to {filepath}")
        
        # Print basic statistics
        print(f"\n{filename} Statistics:")
        print(f"Total samples: {len(df)}")
        print(f"Approval distribution:")
        print(df['approval_decision'].value_counts(normalize=True))
        print(f"Credit score range: {df['credit_score'].min()} - {df['credit_score'].max()}")
        print(f"Salary range: ${df['salary'].min():,.2f} - ${df['salary'].max():,.2f}")
        print("-" * 50)

if __name__ == "__main__":
    main()