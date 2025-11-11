"""지수 API 응답 확인"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app_key = os.getenv('KIWOOM_APP_KEY')
app_secret = os.getenv('KIWOOM_APP_SECRET')
base_url = 'https://mockapi.kiwoom.com'

# 토큰 발급
token_url = f"{base_url}/oauth2/token"
token_data = {
    "grant_type": "client_credentials",
    "appkey": app_key,
    "secretkey": app_secret
}
token_response = requests.post(token_url, json=token_data, timeout=10)
access_token = token_response.json().get('token')

print("Testing KOSPI Index (0001)...")
print("="*80)

# KOSPI 지수 조회
chart_url = f"{base_url}/api/dostk/chart"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "authorization": f"Bearer {access_token}",
    "cont-yn": "N",
    "next-key": "",
    "api-id": "ka10081"
}
body = {
    "stk_cd": "0001",
    "base_dt": "20251027",
    "upd_stkpc_tp": "1"
}

response = requests.post(chart_url, headers=headers, json=body, timeout=10)
print(f"Status: {response.status_code}")
print(f"\nResponse:")
data = response.json()
print(json.dumps(data, indent=2, ensure_ascii=False))
