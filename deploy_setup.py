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
    
    # Generate training data if not exists
    try:
        if not Path("data/training_data_large.csv").exists():
            print("Generating training data...")
            os.system("python scripts/generate_training_data.py")
            print("✓ Training data generated")
        else:
            print("✓ Training data already exists")
    except Exception as e:
        print(f"⚠ Training data generation failed: {e}")
    
    # Train models if not exists
    try:
        models_exist = any(Path("models").glob("*.joblib"))
        if not models_exist:
            print("Training ML models...")
            os.system("python scripts/train_models.py")
            print("✓ ML models trained")
        else:
            print("✓ ML models already exist")
    except Exception as e:
        print(f"⚠ Model training failed: {e}")
    
    print("\n🚀 Application is ready for deployment!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Connect your repository to your chosen hosting platform")
    print("3. Set environment variables if needed")
    print("4. Deploy!")

if __name__ == "__main__":
    setup_for_deployment()