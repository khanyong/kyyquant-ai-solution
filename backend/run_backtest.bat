@echo off
echo ============================================================
echo Real-Time Backtest Engine
echo ============================================================
echo.
echo Choose backtest mode:
echo.
echo   1. Light Mode (Fast, minimal data)
echo      - Only fetches needed days
echo      - Simple strategies
echo      - 5 stocks test
echo.
echo   2. Standard Mode (Balanced)
echo      - Fetches up to 250 days
echo      - Multiple strategies
echo      - Cache enabled
echo.
echo   3. Download All First (Traditional)
echo      - Downloads everything first
echo      - Then runs backtest offline
echo.
echo ============================================================
echo.
echo Which mode? (1-3):
set /p mode=

cd /d D:\Dev\auto_stock\backend

if "%mode%"=="1" (
    echo Starting Light Backtest...
    C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe backtest_light.py
) else if "%mode%"=="2" (
    echo Starting Standard Backtest...
    C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe backtest_realtime.py
) else if "%mode%"=="3" (
    echo Starting Full Download...
    call download_integrated.bat
) else (
    echo Invalid choice
)

pause