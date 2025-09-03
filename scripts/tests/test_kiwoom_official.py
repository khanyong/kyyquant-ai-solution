"""
키움 REST API 공식 스펙 테스트
API ID: au10001 - 접근토큰 발급
"""
import os
import json
import requests
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def test_kiwoom_api():
    print("=" * 60)
    print("키움 REST API 테스트 (공식 스펙)")
    print("=" * 60)
    
    # API 정보
    app_key = os.getenv('KIWOOM_APP_KEY')
    app_secret = os.getenv('KIWOOM_APP_SECRET')
    account_no = os.getenv('KIWOOM_ACCOUNT_NO')
    base_url = "https://mockapi.kiwoom.com"  # 모의투자 도메인
    
    print(f"도메인: {base_url}")
    print(f"계좌: {account_no}")
    print(f"모드: 모의투자")
    print("-" * 60)
    
    # 1. 접근토큰 발급 (au10001)
    print("\n[1] 접근토큰 발급 (au10001)")
    token_url = f"{base_url}/oauth2/token"
    
    # 요청 본문
    request_body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "secretkey": app_secret
    }
    
    # 헤더
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    
    print(f"URL: POST {token_url}")
    print(f"Headers: {headers}")
    print(f"Body: grant_type={request_body['grant_type']}, appkey={app_key[:10]}...")
    
    try:
        response = requests.post(
            token_url,
            json=request_body,
            headers=headers,
            timeout=10
        )
        
        print(f"\n응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("[OK] 토큰 발급 성공!")
            
            # 응답 데이터 출력
            print("\n응답 데이터:")
            for key, value in response_data.items():
                if key in ['access_token', 'token']:
                    print(f"  {key}: {str(value)[:50]}...")
                else:
                    print(f"  {key}: {value}")
            
            # 토큰 추출
            access_token = response_data.get('access_token') or response_data.get('token')
            
            if access_token:
                print(f"\n[성공] 액세스 토큰: {access_token[:30]}...")
                
                # 2. 시세 조회 테스트
                test_market_data(base_url, access_token, app_key, app_secret)
                
            else:
                print("[주의] 토큰을 찾을 수 없습니다.")
                print(f"전체 응답: {response_data}")
                
        else:
            print(f"[ERROR] 토큰 발급 실패")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] 요청 실패: {str(e)}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

def test_market_data(base_url, access_token, app_key, app_secret):
    """시세 조회 테스트"""
    print("\n[2] 시세 조회 테스트")
    
    # 시세 조회 URL (예시)
    price_url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
    
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {access_token}",
        "appkey": app_key,
        "appsecret": app_secret,
        "tr_id": "FHKST01010100"  # 주식현재가 시세
    }
    
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": "005930"  # 삼성전자
    }
    
    try:
        response = requests.get(price_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] 시세 조회 성공!")
            
            if 'output' in data:
                output = data['output']
                if 'stck_prpr' in output:
                    print(f"  현재가: {output.get('stck_prpr', 'N/A')}원")
        else:
            print(f"[ERROR] 시세 조회 실패: {response.status_code}")
            print(f"  응답: {response.text[:200]}")
            
    except Exception as e:
        print(f"[ERROR] 시세 조회 오류: {str(e)}")

if __name__ == "__main__":
    test_kiwoom_api()