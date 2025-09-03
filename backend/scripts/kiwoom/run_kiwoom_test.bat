@echo off
chcp 65001 > nul
echo =====================================
echo 키움 API 연결 테스트 실행
echo =====================================
echo.

cd /d D:\Dev\auto_stock\backend

echo [1] 32비트 가상환경 활성화...
call venv32\Scripts\activate.bat

echo.
echo [2] 테스트 실행...
python test_simple_kiwoom.py

echo.
pause