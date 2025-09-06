@echo off
REM 관리자 권한으로 자동 실행
powershell -Command "Start-Process 'D:\Dev\auto_stock\backend\start_download_admin.bat' -Verb RunAs"
exit
echo.
echo 10년치 일봉 데이터를 다운로드합니다.
echo - KOSPI 전체 종목
echo - KOSDAQ 전체 종목
echo - 진행 상태는 download_progress.json에 저장됩니다
echo - 중단 후 재시작 가능합니다
echo.
echo 32비트 Python 경로: 
echo C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32
echo.
pause

REM 32비트 Python으로 실행 (핸들 오류 수정 버전)
echo.
echo [중요] 키움 OpenAPI+ 실행 중...
start C:\OpenAPI\opstarter.exe
timeout /t 5 >nul
echo.
echo 키움 OpenAPI+에서 로그인을 완료하세요!
echo 로그인 완료 후 Enter를 누르세요...
pause
echo.
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_stocks.py

echo.
echo 다운로드 완료!
pause