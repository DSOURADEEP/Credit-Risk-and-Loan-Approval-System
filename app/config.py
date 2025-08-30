import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application configuration settings"""
    
    # Database configuration
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "3306"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "loan_approval_db")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "root")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "password")
    
    # ML Model configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/")
    
    # Rule engine thresholds
    MIN_SALARY: float = float(os.getenv("MIN_SALARY", "30000"))
    MIN_CREDIT_SCORE: int = int(os.getenv("MIN_CREDIT_SCORE", "600"))
    MAX_DEBT_TO_INCOME_RATIO: float = float(os.getenv("MAX_DEBT_TO_INCOME_RATIO", "0.4"))
    
    # Risk assessment parameters
    LOW_RISK_THRESHOLD: float = float(os.getenv("LOW_RISK_THRESHOLD", "0.8"))
    HIGH_RISK_THRESHOLD: float = float(os.getenv("HIGH_RISK_THRESHOLD", "0.4"))
    
    @property
    def database_url(self) -> str:
        """Construct database URL"""
        return f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

settings = Settings()