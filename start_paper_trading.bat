@echo off
REM AITrading - Paper Trading Startup Script for Windows
REM This script starts the trading bot in paper (simulation) mode

echo ========================================
echo   AITrading - Paper Trading Mode
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check if in correct directory
if not exist "main.py" (
    echo [ERROR] main.py not found!
    echo Please make sure you are running this script from the AITrading directory.
    pause
    exit /b 1
)

echo [OK] main.py found
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import hyperliquid" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Dependencies not installed. Installing now...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)
echo.

REM Check if config file exists
if not exist "config\config.yaml" (
    echo [ERROR] config\config.yaml not found!
    echo Please make sure the config file exists.
    pause
    exit /b 1
)

echo [OK] Config file found
echo.

REM Start the trading bot
echo ========================================
echo   Starting Trading Bot...
echo   Mode: PAPER (Simulation)
echo   Press Ctrl+C to stop
echo ========================================
echo.

python main.py --mode paper

REM If script exits
echo.
echo ========================================
echo   Trading Bot Stopped
echo ========================================
pause
