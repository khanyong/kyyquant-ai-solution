@echo off
echo ========================================
echo OpenAPI OCX Manual Registration
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator privileges required!
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Administrator privileges confirmed
echo.

cd /d C:\OpenAPI

echo Registering OCX files...
echo.

echo 1. Registering khopenapi.ocx...
regsvr32 /s khopenapi.ocx
if %errorLevel% == 0 (
    echo    [OK] khopenapi.ocx registered successfully
) else (
    echo    [ERROR] Failed to register khopenapi.ocx
)

echo.
echo 2. Checking for khoapicomm.ocx...
if exist "khoapicomm.ocx" (
    echo    Found khoapicomm.ocx, registering...
    regsvr32 /s khoapicomm.ocx
    if %errorLevel% == 0 (
        echo    [OK] khoapicomm.ocx registered successfully
    ) else (
        echo    [ERROR] Failed to register khoapicomm.ocx
    )
) else (
    echo    [WARNING] khoapicomm.ocx not found
    echo    This file is required for OpenAPI+ to work properly
)

echo.
echo 3. Verifying registration...
reg query "HKEY_CLASSES_ROOT\CLSID\{A1574A0D-6BFA-4A6F-8947-6E8F0962C86F}" >nul 2>&1
if %errorLevel% == 0 (
    echo    [OK] OCX registration verified in registry
) else (
    echo    [ERROR] OCX registration failed
)

echo.
echo ========================================
echo Registration attempt complete.
echo.
echo Next steps:
echo 1. If errors occurred, download and reinstall OpenAPI+
echo 2. If successful, proceed with KOA Studio installation
echo ========================================
echo.
pause