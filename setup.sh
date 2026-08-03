#!/bin/bash

# OHLCV Data Validation & Monitoring System - Setup Script
# 
# This script sets up the development environment.
# For comprehensive management, use: ./run.sh
#

set -e

echo "🚀 OHLCV Setup Script"
echo "===================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✓ Python: $python_version"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "✓ Virtual environment created"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    source .venv/bin/activate
    pip install -q --upgrade pip setuptools wheel
    pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✗ requirements.txt not found"
    exit 1
fi
echo ""

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "import pandas; import numpy; import yfinance; import plotly; import streamlit; import loguru; print('✓ All packages imported successfully')" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup Complete!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Activate virtual environment:"
    echo "      source .venv/bin/activate  (macOS/Linux)"
    echo "      .venv\\Scripts\\activate     (Windows)"
    echo ""
    echo "   2. Run the pipeline:"
    echo "      ./run.sh run"
    echo ""
    echo "   3. Launch the dashboard:"
    echo "      ./run.sh dashboard"
    echo ""
    echo "   Or use the master command:"
    echo "      ./run.sh full"
    echo ""
else
    echo ""
    echo "✗ Installation verification failed"
    exit 1
fi
