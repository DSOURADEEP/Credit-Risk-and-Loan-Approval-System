-- Sample data for testing the Credit Risk & Loan Approval System

USE loan_approval_db;

-- Insert sample customers
INSERT INTO customers (name, age, salary, credit_score) VALUES
('John Smith', 35, 75000.00, 720),
('Sarah Johnson', 28, 45000.00, 680),
('Michael Brown', 42, 95000.00, 780),
('Emily Davis', 31, 52000.00, 650),
('David Wilson', 39, 68000.00, 700),
('Lisa Anderson', 26, 38000.00, 620),
('Robert Taylor', 45, 110000.00, 800),
('Jennifer Martinez', 33, 58000.00, 690),
('William Garcia', 37, 72000.00, 740),
('Jessica Rodriguez', 29, 41000.00, 640);

-- Insert sample loan applications
INSERT INTO loan_applications (customer_id, loan_amount, existing_loans, monthly_income, employment_years, status, risk_category, decision_reason) VALUES
(1, 250000.00, 1, 6250.00, 8, 'approved', 'low', 'Strong credit score and stable income'),
(2, 180000.00, 0, 3750.00, 4, 'approved', 'medium', 'Good credit score, moderate income'),
(3, 350000.00, 2, 7916.67, 12, 'approved', 'low', 'Excellent credit score and high income'),
(4, 200000.00, 1, 4333.33, 6, 'manual_review', 'medium', 'Borderline credit score requires review'),
(5, 275000.00, 1, 5666.67, 10, 'approved', 'low', 'Good credit score and stable employment'),
(6, 150000.00, 0, 3166.67, 2, 'rejected', 'high', 'Credit score below minimum threshold'),
(7, 450000.00, 3, 9166.67, 15, 'approved', 'low', 'Excellent credit profile'),
(8, 220000.00, 1, 4833.33, 7, 'approved', 'medium', 'Acceptable risk profile'),
(9, 300000.00, 2, 6000.00, 11, 'approved', 'low', 'Strong financial profile'),
(10, 160000.00, 0, 3416.67, 3, 'manual_review', 'medium', 'Limited credit history');

-- Insert sample loan terms for approved applications
INSERT INTO loan_terms (application_id, approved_amount, interest_rate, tenure_months, monthly_payment) VALUES
(1, 250000.00, 9.25, 360, 2068.45),
(2, 180000.00, 11.75, 360, 1847.32),
(3, 350000.00, 3.95, 360, 1656.61),
(5, 275000.00, 4.15, 360, 1330.60),
(7, 450000.00, 3.85, 360, 2108.02),
(8, 220000.00, 4.65, 360, 1131.79),
(9, 300000.00, 4.05, 360, 1432.25);

-- Insert sample ML predictions
INSERT INTO ml_predictions (application_id, model_name, prediction, probability_score, feature_vector) VALUES
(1, 'RandomForest', 'approved', 0.8750, '{"salary": 75000, "age": 35, "credit_score": 720, "existing_loans": 1, "employment_years": 8}'),
(1, 'LogisticRegression', 'approved', 0.8420, '{"salary": 75000, "age": 35, "credit_score": 720, "existing_loans": 1, "employment_years": 8}'),
(2, 'RandomForest', 'approved', 0.7230, '{"salary": 45000, "age": 28, "credit_score": 680, "existing_loans": 0, "employment_years": 4}'),
(2, 'LogisticRegression', 'approved', 0.7150, '{"salary": 45000, "age": 28, "credit_score": 680, "existing_loans": 0, "employment_years": 4}'),
(3, 'RandomForest', 'approved', 0.9250, '{"salary": 95000, "age": 42, "credit_score": 780, "existing_loans": 2, "employment_years": 12}'),
(3, 'LogisticRegression', 'approved', 0.9180, '{"salary": 95000, "age": 42, "credit_score": 780, "existing_loans": 2, "employment_years": 12}'),
(6, 'RandomForest', 'rejected', 0.2150, '{"salary": 38000, "age": 26, "credit_score": 620, "existing_loans": 0, "employment_years": 2}'),
(6, 'LogisticRegression', 'rejected', 0.2380, '{"salary": 38000, "age": 26, "credit_score": 620, "existing_loans": 0, "employment_years": 2}');