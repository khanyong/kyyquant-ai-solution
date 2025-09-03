@echo off
echo ========================================
echo Downloading missing khoapicomm.ocx
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

echo Searching for khoapicomm.ocx in system...
echo.

:: Check if file exists in Windows system folders
if exist "C:\Windows\System32\khoapicomm.ocx" (
    echo Found in System32, copying...
    copy /Y "C:\Windows\System32\khoapicomm.ocx" "C:\OpenAPI\" >nul
    goto :register
)

if exist "C:\Windows\SysWOW64\khoapicomm.ocx" (
    echo Found in SysWOW64, copying...
    copy /Y "C:\Windows\SysWOW64\khoapicomm.ocx" "C:\OpenAPI\" >nul
    goto :register
)

:: Search in Program Files
echo Searching in Program Files...
for /r "C:\Program Files" %%i in (khoapicomm.ocx) do (
    if exist "%%i" (
        echo Found: %%i
        copy /Y "%%i" "C:\OpenAPI\" >nul
        goto :register
    )
)

for /r "C:\Program Files (x86)" %%i in (khoapicomm.ocx) do (
    if exist "%%i" (
        echo Found: %%i
        copy /Y "%%i" "C:\OpenAPI\" >nul
        goto :register
    )
)

:: Try to extract from existing files
echo.
echo Checking if khoapicomm.ocx is embedded in other files...

:: Sometimes it's named differently
if exist "C:\OpenAPI\opcommapi.dll" (
    echo Found opcommapi.dll, this might be the communication module
    echo Attempting alternative registration...
    regsvr32 /s "C:\OpenAPI\opcommapi.dll" 2>nul
)

echo.
echo [WARNING] khoapicomm.ocx not found in system!
echo.
echo You need to:
echo 1. Download and reinstall Kiwoom OpenAPI+ from:
echo    https://www.kiwoom.com
echo 2. Or copy khoapicomm.ocx from another PC with OpenAPI installed
echo.
goto :end

:register
echo.
echo Registering khoapicomm.ocx...
regsvr32 /s "C:\OpenAPI\khoapicomm.ocx"
if %errorlevel% equ 0 (
    echo [SUCCESS] khoapicomm.ocx registered!
) else (
    echo [FAILED] Registration failed!
)

:end
echo.
echo Final check:
if exist "C:\OpenAPI\khoapicomm.ocx" (
    echo [OK] khoapicomm.ocx exists in C:\OpenAPI
) else (
    echo [MISSING] khoapicomm.ocx still missing
)

echo.
pause