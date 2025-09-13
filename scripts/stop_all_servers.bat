@echo off
chcp 65001 > nul
echo =====================================
echo 모든 서버 종료
echo =====================================
echo.

echo [1] Node.js 프로세스 종료 중...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Node.js 프로세스 종료됨
) else (
    echo - Node.js 프로세스가 실행중이지 않음
)

echo.
echo [2] Python 프로세스 종료 중...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Python 프로세스 종료됨
) else (
    echo - Python 프로세스가 실행중이지 않음
)

echo.
echo [3] Uvicorn 프로세스 종료 중...
taskkill /F /IM uvicorn.exe 2>nul
if %errorlevel% equ 0 (
    echo ✓ Uvicorn 프로세스 종료됨
) else (
    echo - Uvicorn 프로세스가 실행중이지 않음
)

echo.
echo =====================================
echo 모든 서버가 종료되었습니다.
echo =====================================
echo.
pause