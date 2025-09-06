@echo off
chcp 65001 > nul
cls

set PYTHON32=C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe

echo =====================================
echo UPDATE ALL STOCK NAMES
echo =====================================
echo.
echo This will update ALL stock names (3,349 stocks)
echo Estimated time: 10-15 minutes
echo.
echo The script will:
echo 1. Get all stock codes from database
echo 2. Fetch correct name from Kiwoom API
echo 3. Update database with correct names
echo.
pause

echo.
echo Starting update...
echo.

%PYTHON32% update_all_stock_names.py

echo.
echo =====================================
echo Update completed!
echo =====================================
pause