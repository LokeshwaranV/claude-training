#!/bin/bash

# Elation Health Chat Bot - Quick Start Script

set -e

echo "🏥 Elation Health Chat Bot - Quick Start"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
    read -p "Press enter once you've updated .env..."
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ] && ! grep -q "ANTHROPIC_API_KEY=" .env; then
    echo "❌ ANTHROPIC_API_KEY not found in .env"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ All prerequisites met"
echo ""
echo "🚀 Starting services..."
echo ""

# Load environment variables
export $(cat .env | grep -v '#' | xargs)

# Create data directory
mkdir -p data/sessions

# Start Docker Compose
docker-compose up

echo ""
echo "========================================"
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To stop the services, press Ctrl+C"
echo "========================================"
