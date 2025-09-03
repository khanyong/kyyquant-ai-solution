@echo off
echo ========================================
echo OpenAPI+ Deep Diagnosis
echo ========================================
echo.

echo [1] System Information:
echo ------------------------------------
echo OS Version:
ver
echo.
echo System Architecture:
wmic os get osarchitecture
echo.

echo [2] Check Windows Defender / Antivirus:
echo ------------------------------------
powershell -Command "Get-MpPreference | Select-Object ExclusionPath"
echo.

echo [3] .NET Framework Version:
echo ------------------------------------
reg query "HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" /v Release 2>nul
if %errorlevel% neq 0 (
    echo .NET Framework 4.x not found - REQUIRED!
)
echo.

echo [4] Visual C++ Redistributables:
echo ------------------------------------
dir "C:\Windows\System32\msvcp*.dll" | findstr /C:"msvcp"
echo.

echo [5] Internet Explorer Version:
echo ------------------------------------
reg query "HKLM\Software\Microsoft\Internet Explorer" /v Version 2>nul
echo.

echo [6] Check OpenAPI Directory Contents:
echo ------------------------------------
dir C:\OpenAPI /b
echo.

echo [7] Check if running in compatibility mode:
echo ------------------------------------
echo Current directory permissions:
icacls C:\OpenAPI
echo.

echo [8] Check UAC Level:
echo ------------------------------------
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v ConsentPromptBehaviorAdmin
echo.

echo [9] Try manual OCX registration with verbose output:
echo ------------------------------------
cd /d C:\OpenAPI
if exist khopenapi.ocx (
    echo Attempting to register khopenapi.ocx...
    regsvr32 khopenapi.ocx
) else (
    echo khopenapi.ocx not found!
)
echo.

echo [10] Check Event Viewer for errors:
echo ------------------------------------
wevtutil qe Application /c:5 /f:text /q:"*[System[Provider[@Name='VBRuntime' or @Name='Application Error']]]" 2>nul
echo.

pause