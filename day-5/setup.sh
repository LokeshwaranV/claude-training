#!/bin/bash

# Elation Health Chat Bot - Setup Script
# This script automates the setup process

set -e  # Exit on error

echo "🏥 Elation Health Chat Bot - Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version | sed 's/v//')
echo -e "${GREEN}✓ Node.js ${NODE_VERSION}${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}⚠️  npm not found. Please install npm${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm$(npm --version | sed 's/^/: /')${NC}"

echo ""

# Setup Backend
echo -e "${BLUE}🔧 Setting up Backend...${NC}"

if [ ! -d "backend" ]; then
    echo -e "${YELLOW}⚠️  backend directory not found${NC}"
    exit 1
fi

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

cd ..

echo ""

# Setup Frontend
echo -e "${BLUE}🎨 Setting up Frontend...${NC}"

cd frontend

# Install dependencies
echo "Installing npm dependencies..."
npm install --silent
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

cd ..

echo ""

# Check environment files
echo -e "${BLUE}🔐 Checking environment configuration...${NC}"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please update .env with your Groq API key${NC}"
    fi
fi

if [ -f ".env" ]; then
    if grep -q "gsk_" .env; then
        echo -e "${GREEN}✓ Groq API key configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Update GROQ_API_KEY in .env${NC}"
    fi
fi

echo ""

# Summary
echo -e "${BLUE}📊 Setup Summary${NC}"
echo "=================="
echo ""
echo "✅ Backend setup complete"
echo "✅ Frontend setup complete"
echo "✅ Environment configured"
echo ""

# Next steps
echo -e "${GREEN}🚀 Next Steps:${NC}"
echo ""
echo "1. Start Backend:"
echo "   cd backend && python main.py"
echo ""
echo "2. Start Frontend (in new terminal):"
echo "   cd frontend && npm start"
echo ""
echo "3. Open in browser:"
echo "   http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "   • QUICKSTART.md - Quick start guide"
echo "   • GROQ_INTEGRATION.md - Groq setup guide"
echo "   • FRONTEND_UPDATE.md - Frontend details"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"
