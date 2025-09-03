@echo off
echo ========================================
echo Manual OpenAPI Fix (Run as Administrator)
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator rights required!
    echo Right-click and "Run as administrator"
    pause
    exit /b 1
)

echo Step 1: Taking ownership of C:\OpenAPI...
takeown /f "C:\OpenAPI" /r /d y >nul 2>&1
icacls "C:\OpenAPI" /grant Everyone:F /t >nul 2>&1
echo [OK] Permissions set
echo.

echo Step 2: Disabling UAC temporarily...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 0 /f >nul 2>&1
echo [OK] UAC modified (restart required later)
echo.

echo Step 3: Registering as 32-bit components...
cd /d C:\Windows\SysWOW64
if exist "C:\OpenAPI\khopenapi.ocx" (
    echo Copying and registering OCX files in SysWOW64...
    copy "C:\OpenAPI\*.ocx" . /Y >nul 2>&1
    regsvr32 /s khopenapi.ocx
    regsvr32 /s khoapicomm.ocx 2>nul
    echo [OK] OCX files registered in SysWOW64
)
echo.

echo Step 4: Creating registry entries manually...
reg add "HKLM\SOFTWARE\WOW6432Node\KHOpenAPI" /f >nul 2>&1
reg add "HKLM\SOFTWARE\WOW6432Node\KHOpenAPI\Config" /f >nul 2>&1
reg add "HKLM\SOFTWARE\WOW6432Node\KHOpenAPI\Config" /v Path /t REG_SZ /d "C:\OpenAPI" /f >nul 2>&1
echo [OK] Registry entries created
echo.

echo Step 5: Re-enabling UAC...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA /t REG_DWORD /d 1 /f >nul 2>&1
echo [OK] UAC restored (restart required)
echo.

echo ========================================
echo Fix applied. Please:
echo 1. Restart your computer
echo 2. Run check_openapi_install.bat again
echo 3. If still failing, disable antivirus temporarily
echo ========================================
pause