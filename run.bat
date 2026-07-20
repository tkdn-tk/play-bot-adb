@echo off
setlocal

echo =========================================
echo Cookie Run - AutoPlay ^& Gift Bot
echo =========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b
)

REM Check if venv exists, create if not
if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [3/3] Installing/Checking dependencies...
pip install -r requirements.txt -q

REM Check config.yaml
if not exist config.yaml (
    echo [!] config.yaml not found! Copying from config.example.yaml...
    copy config.example.yaml config.yaml
    echo [!] Please edit config.yaml with your settings before running again.
    pause
    exit /b
)

echo.
echo Starting bot...
echo =========================================
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [!] Bot exited with an error.
    pause
)