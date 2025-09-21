@echo off
echo 🍒 Starting Cherry AI Desktop Assistant...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo Visit: https://python.org/downloads/
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo ⚠️ Warning: .env file not found!
    echo Please run install.py first or create .env from .env.example
    pause
)

REM Start Cherry
echo ✅ Starting Cherry...
venv\Scripts\activate py main.py

if errorlevel 1 (
    echo.
    echo ❌ Cherry encountered an error!
    echo Check the logs in data/logs/cherry.log
    pause
)
