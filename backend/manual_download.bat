@echo off
chcp 65001 >nul
echo ============================================================
echo Kiwoom Stock Data Download (Manual Mode)
echo ============================================================
echo.
echo IMPORTANT: Please complete these steps first:
echo.
echo 1. Open Kiwoom OpenAPI+ manually:
echo    - Find "Kiwoom OpenAPI+" in Start Menu
echo    - OR find "KiwoomHero" in Start Menu
echo    - OR run C:\OpenAPI\opstarter.exe
echo.
echo 2. Login to Kiwoom OpenAPI+
echo.
echo 3. Keep the OpenAPI+ window open
echo.
echo ============================================================
echo.
echo After completing above steps, press Enter to start download...
pause

echo.
echo Starting download...
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