@echo off
chcp 65001 > nul
echo =====================================
echo 키움증권 로그인 테스트
echo =====================================
echo.

cd /d D:\Dev\auto_stock\backend

echo [1] 32비트 가상환경 활성화...
call venv32\Scripts\activate.bat

echo.
echo [2] 로그인 테스트 실행...
echo.
echo 주의사항:
echo - 키움 로그인 창이 열립니다
echo - 모의투자 ID/PW로 로그인하세요
echo - 공인인증서는 선택사항입니다
echo.
python kiwoom_login_test.py

echo.
pause