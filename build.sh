#!/bin/bash

# Build script for Render deployment
set -o errexit  # exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up application..."
python deploy_setup.py

echo "Build completed successfully!"