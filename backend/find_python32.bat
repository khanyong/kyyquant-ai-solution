@echo off
chcp 65001 > nul
cls
echo =====================================
echo 🔍 32비트 Python 찾기
echo =====================================
echo.

echo 시스템에 설치된 Python 검색 중...
echo.

echo [1] 일반적인 경로 확인:
echo -------------------------------------
if exist "C:\Python38-32\python.exe" (
    echo ✅ C:\Python38-32\python.exe 발견!
    C:\Python38-32\python.exe -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)
if exist "C:\Python39-32\python.exe" (
    echo ✅ C:\Python39-32\python.exe 발견!
    C:\Python39-32\python.exe -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)
if exist "C:\Python310-32\python.exe" (
    echo ✅ C:\Python310-32\python.exe 발견!
    C:\Python310-32\python.exe -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)
if exist "C:\Python311-32\python.exe" (
    echo ✅ C:\Python311-32\python.exe 발견!
    C:\Python311-32\python.exe -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)

echo.
echo [2] 사용자 AppData 경로 확인:
echo -------------------------------------
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38-32\python.exe" (
    echo ✅ %USERPROFILE%\AppData\Local\Programs\Python\Python38-32\python.exe 발견!
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38-32\python.exe" -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39-32\python.exe" (
    echo ✅ %USERPROFILE%\AppData\Local\Programs\Python\Python39-32\python.exe 발견!
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39-32\python.exe" -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310-32\python.exe" (
    echo ✅ %USERPROFILE%\AppData\Local\Programs\Python\Python310-32\python.exe 발견!
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310-32\python.exe" -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)

echo.
echo [3] Program Files 경로 확인:
echo -------------------------------------
if exist "C:\Program Files (x86)\Python38\python.exe" (
    echo ✅ C:\Program Files (x86)\Python38\python.exe 발견!
    "C:\Program Files (x86)\Python38\python.exe" -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)
if exist "C:\Program Files (x86)\Python39\python.exe" (
    echo ✅ C:\Program Files (x86)\Python39\python.exe 발견!
    "C:\Program Files (x86)\Python39\python.exe" -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
)

echo.
echo [4] PATH 환경변수의 Python 확인:
echo -------------------------------------
where python >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=*" %%i in ('where python') do (
        echo 발견: %%i
        "%%i" -c "import struct; print(f'  → {8*struct.calcsize(''P'')} bit Python')"
    )
) else (
    echo PATH에 python이 없습니다.
)

echo.
echo [5] py 런처 확인:
echo -------------------------------------
where py >nul 2>&1
if %errorlevel%==0 (
    echo py 런처 발견!
    py -0
    echo.
    echo 32비트 Python 실행: py -3.x-32
) else (
    echo py 런처가 없습니다.
)

echo.
echo =====================================
echo 위에서 32 bit Python을 찾으셨나요?
echo =====================================
pause