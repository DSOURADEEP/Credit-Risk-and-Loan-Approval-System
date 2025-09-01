#!/usr/bin/env python3
"""
Deployment verification script
Checks that the application is ready for deployment without ML dependencies
"""

import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check that requirements.txt doesn't contain ML dependencies"""
    print("🔍 Checking requirements.txt...")
    
    with open("requirements.txt", "r") as f:
        requirements = f.read().lower()
    
    ml_packages = ["scikit-learn", "sklearn", "pandas", "numpy", "tensorflow", "torch", "keras"]
    found_ml = []
    
    for package in ml_packages:
        if package in requirements:
            found_ml.append(package)
    
    if found_ml:
        print(f"❌ Found ML dependencies: {found_ml}")
        return False
    else:
        print("✅ No ML dependencies found")
        return True

def check_imports():
    """Check Python files for ML imports"""
    print("🔍 Checking for ML imports in Python files...")
    
    ml_imports = ["sklearn", "pandas", "numpy", "tensorflow", "torch", "keras"]
    found_imports = []
    
    for py_file in Path(".").rglob("*.py"):
        if "venv" in str(py_file) or ".git" in str(py_file):
            continue
            
        try:
            with open(py_file, "r") as f:
                content = f.read()
                for ml_import in ml_imports:
                    if f"import {ml_import}" in content or f"from {ml_import}" in content:
                        found_imports.append(f"{py_file}: {ml_import}")
        except:
            continue
    
    if found_imports:
        print(f"❌ Found ML imports: {found_imports}")
        return False
    else:
        print("✅ No ML imports found")
        return True

def check_service():
    """Check that we're using the simple loan service"""
    print("🔍 Checking loan service implementation...")
    
    try:
        service_file = Path("app/services/simple_loan_service.py")
        if service_file.exists():
            print("✅ Using simple_loan_service (rule-based)")
            return True
        else:
            print("❌ simple_loan_service.py not found")
            return False
    except:
        print("❌ Error checking service file")
        return False

def main():
    """Run all deployment checks"""
    print("🚀 Verifying deployment readiness...\n")
    
    checks = [
        check_requirements(),
        check_imports(),
        check_service()
    ]
    
    if all(checks):
        print("\n✅ All checks passed! Ready for deployment 🎉")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Clean deployment without ML dependencies'")
        print("3. git push origin main")
        print("4. Deploy to Render")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())