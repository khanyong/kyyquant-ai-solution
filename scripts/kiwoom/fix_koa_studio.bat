@echo off
echo ========================================
echo KOA Studio 설치 문제 해결 스크립트
echo ========================================
echo.
echo 관리자 권한으로 실행되었는지 확인 중...

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo [오류] 관리자 권한이 필요합니다!
    echo 이 파일을 우클릭하고 "관리자 권한으로 실행"을 선택하세요.
    echo.
    pause
    exit /b 1
)

echo [OK] 관리자 권한 확인됨
echo.

echo 1. OpenAPI 설치 경로 확인 중...
if exist "C:\OpenAPI" (
    echo [OK] OpenAPI 폴더 발견: C:\OpenAPI
) else (
    echo [오류] C:\OpenAPI 폴더가 없습니다.
    echo OpenAPI+를 먼저 설치하세요.
    pause
    exit /b 1
)

echo.
echo 2. KOA Studio 파일 확인 중...
if exist "C:\OpenAPI\KOAStudioSA.exe" (
    echo [OK] KOAStudioSA.exe 발견
) else (
    echo [경고] KOAStudioSA.exe가 없습니다.
    echo KOA Studio 실행파일을 C:\OpenAPI\ 폴더에 복사하세요.
)

if exist "C:\OpenAPI\KOALoader.dll" (
    echo [OK] KOALoader.dll 발견
) else (
    echo [경고] KOALoader.dll이 없습니다.
    echo KOALoader.dll을 C:\OpenAPI\ 폴더에 복사하세요.
)

echo.
echo 3. OCX 파일 재등록 중...
cd /d C:\OpenAPI

echo - khopenapi.ocx 등록 해제 중...
regsvr32 /s /u khopenapi.ocx 2>nul
echo - khopenapi.ocx 재등록 중...
regsvr32 /s khopenapi.ocx
if %errorLevel% == 0 (
    echo [OK] khopenapi.ocx 등록 성공
) else (
    echo [오류] khopenapi.ocx 등록 실패
)

echo - khoapicomm.ocx 등록 해제 중...
regsvr32 /s /u khoapicomm.ocx 2>nul
echo - khoapicomm.ocx 재등록 중...
regsvr32 /s khoapicomm.ocx
if %errorLevel% == 0 (
    echo [OK] khoapicomm.ocx 등록 성공
) else (
    echo [오류] khoapicomm.ocx 등록 실패
)

echo.
echo 4. 방화벽 예외 추가 중...
netsh advfirewall firewall delete rule name="KOA Studio" >nul 2>&1
netsh advfirewall firewall add rule name="KOA Studio" dir=in action=allow program="C:\OpenAPI\KOAStudioSA.exe" enable=yes >nul 2>&1
echo [OK] KOA Studio 방화벽 예외 추가됨

netsh advfirewall firewall delete rule name="OpenAPI" >nul 2>&1
netsh advfirewall firewall add rule name="OpenAPI" dir=in action=allow program="C:\OpenAPI\bin\khoapicomm.exe" enable=yes >nul 2>&1
echo [OK] OpenAPI 방화벽 예외 추가됨

echo.
echo 5. 레지스트리 확인 중...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\KHOpenAPI" >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] OpenAPI 레지스트리 키 존재
) else (
    echo [경고] OpenAPI 레지스트리 키가 없습니다.
    echo OpenAPI+를 재설치하세요.
)

echo.
echo 6. 버전 관리자 실행 확인...
if exist "C:\OpenAPI\VersionAgent.exe" (
    echo [OK] VersionAgent.exe 발견
    echo.
    echo 버전 업데이트를 확인하시겠습니까? (Y/N)
    set /p update=
    if /i "%update%"=="Y" (
        echo 버전 관리자를 실행합니다...
        start "" "C:\OpenAPI\VersionAgent.exe"
        echo 업데이트 완료 후 Enter를 누르세요...
        pause >nul
    )
) else (
    echo [경고] VersionAgent.exe가 없습니다.
)

echo.
echo ========================================
echo 설정 완료!
echo.
echo 다음 단계:
echo 1. KOA Studio를 관리자 권한으로 실행하세요
echo 2. 파일 - 로그인 메뉴에서 로그인하세요
echo 3. 모의투자/실계좌 구분을 정확히 선택하세요
echo 4. 계좌 조회를 테스트하세요
echo.
echo 문제가 지속되면:
echo - 키움증권 홈페이지에서 OpenAPI 사용 신청 확인
echo - 모의투자 신청 여부 확인
echo - Internet Explorer 보안 설정 확인
echo ========================================
echo.
pause