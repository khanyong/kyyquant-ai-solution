@echo off
chcp 65001 >nul
echo ============================================================
echo Kiwoom Stock Data Download (Admin Mode)
echo ============================================================

REM Check admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
    goto :run
) else (
    echo [INFO] Requesting Administrator privileges...
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)

:run
echo.
echo Download Settings:
echo - Period: 10 years daily data
echo - Markets: KOSPI, KOSDAQ  
echo - Progress saved in: download_progress.json
echo - Resume supported
echo.
echo ============================================================
echo.

REM Check KOA Studio
echo [1/2] Please make sure:
echo       - KOA Studio is running (with Administrator privileges)
echo       - You are logged in to KOA Studio
echo.
echo       If not ready:
echo       1. Run KOA Studio as Administrator
echo       2. Login (File -> Login)
echo.
echo [2/2] Press Enter when ready...
pause

echo.
echo [3/3] Starting download...
echo.

REM Change to working directory
cd /d D:\Dev\auto_stock\backend

REM Run with 32-bit Python
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_stocks.py

echo.
echo ============================================================
echo Download Complete!
echo ============================================================
pause