"""키움 API 인증 테스트"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app_key = os.getenv('KIWOOM_APP_KEY')
app_secret = os.getenv('KIWOOM_APP_SECRET')
base_url = os.getenv('KIWOOM_API_URL', 'https://mockapi.kiwoom.com')

print(f"APP_KEY: {app_key[:20]}..." if app_key else "APP_KEY: None")
print(f"APP_SECRET: {app_secret[:20]}..." if app_secret else "APP_SECRET: None")
print(f"BASE_URL: {base_url}")
print()

# 토큰 발급 시도
url = f"{base_url}/oauth2/token"
headers = {
    "Content-Type": "application/json; charset=utf-8"
}

# 방법 1: secretkey 사용
print("=== 방법 1: secretkey 사용 ===")
data1 = {
    "grant_type": "client_credentials",
    "appkey": app_key,
    "secretkey": app_secret
}

try:
    response = requests.post(url, headers=headers, json=data1, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    result = response.json()
    print(f"Return Code: {result.get('return_code')}")
    print(f"Return Message: {result.get('return_msg')}")
except Exception as e:
    print(f"Error: {e}")

print()

# 방법 2: appsecret 사용
print("=== 방법 2: appsecret 사용 ===")
data2 = {
    "grant_type": "client_credentials",
    "appkey": app_key,
    "appsecret": app_secret
}

try:
    response = requests.post(url, headers=headers, json=data2, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    result = response.json()
    print(f"Return Code: {result.get('return_code')}")
    print(f"Return Message: {result.get('return_msg')}")
except Exception as e:
    print(f"Error: {e}")
