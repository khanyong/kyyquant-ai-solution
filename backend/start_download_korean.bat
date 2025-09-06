
@echo off
chcp 949 >nul
echo ============================================================
echo 키움 전체 종목 다운로드 (관리자 모드)
echo ============================================================

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] 관리자 권한 실행 중
    goto :run
) else (
    echo [INFO] 관리자 권한 요청 중...
    echo.
    powershell -Command "Start-Process \"%~f0\" -Verb RunAs"
    exit
)

:run
echo.
echo 다운로드 설정:
echo - 기간: 10년치 일봉 데이터
echo - 시장: KOSPI, KOSDAQ  
echo - 진행상태: download_progress.json
echo - 재개 가능
echo.
echo ============================================================
echo.

REM 키움 OpenAPI+ 실행
echo [1/3] 키움 OpenAPI+ 실행 중...
start C:\OpenAPI\opstarter.exe
timeout /t 5 >nul

echo.
echo [2/3] 키움 OpenAPI+에서 로그인하세요
echo       로그인 후 Enter를 누르세요...
pause

echo.
echo [3/3] 다운로드 시작...
echo.

REM 작업 디렉토리 이동
cd /d D:\Dev\auto_stock\backend

REM 32비트 Python으로 실행
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_stocks.py

echo.
echo ============================================================
echo 다운로드 완료\!
echo ============================================================
pause

