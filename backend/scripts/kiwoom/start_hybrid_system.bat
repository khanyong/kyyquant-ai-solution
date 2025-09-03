@echo off
echo ========================================
echo Ű�� ���̺긮�� �ý��� ����
echo ========================================
echo.

REM 1. OpenAPI �긮�� ���� ���� (32��Ʈ)
echo [1] OpenAPI �긮�� ���� ���� ��...
start "OpenAPI Bridge" cmd /k "cd /d %~dp0 && venv32\Scripts\activate && python kiwoom_openapi_bridge.py"

timeout /t 3 /nobreak > nul

REM 2. ���� API ���� ���� (64��Ʈ)
echo [2] ���� API ���� ���� ��...
start "Main API Server" cmd /k "cd /d %~dp0 && python main_api_server.py"

timeout /t 3 /nobreak > nul

REM 3. ���� Ȯ��
echo [3] �ý��� ���� Ȯ�� ��...
curl -s http://localhost:8100/ > nul
if %errorlevel% equ 0 (
    echo [+] OpenAPI �긮�� ����: ����
) else (
    echo [!] OpenAPI �긮�� ����: ����
)

curl -s http://localhost:8000/ > nul
if %errorlevel% equ 0 (
    echo [+] ���� API ����: ����
) else (
    echo [!] ���� API ����: ����
)

echo.
echo ========================================
echo ���̺긮�� �ý��� ���� �Ϸ�!
echo.
echo ���� URL:
echo - OpenAPI Bridge: http://localhost:8100
echo - Main API: http://localhost:8000
echo - Web UI: http://localhost:3000
echo ========================================
pause
