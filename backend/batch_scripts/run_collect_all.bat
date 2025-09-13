@echo off
chcp 65001 > nul
cls

set PYTHON32=C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe

echo =====================================
echo COLLECT ALL STOCKS DATA
echo =====================================
echo.
echo WARNING: This will collect 2000+ stocks
echo Estimated time: 1-2 hours
echo.
echo Options:
echo [1] Test mode (50 stocks)
echo [2] Small batch (200 stocks)  
echo [3] Medium batch (500 stocks)
echo [4] Full collection (ALL stocks)
echo [5] Resume previous collection
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting test mode - 50 stocks...
    %PYTHON32% collect_all_stocks.py --limit 50
)
if "%choice%"=="2" (
    echo.
    echo Starting small batch - 200 stocks...
    %PYTHON32% collect_all_stocks.py --limit 200
)
if "%choice%"=="3" (
    echo.
    echo Starting medium batch - 500 stocks...
    %PYTHON32% collect_all_stocks.py --limit 500
)
if "%choice%"=="4" (
    echo.
    echo Starting FULL collection...
    echo Press Ctrl+C to stop - progress will be saved
    %PYTHON32% collect_all_stocks.py
)
if "%choice%"=="5" (
    echo.
    echo Resuming previous collection...
    %PYTHON32% collect_all_stocks.py --resume
)

echo.
pause