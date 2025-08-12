#!/bin/bash

echo "🛠️ Vahan Dashboard Environment Setup"
echo "====================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')
required_version="3.9"

if [[ $(echo "$python_version >= $required_version" | bc -l) -eq 1 ]]; then
    echo "✅ Python $python_version found"
else
    echo "❌ Python $required_version or higher required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create data directory
mkdir -p data

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the dashboard:"
echo "  streamlit run main.py"
echo ""
echo "To run with Docker:"
echo "  ./deploy.sh local"
