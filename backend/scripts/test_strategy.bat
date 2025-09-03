@echo off
chcp 65001 > nul
echo =====================================
echo 전략 시스템 테스트
echo =====================================
echo.

cd /d D:\Dev\auto_stock\backend

echo Python 환경에서 테스트 실행 중...
echo.
python test_strategy_system.py

echo.
pause