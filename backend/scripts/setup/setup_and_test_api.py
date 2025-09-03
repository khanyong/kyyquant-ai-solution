"""
키움증권 API 키 설정 및 테스트 도우미
모의투자/실전투자 키 설정 및 검증
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key
from datetime import datetime

class KiwoomAPISetupAndTest:
    def __init__(self):
        self.env_file = Path("../.env")
        if not self.env_file.exists():
            self.env_file = Path(".env")
        load_dotenv(self.env_file)
        
    def show_menu(self):
        """메인 메뉴"""
        print("\n" + "="*60)
        print("키움증권 API 설정 및 테스트")
        print("="*60)
        print("\n현재 설정 모드: ", end="")
        is_demo = os.getenv("KIWOOM_IS_DEMO", "true").lower() == "true"
        print("모의투자" if is_demo else "실전투자")
        
        print("\n메뉴:")
        print("1. 모의투자 키 설정")
        print("2. 실전투자 키 설정")
        print("3. 현재 설정 확인")
        print("4. API 연결 테스트")
        print("5. 모의/실전 모드 전환")
        print("6. 종료")
        
        return input("\n선택 [1-6]: ").strip()
    
    def setup_demo_keys(self):
        """모의투자 키 설정"""
        print("\n" + "="*60)
        print("모의투자 API 키 설정")
        print("="*60)
        print("한국투자증권 모의투자 계정의 API 키를 입력하세요.")
        print("(https://apiportal.koreainvestment.com/)")
        
        app_key = input("\n모의투자 APP_KEY: ").strip()
        app_secret = input("모의투자 APP_SECRET: ").strip()
        account = input("모의투자 계좌번호 (예: 50114455-01): ").strip()
        
        if app_key and app_secret:
            # 모의투자 설정
            set_key(self.env_file, "KIWOOM_DEMO_APP_KEY", app_key)
            set_key(self.env_file, "KIWOOM_DEMO_APP_SECRET", app_secret)
            set_key(self.env_file, "KIWOOM_DEMO_ACCOUNT_NO", account)
            
            # 현재 모드를 모의투자로 설정
            set_key(self.env_file, "KIWOOM_IS_DEMO", "true")
            set_key(self.env_file, "KIWOOM_APP_KEY", app_key)
            set_key(self.env_file, "KIWOOM_APP_SECRET", app_secret)
            set_key(self.env_file, "KIWOOM_ACCOUNT_NO", account)
            set_key(self.env_file, "KIWOOM_API_URL", "https://openapivts.koreainvestment.com:29443")
            
            print("\n[OK] 모의투자 키 설정 완료!")
            return True
        return False
    
    def setup_real_keys(self):
        """실전투자 키 설정"""
        print("\n" + "="*60)
        print("실전투자 API 키 설정")
        print("="*60)
        print("⚠️ 주의: 실전투자는 실제 거래가 발생합니다!")
        print("한국투자증권 실전 계정의 API 키를 입력하세요.")
        
        confirm = input("\n실전투자 키를 설정하시겠습니까? (yes/no): ").lower()
        if confirm != "yes":
            print("취소되었습니다.")
            return False
        
        app_key = input("\n실전투자 APP_KEY: ").strip()
        app_secret = input("실전투자 APP_SECRET: ").strip()
        account = input("실전투자 계좌번호 (예: 12345678-01): ").strip()
        
        if app_key and app_secret:
            # 실전투자 설정
            set_key(self.env_file, "KIWOOM_REAL_APP_KEY", app_key)
            set_key(self.env_file, "KIWOOM_REAL_APP_SECRET", app_secret)
            set_key(self.env_file, "KIWOOM_REAL_ACCOUNT_NO", account)
            
            # 현재 모드를 실전투자로 설정
            set_key(self.env_file, "KIWOOM_IS_DEMO", "false")
            set_key(self.env_file, "KIWOOM_APP_KEY", app_key)
            set_key(self.env_file, "KIWOOM_APP_SECRET", app_secret)
            set_key(self.env_file, "KIWOOM_ACCOUNT_NO", account)
            set_key(self.env_file, "KIWOOM_API_URL", "https://openapi.koreainvestment.com:9443")
            
            print("\n[OK] 실전투자 키 설정 완료!")
            return True
        return False
    
    def switch_mode(self):
        """모의/실전 모드 전환"""
        print("\n" + "="*60)
        print("거래 모드 전환")
        print("="*60)
        
        is_demo = os.getenv("KIWOOM_IS_DEMO", "true").lower() == "true"
        print(f"현재 모드: {'모의투자' if is_demo else '실전투자'}")
        
        print("\n전환할 모드:")
        print("1. 모의투자")
        print("2. 실전투자")
        choice = input("선택 [1/2]: ").strip()
        
        if choice == "1":
            # 모의투자로 전환
            demo_key = os.getenv("KIWOOM_DEMO_APP_KEY")
            demo_secret = os.getenv("KIWOOM_DEMO_APP_SECRET")
            demo_account = os.getenv("KIWOOM_DEMO_ACCOUNT_NO")
            
            if demo_key and demo_secret:
                set_key(self.env_file, "KIWOOM_IS_DEMO", "true")
                set_key(self.env_file, "KIWOOM_APP_KEY", demo_key)
                set_key(self.env_file, "KIWOOM_APP_SECRET", demo_secret)
                set_key(self.env_file, "KIWOOM_ACCOUNT_NO", demo_account or "")
                set_key(self.env_file, "KIWOOM_API_URL", "https://openapivts.koreainvestment.com:29443")
                print("[OK] 모의투자 모드로 전환되었습니다.")
            else:
                print("[FAIL] 모의투자 키가 설정되지 않았습니다. 먼저 설정하세요.")
                
        elif choice == "2":
            # 실전투자로 전환
            real_key = os.getenv("KIWOOM_REAL_APP_KEY")
            real_secret = os.getenv("KIWOOM_REAL_APP_SECRET")
            real_account = os.getenv("KIWOOM_REAL_ACCOUNT_NO")
            
            if real_key and real_secret:
                print("\n⚠️ 경고: 실전투자 모드로 전환하면 실제 거래가 발생합니다!")
                confirm = input("정말 전환하시겠습니까? (yes/no): ").lower()
                if confirm == "yes":
                    set_key(self.env_file, "KIWOOM_IS_DEMO", "false")
                    set_key(self.env_file, "KIWOOM_APP_KEY", real_key)
                    set_key(self.env_file, "KIWOOM_APP_SECRET", real_secret)
                    set_key(self.env_file, "KIWOOM_ACCOUNT_NO", real_account or "")
                    set_key(self.env_file, "KIWOOM_API_URL", "https://openapi.koreainvestment.com:9443")
                    print("[OK] 실전투자 모드로 전환되었습니다.")
            else:
                print("[FAIL] 실전투자 키가 설정되지 않았습니다. 먼저 설정하세요.")
    
    def show_current_config(self):
        """현재 설정 표시"""
        print("\n" + "="*60)
        print("현재 API 설정")
        print("="*60)
        
        # 현재 모드
        is_demo = os.getenv("KIWOOM_IS_DEMO", "true").lower() == "true"
        print(f"\n현재 모드: {'모의투자' if is_demo else '실전투자'}")
        
        # 모의투자 키
        print("\n[모의투자 설정]")
        demo_key = os.getenv("KIWOOM_DEMO_APP_KEY", "")
        demo_secret = os.getenv("KIWOOM_DEMO_APP_SECRET", "")
        demo_account = os.getenv("KIWOOM_DEMO_ACCOUNT_NO", "")
        
        if demo_key:
            print(f"  APP_KEY: {demo_key[:10]}...****")
            print(f"  APP_SECRET: {demo_secret[:10]}...****" if demo_secret else "  APP_SECRET: [미설정]")
            print(f"  계좌번호: {demo_account}")
        else:
            print("  [미설정]")
        
        # 실전투자 키
        print("\n[실전투자 설정]")
        real_key = os.getenv("KIWOOM_REAL_APP_KEY", "")
        real_secret = os.getenv("KIWOOM_REAL_APP_SECRET", "")
        real_account = os.getenv("KIWOOM_REAL_ACCOUNT_NO", "")
        
        if real_key:
            print(f"  APP_KEY: {real_key[:10]}...****")
            print(f"  APP_SECRET: {real_secret[:10]}...****" if real_secret else "  APP_SECRET: [미설정]")
            print(f"  계좌번호: {real_account}")
        else:
            print("  [미설정]")
        
        # 현재 활성 설정
        print("\n[현재 활성 설정]")
        current_key = os.getenv("KIWOOM_APP_KEY", "")
        current_url = os.getenv("KIWOOM_API_URL", "")
        print(f"  APP_KEY: {current_key[:10]}...****" if current_key else "  APP_KEY: [미설정]")
        print(f"  API URL: {current_url}")
    
    def test_api_connection(self):
        """API 연결 테스트"""
        print("\n" + "="*60)
        print("API 연결 테스트")
        print("="*60)
        
        # 환경변수 다시 로드
        load_dotenv(self.env_file)
        
        app_key = os.getenv("KIWOOM_APP_KEY")
        app_secret = os.getenv("KIWOOM_APP_SECRET")
        api_url = os.getenv("KIWOOM_API_URL")
        is_demo = os.getenv("KIWOOM_IS_DEMO", "true").lower() == "true"
        
        print(f"\n테스트 모드: {'모의투자' if is_demo else '실전투자'}")
        print(f"API URL: {api_url}")
        
        if not (app_key and app_secret):
            print("[FAIL] API 키가 설정되지 않았습니다.")
            return
        
        # 토큰 발급 테스트
        print("\n토큰 발급 테스트 중...")
        
        headers = {
            "content-type": "application/json; charset=utf-8"
        }
        
        data = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "appsecret": app_secret
        }
        
        try:
            url = f"{api_url}/oauth2/tokenP"
            response = requests.post(url, data=json.dumps(data), headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 0)
                
                print(f"[OK] 토큰 발급 성공!")
                print(f"   - 토큰 길이: {len(token)}자")
                print(f"   - 유효 기간: {expires_in}초")
                
                # 간단한 API 호출 테스트 (휴장일 조회)
                self.test_api_call(token, app_key, app_secret, api_url)
                
            else:
                print(f"[FAIL] 토큰 발급 실패")
                print(f"   - 상태 코드: {response.status_code}")
                error_data = response.json()
                print(f"   - 오류: {error_data.get('error_description', response.text)}")
                
        except Exception as e:
            print(f"[ERROR] 연결 오류: {e}")
    
    def test_api_call(self, token, app_key, app_secret, api_url):
        """API 호출 테스트"""
        print("\nAPI 호출 테스트 중...")
        
        # 국내휴장일조회 API 테스트
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": app_key,
            "appsecret": app_secret,
            "tr_id": "CTCA0903R",
            "custtype": "P"
        }
        
        params = {
            "BASS_DT": datetime.now().strftime("%Y%m%d"),
            "CTX_AREA_NK": "",
            "CTX_AREA_FK": ""
        }
        
        try:
            url = f"{api_url}/uapi/domestic-stock/v1/quotations/chk-holiday"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                print("[OK] API 호출 성공!")
                data = response.json()
                if data.get("rt_cd") == "0":
                    print("   - 휴장일 조회 API 정상 작동")
            else:
                print(f"[WARNING] API 호출 실패: {response.status_code}")
                
        except Exception as e:
            print(f"[WARNING] API 호출 오류: {e}")
    
    def run(self):
        """메인 실행"""
        print("\n[API KEY SETUP] 키움증권 API 설정 및 테스트")
        print("모의투자와 실전투자 키를 모두 관리합니다.")
        
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.setup_demo_keys()
            elif choice == "2":
                self.setup_real_keys()
            elif choice == "3":
                self.show_current_config()
            elif choice == "4":
                self.test_api_connection()
            elif choice == "5":
                self.switch_mode()
            elif choice == "6":
                print("\n프로그램을 종료합니다.")
                break
            else:
                print("올바른 번호를 선택하세요.")
        
        print("\n" + "="*60)
        print("설정 완료!")
        print("test_api_connection.py를 실행하여 전체 테스트를 진행하세요.")
        print("="*60)

if __name__ == "__main__":
    setup = KiwoomAPISetupAndTest()
    setup.run()