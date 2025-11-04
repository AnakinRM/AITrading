@echo off
REM AITrading - Live Trading Startup Script for Windows
REM This script starts the trading bot in LIVE mode with REAL MONEY

echo ========================================
echo   AITrading - LIVE Trading Mode
echo ========================================
echo.
echo [WARNING] This will trade with REAL MONEY!
echo [WARNING] Make sure you have:
echo   1. Tested thoroughly in paper mode
echo   2. Configured correct API keys
echo   3. Set appropriate stop-loss/take-profit
echo   4. Understand all risks involved
echo.
set /p confirm="Type 'YES' to continue: "

if /i not "%confirm%"=="YES" (
    echo.
    echo [CANCELLED] Live trading not started.
    pause
    exit /b 0
)

echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/downloads/
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
    pause
    exit /b 1
)

echo [OK] Config file found
echo.

REM Final confirmation
echo ========================================
echo   FINAL WARNING
echo ========================================
echo   You are about to start LIVE TRADING
echo   This involves REAL MONEY and REAL RISK
echo.
set /p final="Type 'START' to begin live trading: "

if /i not "%final%"=="START" (
    echo.
    echo [CANCELLED] Live trading not started.
    pause
    exit /b 0
)

echo.

REM Start the trading bot
echo ========================================
echo   Starting Trading Bot...
echo   Mode: LIVE (REAL MONEY!)
echo   Press Ctrl+C to stop
echo ========================================
echo.

python main.py --mode live

REM If script exits
echo.
echo ========================================
echo   Trading Bot Stopped
echo ========================================
pause
