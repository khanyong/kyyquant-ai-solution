@echo off
chcp 65001 > nul
cls
echo =====================================
echo 📊 투자설정 데이터 수집 (32-bit Python)
echo =====================================
echo.

REM 32비트 Python 경로 설정 (일반적인 경로들)
set PYTHON32=
if exist "C:\Python38-32\python.exe" set PYTHON32=C:\Python38-32\python.exe
if exist "C:\Python39-32\python.exe" set PYTHON32=C:\Python39-32\python.exe
if exist "C:\Python310-32\python.exe" set PYTHON32=C:\Python310-32\python.exe
if exist "C:\Python311-32\python.exe" set PYTHON32=C:\Python311-32\python.exe
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38-32\python.exe" set PYTHON32=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38-32\python.exe
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39-32\python.exe" set PYTHON32=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39-32\python.exe
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310-32\python.exe" set PYTHON32=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310-32\python.exe

if "%PYTHON32%"=="" (
    echo ❌ 32비트 Python을 찾을 수 없습니다!
    echo.
    echo 직접 Python 경로를 입력하세요:
    echo 예: C:\Python38-32\python.exe
    set /p PYTHON32="32비트 Python 경로: "
)

echo.
echo 사용할 Python: %PYTHON32%
%PYTHON32% -c "import sys; print(f'Python {sys.version}'); print(f'플랫폼: {sys.platform} ({8*sys.maxsize} bit)')"

echo.
echo =====================================
echo 데이터 수집 옵션:
echo [1] 주요 종목만 (10개)
echo [2] 테스트 (10개 종목)
echo [3] 전체 종목
echo [4] 데이터 정보 확인
echo =====================================
echo.

set /p choice="선택 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🎯 주요 종목 수집 시작...
    %PYTHON32% collect_investment_data.py --major
) else if "%choice%"=="2" (
    echo.
    echo 🧪 테스트 모드 (10개)...
    %PYTHON32% collect_investment_data.py --all --limit 10
) else if "%choice%"=="3" (
    echo.
    echo 📊 전체 종목 수집 시작...
    %PYTHON32% collect_investment_data.py --all
) else if "%choice%"=="4" (
    echo.
    echo 📈 데이터 정보 확인...
    %PYTHON32% collect_investment_data.py --info
) else (
    echo ❌ 잘못된 선택
)

echo.
pause