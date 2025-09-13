@echo off
echo ============================================================
echo 키움 전체 종목 다운로드 (관리자 권한)
echo ============================================================
echo.
echo [확인 사항]
echo 1. 키움 OpenAPI+가 실행되어 있나요?
echo 2. 키움 OpenAPI+에 로그인되어 있나요?
echo.
echo 위 사항을 확인하고 Enter를 누르세요...
pause

REM 관리자 권한으로 실행
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d D:\Dev\auto_stock\backend && C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_stocks.py && pause' -Verb RunAs"