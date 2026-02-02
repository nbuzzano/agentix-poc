#!/bin/bash
# Install script for Agentix

set -e

echo "🚀 Installing Agentix..."

# Check Python version
python_version=$(python3 --version | awk '{print $2}')
required_version="3.10"

echo "📦 Python version: $python_version"

# Create virtual environment
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    echo "📁 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
fi

# Initialize project
echo "📁 Initializing project structure..."
mkdir -p data/input data/output data/synthetic logs

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: agentix init"
echo "  4. Run: agentix translate"
echo ""
