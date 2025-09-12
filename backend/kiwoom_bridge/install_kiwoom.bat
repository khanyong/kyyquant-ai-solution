@echo off
REM 키움 Open API+ 설치 및 환경 설정 스크립트
REM Windows에서 관리자 권한으로 실행 필요

echo ============================================
echo 키움 Open API+ 설치 스크립트
echo ============================================
echo.

REM Python 버전 확인
echo Python 버전 확인...
python --version
if %errorlevel% neq 0 (
    echo Python이 설치되지 않았습니다!
    echo https://www.python.org 에서 Python 3.9 이상 설치 필요
    pause
    exit /b 1
)

echo.
echo ============================================
echo 1단계: 키움 Open API+ 다운로드
echo ============================================
echo.
echo 키움증권 홈페이지에서 Open API+ 설치 파일 다운로드 필요
echo https://www.kiwoom.com/nkw.templateFrameSet.do?m=m1408000000
echo.
echo 다운로드 후 설치를 완료하셨다면 Enter를 누르세요...
pause

echo.
echo ============================================
echo 2단계: Python 가상환경 생성
echo ============================================
echo.

REM 가상환경 생성
if not exist "venv" (
    echo 가상환경 생성 중...
    python -m venv venv
) else (
    echo 가상환경이 이미 존재합니다.
)

REM 가상환경 활성화
echo 가상환경 활성화...
call venv\Scripts\activate.bat

echo.
echo ============================================
echo 3단계: 필요 패키지 설치
echo ============================================
echo.

REM pip 업그레이드
echo pip 업그레이드...
python -m pip install --upgrade pip

REM 필요 패키지 설치
echo 패키지 설치 중...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo 패키지 설치 실패!
    pause
    exit /b 1
)

echo.
echo ============================================
echo 4단계: 키움 API 연결 테스트
echo ============================================
echo.

REM 테스트 스크립트 생성
echo import sys > test_kiwoom.py
echo from PyQt5.QAxContainer import QAxWidget >> test_kiwoom.py
echo from PyQt5.QtWidgets import QApplication >> test_kiwoom.py
echo. >> test_kiwoom.py
echo app = QApplication(sys.argv) >> test_kiwoom.py
echo try: >> test_kiwoom.py
echo     kiwoom = QAxWidget() >> test_kiwoom.py
echo     kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1") >> test_kiwoom.py
echo     print("키움 Open API+ 로드 성공!") >> test_kiwoom.py
echo except Exception as e: >> test_kiwoom.py
echo     print(f"키움 Open API+ 로드 실패: {e}") >> test_kiwoom.py
echo     print("키움 Open API+가 설치되었는지 확인하세요.") >> test_kiwoom.py

REM 테스트 실행
python test_kiwoom.py

REM 테스트 파일 삭제
del test_kiwoom.py

echo.
echo ============================================
echo 5단계: Windows 서비스 등록 (선택사항)
echo ============================================
echo.
echo Windows 서비스로 등록하려면 Y를 입력하세요 (N으로 건너뛰기): 
set /p register_service=

if /i "%register_service%"=="Y" (
    echo.
    echo Windows 서비스 등록 중...
    
    REM 서비스 등록 스크립트 생성
    echo @echo off > run_service.bat
    echo cd /d "%~dp0" >> run_service.bat
    echo call venv\Scripts\activate.bat >> run_service.bat
    echo python kiwoom_wrapper.py --mode paper >> run_service.bat
    
    echo 서비스 실행 스크립트 생성 완료: run_service.bat
    echo.
    echo Windows 작업 스케줄러에서 다음 설정으로 작업 생성:
    echo - 트리거: 시스템 시작 시
    echo - 동작: run_service.bat 실행
    echo - 계정: 현재 사용자
    echo - 최고 권한으로 실행 체크
)

echo.
echo ============================================
echo 설치 완료!
echo ============================================
echo.
echo 다음 명령으로 키움 API 브릿지 실행:
echo   venv\Scripts\activate.bat
echo   python kiwoom_wrapper.py --mode paper
echo.
echo 모의투자 모드로 시작됩니다.
echo 실전투자는 --mode real 옵션을 사용하세요.
echo.
pause