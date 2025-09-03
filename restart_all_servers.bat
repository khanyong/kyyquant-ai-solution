@echo off
chcp 65001 > nul
echo =====================================
echo 모든 서버 재시작
echo =====================================
echo.

echo [1] 기존 프로세스 종료 중...
echo.

REM Node.js 프로세스 종료 (프론트엔드)
echo Node.js 서버 종료...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Node.js 프로세스 종료됨
) else (
    echo - Node.js 프로세스가 실행중이지 않음
)

REM Python 프로세스 종료 (백엔드 API)
echo Python 서버 종료...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Python 프로세스 종료됨
) else (
    echo - Python 프로세스가 실행중이지 않음
)

REM uvicorn 프로세스 종료
taskkill /F /IM uvicorn.exe 2>nul

echo.
echo [2] 3초 대기...
timeout /t 3 /nobreak > nul

echo.
echo =====================================
echo 서버 재시작
echo =====================================
echo.

echo [3] 프론트엔드 서버 시작...
cd /d D:\Dev\auto_stock
start cmd /k "echo [프론트엔드] http://localhost:5173 && npm run dev"

echo.
echo [4] 2초 대기...
timeout /t 2 /nobreak > nul

echo.
echo [5] 백엔드 API 서버 시작...
cd /d D:\Dev\auto_stock\backend
start cmd /k "echo [백엔드 API] http://localhost:8001 && python -m uvicorn api_strategy_routes:app --host 0.0.0.0 --port 8001 --reload"

echo.
echo =====================================
echo 서버 시작 완료!
echo =====================================
echo.
echo 실행된 서버:
echo - 프론트엔드: http://localhost:5173
echo - 백엔드 API: http://localhost:8001
echo - API 문서: http://localhost:8001/docs
echo.
echo 키움 브릿지가 필요한 경우:
echo backend\run_trading_system.bat 실행 후 옵션 1 선택
echo.
echo 모든 창을 닫으려면 이 창을 닫으세요.
echo.
pause