@echo off
chcp 65001 > nul
echo =====================================
echo 32비트 환경 패키지 설치
echo =====================================
echo.

cd /d D:\Dev\auto_stock\backend

echo [1] 가상환경 활성화...
call venv32\Scripts\activate.bat

echo.
echo [2] Python 버전 확인...
python --version
python -c "import platform; print('Architecture:', platform.architecture()[0])"

echo.
echo [3] pip 업그레이드...
python -m pip install --upgrade pip

echo.
echo [4] 필수 패키지 설치...
echo.
echo PyQt5 설치 중...
pip install PyQt5==5.15.10

echo.
echo pywin32 설치 중...
pip install pywin32

echo.
echo 기타 패키지 설치 중...
pip install python-dotenv requests

echo.
echo [5] 설치 확인...
python -c "import PyQt5; print('[OK] PyQt5 버전:', PyQt5.QtCore.QT_VERSION_STR)"
python -c "import win32com.client; print('[OK] pywin32 설치됨')"
python -c "from PyQt5.QAxContainer import QAxWidget; print('[OK] QAxContainer 사용 가능')"

echo.
echo =====================================
echo 패키지 설치 완료!
echo =====================================
echo.
echo 키움 API 테스트 실행:
echo python test_kiwoom_mock.py
echo.
pause