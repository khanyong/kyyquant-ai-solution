"""
키움증권 REST API 간단 테스트
"""
import os
import requests
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def test_kiwoom_api():
    print("=" * 60)
    print("키움증권 REST API 테스트")
    print("=" * 60)
    
    # API 정보
    app_key = os.getenv('KIWOOM_APP_KEY')
    app_secret = os.getenv('KIWOOM_APP_SECRET')
    account_no = os.getenv('KIWOOM_ACCOUNT_NO')
    base_url = os.getenv('KIWOOM_API_URL', 'https://mockapi.kiwoom.com')
    
    print(f"계좌: {account_no}")
    print(f"모드: 모의투자")
    print("-" * 60)
    
    # 1. 토큰 발급
    print("\n[1] 토큰 발급 테스트")
    url = f"{base_url}/oauth2/token"
    # 키움 REST API 토큰 발급 파라미터
    data = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "secretkey": app_secret  # appsecret -> secretkey로 변경
    }
    
    try:
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            print("[OK] 토큰 발급 성공!")
            
            # 토큰 데이터 확인
            if 'access_token' in token_data:
                access_token = token_data.get('access_token')
                print(f"    토큰: {access_token[:30]}...")
            elif 'token' in token_data:
                access_token = token_data.get('token')
                print(f"    토큰: {access_token[:30]}...")
            else:
                print(f"    응답: {token_data}")
                access_token = token_data.get('token', token_data.get('access_token', None))
            
            # 2. 시세 조회
            print("\n[2] 삼성전자 시세 조회")
            price_url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "authorization": f"Bearer {access_token}",
                "appkey": app_key,
                "appsecret": app_secret,
                "tr_id": "FHKST01010100"
            }
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": "005930"  # 삼성전자
            }
            
            price_response = requests.get(price_url, headers=headers, params=params, timeout=10)
            
            if price_response.status_code == 200:
                price_data = price_response.json()
                
                if price_data.get('rt_cd') == '0':
                    output = price_data.get('output', {})
                    current_price = int(output.get('stck_prpr', 0))
                    change = int(output.get('prdy_vrss', 0))
                    change_rate = float(output.get('prdy_ctrt', 0))
                    
                    print("[OK] 시세 조회 성공!")
                    print(f"    현재가: {current_price:,}원")
                    print(f"    전일대비: {change:+,}원 ({change_rate:+.2f}%)")
                    
                    # 3. 잔고 조회
                    print("\n[3] 계좌 잔고 조회")
                    balance_url = f"{base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
                    balance_headers = {
                        "authorization": f"Bearer {access_token}",
                        "appkey": app_key,
                        "appsecret": app_secret,
                        "tr_id": "VTTC8434R"  # 모의투자
                    }
                    balance_params = {
                        "CANO": account_no[:8],
                        "ACNT_PRDT_CD": "01",
                        "AFHR_FLPR_YN": "N",
                        "OFL_YN": "N",
                        "INQR_DVSN": "01",
                        "UNPR_DVSN": "01",
                        "FUND_STTL_ICLD_YN": "N",
                        "FNCG_AMT_AUTO_RDPT_YN": "N",
                        "PRCS_DVSN": "00",
                        "CTX_AREA_FK100": "",
                        "CTX_AREA_NK100": ""
                    }
                    
                    balance_response = requests.get(balance_url, headers=balance_headers, params=balance_params, timeout=10)
                    
                    if balance_response.status_code == 200:
                        balance_data = balance_response.json()
                        
                        if balance_data.get('rt_cd') == '0':
                            print("[OK] 잔고 조회 성공!")
                            output2 = balance_data.get('output2', [{}])[0]
                            total_money = int(output2.get('dnca_tot_amt', 0))
                            print(f"    예수금: {total_money:,}원")
                        else:
                            print(f"[ERROR] 잔고 조회 실패: {balance_data.get('msg1')}")
                    else:
                        print(f"[ERROR] 잔고 API 호출 실패: {balance_response.status_code}")
                        
                else:
                    print(f"[ERROR] 시세 조회 실패: {price_data.get('msg1')}")
            else:
                print(f"[ERROR] 시세 API 호출 실패: {price_response.status_code}")
                
        else:
            print(f"[ERROR] 토큰 발급 실패")
            print(f"    상태코드: {response.status_code}")
            print(f"    응답: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] 요청 실패: {str(e)}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_kiwoom_api()