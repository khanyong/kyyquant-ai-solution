"""
키움증권 API 연결 테스트
REST API와 OpenAPI 연결 상태 확인
"""

import os
import sys
import json
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv
import time

# 환경변수 로드
load_dotenv()

class KiwoomAPITester:
    """키움 API 연결 테스터"""
    
    def __init__(self):
        # REST API 설정
        self.app_key = os.getenv("KIWOOM_APP_KEY")
        self.app_secret = os.getenv("KIWOOM_APP_SECRET")
        self.account_no = os.getenv("KIWOOM_ACCOUNT_NO")
        self.is_demo = os.getenv("KIWOOM_IS_DEMO", "true").lower() == "true"
        
        # API URL 설정 (모의/실전)
        if self.is_demo:
            self.api_url = "https://openapivts.koreainvestment.com:29443"
            print("모드: 모의투자")
        else:
            self.api_url = "https://openapi.koreainvestment.com:9443"
            print("모드: 실전투자")
        
        self.token = None
        self.headers = {
            "content-type": "application/json; charset=utf-8"
        }
    
    def check_config(self):
        """설정 확인"""
        print("\n" + "="*60)
        print("1. API 설정 확인")
        print("="*60)
        
        checks = {
            "APP_KEY": bool(self.app_key),
            "APP_SECRET": bool(self.app_secret),
            "계좌번호": bool(self.account_no),
            "API URL": bool(self.api_url)
        }
        
        all_good = True
        for key, value in checks.items():
            status = "[OK]" if value else "[FAIL]"
            print(f"  {status} {key}: {'설정됨' if value else '미설정'}")
            if not value:
                all_good = False
        
        if not all_good:
            print("\n[WARNING] 필요한 설정이 누락되었습니다.")
            print("backend/setup_api_keys.py를 실행하여 설정하세요.")
            return False
        
        print("\n[OK] 모든 설정이 확인되었습니다.")
        return True
    
    def get_hashkey(self, data):
        """해시키 생성"""
        path = "/uapi/hashkey"
        url = f"{self.api_url}{path}"
        headers = {
            "content-Type": "application/json",
            "appKey": self.app_key,
            "appSecret": self.app_secret,
        }
        
        try:
            res = requests.post(url, headers=headers, data=json.dumps(data))
            if res.status_code == 200:
                return res.json()["HASH"]
            else:
                print(f"해시키 생성 실패: {res.status_code}")
                return None
        except Exception as e:
            print(f"해시키 생성 오류: {e}")
            return None
    
    def get_access_token(self):
        """접근 토큰 발급"""
        print("\n" + "="*60)
        print("2. REST API 토큰 발급 테스트")
        print("="*60)
        
        path = "/oauth2/tokenP"
        url = f"{self.api_url}{path}"
        
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            print(f"  토큰 요청 중... ({self.api_url})")
            res = requests.post(url, data=json.dumps(data), headers=self.headers)
            
            if res.status_code == 200:
                token_data = res.json()
                self.token = token_data.get("access_token")
                token_type = token_data.get("token_type", "Bearer")
                expires_in = token_data.get("expires_in", 0)
                
                print(f"  [OK] 토큰 발급 성공!")
                print(f"     - 토큰 타입: {token_type}")
                print(f"     - 유효 기간: {expires_in}초")
                print(f"     - 토큰 길이: {len(self.token)}자")
                
                # 헤더에 토큰 추가
                self.headers.update({
                    "authorization": f"{token_type} {self.token}",
                    "appkey": self.app_key,
                    "appsecret": self.app_secret,
                })
                
                return True
            else:
                print(f"  [FAIL] 토큰 발급 실패")
                print(f"     - 상태 코드: {res.status_code}")
                print(f"     - 응답: {res.text[:200]}")
                return False
                
        except Exception as e:
            print(f"  [ERROR] 토큰 발급 오류: {e}")
            return False
    
    def test_account_balance(self):
        """계좌 잔고 조회 테스트"""
        print("\n" + "="*60)
        print("3. 계좌 정보 조회 테스트")
        print("="*60)
        
        if not self.token:
            print("  [SKIP] 토큰이 없어 테스트를 건너뜁니다.")
            return False
        
        # 계좌 잔고 조회 API
        if self.is_demo:
            path = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
            tr_id = "VTTC8908R"  # 모의투자 주문가능 조회
        else:
            path = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
            tr_id = "TTTC8908R"  # 실전투자 주문가능 조회
        
        url = f"{self.api_url}{path}"
        
        params = {
            "CANO": self.account_no[:8],  # 계좌번호 앞 8자리
            "ACNT_PRDT_CD": self.account_no[9:11],  # 계좌번호 뒤 2자리
            "PDNO": "005930",  # 삼성전자 종목코드 (테스트용)
            "ORD_UNPR": "",
            "ORD_DVSN": "01",  # 시장가
            "CMA_EVLU_AMT_ICLD_YN": "N",
            "OVRS_ICLD_YN": "N"
        }
        
        headers = self.headers.copy()
        headers.update({
            "tr_id": tr_id,
            "custtype": "P",  # 개인
        })
        
        try:
            print(f"  계좌 조회 중... ({self.account_no})")
            res = requests.get(url, params=params, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                rt_cd = data.get("rt_cd", "")
                msg = data.get("msg1", "")
                
                if rt_cd == "0":
                    print(f"  [OK] 계좌 조회 성공!")
                    
                    if "output" in data:
                        output = data["output"]
                        print(f"     - 주문가능현금: {output.get('ord_psbl_cash', 0):,}원")
                        print(f"     - 최대주문가능수량: {output.get('max_buy_qty', 0)}주")
                else:
                    print(f"  [WARNING] 계좌 조회 실패: {msg}")
                    
                return rt_cd == "0"
            else:
                print(f"  [FAIL] 계좌 조회 실패")
                print(f"     - 상태 코드: {res.status_code}")
                print(f"     - 응답: {res.text[:200]}")
                return False
                
        except Exception as e:
            print(f"  [ERROR] 계좌 조회 오류: {e}")
            return False
    
    def test_market_price(self):
        """시세 조회 테스트"""
        print("\n" + "="*60)
        print("4. 시세 조회 테스트")
        print("="*60)
        
        if not self.token:
            print("  [SKIP] 토큰이 없어 테스트를 건너뜁니다.")
            return False
        
        # 주식 현재가 조회
        path = "/uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self.api_url}{path}"
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # 주식
            "FID_INPUT_ISCD": "005930"  # 삼성전자
        }
        
        headers = self.headers.copy()
        headers.update({
            "tr_id": "FHKST01010100",  # 주식현재가 조회
            "custtype": "P",
        })
        
        try:
            print(f"  삼성전자(005930) 시세 조회 중...")
            res = requests.get(url, params=params, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                rt_cd = data.get("rt_cd", "")
                
                if rt_cd == "0" and "output" in data:
                    output = data["output"]
                    print(f"  [OK] 시세 조회 성공!")
                    print(f"     - 현재가: {output.get('stck_prpr', 0):,}원")
                    print(f"     - 전일대비: {output.get('prdy_vrss', 0):,}원")
                    print(f"     - 등락률: {output.get('prdy_ctrt', 0)}%")
                    print(f"     - 거래량: {output.get('acml_vol', 0):,}주")
                    return True
                else:
                    print(f"  [WARNING] 시세 조회 실패: {data.get('msg1', '')}")
                    return False
            else:
                print(f"  [FAIL] 시세 조회 실패: {res.status_code}")
                return False
                
        except Exception as e:
            print(f"  [ERROR] 시세 조회 오류: {e}")
            return False
    
    def test_openapi_bridge(self):
        """OpenAPI 브리지 서버 테스트"""
        print("\n" + "="*60)
        print("5. OpenAPI 브리지 서버 테스트")
        print("="*60)
        
        bridge_url = "http://localhost:8100"
        
        try:
            print(f"  브리지 서버 연결 테스트... ({bridge_url})")
            res = requests.get(f"{bridge_url}/", timeout=2)
            
            if res.status_code == 200:
                data = res.json()
                print(f"  [OK] 브리지 서버 연결 성공!")
                print(f"     - 상태: {data.get('status', 'unknown')}")
                print(f"     - 연결여부: {'연결됨' if data.get('connected') else '미연결'}")
                return True
            else:
                print(f"  [FAIL] 브리지 서버 응답 오류: {res.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"  [WARNING] 브리지 서버가 실행되지 않았습니다.")
            print(f"     다음 명령으로 실행하세요:")
            print(f"     cd backend && venv32\\Scripts\\activate && python kiwoom_openapi_bridge.py")
            return False
        except Exception as e:
            print(f"  [ERROR] 브리지 서버 연결 오류: {e}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "="*60)
        print("키움증권 API 연결 테스트 시작")
        print("="*60)
        
        results = {}
        
        # 1. 설정 확인
        if not self.check_config():
            print("\n테스트를 중단합니다.")
            return
        
        # 2. REST API 토큰 발급
        results["토큰 발급"] = self.get_access_token()
        
        # 3. 계좌 조회 (토큰이 있을 때만)
        if results["토큰 발급"]:
            results["계좌 조회"] = self.test_account_balance()
            results["시세 조회"] = self.test_market_price()
        
        # 4. OpenAPI 브리지 테스트
        results["브리지 서버"] = self.test_openapi_bridge()
        
        # 결과 요약
        print("\n" + "="*60)
        print("테스트 결과 요약")
        print("="*60)
        
        for test_name, passed in results.items():
            status = "[OK]" if passed else "[FAIL]"
            print(f"  {test_name}: {status}")
        
        all_passed = all(results.values())
        
        if all_passed:
            print("\n[SUCCESS] 모든 테스트를 통과했습니다!")
            print("키움 API를 사용할 준비가 완료되었습니다.")
        else:
            print("\n[WARNING] 일부 테스트가 실패했습니다.")
            print("위의 오류 메시지를 확인하고 문제를 해결하세요.")
        
        return all_passed

def main():
    """메인 실행"""
    tester = KiwoomAPITester()
    success = tester.run_all_tests()
    
    print("\n" + "="*60)
    if success:
        print("다음 단계:")
        print("1. 하이브리드 시스템 시작: start_hybrid_system.bat")
        print("2. 웹 UI 접속: http://localhost:3000")
    else:
        print("문제 해결:")
        print("1. API 키 확인: backend/setup_api_keys.py")
        print("2. 브리지 서버 실행: cd backend && venv32\\Scripts\\activate")
        print("3. 문서 참조: docs/kiwoom/API_KEY_SETUP_GUIDE.md")
    print("="*60)

if __name__ == "__main__":
    main()