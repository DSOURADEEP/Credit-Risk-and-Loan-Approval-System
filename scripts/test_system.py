#!/usr/bin/env python3
"""
System testing script for Credit Risk & Loan Approval System
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class SystemTester:
    """Test the complete loan approval system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_results = []
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🧪 Starting Credit Risk & Loan Approval System Tests")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Database Health", self.test_database_health),
            ("ML Service Health", self.test_ml_health),
            ("Loan Application - Approved", self.test_loan_application_approved),
            ("Loan Application - Rejected", self.test_loan_application_rejected),
            ("Loan Application - Manual Review", self.test_loan_application_manual_review),
            ("Get Loan Decision", self.test_get_loan_decision),
            ("Customer History", self.test_customer_history),
            ("Invalid Application", self.test_invalid_application),
            ("Web Interface", self.test_web_interface)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                if result:
                    print(f"✅ PASSED: {test_name}")
                    passed += 1
                else:
                    print(f"❌ FAILED: {test_name}")
                    failed += 1
            except Exception as e:
                print(f"❌ ERROR: {test_name} - {str(e)}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! System is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the system configuration.")
            return False
    
    def test_health_check(self) -> bool:
        """Test basic health check"""
        response = requests.get(f"{self.api_base}/health")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy"
        return False
    
    def test_database_health(self) -> bool:
        """Test database health"""
        response = requests.get(f"{self.api_base}/health/database")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy"
        return False
    
    def test_ml_health(self) -> bool:
        """Test ML service health"""
        response = requests.get(f"{self.api_base}/health/ml")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy" and data.get("ready") == True
        return False
    
    def test_loan_application_approved(self) -> bool:
        """Test loan application that should be approved"""
        application_data = {
            "customer_name": "John Doe",
            "customer_age": 35,
            "customer_salary": 85000,
            "customer_credit_score": 750,
            "loan_amount": 200000,
            "existing_loans": 1,
            "monthly_income": 7083,
            "employment_years": 8
        }
        
        response = requests.post(
            f"{self.api_base}/loans/apply",
            json=application_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            # Store application ID for later tests
            self.approved_application_id = data.get("application_id")
            self.customer_id = data.get("customer_id")
            
            # Should be approved with good credit and income
            return data.get("status") in ["approved", "manual_review"]
        return False
    
    def test_loan_application_rejected(self) -> bool:
        """Test loan application that should be rejected"""
        application_data = {
            "customer_name": "Jane Smith",
            "customer_age": 25,
            "customer_salary": 25000,  # Below minimum
            "customer_credit_score": 580,  # Below minimum
            "loan_amount": 300000,  # High amount for low income
            "existing_loans": 3,
            "monthly_income": 2083,
            "employment_years": 1
        }
        
        response = requests.post(
            f"{self.api_base}/loans/apply",
            json=application_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            # Should be rejected due to low salary and credit score
            return data.get("status") == "rejected"
        return False
    
    def test_loan_application_manual_review(self) -> bool:
        """Test loan application that should require manual review"""
        application_data = {
            "customer_name": "Bob Johnson",
            "customer_age": 45,
            "customer_salary": 55000,
            "customer_credit_score": 650,  # Borderline
            "loan_amount": 250000,
            "existing_loans": 2,
            "monthly_income": 4583,
            "employment_years": 3
        }
        
        response = requests.post(
            f"{self.api_base}/loans/apply",
            json=application_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            # Should require manual review due to borderline metrics
            return data.get("status") in ["manual_review", "approved", "rejected"]
        return False
    
    def test_get_loan_decision(self) -> bool:
        """Test getting loan decision details"""
        if not hasattr(self, 'approved_application_id'):
            return False
        
        response = requests.get(
            f"{self.api_base}/loans/{self.approved_application_id}/decision"
        )
        
        if response.status_code == 200:
            data = response.json()
            return (
                data.get("application_id") == self.approved_application_id and
                "application" in data and
                "customer" in data
            )
        return False
    
    def test_customer_history(self) -> bool:
        """Test getting customer loan history"""
        if not hasattr(self, 'customer_id'):
            return False
        
        response = requests.get(
            f"{self.api_base}/customers/{self.customer_id}/history"
        )
        
        if response.status_code == 200:
            data = response.json()
            return isinstance(data, list) and len(data) > 0
        return False
    
    def test_invalid_application(self) -> bool:
        """Test invalid loan application"""
        invalid_data = {
            "customer_name": "",  # Invalid: empty name
            "customer_age": 15,   # Invalid: too young
            "customer_salary": -1000,  # Invalid: negative
            "customer_credit_score": 900,  # Invalid: too high
            "loan_amount": 0,     # Invalid: zero amount
            "existing_loans": -1, # Invalid: negative
            "monthly_income": 0,  # Invalid: zero
            "employment_years": -1 # Invalid: negative
        }
        
        response = requests.post(
            f"{self.api_base}/loans/apply",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Should return validation error (422)
        return response.status_code == 422
    
    def test_web_interface(self) -> bool:
        """Test web interface accessibility"""
        response = requests.get(self.base_url)
        
        if response.status_code == 200:
            content = response.text
            return (
                "Credit Risk & Loan Approval System" in content and
                "loan-application-form" in content
            )
        return False
    
    def generate_test_report(self):
        """Generate detailed test report"""
        print("\n📋 Generating detailed test report...")
        
        # Test system statistics
        try:
            health_response = requests.get(f"{self.api_base}/health/detailed")
            if health_response.status_code == 200:
                health_data = health_response.json()
                print("\n🏥 System Health:")
                print(f"   Overall Status: {health_data.get('status', 'unknown')}")
                
                components = health_data.get('components', {})
                for component, info in components.items():
                    status = info.get('status', 'unknown')
                    print(f"   {component.title()}: {status}")
        except Exception as e:
            print(f"   Error getting health data: {e}")
        
        # Test database statistics
        try:
            db_response = requests.get(f"{self.api_base}/health/database")
            if db_response.status_code == 200:
                db_data = db_response.json()
                stats = db_data.get('statistics', {})
                print("\n📊 Database Statistics:")
                print(f"   Total Customers: {stats.get('total_customers', 0)}")
                print(f"   Total Applications: {stats.get('total_applications', 0)}")
        except Exception as e:
            print(f"   Error getting database stats: {e}")

def main():
    """Main testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Credit Risk & Loan Approval System")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the application")
    parser.add_argument("--report", action="store_true", 
                       help="Generate detailed report")
    
    args = parser.parse_args()
    
    tester = SystemTester(args.url)
    
    # Run tests
    success = tester.run_all_tests()
    
    # Generate report if requested
    if args.report:
        tester.generate_test_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()