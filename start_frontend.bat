@echo off
chcp 65001 > nul
echo =====================================
echo 프론트엔드 서버 시작
echo =====================================
echo.

cd /d D:\Dev\auto_stock

echo [1] 패키지 확인 중...
if not exist node_modules (
    echo 패키지 설치 필요. npm install 실행 중...
    npm install
)

echo.
echo [2] 프론트엔드 개발 서버 시작...
echo.
echo 서버 주소: http://localhost:5173
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.
npm run dev