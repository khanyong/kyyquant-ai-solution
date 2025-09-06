@echo off
echo 키움 OpenAPI+ 최종 수정 버전 실행
echo ================================
echo.

REM 32비트 Python 경로
set PYTHON32=C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe

REM Python 버전 확인
echo Python 버전:
%PYTHON32% --version
echo.

REM 스크립트 실행
echo 실행 중...
%PYTHON32% kiwoom_final_fix.py

pause