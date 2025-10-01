@echo off
echo ========================================
echo NAS Server Deployment Script
echo ========================================
echo.

set NAS_IP=192.168.50.150
set NAS_USER=admin
set NAS_PATH=/volume1/docker/auto_stock/backend

echo Files to deploy:
echo   1. backtest/engine.py (762 lines)
echo   2. indicators/calculator.py (967 lines)
echo.

echo Step 1: Uploading engine.py...
scp "backend\backtest\engine.py" %NAS_USER%@%NAS_IP%:%NAS_PATH%/backtest/engine.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to upload engine.py
    pause
    exit /b 1
)
echo [OK] engine.py uploaded

echo.
echo Step 2: Uploading calculator.py...
scp "backend\indicators\calculator.py" %NAS_USER%@%NAS_IP%:%NAS_PATH%/indicators/calculator.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to upload calculator.py
    pause
    exit /b 1
)
echo [OK] calculator.py uploaded

echo.
echo Step 3: Restarting Docker container...
ssh %NAS_USER%@%NAS_IP% "cd /volume1/docker/auto_stock && docker-compose restart backend"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to restart container
    pause
    exit /b 1
)
echo [OK] Container restarted

echo.
echo Step 4: Checking logs...
timeout /t 3 >nul
ssh %NAS_USER%@%NAS_IP% "docker logs --tail=50 auto_stock_backend | grep -i -E 'startup|ready|error'"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Test backtest with MACD strategy
echo   2. Check for "Calculating 1 indicators"
echo   3. Verify trade count ^> 0
echo.

pause