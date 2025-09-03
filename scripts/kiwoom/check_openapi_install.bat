@echo off
chcp 437 >nul
echo ========================================
echo OpenAPI+ Installation Status Check
echo ========================================
echo.

echo [1] OpenAPI folder check...
if exist "C:\OpenAPI" (
    echo    OK: C:\OpenAPI folder exists
    dir C:\OpenAPI\*.ocx 2>nul | findstr /C:".ocx"
) else (
    echo    ERROR: C:\OpenAPI folder not found - OpenAPI+ installation required
)
echo.

echo [2] Registry check (64-bit)...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\KHOpenAPI" >nul 2>&1
if %errorlevel%==0 (
    echo    OK: 64-bit registry registered
) else (
    echo    ERROR: 64-bit registry not found
)

echo [3] Registry check (32-bit)...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\KHOpenAPI" >nul 2>&1
if %errorlevel%==0 (
    echo    OK: 32-bit registry registered
) else (
    echo    ERROR: 32-bit registry not found
)
echo.

echo [4] OCX registration status...
reg query "HKEY_CLASSES_ROOT\CLSID\{A1574A0D-6BFA-4A6F-8947-6E8F0962C86F}" >nul 2>&1
if %errorlevel%==0 (
    echo    OK: khopenapi.ocx registered
) else (
    echo    ERROR: khopenapi.ocx not registered
    if exist "C:\OpenAPI\khopenapi.ocx" (
        echo    - OCX file exists but needs registration
        echo    - Run as admin: regsvr32 C:\OpenAPI\khopenapi.ocx
    )
)
echo.

echo [5] Required files check...
set files_ok=1
if exist "C:\OpenAPI\khopenapi.ocx" (
    echo    OK: khopenapi.ocx exists
) else (
    echo    ERROR: khopenapi.ocx not found
    set files_ok=0
)

if exist "C:\OpenAPI\khoapicomm.ocx" (
    echo    OK: khoapicomm.ocx exists
) else (
    echo    ERROR: khoapicomm.ocx not found
    set files_ok=0
)

if exist "C:\OpenAPI\bin\khoapicomm.exe" (
    echo    OK: khoapicomm.exe exists
) else (
    echo    ERROR: khoapicomm.exe not found
    set files_ok=0
)
echo.

echo ========================================
if %files_ok%==0 (
    echo Result: OpenAPI+ installation required
    echo.
    echo Solution:
    echo 1. Download OpenAPI+ from Kiwoom website
    echo 2. Right-click installer - Run as administrator
    echo 3. Keep installation path as C:\OpenAPI
) else (
    echo Result: OpenAPI+ installation confirmed
    echo.
    echo Ready to install KOA Studio.
)
echo ========================================
echo.
pause