# Requirements Document

## Introduction

The Credit Risk & Loan Approval System is a comprehensive loan processing application that combines rule-based validation with machine learning models to evaluate loan applications. The system collects customer financial data, performs automated risk assessment using both traditional business rules and ML algorithms, and provides loan approval decisions with risk categorization and suggested terms. The application includes a complete backend API, database storage, ML model integration, and a professional banking-style frontend interface.

## Requirements

### Requirement 1

**User Story:** As a loan applicant, I want to submit my financial information through a web form, so that I can apply for a loan and receive an automated decision.

#### Acceptance Criteria

1. WHEN a user accesses the loan application form THEN the system SHALL display input fields for name, age, salary, existing loans, credit score, and past transaction history
2. WHEN a user submits the application form THEN the system SHALL validate all required fields are completed
3. WHEN form validation passes THEN the system SHALL send the application data to the backend API
4. IF any required field is missing THEN the system SHALL display specific error messages for each missing field
5. WHEN the application is successfully submitted THEN the system SHALL redirect to the approval result page

### Requirement 2

**User Story:** As a loan officer, I want the system to automatically evaluate applications using rule-based checks, so that basic eligibility criteria are enforced consistently.

#### Acceptance Criteria

1. WHEN an application is received THEN the system SHALL check minimum salary requirements
2. WHEN an application is received THEN the system SHALL verify credit score meets minimum thresholds
3. WHEN an application is received THEN the system SHALL calculate and validate debt-to-income ratio
4. IF salary is below minimum threshold THEN the system SHALL automatically reject the application
5. IF credit score is below minimum threshold THEN the system SHALL automatically reject the application
6. IF debt-to-income ratio exceeds maximum allowed THEN the system SHALL automatically reject the application
7. WHEN rule-based checks pass THEN the system SHALL proceed to ML model evaluation

### Requirement 3

**User Story:** As a loan officer, I want the system to use machine learning models to assess loan risk, so that approval decisions are data-driven and accurate.

#### Acceptance Criteria

1. WHEN rule-based checks pass THEN the system SHALL run both Random Forest and Logistic Regression models
2. WHEN ML models execute THEN the system SHALL classify applications as Approved, Rejected, or Requires Manual Review
3. WHEN ML models execute THEN the system SHALL generate probability scores for the prediction
4. WHEN models disagree significantly THEN the system SHALL flag the application for manual review
5. WHEN ML prediction is complete THEN the system SHALL store the model results in the database

### Requirement 4

**User Story:** As a loan officer, I want the system to categorize risk levels and suggest appropriate loan terms, so that loan offers are tailored to the applicant's risk profile.

#### Acceptance Criteria

1. WHEN an application is approved THEN the system SHALL assign a risk category of Low, Medium, or High
2. WHEN risk category is Low THEN the system SHALL suggest competitive interest rates and standard loan amounts
3. WHEN risk category is Medium THEN the system SHALL suggest moderate interest rates and adjusted loan amounts
4. WHEN risk category is High THEN the system SHALL suggest higher interest rates and reduced loan amounts
5. WHEN loan terms are calculated THEN the system SHALL include recommended tenure based on risk assessment
6. WHEN terms are generated THEN the system SHALL store the suggested terms in the database

### Requirement 5

**User Story:** As a system administrator, I want customer data and loan applications stored in a MySQL database, so that all information is persisted and can be retrieved for analysis.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL connect to a MySQL database
2. WHEN a loan application is submitted THEN the system SHALL store customer details in the database
3. WHEN an application is processed THEN the system SHALL store the approval status and risk category
4. WHEN loan terms are generated THEN the system SHALL store the suggested terms in the database
5. WHEN database operations fail THEN the system SHALL log errors and return appropriate error messages
6. WHEN the database is set up THEN it SHALL include proper indexes for performance optimization

### Requirement 6

**User Story:** As a loan applicant, I want to view my loan application history, so that I can track the status of my applications over time.

#### Acceptance Criteria

1. WHEN a user requests loan history THEN the system SHALL retrieve all applications for that customer
2. WHEN loan history is displayed THEN it SHALL show application date, status, risk category, and loan terms
3. WHEN no loan history exists THEN the system SHALL display an appropriate message
4. WHEN loan history is retrieved THEN it SHALL be sorted by application date in descending order
5. IF database errors occur THEN the system SHALL display a user-friendly error message

### Requirement 7

**User Story:** As a developer, I want REST APIs for all loan operations, so that the frontend can communicate with the backend and external systems can integrate.

#### Acceptance Criteria

1. WHEN the backend starts THEN it SHALL expose an API endpoint for submitting loan applications
2. WHEN the backend starts THEN it SHALL expose an API endpoint for retrieving risk evaluation and decisions
3. WHEN the backend starts THEN it SHALL expose an API endpoint for fetching customer loan history
4. WHEN API requests are made THEN the system SHALL validate input data and return appropriate HTTP status codes
5. WHEN API errors occur THEN the system SHALL return structured error responses with meaningful messages
6. WHEN API responses are sent THEN they SHALL include proper CORS headers for frontend access

### Requirement 8

**User Story:** As a data scientist, I want machine learning models trained on sample data and saved for production use, so that the system can make consistent predictions.

#### Acceptance Criteria

1. WHEN the ML training script runs THEN it SHALL load sample dataset with salary, age, loan amount, credit score, existing loans, and repayment history
2. WHEN training begins THEN the system SHALL train both Logistic Regression and Random Forest models
3. WHEN training completes THEN the system SHALL save models using joblib for production loading
4. WHEN models are saved THEN they SHALL include model metadata and performance metrics
5. WHEN the backend loads models THEN it SHALL verify model integrity and compatibility
6. IF synthetic data is needed THEN the system SHALL generate realistic financial data for training

### Requirement 9

**User Story:** As a loan applicant, I want a professional banking-style user interface, so that I have confidence in the system's credibility and ease of use.

#### Acceptance Criteria

1. WHEN users access the application THEN they SHALL see a modern, responsive design that works on desktop and mobile
2. WHEN users interact with forms THEN they SHALL receive immediate feedback on input validation
3. WHEN the approval result is displayed THEN it SHALL show the decision, risk category, and suggested terms in a clear format
4. WHEN users navigate between pages THEN the interface SHALL maintain consistent styling and branding
5. WHEN loading operations occur THEN the system SHALL display appropriate loading indicators
6. WHEN errors occur THEN the system SHALL display user-friendly error messages with clear next steps

### Requirement 10

**User Story:** As a system administrator, I want comprehensive setup instructions and database scripts, so that the system can be deployed and maintained easily.

#### Acceptance Criteria

1. WHEN setting up the system THEN there SHALL be clear instructions for MySQL database setup and seeding
2. WHEN setting up the system THEN there SHALL be instructions for training and saving ML models
3. WHEN setting up the system THEN there SHALL be instructions for running the Flask/FastAPI backend
4. WHEN setting up the system THEN there SHALL be instructions for launching the frontend and testing the complete flow
5. WHEN database setup runs THEN it SHALL create all required tables with proper relationships and constraints
6. WHEN the system is deployed THEN all components SHALL work together seamlessly with the provided instructions