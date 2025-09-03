@echo off
chcp 65001 > nul
echo =====================================
echo 키움 트레이딩 API 테스트
echo =====================================
echo.

cd /d D:\Dev\auto_stock\backend

echo [1] 32비트 가상환경 활성화...
call venv32\Scripts\activate.bat

echo.
echo [2] 트레이딩 API 테스트 실행...
echo.
echo 기능:
echo - 종목정보 조회 (삼성전자)
echo - 실시간 시세 수신
echo - 계좌잔고 조회
echo - 주문 기능 (테스트용)
echo.
python kiwoom_trading_api.py

echo.
pause