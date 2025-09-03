@echo off
echo =====================================
echo 32비트 Python 설치 경로 찾기
echo =====================================
echo.

echo [1] 일반적인 Python 설치 경로 확인 중...
echo.

REM 사용자 AppData 경로 확인
if exist "%LOCALAPPDATA%\Programs\Python\Python310-32\python.exe" (
    echo [찾음] %LOCALAPPDATA%\Programs\Python\Python310-32\python.exe
    "%LOCALAPPDATA%\Programs\Python\Python310-32\python.exe" --version
    "%LOCALAPPDATA%\Programs\Python\Python310-32\python.exe" -c "import platform; print('Architecture:', platform.architecture())"
    set PYTHON32=%LOCALAPPDATA%\Programs\Python\Python310-32\python.exe
    goto :FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311-32\python.exe" (
    echo [찾음] %LOCALAPPDATA%\Programs\Python\Python311-32\python.exe
    "%LOCALAPPDATA%\Programs\Python\Python311-32\python.exe" --version
    "%LOCALAPPDATA%\Programs\Python\Python311-32\python.exe" -c "import platform; print('Architecture:', platform.architecture())"
    set PYTHON32=%LOCALAPPDATA%\Programs\Python\Python311-32\python.exe
    goto :FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312-32\python.exe" (
    echo [찾음] %LOCALAPPDATA%\Programs\Python\Python312-32\python.exe
    "%LOCALAPPDATA%\Programs\Python\Python312-32\python.exe" --version
    "%LOCALAPPDATA%\Programs\Python\Python312-32\python.exe" -c "import platform; print('Architecture:', platform.architecture())"
    set PYTHON32=%LOCALAPPDATA%\Programs\Python\Python312-32\python.exe
    goto :FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python39-32\python.exe" (
    echo [찾음] %LOCALAPPDATA%\Programs\Python\Python39-32\python.exe
    "%LOCALAPPDATA%\Programs\Python\Python39-32\python.exe" --version
    "%LOCALAPPDATA%\Programs\Python\Python39-32\python.exe" -c "import platform; print('Architecture:', platform.architecture())"
    set PYTHON32=%LOCALAPPDATA%\Programs\Python\Python39-32\python.exe
    goto :FOUND
)

REM Program Files 경로 확인
if exist "%ProgramFiles(x86)%\Python310\python.exe" (
    echo [찾음] %ProgramFiles(x86)%\Python310\python.exe
    "%ProgramFiles(x86)%\Python310\python.exe" --version
    "%ProgramFiles(x86)%\Python310\python.exe" -c "import platform; print('Architecture:', platform.architecture())"
    set PYTHON32=%ProgramFiles(x86)%\Python310\python.exe
    goto :FOUND
)

if exist "%ProgramFiles(x86)%\Python39\python.exe" (
    echo [찾음] %ProgramFiles(x86)%\Python39\python.exe
    "%ProgramFiles(x86)%\Python39\python.exe" --version
    "%ProgramFiles(x86)%\Python39\python.exe" -c "import platform; print('Architecture:', platform.architecture())"
    set PYTHON32=%ProgramFiles(x86)%\Python39\python.exe
    goto :FOUND
)

REM C:\ 루트 경로 확인
if exist "C:\Python310-32\python.exe" (
    echo [찾음] C:\Python310-32\python.exe
    "C:\Python310-32\python.exe" --version
    "C:\Python310-32\python.exe" -c "import platform; print('Architecture:', platform.architecture())"
    set PYTHON32=C:\Python310-32\python.exe
    goto :FOUND
)

if exist "C:\Python310\python.exe" (
    echo [찾음] C:\Python310\python.exe
    "C:\Python310\python.exe" --version
    "C:\Python310\python.exe" -c "import platform; print('Architecture:', platform.architecture())"
    set PYTHON32=C:\Python310\python.exe
    goto :FOUND
)

echo.
echo [2] where 명령으로 Python 찾기...
where python 2>nul
if %errorlevel% equ 0 (
    echo.
    echo 위에서 찾은 Python 중 32비트 버전 확인:
    for /f "delims=" %%i in ('where python') do (
        echo.
        echo 확인 중: %%i
        "%%i" --version 2>nul
        "%%i" -c "import platform; print(platform.architecture())" 2>nul
    )
)

echo.
echo =====================================
echo 32비트 Python을 찾을 수 없습니다!
echo =====================================
echo.
echo Python 설치 확인 방법:
echo 1. 제어판 - 프로그램 및 기능에서 Python 확인
echo 2. 시작 메뉴에서 Python 검색
echo 3. 파일 탐색기에서 다음 경로 확인:
echo    - C:\Users\%USERNAME%\AppData\Local\Programs\Python\
echo    - C:\Program Files (x86)\Python*
echo    - C:\Python*
echo.
pause
exit /b 1

:FOUND
echo.
echo =====================================
echo 32비트 Python 찾음!
echo =====================================
echo 경로: %PYTHON32%
echo.
echo 이제 가상환경을 생성합니다...
echo.

if exist venv32 (
    echo 기존 venv32 삭제 중...
    rmdir /s /q venv32
)

echo 가상환경 생성 중...
"%PYTHON32%" -m venv venv32

if errorlevel 1 (
    echo [ERROR] 가상환경 생성 실패!
    pause
    exit /b 1
)

echo.
echo [성공] 가상환경 생성 완료!
echo.
echo 다음 명령으로 환경 활성화:
echo venv32\Scripts\activate
echo.
echo 그 다음 패키지 설치:
echo pip install PyQt5==5.15.10 pywin32 python-dotenv
echo.
pause