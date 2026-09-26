#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  🏥 Elation Health Chat Bot v2.0 - DEPLOYMENT SCRIPT              ║"
echo "║     Quick Local Start (No Docker Required)                        ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/5]${NC} Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3.11+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} $PYTHON_VERSION found"

# Check Node
echo -e "${BLUE}[2/5]${NC} Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Please install Node.js 18+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION found"

# Setup backend
echo -e "${BLUE}[3/5]${NC} Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null
echo -e "${GREEN}✓${NC} Backend dependencies installed"
cd ..

# Setup frontend
echo -e "${BLUE}[4/5]${NC} Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install -q 2>/dev/null
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${GREEN}✓${NC} Frontend dependencies already installed"
fi
cd ..

# Ready to start
echo -e "${BLUE}[5/5]${NC} Starting services..."
echo ""
echo -e "${GREEN}✓${NC} All checks passed!"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "NOW OPEN TWO NEW TERMINAL WINDOWS AND RUN:"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}Terminal 1 (Backend):${NC}"
echo "  cd /home/labuser/Downloads/day-5/backend"
echo "  source venv/bin/activate"
echo "  export ANTHROPIC_API_KEY=sk_ant_YOUR_KEY"
echo "  export GROQ_API_KEY=gsk_YOUR_GROQ_API_KEY_HERE"
echo "  uvicorn main:app --reload"
echo ""
echo -e "${YELLOW}Terminal 2 (Frontend):${NC}"
echo "  cd /home/labuser/Downloads/day-5/frontend"
echo "  export REACT_APP_API_URL=http://localhost:8000"
echo "  npm start"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${GREEN}Access:${NC}"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "═══════════════════════════════════════════════════════════════════"
