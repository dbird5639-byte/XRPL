@echo off
echo ============================================================
echo Safety and Defense Software - Environment Setup
echo ============================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

echo Python found. Running setup script...
python scripts/setup_environment.py

echo.
echo Setup complete. Press any key to exit...
pause >nul
