#!/bin/bash

# Simplified build script for Render deployment
set -o errexit  # exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip

# Install dependencies with no cache to avoid compilation issues
pip install --no-cache-dir -r requirements.txt

echo "Setting up application directories..."
mkdir -p data models static templates

echo "Running deployment setup..."
python deploy_setup.py

echo "Application setup completed successfully!"
echo "Using rule-based loan assessment system"