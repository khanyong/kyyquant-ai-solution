@echo off
echo ====================================
echo 키움 OpenAPI+ 연동 환경 설정
echo ====================================
echo.

echo 1. Python 가상환경 생성 및 활성화
python -m venv venv
call venv\Scripts\activate

echo.
echo 2. 필요 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo 3. 환경변수 파일 생성
if not exist .env (
    echo SUPABASE_URL=your_supabase_url> .env
    echo SUPABASE_ANON_KEY=your_supabase_anon_key>> .env
    echo KIWOOM_ACCOUNT_NO=your_account_number>> .env
    echo KIWOOM_PASSWORD=your_password>> .env
    echo KIWOOM_CERT_PASSWORD=your_cert_password>> .env
    echo.
    echo .env 파일이 생성되었습니다. 실제 값으로 수정해주세요.
)

echo.
echo ====================================
echo 설치 완료!
echo ====================================
echo.
echo 다음 단계:
echo 1. 키움증권 OpenAPI+ 설치
echo 2. 키움증권 로그인 및 공인인증서 등록
echo 3. .env 파일에 실제 정보 입력
echo 4. python kiwoom_bridge_server.py 실행
echo.
pause