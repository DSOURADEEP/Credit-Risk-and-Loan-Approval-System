# Credit Risk & Loan Approval System

A comprehensive loan processing application that combines rule-based validation with machine learning models to evaluate loan applications. The system provides automated risk assessment using both traditional business rules and ML algorithms, delivering loan approval decisions with risk categorization and suggested terms.

## Features

- **Automated Loan Processing**: Complete workflow from application to decision
- **Rule-Based Validation**: Configurable business rules for initial screening
- **ML-Powered Risk Assessment**: Random Forest and Logistic Regression models
- **Risk Categorization**: Low, Medium, High risk classification
- **Dynamic Loan Terms**: Interest rates and terms based on risk assessment
- **Professional Banking UI**: Modern, responsive web interface
- **Real-time Processing**: Instant loan decisions with detailed reasoning
- **Comprehensive API**: RESTful endpoints for all operations
- **Loan History Tracking**: Complete application history per customer

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MySQL**: Relational database for data persistence
- **Rule Engine**: Smart loan assessment algorithm
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Modern CSS**: Professional banking-style UI
- **Responsive Design**: Works on desktop and mobile

### ML Models
- **Random Forest Classifier**: Ensemble learning for robust predictions
- **Logistic Regression**: Linear model for interpretable results
- **Feature Engineering**: Derived features for better predictions

## Quick Start

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd credit-risk-loan-approval
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your database credentials
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   DATABASE_NAME=loan_approval_db
   DATABASE_USER=root
   DATABASE_PASSWORD=your_password
   ```

4. **Set up the database**
   ```bash
   python scripts/setup_database.py
   ```

5. **Generate training data and train ML models**
   ```bash
   python scripts/generate_training_data.py
   python scripts/train_models.py
   ```

6. **Start the application**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Detailed Setup Instructions

### 1. Database Setup

The system uses MySQL to store customer data, loan applications, and ML predictions.

```bash
# Start MySQL service
sudo systemctl start mysql  # Linux
brew services start mysql   # macOS

# Create database and tables
python scripts/setup_database.py
```

The setup script will:
- Create the `loan_approval_db` database
- Create all required tables with proper relationships
- Insert sample data for testing
- Set up indexes for optimal performance

### 2. Machine Learning Model Training

Generate synthetic training data and train the ML models:

```bash
# Generate training datasets
python scripts/generate_training_data.py

# Train and save ML models
python scripts/train_models.py
```

This will create:
- `data/training_data_large.csv`: 10,000 synthetic loan applications
- `models/random_forest_model.joblib`: Trained Random Forest model
- `models/logistic_regression_model.joblib`: Trained Logistic Regression model
- `models/training_results.json`: Model performance metrics

### 3. Backend Configuration

The backend uses environment variables for configuration:

```bash
# Database settings
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=loan_approval_db
DATABASE_USER=root
DATABASE_PASSWORD=your_password

# Rule engine thresholds
MIN_SALARY=30000
MIN_CREDIT_SCORE=600
MAX_DEBT_TO_INCOME_RATIO=0.4

# Risk assessment parameters
LOW_RISK_THRESHOLD=0.8
HIGH_RISK_THRESHOLD=0.4
```

### 4. Running the Application

Start the FastAPI backend:

```bash
# Development mode with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

### Core Endpoints

#### Submit Loan Application
```http
POST /api/v1/loans/apply
Content-Type: application/json

{
  "customer_name": "John Smith",
  "customer_age": 35,
  "customer_salary": 75000,
  "customer_credit_score": 720,
  "loan_amount": 250000,
  "existing_loans": 1,
  "monthly_income": 6250,
  "employment_years": 8
}
```

#### Get Loan Decision
```http
GET /api/v1/loans/{application_id}/decision
```

#### Get Customer Loan History
```http
GET /api/v1/customers/{customer_id}/history
```

#### Health Check
```http
GET /api/v1/health/detailed
```

### Response Examples

**Successful Loan Application:**
```json
{
  "application_id": 123,
  "customer_id": 456,
  "status": "approved",
  "risk_category": "low",
  "decision_reason": "Approved by ML models (confidence: 87%)",
  "processing_time_ms": 245,
  "loan_terms": {
    "approved_amount": 250000,
    "interest_rate": 4.25,
    "tenure_months": 360,
    "monthly_payment": 1230.12
  }
}
```

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │◄──►│ • FastAPI       │◄──►│ • MySQL         │
│ • Form Validation│    │ • Pydantic      │    │ • Customer Data │
│ • Results Display│    │ • Business Logic│    │ • Applications  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   ML Models     │
                       │                 │
                       │ • Random Forest │
                       │ • Logistic Reg. │
                       │ • Risk Assessment│
                       └─────────────────┘
```

## Loan Processing Workflow

1. **Customer Input**: User submits loan application through web form
2. **Data Validation**: Pydantic models validate input data
3. **Rule-Based Checks**: Business rules evaluate basic eligibility
4. **ML Prediction**: Both models predict approval probability
5. **Risk Assessment**: System determines risk category
6. **Loan Terms Calculation**: Interest rate and terms based on risk
7. **Final Decision**: Combined rule and ML results determine outcome
8. **Response**: User receives instant decision with detailed reasoning

## Rule-Based Validation

The system enforces configurable business rules:

- **Minimum Salary**: $30,000 (configurable)
- **Minimum Credit Score**: 600 (configurable)
- **Maximum Debt-to-Income Ratio**: 40% (configurable)
- **Age Requirements**: 18-75 years
- **Employment History**: Minimum 6 months
- **Loan Amount Limits**: $1,000 - $2,000,000

## ML Model Details

### Features Used
- Age
- Annual Salary
- Credit Score
- Loan Amount
- Number of Existing Loans
- Employment Years
- Monthly Income
- Loan-to-Income Ratio
- Debt-to-Income Ratio

### Model Performance
- **Random Forest**: ~92% accuracy, high precision
- **Logistic Regression**: ~89% accuracy, good interpretability
- **Combined Decision**: Uses consensus and confidence scoring

## Risk Assessment

### Risk Categories
- **Low Risk**: High approval probability, best terms
- **Medium Risk**: Moderate approval probability, standard terms
- **High Risk**: Lower approval probability, higher interest rates (13.5% - 18%)

### Loan Terms Calculation
- **Interest Rates**: 8.5% - 18% based on risk (realistic market rates)
- **Loan Amount**: May be reduced for higher risk applicants
- **Tenure**: 12-30 years based on risk and affordability
- **DTI Limits**: Enforced per risk category

## Testing

### Manual Testing
1. Access http://localhost:8000
2. Fill out the loan application form
3. Submit and verify the decision process
4. Test different scenarios (high/low credit scores, etc.)
5. Check loan history functionality

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test loan application
curl -X POST http://localhost:8000/api/v1/loans/apply \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Test User","customer_age":30,"customer_salary":50000,"customer_credit_score":700,"loan_amount":200000,"existing_loans":0,"monthly_income":4167,"employment_years":5}'
```

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check MySQL service
sudo systemctl status mysql

# Verify credentials in .env file
# Ensure database exists
mysql -u root -p -e "SHOW DATABASES;"
```

**ML Models Not Loading**
```bash
# Verify model files exist
ls -la models/

# Retrain models if needed
python scripts/train_models.py
```

**Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process or use different port
uvicorn app.main:app --port 8001
```

## Production Deployment

### Environment Setup
```bash
# Set production environment variables
export ENVIRONMENT=production
export DEBUG=false
export DATABASE_URL=mysql://user:pass@host:port/db

# Use production WSGI server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Security Considerations
- Use environment variables for sensitive data
- Enable HTTPS in production
- Configure CORS appropriately
- Implement rate limiting
- Add authentication if required
- Regular security updates

### Monitoring
- Health check endpoints available
- Database connection monitoring
- ML model performance tracking
- Application metrics and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Check application logs for errors
- Verify database connectivity and ML model availability