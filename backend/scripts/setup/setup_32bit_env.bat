@echo off
echo ========================================
echo 키움 OpenAPI용 32비트 Python 환경 설정
echo ========================================
echo.

REM 32비트 Python 설치 확인
echo [1] 32비트 Python 설치 확인 중...
where py -3.10-32 >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [!] 32비트 Python이 설치되지 않았습니다.
    echo.
    echo 다음 단계를 따라주세요:
    echo 1. https://www.python.org/downloads/windows/ 접속
    echo 2. Python 3.10.x Windows installer (32-bit) 다운로드
    echo 3. 설치 시 "Add Python to PATH" 체크
    echo 4. 설치 완료 후 이 스크립트 다시 실행
    echo.
    pause
    exit /b 1
)

echo [+] 32비트 Python 발견!
echo.

REM 가상환경 생성
echo [2] 32비트 가상환경 생성 중...
if exist venv32 (
    echo [!] 기존 venv32 폴더 삭제 중...
    rmdir /s /q venv32
)

py -3.10-32 -m venv venv32
if %errorlevel% neq 0 (
    echo [!] 가상환경 생성 실패
    pause
    exit /b 1
)
echo [+] 가상환경 생성 완료: venv32
echo.

REM 가상환경 활성화
echo [3] 가상환경 활성화 중...
call venv32\Scripts\activate.bat

REM pip 업그레이드
echo [4] pip 업그레이드 중...
python -m pip install --upgrade pip --quiet

REM 필수 패키지 설치
echo [5] 필수 패키지 설치 중...
echo    - PyQt5 설치 중...
pip install PyQt5==5.15.10 --quiet
echo    - pywin32 설치 중...
pip install pywin32 --quiet
echo    - pykiwoom 설치 중...
pip install pykiwoom --quiet
echo    - FastAPI 관련 패키지 설치 중...
pip install fastapi uvicorn python-multipart websockets --quiet
echo    - 기타 패키지 설치 중...
pip install python-dotenv supabase pandas numpy --quiet

echo.
echo [6] 설치 확인 중...
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import platform; print(f'Architecture: {platform.architecture()[0]}')"
python -c "import PyQt5; print(f'PyQt5: {PyQt5.QtCore.QT_VERSION_STR}')"
python -c "import pykiwoom; print('pykiwoom: OK')"

echo.
echo ========================================
echo 설정 완료!
echo.
echo 사용 방법:
echo 1. venv32\Scripts\activate.bat 실행하여 환경 활성화
echo 2. python test_kiwoom_simple.py 실행하여 연결 테스트
echo ========================================
echo.
pause