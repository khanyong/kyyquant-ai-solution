@echo off
echo ========================================
echo Fix OCX Registration for KOA Studio
echo ========================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator rights required!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

cd /d C:\OpenAPI

echo [1] Testing with available components...
echo.

:: Register khopenapi.ocx with full path
echo Registering khopenapi.ocx with full path...
regsvr32 "C:\OpenAPI\khopenapi.ocx"
echo.

:: Register communication DLLs as alternative
echo Registering communication DLLs...
regsvr32 /s "C:\OpenAPI\opcommapi.dll" 2>nul
regsvr32 /s "C:\OpenAPI\opcomms.dll" 2>nul
echo.

echo [2] Setting compatibility mode for KOAStudioSA.exe...
echo.
echo Please manually:
echo 1. Right-click C:\OpenAPI\KOAStudioSA.exe
echo 2. Select Properties
echo 3. Go to Compatibility tab
echo 4. Check "Run this program in compatibility mode for: Windows 7"
echo 5. Check "Run this program as an administrator"
echo 6. Click OK
echo.

echo [3] Adding firewall exceptions...
netsh advfirewall firewall add rule name="KOA Studio" dir=in action=allow program="C:\OpenAPI\KOAStudioSA.exe" enable=yes >nul 2>&1
netsh advfirewall firewall add rule name="OpenAPI Starter" dir=in action=allow program="C:\OpenAPI\opstarter.exe" enable=yes >nul 2>&1
echo Firewall rules added.
echo.

echo [4] Now try running KOA Studio:
echo.
echo Start KOAStudioSA.exe and test login.
echo.
echo If login still fails, the issue is likely:
echo - Missing khoapicomm.ocx (communication module)
echo - You need to reinstall OpenAPI+ completely
echo.
pause