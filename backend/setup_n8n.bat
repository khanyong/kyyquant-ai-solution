@echo off
echo ========================================
echo n8n 로컬 서버 설치 및 구성
echo ========================================
echo.

REM n8n 설치 (글로벌)
echo [1/4] n8n 설치 중...
npm install -g n8n

REM n8n 데이터 폴더 생성
echo [2/4] n8n 데이터 폴더 생성...
if not exist "n8n-data" mkdir n8n-data

REM 환경변수 설정
echo [3/4] 환경변수 설정...
set N8N_BASIC_AUTH_ACTIVE=false
set N8N_PORT=5678
set N8N_PROTOCOL=http
set N8N_HOST=localhost
set N8N_ENCRYPTION_KEY=your-encryption-key-here
set N8N_USER_FOLDER=%cd%\n8n-data

echo.
echo ========================================
echo n8n 설정 완료!
echo.
echo n8n 서버 시작: n8n start
echo 접속 주소: http://localhost:5678
echo ========================================
echo.

REM n8n 시작
echo [4/4] n8n 서버를 시작합니다...
n8n start