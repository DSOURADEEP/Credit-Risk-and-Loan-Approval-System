"""
Deployment setup script - prepares the application for hosting
"""
import os
import sys
from pathlib import Path

def setup_for_deployment():
    """Setup application for deployment"""
    print("Setting up application for deployment...")
    
    # Create necessary directories
    directories = ["data", "models", "static", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created/verified directory: {directory}")
    
    # Initialize SQLite database
    try:
        from app.database_sqlite import init_sqlite_db
        init_sqlite_db()
        print("✓ SQLite database initialized")
    except Exception as e:
        print(f"⚠ Database initialization failed: {e}")
    
    # Skip ML model training for simplified deployment
    print("✓ Using rule-based assessment (no ML models needed)")
    
    print("\n🚀 Application is ready for deployment!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your repository to your chosen hosting platform")
    print("3. Set environment variables if needed")
    print("4. Deploy!")

if __name__ == "__main__":
    setup_for_deployment()