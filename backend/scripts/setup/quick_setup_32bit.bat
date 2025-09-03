@echo off
chcp 65001 > nul
echo =====================================
echo 키움 OpenAPI 32비트 환경 빠른 설정
echo =====================================
echo.

REM OpenAPI 설치 확인
echo [1] 키움 OpenAPI 설치 확인...
if exist "C:\OpenAPI\bin\khopenapi.ocx" (
    echo [OK] OpenAPI가 설치되어 있습니다.
) else (
    echo [WARNING] OpenAPI가 기본 경로에 없습니다. 다른 경로에 설치되었을 수 있습니다.
)
echo.

REM 32비트 Python 확인
echo [2] 32비트 Python 확인...
set PYTHON32=
if exist "C:\Python310-32\python.exe" (
    set PYTHON32=C:\Python310-32\python.exe
    echo [OK] 32비트 Python 발견: C:\Python310-32
) else if exist "C:\Python39-32\python.exe" (
    set PYTHON32=C:\Python39-32\python.exe
    echo [OK] 32비트 Python 발견: C:\Python39-32
) else if exist "C:\Python38-32\python.exe" (
    set PYTHON32=C:\Python38-32\python.exe
    echo [OK] 32비트 Python 발견: C:\Python38-32
) else (
    echo [ERROR] 32비트 Python이 설치되지 않았습니다!
    echo.
    echo 다음 링크에서 Python 3.10 (32-bit)를 다운로드하세요:
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11.exe
    echo.
    echo 설치 시 주의사항:
    echo - "Add Python to PATH" 체크
    echo - 설치 경로: C:\Python310-32
    echo.
    pause
    exit /b 1
)
echo.

REM 가상환경 생성
echo [3] 32비트 가상환경 설정...
if exist venv32 (
    echo 기존 venv32 폴더가 있습니다. 삭제하시겠습니까? (Y/N)
    set /p DELETE_VENV=선택: 
    if /i "%DELETE_VENV%"=="Y" (
        echo 기존 환경 삭제 중...
        rmdir /s /q venv32
    ) else (
        echo 기존 환경 유지
        goto :ACTIVATE_ENV
    )
)

echo 가상환경 생성 중...
%PYTHON32% -m venv venv32
if errorlevel 1 (
    echo [ERROR] 가상환경 생성 실패!
    pause
    exit /b 1
)
echo [OK] 가상환경 생성 완료
echo.

:ACTIVATE_ENV
REM 가상환경 활성화 및 패키지 설치
echo [4] 필수 패키지 설치...
call venv32\Scripts\activate.bat

echo Python 버전 확인:
python --version
python -c "import platform; print('Architecture:', platform.architecture()[0])"
echo.

echo pip 업그레이드...
python -m pip install --upgrade pip --quiet

echo PyQt5 설치 중...
pip install PyQt5==5.15.10 --quiet
if errorlevel 1 (
    echo [WARNING] PyQt5 설치 실패. 수동 설치 필요.
)

echo pywin32 설치 중...
pip install pywin32 --quiet
if errorlevel 1 (
    echo [WARNING] pywin32 설치 실패. 수동 설치 필요.
)

echo 기타 패키지 설치 중...
pip install python-dotenv requests --quiet

echo.
echo [5] 설치 확인...
python -c "import PyQt5; print('[OK] PyQt5 설치됨')" 2>nul || echo [FAIL] PyQt5 미설치
python -c "import win32com.client; print('[OK] pywin32 설치됨')" 2>nul || echo [FAIL] pywin32 미설치
python -c "from PyQt5.QAxContainer import QAxWidget; print('[OK] QAxContainer 사용 가능')" 2>nul || echo [FAIL] QAxContainer 오류

echo.
echo =====================================
echo 설정 완료!
echo =====================================
echo.
echo 테스트 실행:
echo python test_kiwoom_mock.py
echo.
echo 가상환경 재활성화:
echo venv32\Scripts\activate
echo.
pause