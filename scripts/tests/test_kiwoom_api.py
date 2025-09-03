"""
키움증권 REST API 연결 테스트 스크립트
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class KiwoomAPITester:
    def __init__(self):
        self.app_key = os.getenv('KIWOOM_APP_KEY')
        self.app_secret = os.getenv('KIWOOM_APP_SECRET')
        self.account_no = os.getenv('KIWOOM_ACCOUNT_NO')
        self.base_url = os.getenv('KIWOOM_API_URL', 'https://openapi.kiwoom.com:9443')
        self.is_demo = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'
        self.access_token = None
        
        print("=" * 60)
        print("키움증권 REST API 테스터")
        print("=" * 60)
        print(f"서버: {self.base_url}")
        print(f"모드: {'모의투자' if self.is_demo else '실전투자'}")
        print(f"계좌: {self.account_no}")
        print("=" * 60)
    
    def check_credentials(self):
        """API 인증정보 확인"""
        print("\n1️⃣ API 인증정보 확인")
        print("-" * 40)
        
        if not self.app_key or not self.app_secret:
            print("❌ APP Key 또는 Secret이 설정되지 않았습니다.")
            print("   .env 파일을 확인하세요.")
            return False
        
        print(f"✅ APP Key: {self.app_key[:10]}...")
        print(f"✅ APP Secret: {'*' * 10}")
        return True
    
    def get_access_token(self):
        """액세스 토큰 발급"""
        print("\n2️⃣ 액세스 토큰 발급")
        print("-" * 40)
        
        url = f"{self.base_url}/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 0)
                
                print(f"✅ 토큰 발급 성공!")
                print(f"   유효시간: {expires_in}초 ({expires_in//3600}시간)")
                print(f"   토큰: {self.access_token[:20]}...")
                return True
            else:
                print(f"❌ 토큰 발급 실패")
                print(f"   상태코드: {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 연결 실패: {str(e)}")
            return False
    
    def test_market_price(self, stock_code="005930"):
        """시세 조회 테스트"""
        print(f"\n3️⃣ 시세 조회 테스트 - {stock_code}")
        print("-" * 40)
        
        if not self.access_token:
            print("❌ 액세스 토큰이 없습니다.")
            return False
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "FHKST01010100"  # 실시간 시세 조회
        }
        params = {
            "fid_cond_mrkt_div_code": "J",  # 주식
            "fid_input_iscd": stock_code
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('rt_cd') == '0':  # 정상
                    output = data.get('output', {})
                    
                    print(f"✅ 시세 조회 성공!")
                    print(f"   종목명: {output.get('stck_prpr_name', 'N/A')}")
                    print(f"   현재가: {int(output.get('stck_prpr', 0)):,}원")
                    print(f"   전일대비: {int(output.get('prdy_vrss', 0)):+,}원")
                    print(f"   등락률: {float(output.get('prdy_ctrt', 0)):+.2f}%")
                    print(f"   거래량: {int(output.get('acml_vol', 0)):,}주")
                    return True
                else:
                    print(f"❌ 시세 조회 실패")
                    print(f"   메시지: {data.get('msg1')}")
                    return False
            else:
                print(f"❌ API 호출 실패")
                print(f"   상태코드: {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 요청 실패: {str(e)}")
            return False
    
    def test_account_balance(self):
        """계좌 잔고 조회 테스트"""
        print(f"\n4️⃣ 계좌 잔고 조회 테스트")
        print("-" * 40)
        
        if not self.access_token or not self.account_no:
            print("❌ 액세스 토큰 또는 계좌번호가 없습니다.")
            return False
        
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        headers = {
            "authorization": f"Bearer {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "tr_id": "VTTC8434R" if self.is_demo else "TTTC8434R"  # 모의/실전 구분
        }
        params = {
            "CANO": self.account_no[:8],  # 계좌번호
            "ACNT_PRDT_CD": self.account_no[9:11] if len(self.account_no) > 9 else "01",  # 계좌상품코드
            "AFHR_FLPR_YN": "N",  # 시간외단가여부
            "OFL_YN": "N",  # 오프라인여부
            "INQR_DVSN": "01",  # 조회구분
            "UNPR_DVSN": "01",  # 단가구분
            "FUND_STTL_ICLD_YN": "N",  # 펀드결제분포함여부
            "FNCG_AMT_AUTO_RDPT_YN": "N",  # 융자금액자동상환여부
            "PRCS_DVSN": "00",  # 처리구분
            "CTX_AREA_FK100": "",  # 연속조회검색조건
            "CTX_AREA_NK100": ""  # 연속조회키
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('rt_cd') == '0':  # 정상
                    output1 = data.get('output1', [])
                    output2 = data.get('output2', [{}])[0]
                    
                    print(f"✅ 잔고 조회 성공!")
                    print(f"   예수금: {int(output2.get('dnca_tot_amt', 0)):,}원")
                    print(f"   총평가금액: {int(output2.get('tot_evlu_amt', 0)):,}원")
                    print(f"   총손익: {int(output2.get('evlu_pfls_smtl_amt', 0)):+,}원")
                    
                    if output1:
                        print(f"\n   보유종목 ({len(output1)}개):")
                        for stock in output1[:5]:  # 최대 5개만 표시
                            print(f"   - {stock.get('prdt_name', 'N/A')}: {int(stock.get('hldg_qty', 0)):,}주")
                    
                    return True
                else:
                    print(f"❌ 잔고 조회 실패")
                    print(f"   메시지: {data.get('msg1')}")
                    return False
            else:
                print(f"❌ API 호출 실패")
                print(f"   상태코드: {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 요청 실패: {str(e)}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "=" * 60)
        print("🧪 키움증권 REST API 전체 테스트 시작")
        print("=" * 60)
        
        results = []
        
        # 1. 인증정보 확인
        if self.check_credentials():
            results.append("✅ 인증정보 확인")
            
            # 2. 토큰 발급
            if self.get_access_token():
                results.append("✅ 토큰 발급")
                
                # 3. 시세 조회
                if self.test_market_price("005930"):  # 삼성전자
                    results.append("✅ 시세 조회 (삼성전자)")
                else:
                    results.append("❌ 시세 조회 실패")
                
                # 4. 추가 종목 테스트
                if self.test_market_price("000660"):  # SK하이닉스
                    results.append("✅ 시세 조회 (SK하이닉스)")
                
                # 5. 계좌 잔고 조회
                if self.account_no:
                    if self.test_account_balance():
                        results.append("✅ 계좌 잔고 조회")
                    else:
                        results.append("❌ 계좌 잔고 조회 실패")
            else:
                results.append("❌ 토큰 발급 실패")
        else:
            results.append("❌ 인증정보 미설정")
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        for result in results:
            print(f"   {result}")
        
        success_count = len([r for r in results if "✅" in r])
        total_count = len(results)
        
        print("-" * 60)
        print(f"   성공: {success_count}/{total_count}")
        print("=" * 60)
        
        if success_count == total_count:
            print("\n🎉 모든 테스트가 성공했습니다!")
            print("   키움증권 REST API를 사용할 준비가 되었습니다.")
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다.")
            print("   .env 파일과 API 설정을 확인하세요.")


if __name__ == "__main__":
    tester = KiwoomAPITester()
    tester.run_all_tests()
    
    print("\n💡 도움말:")
    print("   - API Key 발급: https://openapi.kiwoom.com")
    print("   - 문서: docs/키움 REST API 문서.xlsx")
    print("   - 가이드: KIWOOM_REST_API_GUIDE.md")