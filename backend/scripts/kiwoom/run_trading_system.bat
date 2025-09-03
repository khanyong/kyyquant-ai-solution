@echo off
chcp 65001 > nul
echo =====================================
echo 키움 자동매매 시스템 실행
echo =====================================
echo.

cd /d D:\Dev\auto_stock\backend

echo [1] 32비트 가상환경 활성화...
call venv32\Scripts\activate.bat

echo.
echo [2] 필수 패키지 확인...
pip install supabase fastapi uvicorn numpy -q

echo.
echo 실행할 모드를 선택하세요:
echo 1. 키움-Supabase 브릿지 (실시간 데이터 수신)
echo 2. 전략 관리 API 서버
echo 3. 전체 시스템 (브릿지 + API)
echo.
set /p MODE=선택 (1-3): 

if "%MODE%"=="1" (
    echo.
    echo [키움-Supabase 브릿지 실행]
    echo - 실시간 시세 수신
    echo - 전략 모니터링
    echo - 자동 주문 실행
    echo.
    python kiwoom_supabase_bridge.py
) else if "%MODE%"=="2" (
    echo.
    echo [전략 관리 API 서버 실행]
    echo - 포트: 8001
    echo - 주소: http://localhost:8001
    echo.
    python -m uvicorn api_strategy_routes:app --host 0.0.0.0 --port 8001 --reload
) else if "%MODE%"=="3" (
    echo.
    echo [전체 시스템 실행]
    echo 두 개의 창이 열립니다:
    echo 1. 키움 브릿지
    echo 2. API 서버
    echo.
    start cmd /k "call venv32\Scripts\activate && python kiwoom_supabase_bridge.py"
    timeout /t 3 > nul
    start cmd /k "call venv32\Scripts\activate && python -m uvicorn api_strategy_routes:app --host 0.0.0.0 --port 8001 --reload"
    echo.
    echo 시스템이 실행되었습니다.
    echo 종료하려면 각 창을 닫아주세요.
) else (
    echo 잘못된 선택입니다.
)

echo.
pause