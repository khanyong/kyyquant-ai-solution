@echo off
chcp 65001 > nul
cls

set PYTHON32=C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe

echo =====================================
echo 📦 32비트 Python 모듈 설치
echo =====================================
echo.
echo Python 경로: %PYTHON32%
echo.

echo Python 버전:
%PYTHON32% --version
echo.

echo -------------------------------------
echo pip 업그레이드...
%PYTHON32% -m pip install --upgrade pip

echo.
echo -------------------------------------
echo 필수 모듈 설치 중...
echo.

echo [1/6] PyQt5 설치...
%PYTHON32% -m pip install PyQt5

echo.
echo [2/6] pykiwoom 설치...
%PYTHON32% -m pip install pykiwoom

echo.
echo [3/6] pandas 설치...
%PYTHON32% -m pip install pandas

echo.
echo [4/6] supabase 설치...
%PYTHON32% -m pip install supabase

echo.
echo [5/6] python-dotenv 설치...
%PYTHON32% -m pip install python-dotenv

echo.
echo [6/6] pywin32 설치...
%PYTHON32% -m pip install pywin32

echo.
echo =====================================
echo 설치 확인 중...
echo =====================================
echo.

%PYTHON32% -c "import PyQt5; print('✅ PyQt5 설치됨')" 2>nul || echo ❌ PyQt5 설치 실패
%PYTHON32% -c "import pykiwoom; print('✅ pykiwoom 설치됨')" 2>nul || echo ❌ pykiwoom 설치 실패
%PYTHON32% -c "import pandas; print('✅ pandas 설치됨')" 2>nul || echo ❌ pandas 설치 실패
%PYTHON32% -c "import supabase; print('✅ supabase 설치됨')" 2>nul || echo ❌ supabase 설치 실패
%PYTHON32% -c "import dotenv; print('✅ python-dotenv 설치됨')" 2>nul || echo ❌ python-dotenv 설치 실패
%PYTHON32% -c "import win32com.client; print('✅ pywin32 설치됨')" 2>nul || echo ❌ pywin32 설치 실패

echo.
echo =====================================
echo 설치 완료!
echo =====================================
pause