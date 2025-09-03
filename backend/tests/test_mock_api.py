"""
키움증권 모의투자 API 연결 테스트
간단한 연결 확인 및 기본 기능 테스트
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# 환경변수 로드
load_dotenv()

def test_mock_trading_api():
    """모의투자 API 연결 테스트"""
    
    print("="*60)
    print("키움증권 모의투자 API 연결 테스트")
    print("="*60)
    
    # 모의투자 설정 확인
    app_key = os.getenv("KIWOOM_APP_KEY")
    app_secret = os.getenv("KIWOOM_APP_SECRET")
    account_no = os.getenv("KIWOOM_ACCOUNT_NO")
    
    # 모의투자 URL (한국투자증권)
    api_url = "https://openapivts.koreainvestment.com:29443"
    
    print(f"\n[설정 정보]")
    print(f"- APP_KEY: {app_key[:20]}..." if app_key and len(app_key) > 20 else f"- APP_KEY: {app_key}")
    print(f"- 계좌번호: {account_no}")
    print(f"- API URL: {api_url}")
    print(f"- 모드: 모의투자")
    
    if not app_key or not app_secret:
        print("\n[ERROR] API 키가 설정되지 않았습니다.")
        print("한국투자증권에서 모의투자 API 키를 발급받으세요:")
        print("https://apiportal.koreainvestment.com/")
        return False
    
    # 1. 토큰 발급 테스트
    print("\n[1] 접근 토큰 발급 테스트")
    print("-" * 40)
    
    token_url = f"{api_url}/oauth2/tokenP"
    token_headers = {
        "content-type": "application/json; charset=utf-8"
    }
    token_data = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }
    
    try:
        response = requests.post(token_url, headers=token_headers, data=json.dumps(token_data))
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get("access_token")
            expires_in = token_info.get("expires_in", 0)
            
            print(f"[OK] 토큰 발급 성공!")
            print(f"     토큰 길이: {len(access_token)}자")
            print(f"     유효 시간: {expires_in:,}초 (약 {expires_in//3600}시간)")
            
            # 2. 주식 현재가 조회 테스트 (삼성전자)
            print("\n[2] 주식 시세 조회 테스트")
            print("-" * 40)
            
            price_url = f"{api_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            price_headers = {
                "content-type": "application/json; charset=utf-8",
                "authorization": f"Bearer {access_token}",
                "appkey": app_key,
                "appsecret": app_secret,
                "tr_id": "FHKST01010100",
                "custtype": "P"
            }
            price_params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": "005930"  # 삼성전자
            }
            
            response = requests.get(price_url, headers=price_headers, params=price_params)
            
            if response.status_code == 200:
                price_data = response.json()
                if price_data.get("rt_cd") == "0":
                    output = price_data.get("output", {})
                    print(f"[OK] 삼성전자(005930) 시세 조회 성공!")
                    print(f"     현재가: {int(output.get('stck_prpr', 0)):,}원")
                    print(f"     전일대비: {int(output.get('prdy_vrss', 0)):,}원")
                    print(f"     등락률: {output.get('prdy_ctrt', 0)}%")
                    print(f"     거래량: {int(output.get('acml_vol', 0)):,}주")
                else:
                    print(f"[WARNING] 시세 조회 실패: {price_data.get('msg1', '')}")
            else:
                print(f"[FAIL] 시세 조회 HTTP 오류: {response.status_code}")
            
            # 3. 계좌 잔고 조회 테스트
            if account_no:
                print("\n[3] 계좌 정보 조회 테스트")
                print("-" * 40)
                
                balance_url = f"{api_url}/uapi/domestic-stock/v1/trading/inquire-balance"
                balance_headers = {
                    "content-type": "application/json; charset=utf-8",
                    "authorization": f"Bearer {access_token}",
                    "appkey": app_key,
                    "appsecret": app_secret,
                    "tr_id": "VTTC8434R",  # 모의투자 잔고조회
                    "custtype": "P"
                }
                balance_params = {
                    "CANO": account_no[:8],
                    "ACNT_PRDT_CD": account_no[9:11] if len(account_no) > 9 else "01",
                    "AFHR_FLPR_YN": "N",
                    "OFL_YN": "",
                    "INQR_DVSN": "01",
                    "UNPR_DVSN": "01",
                    "FUND_STTL_ICLD_YN": "N",
                    "FNCG_AMT_AUTO_RDPT_YN": "N",
                    "PRCS_DVSN": "01",
                    "CTX_AREA_FK100": "",
                    "CTX_AREA_NK100": ""
                }
                
                response = requests.get(balance_url, headers=balance_headers, params=balance_params)
                
                if response.status_code == 200:
                    balance_data = response.json()
                    if balance_data.get("rt_cd") == "0":
                        output2 = balance_data.get("output2", [{}])[0]
                        print(f"[OK] 계좌 잔고 조회 성공!")
                        print(f"     예수금: {int(float(output2.get('prvs_rcdl_excc_amt', 0))):,}원")
                        print(f"     총평가금액: {int(float(output2.get('tot_evlu_amt', 0))):,}원")
                        print(f"     총매입금액: {int(float(output2.get('pchs_amt_smtl_amt', 0))):,}원")
                    else:
                        print(f"[WARNING] 잔고 조회 실패: {balance_data.get('msg1', '')}")
                else:
                    print(f"[FAIL] 잔고 조회 HTTP 오류: {response.status_code}")
            
            print("\n" + "="*60)
            print("[SUCCESS] 모의투자 API 연결 테스트 완료!")
            print("="*60)
            print("\n다음 단계:")
            print("1. 전략 개발 및 백테스트")
            print("2. 모의투자로 실시간 테스트")
            print("3. 성과 검증 후 실전 적용")
            
            return True
            
        else:
            print(f"[FAIL] 토큰 발급 실패")
            print(f"     상태 코드: {response.status_code}")
            error_data = response.json()
            print(f"     오류: {error_data.get('error_description', '')}")
            print(f"     오류 코드: {error_data.get('error_code', '')}")
            
            print("\n[해결 방법]")
            print("1. APP_KEY와 APP_SECRET이 올바른지 확인")
            print("2. 모의투자 계정이 활성화되어 있는지 확인")
            print("3. IP 주소가 등록되어 있는지 확인 (한국투자증권 마이페이지)")
            
            return False
            
    except Exception as e:
        print(f"[ERROR] 연결 오류: {e}")
        return False

def main():
    """메인 실행"""
    print("\n키움증권 모의투자 API 연결 테스트를 시작합니다.")
    print("실제 거래가 발생하지 않는 안전한 테스트입니다.\n")
    
    success = test_mock_trading_api()
    
    if not success:
        print("\n" + "="*60)
        print("API 키 설정이 필요합니다.")
        print("="*60)
        print("\n설정 방법:")
        print("1. 한국투자증권 개발자센터 가입")
        print("   https://apiportal.koreainvestment.com/")
        print("2. 모의투자 앱 등록 및 API 키 발급")
        print("3. .env 파일에 키 입력:")
        print("   KIWOOM_APP_KEY=발급받은_APP_KEY")
        print("   KIWOOM_APP_SECRET=발급받은_APP_SECRET")
        print("   KIWOOM_ACCOUNT_NO=모의투자_계좌번호")

if __name__ == "__main__":
    main()