@echo off
chcp 65001 > nul
echo =====================================
echo 백엔드 API 서버 시작
echo =====================================
echo.

cd /d D:\Dev\auto_stock\backend

echo [1] Python 환경 확인 중...
python --version

echo.
echo [2] 필수 패키지 확인 중...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo FastAPI 설치 중...
    pip install fastapi uvicorn python-dotenv supabase requests
)

echo.
echo [3] API 서버 시작...
echo.
echo API 주소: http://localhost:8001
echo API 문서: http://localhost:8001/docs
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.
python -m uvicorn api_strategy_routes:app --host 0.0.0.0 --port 8001 --reload