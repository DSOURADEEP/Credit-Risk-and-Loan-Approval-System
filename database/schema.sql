-- Credit Risk & Loan Approval System Database Schema

-- Create database
CREATE DATABASE IF NOT EXISTS loan_approval_db;
USE loan_approval_db;

-- Customers table
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL CHECK (age >= 18 AND age <= 100),
    salary DECIMAL(12,2) NOT NULL CHECK (salary >= 0),
    credit_score INT NOT NULL CHECK (credit_score >= 300 AND credit_score <= 850),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_credit_score (credit_score),
    INDEX idx_salary (salary),
    INDEX idx_created_at (created_at)
);

-- Loan applications table
CREATE TABLE loan_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    loan_amount DECIMAL(12,2) NOT NULL CHECK (loan_amount > 0),
    existing_loans INT DEFAULT 0 CHECK (existing_loans >= 0),
    monthly_income DECIMAL(12,2) NOT NULL CHECK (monthly_income > 0),
    employment_years INT NOT NULL CHECK (employment_years >= 0),
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'approved', 'rejected', 'manual_review') NOT NULL DEFAULT 'pending',
    risk_category ENUM('low', 'medium', 'high') NULL,
    decision_reason TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_customer_id (customer_id),
    INDEX idx_status (status),
    INDEX idx_application_date (application_date),
    INDEX idx_risk_category (risk_category)
);

-- Loan terms table
CREATE TABLE loan_terms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    approved_amount DECIMAL(12,2) CHECK (approved_amount > 0),
    interest_rate DECIMAL(5,2) CHECK (interest_rate >= 0 AND interest_rate <= 100),
    tenure_months INT CHECK (tenure_months > 0 AND tenure_months <= 360),
    monthly_payment DECIMAL(12,2) CHECK (monthly_payment > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(id) ON DELETE CASCADE,
    INDEX idx_application_id (application_id)
);

-- ML predictions table
CREATE TABLE ml_predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prediction VARCHAR(50) NOT NULL,
    probability_score DECIMAL(5,4) NOT NULL CHECK (probability_score >= 0 AND probability_score <= 1),
    feature_vector JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(id) ON DELETE CASCADE,
    INDEX idx_application_id (application_id),
    INDEX idx_model_prediction (model_name, prediction),
    INDEX idx_created_at (created_at)
);