#!/bin/bash

# GAIA Project - Setup Script
# Initializes the development environment

set -e

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                     GAIA Setup Script                             ║"
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
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION found"
    else
        log_error "Python 3 is not installed. Please install Python 3.10+."
        exit 1
    fi

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js $NODE_VERSION found"
    else
        log_error "Node.js is not installed. Please install Node.js 18+."
        exit 1
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        log_success "npm $NPM_VERSION found"
    else
        log_error "npm is not installed. Please install npm."
        exit 1
    fi

    # Check pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 found"
    else
        log_warning "pip3 not found, will use python3 -m pip"
    fi
}

# Setup Backend
setup_backend() {
    log_info "Setting up backend..."
    cd "$BACKEND_DIR"

    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    else
        log_info "Virtual environment already exists"
    fi

    # Activate and install dependencies
    source venv/bin/activate
    log_info "Installing Python dependencies..."
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt

    # Create .env file
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warning "Please edit backend/.env with your API keys"
    fi

    # Create necessary directories
    mkdir -p logs
    mkdir -p data

    log_success "Backend setup complete!"
    deactivate
}

# Setup Frontend
setup_frontend() {
    log_info "Setting up frontend..."
    cd "$FRONTEND_DIR"

    # Install npm dependencies
    log_info "Installing npm dependencies..."
    npm install

    # Create .env file
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
    fi

    log_success "Frontend setup complete!"
}

# Main setup flow
main() {
    echo "Starting GAIA project setup..."
    echo ""

    check_prerequisites
    echo ""

    setup_backend
    echo ""

    setup_frontend
    echo ""

    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                     Setup Complete!                               ║"
    echo "╠═══════════════════════════════════════════════════════════════════╣"
    echo "║                                                                   ║"
    echo "║   To start the application:                                       ║"
    echo "║                                                                   ║"
    echo "║   Option 1 - Run everything:                                      ║"
    echo "║     ./run.sh                                                      ║"
    echo "║                                                                   ║"
    echo "║   Option 2 - Run with Docker:                                     ║"
    echo "║     docker-compose up                                             ║"
    echo "║                                                                   ║"
    echo "║   Option 3 - Run separately:                                      ║"
    echo "║     Backend:  cd backend && source venv/bin/activate              ║"
    echo "║               python main.py                                      ║"
    echo "║     Frontend: cd frontend && npm run dev                          ║"
    echo "║                                                                   ║"
    echo "║   URLs:                                                           ║"
    echo "║     Frontend:    http://localhost:3000                            ║"
    echo "║     Backend API: http://localhost:8000                            ║"
    echo "║     API Docs:    http://localhost:8000/docs                       ║"
    echo "║                                                                   ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
}

main "$@"
