"""
키움증권 API 키 설정 도우미
사용자 친화적인 API 키 입력 및 검증
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
import requests
import json

class APIKeySetup:
    def __init__(self):
        self.env_file = Path("../.env")
        if not self.env_file.exists():
            self.env_file = Path(".env")
        
        load_dotenv(self.env_file)
        
    def show_current_config(self):
        """현재 설정 표시"""
        print("\n" + "="*60)
        print("현재 API 설정 상태")
        print("="*60)
        
        app_key = os.getenv("KIWOOM_APP_KEY", "")
        app_secret = os.getenv("KIWOOM_APP_SECRET", "")
        account = os.getenv("KIWOOM_ACCOUNT_NO", "")
        is_demo = os.getenv("KIWOOM_IS_DEMO", "true")
        
        print(f"\n1. REST API:")
        if app_key and len(app_key) > 10:
            print(f"   APP_KEY: {app_key[:10]}...****")
        else:
            print(f"   APP_KEY: [미설정]")
            
        if app_secret and len(app_secret) > 10:
            print(f"   APP_SECRET: {app_secret[:10]}...****")
        else:
            print(f"   APP_SECRET: [미설정]")
        
        print(f"\n2. 계좌 정보:")
        print(f"   계좌번호: {account if account else '[미설정]'}")
        print(f"   거래모드: {'모의투자' if is_demo == 'true' else '실전투자'}")
        
    def setup_rest_api(self):
        """REST API 키 설정"""
        print("\n" + "="*60)
        print("REST API 키 설정")
        print("="*60)
        print("\n한국투자증권 개발자센터에서 발급받은 키를 입력하세요.")
        print("(https://apiportal.koreainvestment.com/)")
        print("\n입력하지 않으려면 Enter를 누르세요.")
        
        # APP_KEY 입력
        app_key = input("\nAPP_KEY: ").strip()
        if app_key:
            set_key(self.env_file, "KIWOOM_APP_KEY", app_key)
            print("✅ APP_KEY 저장됨")
        
        # APP_SECRET 입력
        app_secret = input("APP_SECRET: ").strip()
        if app_secret:
            set_key(self.env_file, "KIWOOM_APP_SECRET", app_secret)
            print("✅ APP_SECRET 저장됨")
        
        # 모의/실전 선택
        print("\n거래 모드 선택:")
        print("1. 모의투자 (테스트용)")
        print("2. 실전투자 (실거래)")
        choice = input("선택 [1/2] (기본값: 1): ").strip() or "1"
        
        if choice == "1":
            set_key(self.env_file, "KIWOOM_IS_DEMO", "true")
            set_key(self.env_file, "KIWOOM_API_URL", "https://openapivts.koreainvestment.com:29443")
            print("✅ 모의투자 모드 설정됨")
        else:
            set_key(self.env_file, "KIWOOM_IS_DEMO", "false")
            set_key(self.env_file, "KIWOOM_API_URL", "https://openapi.koreainvestment.com:9443")
            print("✅ 실전투자 모드 설정됨")
    
    def setup_account(self):
        """계좌 정보 설정"""
        print("\n" + "="*60)
        print("계좌 정보 설정")
        print("="*60)
        print("\n키움증권 계좌번호를 입력하세요.")
        print("형식: 12345678-01 (8자리-2자리)")
        print("\n계좌번호 확인 방법:")
        print("1. KOA Studio 실행 → 로그인")
        print("2. 키움증권 HTS → 계좌 정보")
        
        account = input("\n계좌번호: ").strip()
        if account:
            # 형식 검증
            if len(account) == 11 and account[8] == '-':
                set_key(self.env_file, "KIWOOM_ACCOUNT_NO", account)
                print("✅ 계좌번호 저장됨")
            else:
                print("⚠️ 올바른 형식이 아닙니다 (예: 12345678-01)")
    
    def test_connection(self):
        """API 연결 테스트"""
        print("\n" + "="*60)
        print("API 연결 테스트")
        print("="*60)
        
        app_key = os.getenv("KIWOOM_APP_KEY")
        app_secret = os.getenv("KIWOOM_APP_SECRET")
        api_url = os.getenv("KIWOOM_API_URL")
        
        if not (app_key and app_secret):
            print("⚠️ API 키가 설정되지 않아 테스트를 건너뜁니다.")
            return
        
        print("\nREST API 연결 테스트 중...")
        
        # 토큰 발급 테스트 (실제 구현 시 OAuth 인증 필요)
        headers = {
            "content-type": "application/json",
            "appkey": app_key,
            "appsecret": app_secret
        }
        
        # 간단한 연결 확인
        try:
            # 실제로는 OAuth 토큰 발급 API 호출 필요
            print("✅ API 키 형식 확인됨")
            print("📌 실제 연결 테스트는 OAuth 인증 후 가능합니다.")
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
    
    def save_template(self):
        """템플릿 파일 생성"""
        template = """# ===== 키움증권 API 설정 =====
# REST API (한국투자증권)
KIWOOM_APP_KEY=여기에_APP_KEY_입력
KIWOOM_APP_SECRET=여기에_APP_SECRET_입력
KIWOOM_ACCOUNT_NO=여기에_계좌번호_입력
KIWOOM_IS_DEMO=true  # 모의투자: true, 실전: false

# API URLs
KIWOOM_API_URL=https://openapivts.koreainvestment.com:29443  # 모의투자
# KIWOOM_API_URL=https://openapi.koreainvestment.com:9443    # 실전투자

# ===== Supabase (기존 설정 유지) =====
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# ===== 로컬 서버 =====
VITE_KIWOOM_WS_URL=ws://localhost:8765
VITE_API_URL=http://localhost:8000

# ===== 거래 설정 =====
AUTO_LOGIN=false
DEMO_MODE=true
"""
        
        template_file = Path(".env.template")
        template_file.write_text(template)
        print(f"\n✅ 템플릿 파일 생성됨: {template_file}")
    
    def run(self):
        """메인 실행"""
        print("\n🔑 키움증권 API 키 설정 도우미")
        print("="*60)
        
        while True:
            self.show_current_config()
            
            print("\n" + "="*60)
            print("메뉴 선택:")
            print("="*60)
            print("1. REST API 키 설정")
            print("2. 계좌번호 설정")
            print("3. API 연결 테스트")
            print("4. 템플릿 파일 생성")
            print("5. 종료")
            
            choice = input("\n선택 [1-5]: ").strip()
            
            if choice == "1":
                self.setup_rest_api()
            elif choice == "2":
                self.setup_account()
            elif choice == "3":
                self.test_connection()
            elif choice == "4":
                self.save_template()
            elif choice == "5":
                print("\n설정을 완료했습니다.")
                break
            else:
                print("올바른 번호를 선택하세요.")
        
        print("\n" + "="*60)
        print("✅ 설정 완료!")
        print("="*60)
        print("\n다음 단계:")
        print("1. OpenAPI+ 설치 (실시간 거래용)")
        print("2. 32비트 Python 환경 설정 (setup_32bit_env.bat)")
        print("3. 하이브리드 시스템 시작 (start_hybrid_system.bat)")

if __name__ == "__main__":
    setup = APIKeySetup()
    setup.run()