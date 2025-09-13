@echo off
chcp 65001 > nul
cls

REM 32비트 Python 경로 직접 지정
set PYTHON32=C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe

echo =====================================
echo 📊 투자설정 데이터 수집 (32-bit Python)
echo =====================================
echo.
echo Python 경로: %PYTHON32%
echo.

REM Python 버전 확인
echo Python 버전 확인:
%PYTHON32% --version
echo.

echo =====================================
echo 데이터 수집 옵션:
echo [1] 주요 종목만 (10개) - 권장
echo [2] 테스트 모드 (10개)
echo [3] 전체 종목 수집
echo [4] 데이터 정보 확인
echo [5] 모듈 설치 확인
echo =====================================
echo.

set /p choice="선택 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🎯 주요 종목 수집 시작...
    echo -------------------------------------
    %PYTHON32% collect_investment_data.py --major
) else if "%choice%"=="2" (
    echo.
    echo 🧪 테스트 모드 실행...
    echo -------------------------------------
    %PYTHON32% collect_investment_data.py --all --limit 10
) else if "%choice%"=="3" (
    echo.
    echo 📊 전체 종목 수집 시작...
    echo -------------------------------------
    %PYTHON32% collect_investment_data.py --all
) else if "%choice%"=="4" (
    echo.
    echo 📈 데이터 정보 확인...
    echo -------------------------------------
    %PYTHON32% collect_investment_data.py --info
) else if "%choice%"=="5" (
    echo.
    echo 📦 모듈 설치 확인...
    echo -------------------------------------
    %PYTHON32% check_modules.py
) else (
    echo.
    echo ❌ 잘못된 선택입니다.
)

echo.
echo =====================================
echo 작업이 완료되었습니다.
echo =====================================
pause