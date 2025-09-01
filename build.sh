#!/bin/bash

# Render deployment script - optimized for Python 3.13
set -o errexit  # exit on error

echo "🚀 Starting Render deployment..."
echo "Python version: $(python --version)"

echo "📦 Installing dependencies..."
pip install --upgrade pip

# Use render-optimized requirements with pre-compiled wheels only
pip install --only-binary=all --no-cache-dir -r requirements-render.txt

echo "📁 Setting up directories..."
mkdir -p data models static templates

echo "⚙️ Running setup..."
python deploy_setup.py

echo "✅ Deployment ready!"
echo "🎯 Using rule-based loan assessment system"