@echo off
REM Elation Health Chat Bot - Quick Start Script (Windows)

echo.
echo 🏥 Elation Health Chat Bot - Quick Start
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo ✏️  Please edit .env and add your ANTHROPIC_API_KEY
    echo.
    pause
)

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ All prerequisites met
echo.
echo 🚀 Starting services...
echo.

REM Create data directory
if not exist data\sessions mkdir data\sessions

REM Start Docker Compose
docker-compose up

echo.
echo ========================================
echo ✅ Services started successfully!
echo.
echo 🌐 Access the application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 📝 To stop the services, press Ctrl+C
echo ========================================
pause
