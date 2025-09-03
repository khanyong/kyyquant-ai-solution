@echo off
chcp 65001 > nul
echo =====================================
echo 서버 상태 확인
echo =====================================
echo.

echo [1] 실행 중인 프로세스 확인...
echo.

REM Node.js 확인
echo Node.js 프로세스:
tasklist /FI "IMAGENAME eq node.exe" 2>nul | find /I "node.exe" >nul
if %errorlevel% equ 0 (
    echo ✓ Node.js 실행 중
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" ^| find /I "node.exe"') do (
        echo   PID: %%a
    )
) else (
    echo ✗ Node.js 실행 안 됨
)

echo.
REM Python 확인
echo Python 프로세스:
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo ✓ Python 실행 중
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" ^| find /I "python.exe"') do (
        echo   PID: %%a
    )
) else (
    echo ✗ Python 실행 안 됨
)

echo.
echo [2] 포트 사용 확인...
echo.

REM 포트 5173 확인 (프론트엔드)
netstat -an | find ":5173" >nul
if %errorlevel% equ 0 (
    echo ✓ 포트 5173 (프론트엔드) 사용 중
) else (
    echo ✗ 포트 5173 (프론트엔드) 사용 안 됨
)

REM 포트 8001 확인 (백엔드)
netstat -an | find ":8001" >nul
if %errorlevel% equ 0 (
    echo ✓ 포트 8001 (백엔드 API) 사용 중
) else (
    echo ✗ 포트 8001 (백엔드 API) 사용 안 됨
)

echo.
echo [3] 서비스 접속 테스트...
echo.

REM 프론트엔드 확인
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5173' -UseBasicParsing -TimeoutSec 2; Write-Host '✓ 프론트엔드 응답 정상' } catch { Write-Host '✗ 프론트엔드 응답 없음' }"

REM 백엔드 확인
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001' -UseBasicParsing -TimeoutSec 2; Write-Host '✓ 백엔드 API 응답 정상' } catch { Write-Host '✗ 백엔드 API 응답 없음' }"

echo.
echo =====================================
echo 상태 확인 완료
echo =====================================
echo.
echo 서버 시작 명령:
echo - 모두 시작: restart_all_servers.bat
echo - 프론트엔드만: start_frontend.bat
echo - 백엔드만: start_backend.bat
echo - 모두 종료: stop_all_servers.bat
echo.
pause