#!/bin/bash

# AI Voice Chat - Startup Script

echo "=========================================="
echo "  AI Voice Chat Application"
echo "=========================================="
echo ""

# Kill any existing process on port 1111
echo "🔧 Checking for existing processes on port 1111..."
if lsof -ti:1111 >/dev/null 2>&1; then
    echo "   Stopping existing server..."
    lsof -ti:1111 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Check if required files exist
echo "🔍 Checking required files..."
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    exit 1
fi

if [ ! -f "reference_audio.wav" ]; then
    echo "❌ Error: reference_audio.wav not found!"
    exit 1
fi

if [ ! -d "templates" ] || [ ! -d "static" ]; then
    echo "❌ Error: templates or static directory not found!"
    exit 1
fi

echo "✓ All required files found"
echo ""

# Start the application
echo "🚀 Starting AI Voice Chat server..."
echo "   Loading models (this may take 30-60 seconds)..."
echo ""

python app.py

# This line will only execute if the server stops
echo ""
echo "Server stopped."
