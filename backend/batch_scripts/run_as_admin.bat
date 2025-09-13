@echo off
echo 키움 OpenAPI+ 실행 (관리자 권한)
echo ================================

REM 관리자 권한 요청
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d D:\Dev\auto_stock\backend && C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe kiwoom_handle_fix.py && pause' -Verb RunAs"