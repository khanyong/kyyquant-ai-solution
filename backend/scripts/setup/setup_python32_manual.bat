@echo off
chcp 65001 > nul
echo =====================================
echo 32비트 Python 수동 설정
echo =====================================
echo.
echo 32비트 Python이 설치되었지만 자동으로 찾을 수 없습니다.
echo 설치된 Python 경로를 직접 입력해주세요.
echo.
echo 일반적인 설치 경로:
echo - C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310-32
echo - C:\Program Files (x86)\Python310
echo - C:\Python310-32
echo - C:\Python310
echo.
echo Python 설치 경로 확인 방법:
echo 1. 시작 메뉴에서 "Python" 검색
echo 2. Python 아이콘 우클릭 - "파일 위치 열기"
echo 3. 표시된 경로 확인
echo.
set /p PYTHON_PATH="32비트 Python.exe 전체 경로 입력 (예: C:\Python310\python.exe): "

if not exist "%PYTHON_PATH%" (
    echo.
    echo [ERROR] 파일을 찾을 수 없습니다: %PYTHON_PATH%
    echo.
    pause
    exit /b 1
)

echo.
echo Python 버전 확인 중...
"%PYTHON_PATH%" --version
"%PYTHON_PATH%" -c "import platform; print('Architecture:', platform.architecture())"

echo.
echo 이 Python을 사용하시겠습니까? (Y/N)
set /p CONFIRM=선택: 

if /i not "%CONFIRM%"=="Y" (
    echo 취소되었습니다.
    pause
    exit /b 0
)

echo.
echo 가상환경 생성 중...

if exist venv32 (
    echo 기존 venv32 삭제 중...
    rmdir /s /q venv32
)

"%PYTHON_PATH%" -m venv venv32

if errorlevel 1 (
    echo [ERROR] 가상환경 생성 실패!
    echo Python이 제대로 설치되었는지 확인하세요.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] 가상환경 생성 완료!
echo.
echo 환경 활성화 중...
call venv32\Scripts\activate.bat

echo.
echo Python 및 pip 버전:
python --version
pip --version

echo.
echo 필수 패키지 설치를 시작하시겠습니까? (Y/N)
set /p INSTALL=선택: 

if /i "%INSTALL%"=="Y" (
    echo.
    echo pip 업그레이드...
    python -m pip install --upgrade pip
    
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
    echo 설치 확인...
    python -c "import PyQt5; print('[OK] PyQt5 설치됨')"
    python -c "import win32com.client; print('[OK] pywin32 설치됨')"
)

echo.
echo =====================================
echo 설정 완료!
echo =====================================
echo.
echo 키움 API 테스트:
echo python test_kiwoom_mock.py
echo.
echo 가상환경 재활성화:
echo venv32\Scripts\activate
echo.
pause