@echo off
echo ============================================================
echo Kiwoom Stock Data Download
echo ============================================================
echo.
echo Prerequisites:
echo   1. KOA Studio is running (as Administrator)
echo   2. You are logged in to KOA Studio
echo.
echo Press Enter to start download...
pause

cd /d D:\Dev\auto_stock\backend
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_stocks.py

echo.
echo Download Complete!
pause