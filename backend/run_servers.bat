@echo off
echo ======================================
echo   키움 자동매매 시스템 실행
echo ======================================
echo.

echo [1/2] 백엔드 서버 시작...
start cmd /k "python api_server.py"

timeout /t 3 /nobreak > nul

echo [2/2] 프론트엔드 서버 시작...
start cmd /k "npm run dev"

echo.
echo ======================================
echo   서버 실행 완료!
echo ======================================
echo.
echo 백엔드: http://localhost:8000
echo 프론트엔드: http://localhost:3000
echo API 문서: http://localhost:8000/docs
echo.
echo 종료하려면 각 터미널 창을 닫으세요.
pause