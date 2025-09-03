@echo off
chcp 65001 > nul
echo =====================================
echo 32비트 환경 패키지 설치 및 테스트
echo =====================================
echo.

cd /d D:\Dev\auto_stock\backend

REM 가상환경 활성화
echo [1] 가상환경 활성화...
call venv32\Scripts\activate.bat

REM Python 버전 확인
echo.
echo [2] Python 버전 확인...
python --version
python -c "import platform; print('Architecture:', platform.architecture()[0])"

REM pip 업그레이드
echo.
echo [3] pip 업그레이드...
python -m pip install --upgrade pip

REM PyQt5 설치
echo.
echo [4] PyQt5 설치 중... (시간이 걸릴 수 있습니다)
pip install PyQt5==5.15.10

REM pywin32 설치
echo.
echo [5] pywin32 설치 중...
pip install pywin32

REM 기타 패키지 설치
echo.
echo [6] 기타 패키지 설치 중...
pip install python-dotenv requests

REM 설치 확인
echo.
echo [7] 설치 확인...
echo.
python -c "import sys; print('Python:', sys.version)"
python -c "import PyQt5.QtCore; print('[OK] PyQt5 버전:', PyQt5.QtCore.QT_VERSION_STR)"
python -c "import win32com.client; print('[OK] pywin32 설치됨')"
python -c "from PyQt5.QAxContainer import QAxWidget; print('[OK] QAxContainer 사용 가능')"

REM 키움 API 테스트 실행
echo.
echo =====================================
echo 패키지 설치 완료!
echo =====================================
echo.
echo 키움 API 테스트를 실행하시겠습니까? (Y/N)
set /p RUN_TEST=선택: 

if /i "%RUN_TEST%"=="Y" (
    echo.
    echo 키움 API 테스트 실행 중...
    echo.
    python test_kiwoom_mock.py
)

echo.
echo 완료되었습니다!
echo.
echo 다음에 테스트하려면:
echo 1. venv32\Scripts\activate
echo 2. python test_kiwoom_mock.py
echo.
pause