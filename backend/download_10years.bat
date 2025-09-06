@echo off
echo ============================================================
echo Kiwoom Stock Data Download - 10 YEARS COMPLETE VERSION
echo ============================================================
echo.
echo IMPORTANT: This will download 10 years of daily data
echo - Uses continuous queries (slower but complete)
echo - About 2500-3000 days per stock
echo - Estimated time: 8-10 hours for all stocks
echo.
echo Data will be saved to: D:\Dev\auto_stock\data\kiwoom_10years
echo.
echo Prerequisites:
echo   1. KOA Studio is running (as Administrator)
echo   2. You are logged in to KOA Studio
echo.
echo Press Ctrl+C to cancel, or Enter to start...
pause

cd /d D:\Dev\auto_stock\backend

REM Delete old data
echo.
echo Cleaning old data...
del /q D:\Dev\auto_stock\data\kiwoom\*.csv 2>nul
rmdir /s /q D:\Dev\auto_stock\data\kiwoom 2>nul

REM Run 10-year download
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_stocks_10years.py

echo.
echo Download Complete!
pause