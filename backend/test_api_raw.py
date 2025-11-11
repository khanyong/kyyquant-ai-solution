"""키움 API 원시 응답 확인"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app_key = os.getenv('KIWOOM_APP_KEY')
app_secret = os.getenv('KIWOOM_APP_SECRET')
base_url = 'https://mockapi.kiwoom.com'

# 1. 토큰 발급
token_url = f"{base_url}/oauth2/token"
token_headers = {
    "Content-Type": "application/json; charset=utf-8"
}
token_data = {
    "grant_type": "client_credentials",
    "appkey": app_key,
    "secretkey": app_secret
}

token_response = requests.post(token_url, headers=token_headers, json=token_data, timeout=10)
token_result = token_response.json()
access_token = token_result.get('token')

print("=== Token ===")
print(f"Access Token: {access_token[:50]}...")
print()

# 2. 현재가 조회 (ka10007)
print("=== 1. Current Price (ka10007) ===")
price_url = f"{base_url}/api/dostk/mrkcond"
price_headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "authorization": f"Bearer {access_token}",
    "cont-yn": "N",
    "next-key": "",
    "api-id": "ka10007"
}
price_body = {
    "stk_cd": "005930"
}

price_response = requests.post(price_url, headers=price_headers, json=price_body, timeout=10)
print(f"Status: {price_response.status_code}")
print(f"Response Headers:")
for key in ['cont-yn', 'next-key', 'api-id']:
    print(f"  {key}: {price_response.headers.get(key)}")
print(f"\nResponse Body:")
print(json.dumps(price_response.json(), indent=2, ensure_ascii=False))
print()

# 3. 일봉 조회 (ka10081)
print("=== 2. Daily Chart (ka10081) ===")
chart_url = f"{base_url}/api/dostk/chart"
chart_headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "authorization": f"Bearer {access_token}",
    "cont-yn": "N",
    "next-key": "",
    "api-id": "ka10081"
}
chart_body = {
    "stk_cd": "005930",
    "base_dt": "20251027",
    "upd_stkpc_tp": "1"
}

chart_response = requests.post(chart_url, headers=chart_headers, json=chart_body, timeout=10)
print(f"Status: {chart_response.status_code}")
print(f"Response Headers:")
for key in ['cont-yn', 'next-key', 'api-id']:
    print(f"  {key}: {chart_response.headers.get(key)}")
print(f"\nResponse Body (first 2 items):")
chart_data = chart_response.json()
if 'output' in chart_data and len(chart_data['output']) > 0:
    print(json.dumps(chart_data['output'][:2], indent=2, ensure_ascii=False))
else:
    print(json.dumps(chart_data, indent=2, ensure_ascii=False))
