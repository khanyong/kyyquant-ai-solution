@echo off
setlocal enabledelayedexpansion

REM Comprehensive NAS deployment script for all Python files
REM Usage: deploy_all_to_nas.bat [NAS_IP] [NAS_USER]

set NAS_IP=%1
set NAS_USER=%2

if "%NAS_IP%"=="" set NAS_IP=192.168.50.150
if "%NAS_USER%"=="" set NAS_USER=khanyong

set REMOTE_PATH=/volume1/docker/kiwoom_bridge

echo ====================================================
echo Deploying ALL Python files to NAS
echo Target: %NAS_USER%@%NAS_IP%
echo Path: %REMOTE_PATH%
echo ====================================================
echo.

REM Test SSH connection
echo Testing SSH connection...
ssh -o ConnectTimeout=5 %NAS_USER%@%NAS_IP% "echo Connection OK" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: SSH connection failed
    pause
    exit /b 1
)
echo [OK] SSH connected
echo.

REM Create directories
echo Creating directories...
ssh %NAS_USER%@%NAS_IP% "mkdir -p %REMOTE_PATH%/core %REMOTE_PATH%/logs"
echo [OK] Directories created
echo.

REM Transfer all Python files
echo Transferring Python files...

REM Main files
for %%f in (*.py) do (
    echo   - %%f
    scp "%%f" %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
)

REM Core module files
if exist core\*.py (
    echo   - Transferring core module...
    for %%f in (core\*.py) do (
        scp "%%f" %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/core/ >nul 2>&1
    )
)

REM Configuration files
if exist requirements.txt scp requirements.txt %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
if exist Dockerfile scp Dockerfile %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
if exist docker-compose.yml scp docker-compose.yml %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1
if exist .env scp .env %NAS_USER%@%NAS_IP%:%REMOTE_PATH%/ >nul 2>&1

echo [OK] All files transferred
echo.

REM Rebuild Docker image
echo Rebuilding Docker image...
ssh %NAS_USER%@%NAS_IP% "cd %REMOTE_PATH% && sudo docker build -t kiwoom-bridge:latest ."
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)
echo [OK] Docker image built
echo.

REM Restart container
echo Restarting container...
ssh %NAS_USER%@%NAS_IP% "cd %REMOTE_PATH% && sudo docker-compose restart"
echo [OK] Container restarted
echo.

REM Wait for service to start
echo Waiting for service to start...
timeout /t 10 /nobreak >nul
echo.

REM Check service status
echo Checking service status...
ssh %NAS_USER%@%NAS_IP% "sudo docker ps | grep kiwoom-bridge"
echo.

REM Show recent logs
echo Recent logs:
echo ====================================================
ssh %NAS_USER%@%NAS_IP% "sudo docker logs --tail 20 kiwoom-bridge 2>&1"
echo ====================================================
echo.

echo Deployment complete!
echo Test the API at: http://%NAS_IP%:8080/
echo Or via Cloudflare: https://api.bll-pro.com/
echo.
pause