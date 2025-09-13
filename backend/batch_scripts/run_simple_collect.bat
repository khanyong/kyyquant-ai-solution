@echo off
chcp 65001 > nul
cls

set PYTHON32=C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe

echo =====================================
echo Kiwoom Data Collection (No Login)
echo =====================================
echo.
echo KOA Studio must be logged in already!
echo.
echo Collecting 5 major stocks:
echo - Samsung Electronics, SK Hynix
echo - Kakao, Naver, Hyundai Motor
echo.
pause

echo.
echo 🚀 데이터 수집 시작...
echo.

%PYTHON32% collect_simple_kiwoom.py

echo.
pause