#!/bin/bash

# Start script for Meeting Performance Analyzer

echo "🚀 Starting Meeting Performance Analyzer..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your configuration:"
    echo "  GCS_BUCKET_NAME=your-bucket-name"
    echo "  GOOGLE_PROJECT_ID=your-project-id"
    echo ""
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads results static

# Start the server
echo ""
echo "✨ Starting FastAPI server..."
echo "🌐 Access the web interface at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
