@echo off
chcp 437 >nul 2>&1
echo ========================================
echo OCX File Check and Fix Script
echo ========================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator rights required!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

cd /d C:\OpenAPI

echo [1] Checking C:\OpenAPI folder:
echo ----------------------------------------
dir *.ocx *.dll *.exe 2>nul

echo.
echo [2] Checking bin folder:
echo ----------------------------------------
if exist "C:\OpenAPI\bin" (
    dir "C:\OpenAPI\bin\*.ocx" "C:\OpenAPI\bin\*.dll" 2>nul
) else (
    echo bin folder not found!
)

echo.
echo [3] Checking System32 for OCX files:
echo ----------------------------------------
dir "C:\Windows\System32\khoa*.ocx" 2>nul
dir "C:\Windows\SysWOW64\khoa*.ocx" 2>nul

echo.
echo [4] Attempting to copy OCX files:
echo ----------------------------------------

:: Copy OCX files from bin folder
if exist "C:\OpenAPI\bin\khoapicomm.ocx" (
    echo Copying khoapicomm.ocx from bin folder...
    copy /Y "C:\OpenAPI\bin\khoapicomm.ocx" "C:\OpenAPI\" >nul
    echo Copy complete!
) else (
    echo [WARNING] bin\khoapicomm.ocx not found!
)

if exist "C:\OpenAPI\bin\khopenapi.ocx" (
    echo Copying khopenapi.ocx from bin folder...
    copy /Y "C:\OpenAPI\bin\khopenapi.ocx" "C:\OpenAPI\" >nul
    echo Copy complete!
) else (
    echo [WARNING] bin\khopenapi.ocx not found!
)

echo.
echo [5] Registering OCX files:
echo ----------------------------------------

:: Unregister first (ignore errors)
echo Unregistering existing OCX files...
regsvr32 /s /u "C:\OpenAPI\khopenapi.ocx" 2>nul
regsvr32 /s /u "C:\OpenAPI\khoapicomm.ocx" 2>nul

:: Register new
if exist "C:\OpenAPI\khopenapi.ocx" (
    echo Registering khopenapi.ocx...
    regsvr32 /s "C:\OpenAPI\khopenapi.ocx"
    if %errorlevel% equ 0 (
        echo [SUCCESS] khopenapi.ocx registered!
    ) else (
        echo [FAILED] khopenapi.ocx registration failed!
    )
) else (
    echo [ERROR] khopenapi.ocx file not found!
)

if exist "C:\OpenAPI\khoapicomm.ocx" (
    echo Registering khoapicomm.ocx...
    regsvr32 /s "C:\OpenAPI\khoapicomm.ocx"
    if %errorlevel% equ 0 (
        echo [SUCCESS] khoapicomm.ocx registered!
    ) else (
        echo [FAILED] khoapicomm.ocx registration failed!
    )
) else (
    echo [ERROR] khoapicomm.ocx file not found!
)

echo.
echo [6] Final check:
echo ----------------------------------------
if exist "C:\OpenAPI\khopenapi.ocx" (
    echo [OK] khopenapi.ocx exists
) else (
    echo [MISSING] khopenapi.ocx not found
)

if exist "C:\OpenAPI\khoapicomm.ocx" (
    echo [OK] khoapicomm.ocx exists
) else (
    echo [MISSING] khoapicomm.ocx not found
)

if exist "C:\OpenAPI\KOAStudioSA.exe" (
    echo [OK] KOAStudioSA.exe exists
) else (
    echo [MISSING] KOAStudioSA.exe not found
)

if exist "C:\OpenAPI\KOALoader.dll" (
    echo [OK] KOALoader.dll exists
) else (
    echo [MISSING] KOALoader.dll not found
)

echo.
echo ========================================
echo Task completed!
echo.
echo Next steps:
echo 1. If any files show MISSING above, reinstall OpenAPI+
echo 2. If all files show OK, you can run KOA Studio
echo ========================================
pause