@echo off
setlocal enabledelayedexpansion

REM 시놀로지 NAS 자동 배포 스크립트 (Windows)
REM Usage: deploy_to_nas.bat [NAS_IP] [NAS_USER]

set NAS_IP=%1
set NAS_USER=%2

if "%NAS_IP%"=="" set NAS_IP=192.168.1.100
if "%NAS_USER%"=="" set NAS_USER=admin

set REMOTE_PATH=/volume1/docker/kiwoom_bridge

echo ====================================================
echo 🚀 시놀로지 NAS 배포 시작
echo 📍 대상: %NAS_USER%@%NAS_IP%
echo 📂 경로: %REMOTE_PATH%
echo ====================================================
echo.

REM Step 1: SSH 연결 테스트
echo 1. SSH 연결 테스트...
ssh -o ConnectTimeout=5 %NAS_USER%@%NAS_IP% "echo 연결 성공" >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] SSH 연결 성공
) else (
    echo    [ERROR] SSH 연결 실패. NAS IP와 사용자명을 확인하세요.
    pause
    exit /b 1
)
echo.

REM Step 2: NAS에 디렉토리 생성
echo 2. NAS에 디렉토리 생성...
ssh %NAS_USER%@%NAS_IP% "mkdir -p %REMOTE_PATH%/logs %REMOTE_PATH%/n8n_workflows"
if %errorlevel% equ 0 (
    echo    [OK] 디렉토리 생성 완료
) else (
    echo    [ERROR] 디렉토리 생성 실패
    pause
    exit /b 1
)
echo.

REM Step 3: 파일 전송
echo 3. 파일 전송 중...

REM main.py 전송
if exist main.py (
    scp main.py %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
    echo    - main.py 전송 완료
) else (
    echo    - main.py 파일 없음
)

REM requirements.txt 전송
if exist requirements.txt (
    scp requirements.txt %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
    echo    - requirements.txt 전송 완료
) else (
    echo    - requirements.txt 파일 없음
)

REM Dockerfile 전송
if exist Dockerfile (
    scp Dockerfile %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
    echo    - Dockerfile 전송 완료
) else (
    echo    - Dockerfile 파일 없음
)

REM docker-compose.yml 전송
if exist docker-compose.yml (
    scp docker-compose.yml %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
    echo    - docker-compose.yml 전송 완료
) else (
    echo    - docker-compose.yml 파일 없음
)

REM .env.example 전송
if exist .env.example (
    scp .env.example %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
    echo    - .env.example 전송 완료
) else (
    echo    - .env.example 파일 없음
)

REM N8N 워크플로우 전송
if exist n8n_workflows\auto_trading_workflow.json (
    scp n8n_workflows\auto_trading_workflow.json %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/n8n_workflows/ >nul 2>&1
    echo    - N8N 워크플로우 전송 완료
) else (
    echo    - N8N 워크플로우 파일 없음
)
echo.

REM Step 4: .env 파일 설정
echo 4. 환경 변수 설정...
ssh %NAS_USER%@%NAS_IP% "cd %REMOTE_PATH% && cp .env.example .env"
echo    [INFO] .env 파일이 생성되었습니다.
echo    [TODO] 다음 값들을 설정해주세요:
echo           - SUPABASE_KEY: 실제 Supabase 키 입력
echo           - FRONTEND_URL: Vercel 앱 URL 또는 http://localhost:3000
echo           - NAS_IP: 실제 NAS IP (현재: %NAS_IP%)
echo.

REM Step 5: Docker 이미지 빌드
echo 5. Docker 이미지 빌드 (몇 분 소요)...
ssh %NAS_USER%@%NAS_IP% "cd %REMOTE_PATH% && sudo docker build -t kiwoom-bridge:latest ."
if %errorlevel% equ 0 (
    echo    [OK] Docker 이미지 빌드 완료
) else (
    echo    [ERROR] Docker 이미지 빌드 실패
    pause
    exit /b 1
)
echo.

REM Step 6: 기존 컨테이너 정리
echo 6. 기존 컨테이너 정리...
ssh %NAS_USER%@%NAS_IP% "sudo docker stop kiwoom-bridge 2>nul & sudo docker rm kiwoom-bridge 2>nul"
echo    [OK] 정리 완료
echo.

REM Step 7: Docker 컨테이너 실행
echo 7. Docker 컨테이너 실행...
ssh %NAS_USER%@%NAS_IP% "cd %REMOTE_PATH% && sudo docker-compose up -d"
if %errorlevel% equ 0 (
    echo    [OK] Docker 컨테이너 실행 중
) else (
    echo    [ERROR] Docker 컨테이너 실행 실패
    pause
    exit /b 1
)
echo.

REM Step 8: 상태 확인
echo 8. 서비스 상태 확인...
timeout /t 5 /nobreak >nul

REM API 서버 상태 확인
ssh %NAS_USER%@%NAS_IP% "curl -s http://localhost:8001/" >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] 키움 API Bridge 서버 정상 작동 중
) else (
    echo    [WARNING] API 서버 응답 대기 중...
)

REM N8N 상태 확인
ssh %NAS_USER%@%NAS_IP% "curl -s http://localhost:5678/" >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] N8N 서버 정상 작동 중
) else (
    echo    [INFO] N8N 서버를 확인하세요
)
echo.

REM Step 9: 로그 확인
echo 9. 최근 로그 (마지막 10줄)...
echo ====================================================
ssh %NAS_USER%@%NAS_IP% "sudo docker logs --tail 10 kiwoom-bridge 2>&1"
echo ====================================================
echo.

REM 완료 메시지
echo ====================================================
echo 배포가 완료되었습니다!
echo ====================================================
echo.
echo 다음 단계:
echo 1. SSH로 NAS 접속: ssh %NAS_USER%@%NAS_IP%
echo 2. 환경 변수 설정: nano %REMOTE_PATH%/.env
echo 3. Docker 재시작: cd %REMOTE_PATH% ^&^& sudo docker-compose restart
echo 4. API 테스트: http://%NAS_IP%:8001/
echo 5. N8N 워크플로우 설정: http://%NAS_IP%:5678/
echo.
echo 전체 가이드: SYNOLOGY_NAS_DEPLOYMENT_GUIDE.md 참조
echo.
pause