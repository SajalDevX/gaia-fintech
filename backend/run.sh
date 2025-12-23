#!/bin/bash

# GAIA Backend Startup Script

echo "Starting GAIA Backend..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your API keys before running again."
    exit 1
fi

# Run the FastAPI server
echo "Starting FastAPI server on http://0.0.0.0:8000"
python main.py
