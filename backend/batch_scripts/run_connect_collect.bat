@echo off
chcp 65001 > nul
cls

set PYTHON32=C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe

echo =====================================
echo Kiwoom Connect and Collect
echo =====================================
echo.
echo This script will:
echo 1. Connect to Kiwoom OpenAPI
echo 2. Collect major stock data
echo 3. Save to Supabase
echo.
echo If login window appears, please login.
echo.
pause

echo.
echo Starting...
echo.

%PYTHON32% connect_and_collect.py

echo.
pause