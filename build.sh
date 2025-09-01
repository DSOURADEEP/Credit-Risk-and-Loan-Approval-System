#!/bin/bash

# Simplified build script for Render deployment
set -o errexit  # exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up application directories..."
mkdir -p data models static templates

echo "Application setup completed successfully!"
echo "Using rule-based loan assessment system"