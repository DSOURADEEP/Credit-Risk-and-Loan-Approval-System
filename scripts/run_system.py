#!/usr/bin/env python3
"""
Complete system setup and run script for Credit Risk & Loan Approval System
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print system banner"""
    print("=" * 60)
    print("  Credit Risk & Loan Approval System")
    print("  Complete Setup and Launch Script")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_mysql():
    """Check if MySQL is available"""
    try:
        result = subprocess.run(['mysql', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ MySQL: {result.stdout.strip()}")
            return True
        else:
            print("❌ MySQL not found")
            return False
    except FileNotFoundError:
        print("❌ MySQL not found in PATH")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Set up the database"""
    print("\n🗄️  Setting up database...")
    try:
        subprocess.run([sys.executable, 'scripts/setup_database.py'], check=True)
        print("✅ Database setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def generate_training_data():
    """Generate synthetic training data"""
    print("\n📊 Generating training data...")
    try:
        subprocess.run([sys.executable, 'scripts/generate_training_data.py'], check=True)
        print("✅ Training data generated")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Training data generation failed: {e}")
        return False

def train_models():
    """Train ML models"""
    print("\n🤖 Training ML models...")
    try:
        subprocess.run([sys.executable, 'scripts/train_models.py'], check=True)
        print("✅ ML models trained successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ML model training failed: {e}")
        return False

def check_environment():
    """Check if .env file exists"""
    env_file = Path('.env')
    if not env_file.exists():
        print("\n⚠️  .env file not found")
        print("Creating .env file from template...")
        try:
            with open('.env.example', 'r') as template:
                with open('.env', 'w') as env:
                    env.write(template.read())
            print("✅ .env file created from template")
            print("📝 Please edit .env file with your database credentials")
            return False
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✅ .env file found")
        return True

def test_system():
    """Test system components"""
    print("\n🧪 Testing system components...")
    
    # Test database connection
    try:
        from app.database import test_connection
        if test_connection():
            print("✅ Database connection: OK")
        else:
            print("❌ Database connection: Failed")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    # Test ML models
    try:
        from app.services.ml_service import ml_service
        if ml_service.is_ready():
            print("✅ ML models: Loaded")
        else:
            print("❌ ML models: Not ready")
            return False
    except Exception as e:
        print(f"❌ ML models test failed: {e}")
        return False
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting the application server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")

def main():
    """Main setup and run function"""
    print_banner()
    
    # Check prerequisites
    check_python_version()
    
    if not check_mysql():
        print("\n❌ MySQL is required but not found")
        print("Please install MySQL and ensure it's in your PATH")
        sys.exit(1)
    
    # Check environment file
    if not check_environment():
        print("\n⚠️  Please configure your .env file and run this script again")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Setup Database", setup_database),
        ("Generate Training Data", generate_training_data),
        ("Train ML Models", train_models),
        ("Test System", test_system)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at step: {step_name}")
            print("Please check the error messages above and try again")
            sys.exit(1)
    
    print("\n🎉 System setup completed successfully!")
    print("\nSystem is ready to use:")
    print("- Database: Configured and populated")
    print("- ML Models: Trained and ready")
    print("- API: Ready to serve requests")
    print("- Web Interface: Ready for users")
    
    # Ask user if they want to start the server
    try:
        response = input("\nWould you like to start the server now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            start_server()
        else:
            print("\n📝 To start the server manually, run:")
            print("   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    except KeyboardInterrupt:
        print("\n\n👋 Setup completed. Goodbye!")

if __name__ == "__main__":
    main()