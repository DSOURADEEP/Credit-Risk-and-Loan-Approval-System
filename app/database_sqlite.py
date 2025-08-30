"""
SQLite database configuration for deployment
"""
import sqlite3
import os
from pathlib import Path

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR}/loan_approval.db"

def init_sqlite_db():
    """Initialize SQLite database with required tables"""
    db_path = DATA_DIR / "loan_approval.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            age INTEGER NOT NULL,
            salary DECIMAL(12,2) NOT NULL,
            credit_score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create loan_applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            loan_amount DECIMAL(12,2) NOT NULL,
            existing_loans INTEGER DEFAULT 0,
            monthly_income DECIMAL(12,2) NOT NULL,
            employment_years DECIMAL(4,2) NOT NULL,
            preferred_tenure_years INTEGER,
            status VARCHAR(50) NOT NULL,
            risk_category VARCHAR(20),
            decision_reason TEXT,
            processing_time_ms INTEGER,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    # Create loan_terms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_terms (
            term_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            approved_amount DECIMAL(12,2) NOT NULL,
            interest_rate DECIMAL(5,2) NOT NULL,
            tenure_months INTEGER NOT NULL,
            monthly_payment DECIMAL(12,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        )
    """)
    
    # Create ml_evaluations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_evaluations (
            evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            model_name VARCHAR(100) NOT NULL,
            prediction INTEGER NOT NULL,
            probability DECIMAL(5,4) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"SQLite database initialized at {db_path}")

if __name__ == "__main__":
    init_sqlite_db()