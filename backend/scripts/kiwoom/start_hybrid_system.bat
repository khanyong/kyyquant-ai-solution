@echo off
echo ========================================
echo 키움 하이브리드 시스템 시작
echo ========================================
echo.

REM 1. OpenAPI 브리지 서버 시작 (32비트)
echo [1] OpenAPI 브리지 서버 시작 중...
start "OpenAPI Bridge" cmd /k "cd /d %~dp0 && venv32\Scripts\activate && python kiwoom_openapi_bridge.py"

timeout /t 3 /nobreak > nul

REM 2. 메인 API 서버 시작 (64비트)
echo [2] 메인 API 서버 시작 중...
start "Main API Server" cmd /k "cd /d %~dp0 && python main_api_server.py"

timeout /t 3 /nobreak > nul

REM 3. 상태 확인
echo [3] 시스템 상태 확인 중...
curl -s http://localhost:8100/ > nul
if %errorlevel% equ 0 (
    echo [+] OpenAPI 브리지 서버: 정상
) else (
    echo [!] OpenAPI 브리지 서버: 오류
)

curl -s http://localhost:8000/ > nul
if %errorlevel% equ 0 (
    echo [+] 메인 API 서버: 정상
) else (
    echo [!] 메인 API 서버: 오류
)

echo.
echo ========================================
echo 하이브리드 시스템 시작 완료!
echo.
echo 접속 URL:
echo - OpenAPI Bridge: http://localhost:8100
echo - Main API: http://localhost:8000
echo - Web UI: http://localhost:3000
echo ========================================
pause
