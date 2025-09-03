@echo off
echo ========================================
echo OpenAPI Final Fix Solution
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator privileges required!
    echo Right-click and "Run as administrator"
    pause
    exit /b 1
)

echo [1] Enabling UAC (Required for OCX registration)...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 1 /f >nul
echo [OK] UAC enabled - RESTART REQUIRED LATER
echo.

echo [2] Downloading missing khoapicomm.ocx...
cd /d C:\OpenAPI
echo Please download the full OpenAPI+ installer from:
echo https://download.kiwoom.com/web/openapi/OpenAPISetup.exe
echo.
echo After downloading, extract or install to get khoapicomm.ocx
echo.
pause

echo [3] Registering OCX files with 32-bit regsvr32...
cd /d C:\OpenAPI
C:\Windows\SysWOW64\regsvr32.exe /s khopenapi.ocx
if %errorLevel% == 0 (
    echo [OK] khopenapi.ocx registered (32-bit)
) else (
    echo [ERROR] Failed to register khopenapi.ocx
)

if exist khoapicomm.ocx (
    C:\Windows\SysWOW64\regsvr32.exe /s khoapicomm.ocx
    if %errorLevel% == 0 (
        echo [OK] khoapicomm.ocx registered (32-bit)
    ) else (
        echo [ERROR] Failed to register khoapicomm.ocx
    )
) else (
    echo [WARNING] khoapicomm.ocx not found
)
echo.

echo [4] Creating registry entries manually...
reg add "HKLM\SOFTWARE\WOW6432Node\KHOpenAPI" /f >nul
reg add "HKLM\SOFTWARE\WOW6432Node\KHOpenAPI\Config" /v InstallPath /t REG_SZ /d "C:\OpenAPI" /f >nul
reg add "HKLM\SOFTWARE\WOW6432Node\KHOpenAPI\Config" /v Version /t REG_SZ /d "1.0.0.0" /f >nul
echo [OK] Registry entries created
echo.

echo [5] Copying OCX to System32 folders...
copy khopenapi.ocx C:\Windows\SysWOW64\ /Y >nul 2>&1
if exist khoapicomm.ocx (
    copy khoapicomm.ocx C:\Windows\SysWOW64\ /Y >nul 2>&1
)
echo [OK] OCX files copied to system folders
echo.

echo ========================================
echo IMPORTANT: You must RESTART your computer now!
echo After restart:
echo 1. Run check_openapi_install.bat
echo 2. Install KOA Studio
echo ========================================
echo.
echo Press any key to restart now, or close this window to restart later...
pause >nul
shutdown /r /t 0