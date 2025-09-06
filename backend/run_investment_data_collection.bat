@echo off
chcp 65001 > nul
echo =====================================
echo 키움 투자설정 데이터 수집
echo =====================================
echo.

REM Python 환경 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

echo 1. 키움 OpenAPI+ 로그인 확인
echo    - 키움 OpenAPI+가 실행되어 있는지 확인하세요
echo    - 로그인이 되어 있는지 확인하세요
echo.
echo 계속하려면 아무 키나 누르세요...
pause > nul

echo.
echo 2. 데이터 수집 옵션 선택:
echo    [1] 전체 종목 데이터 수집
echo    [2] 테스트 (10개 종목만)
echo    [3] 최신 데이터 정보 확인
echo    [4] 주요 종목만 수집 (삼성전자, SK하이닉스 등)
echo.

set /p choice="선택하세요 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 📊 전체 종목 데이터 수집을 시작합니다...
    echo    (시간이 오래 걸릴 수 있습니다)
    echo.
    python collect_investment_data.py --all
) else if "%choice%"=="2" (
    echo.
    echo 🧪 테스트 모드: 10개 종목만 수집합니다...
    echo.
    python collect_investment_data.py --all --limit 10
) else if "%choice%"=="3" (
    echo.
    echo 📈 최신 데이터 정보를 확인합니다...
    echo.
    python collect_investment_data.py --info
) else if "%choice%"=="4" (
    echo.
    echo 🎯 주요 종목만 수집합니다...
    echo.
    python collect_investment_data.py --major
) else (
    echo.
    echo ❌ 잘못된 선택입니다.
    pause
    exit /b 1
)

echo.
echo =====================================
echo ✅ 작업 완료
echo =====================================
echo.
echo Supabase에서 데이터를 확인하세요:
echo - kw_financial_snapshot (시계열 데이터)
echo - kw_financial_ratio (최신 재무비율)
echo - kw_price_current (현재가 정보)
echo.
pause