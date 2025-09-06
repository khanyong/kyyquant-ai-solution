@echo off
chcp 65001 > nul
cls

set PYTHON32=C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe

echo =====================================
echo Fix Stock Names Encoding
echo =====================================
echo.
echo This will fix broken Korean stock names
echo.
pause

echo.
echo Starting...
echo.

%PYTHON32% fix_stock_names.py

echo.
pause