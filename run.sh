#!/bin/bash

# GAIA Project - Quick Start Script
# Starts both backend and frontend servers

set -e

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║   ██████╗  █████╗ ██╗ █████╗                                     ║"
echo "║  ██╔════╝ ██╔══██╗██║██╔══██╗                                    ║"
echo "║  ██║  ███╗███████║██║███████║                                    ║"
echo "║  ██║   ██║██╔══██║██║██╔══██║                                    ║"
echo "║  ╚██████╔╝██║  ██║██║██║  ██║                                    ║"
echo "║   ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝                                    ║"
echo "║                                                                   ║"
echo "║   Global AI-powered Impact Assessment                            ║"
echo "║   Multi-Agent ESG & SDG Analysis Platform                        ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cleanup function
cleanup() {
    log_info "Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.10+."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 18+."
    exit 1
fi

# Start Backend
log_info "Starting GAIA Backend..."
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    log_info "Installing Python dependencies..."
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt > /dev/null
    touch venv/.installed
    log_success "Python dependencies installed!"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    log_info "Creating backend .env file..."
    cp .env.example .env 2>/dev/null || echo "ENVIRONMENT=development" > .env
fi

# Start backend server in background
log_info "Launching FastAPI server on http://localhost:8000..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend
log_info "Starting GAIA Frontend..."
cd "$FRONTEND_DIR"

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    log_info "Installing npm dependencies..."
    npm install > /dev/null 2>&1
    log_success "npm dependencies installed!"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    log_info "Creating frontend .env file..."
    cp .env.example .env 2>/dev/null || echo "VITE_API_URL=http://localhost:8000" > .env
fi

# Start frontend server in background
log_info "Launching Vite dev server on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                     GAIA is now running!                          ║"
echo "╠═══════════════════════════════════════════════════════════════════╣"
echo "║                                                                   ║"
echo "║   Frontend:     http://localhost:3000                             ║"
echo "║   Backend API:  http://localhost:8000                             ║"
echo "║   API Docs:     http://localhost:8000/docs                        ║"
echo "║                                                                   ║"
echo "║   Press Ctrl+C to stop all servers                                ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Wait for processes
wait
