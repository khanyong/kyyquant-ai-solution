@echo off
echo Checking NAS backend logs...
echo.

REM NAS 서버 정보
set NAS_IP=192.168.50.150
set NAS_USER=admin

echo Connecting to NAS and showing recent logs...
echo.

REM SSH로 NAS 접속하여 로그 확인
ssh %NAS_USER%@%NAS_IP% "docker logs --tail=100 auto_stock_backend 2>&1 | grep -i -E 'engine|indicator|calculating|error'"

pause