@echo off
setlocal

echo =========================================
echo Template Detection Tester
echo =========================================

if not exist venv (
    echo [!] Virtual environment not found. Please run run.bat first to install.
    pause
    exit /b
)

call venv\Scripts\activate.bat
python test_templates.py

echo.
pause
