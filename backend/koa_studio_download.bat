@echo off
chcp 65001 >nul
echo ============================================================
echo Kiwoom Download with KOA Studio
echo ============================================================
echo.
echo Step 1: Open KOA Studio
echo -------------------------
echo Starting KOA Studio...
echo.

REM Try to start KOA Studio
if exist "C:\OpenAPI\KOAStudioSA.exe" (
    start "" "C:\OpenAPI\KOAStudioSA.exe"
    echo KOA Studio started!
) else (
    echo KOA Studio not found at C:\OpenAPI\KOAStudioSA.exe
    echo Please open KOA Studio manually from Start Menu
)

echo.
echo ============================================================
echo.
echo Step 2: Login to KOA Studio
echo -------------------------
echo In KOA Studio:
echo   1. Click [File] menu
echo   2. Select [Login] or press Ctrl+L
echo   3. Enter your Kiwoom account credentials
echo   4. Wait for "Login successful" message
echo.
echo After login, press Enter here to continue...
pause

echo.
echo ============================================================
echo.
echo Step 3: Starting Download
echo -------------------------
echo Downloading stock data...
echo.

cd /d D:\Dev\auto_stock\backend
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_stocks.py

echo.
echo ============================================================
echo Download Complete!
echo ============================================================
echo.
echo You can close KOA Studio now.
pause