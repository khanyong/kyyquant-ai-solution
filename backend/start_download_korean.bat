
@echo off
chcp 949 >nul
echo ============================================================
echo Ű�� ��ü ���� �ٿ�ε� (������ ���)
echo ============================================================

REM ������ ���� Ȯ��
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] ������ ���� ���� ��
    goto :run
) else (
    echo [INFO] ������ ���� ��û ��...
    echo.
    powershell -Command "Start-Process \"%~f0\" -Verb RunAs"
    exit
)

:run
echo.
echo �ٿ�ε� ����:
echo - �Ⱓ: 10��ġ �Ϻ� ������
echo - ����: KOSPI, KOSDAQ  
echo - �������: download_progress.json
echo - �簳 ����
echo.
echo ============================================================
echo.

REM Ű�� OpenAPI+ ����
echo [1/3] Ű�� OpenAPI+ ���� ��...
start C:\OpenAPI\opstarter.exe
timeout /t 5 >nul

echo.
echo [2/3] Ű�� OpenAPI+���� �α����ϼ���
echo       �α��� �� Enter�� ��������...
pause

echo.
echo [3/3] �ٿ�ε� ����...
echo.

REM �۾� ���丮 �̵�
cd /d D:\Dev\auto_stock\backend

REM 32��Ʈ Python���� ����
C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe download_all_stocks.py

echo.
echo ============================================================
echo �ٿ�ε� �Ϸ�\!
echo ============================================================
pause

