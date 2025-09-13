"""
키움 API 직접 테스트 (로컬에서)
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_kiwoom_api():
    """키움 API 직접 테스트"""

    print("=" * 60)
    print("키움 API 직접 테스트")
    print("=" * 60)

    # API 키 확인
    app_key = os.getenv('KIWOOM_APP_KEY')
    app_secret = os.getenv('KIWOOM_APP_SECRET')

    print(f"\nAPI Key: {app_key[:10]}...")
    print(f"API Secret: {app_secret[:10]}...")

    # 1. 토큰 발급 테스트
    print("\n1. 토큰 발급 테스트...")

    # 키움 REST API 모의투자 엔드포인트
    test_urls = [
        "https://mockapi.kiwoom.com/oauth2/token",  # 모의투자
    ]

    for token_url in test_urls:
        print(f"\n   테스트 URL: {token_url}")

        token_data = {
            "grant_type": "client_credentials",
            "appkey": app_key,
            "secretkey": app_secret  # appsecret이 아니라 secretkey
        }

        # JSON 방식 시도
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(token_url, json=token_data, headers=headers, timeout=3)
            print(f"   JSON - 상태 코드: {response.status_code}")

            if response.status_code == 200:
                print("   성공!")
                token_info = response.json()
                access_token = token_info.get('token')  # 키움은 'token' 필드 사용
                if access_token:
                    print(f"   토큰: {access_token[:30]}...")

                    # 시세 조회 테스트
                    print("\n2. 삼성전자(005930) 시세 조회...")
                    base_url = token_url.replace('/oauth2/token', '')
                    price_url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"

                    price_headers = {
                        "authorization": f"Bearer {access_token}",
                        "appkey": app_key,
                        "appsecret": app_secret,  # 한투 형식
                        "tr_id": "FHKST01010100",
                        "Content-Type": "application/json; charset=UTF-8"
                    }

                    price_params = {
                        "fid_cond_mrkt_div_code": "J",
                        "fid_input_iscd": "005930"
                    }

                    try:
                        print(f"   시세 URL: {price_url}")
                        price_response = requests.get(price_url, headers=price_headers, params=price_params, timeout=10)
                        print(f"   상태 코드: {price_response.status_code}")

                        if price_response.status_code == 200:
                            price_data = price_response.json()
                            print(f"   응답: {price_data}")
                            output = price_data.get('output', {})
                            current_price = output.get('stck_prpr', '0')
                            print(f"   현재가: {current_price}원")
                        else:
                            print(f"   시세 조회 실패: {price_response.text}")
                    except Exception as e:
                        print(f"   시세 조회 오류: {e}")

                    break
                else:
                    print(f"   응답: {token_info}")

        except requests.exceptions.Timeout:
            print("   타임아웃")
        except requests.exceptions.ConnectionError:
            print("   연결 실패")
        except Exception as e:
            print(f"   오류: {str(e)[:50]}")

        # Form 방식 시도
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = requests.post(token_url, data=token_data, headers=headers, timeout=3)
            print(f"   Form - 상태 코드: {response.status_code}")

            if response.status_code == 200:
                print("   성공!")
                token_info = response.json()
                access_token = token_info.get('token')  # 키움은 'token' 필드 사용
                if access_token:
                    print(f"   토큰: {access_token[:30]}...")

                    # 시세 조회 테스트
                    print("\n2. 삼성전자(005930) 시세 조회...")
                    base_url = token_url.replace('/oauth2/token', '')
                    price_url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"

                    price_headers = {
                        "authorization": f"Bearer {access_token}",
                        "appkey": app_key,
                        "appsecret": app_secret,  # 한투 형식
                        "tr_id": "FHKST01010100",
                        "Content-Type": "application/json; charset=UTF-8"
                    }

                    price_params = {
                        "fid_cond_mrkt_div_code": "J",
                        "fid_input_iscd": "005930"
                    }

                    try:
                        print(f"   시세 URL: {price_url}")
                        price_response = requests.get(price_url, headers=price_headers, params=price_params, timeout=10)
                        print(f"   상태 코드: {price_response.status_code}")

                        if price_response.status_code == 200:
                            price_data = price_response.json()
                            print(f"   응답: {price_data}")
                            output = price_data.get('output', {})
                            current_price = output.get('stck_prpr', '0')
                            print(f"   현재가: {current_price}원")
                        else:
                            print(f"   시세 조회 실패: {price_response.text}")
                    except Exception as e:
                        print(f"   시세 조회 오류: {e}")

                    break
                else:
                    print(f"   응답: {token_info}")

        except requests.exceptions.Timeout:
            print("   타임아웃")
        except requests.exceptions.ConnectionError:
            print("   연결 실패")
        except Exception as e:
            print(f"   오류: {str(e)[:50]}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_kiwoom_api()