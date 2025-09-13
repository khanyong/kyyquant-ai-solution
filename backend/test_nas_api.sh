#!/bin/bash

# NAS Docker 컨테이너에서 키움 REST API 테스트
# 사용법: ssh admin@192.168.50.150 'bash -s' < test_nas_api.sh

echo "============================================"
echo "NAS Docker - 키움 REST API 연결 테스트"
echo "============================================"

# Docker 컨테이너 내부에서 실행
docker exec kiwoom-bridge sh -c '
echo "1. 컨테이너 내부 네트워크 확인"
ping -c 1 google.com

echo ""
echo "2. 키움 API 서버 연결 테스트"
curl -v --connect-timeout 5 https://openapi.kiwoom.com:9443/ 2>&1 | head -20

echo ""
echo "3. 환경변수 확인"
env | grep KIWOOM

echo ""
echo "4. Python에서 연결 테스트"
python3 -c "
import requests
import os

app_key = os.getenv(\"KIWOOM_APP_KEY\")
app_secret = os.getenv(\"KIWOOM_APP_SECRET\")

print(f\"APP_KEY: {app_key[:10] if app_key else None}\")
print(f\"APP_SECRET: {app_secret[:10] if app_secret else None}\")

try:
    # 키움 REST API 토큰 요청
    url = \"https://openapi.kiwoom.com:9443/oauth2/token\"
    data = {
        \"grant_type\": \"client_credentials\",
        \"appkey\": app_key,
        \"appsecret\": app_secret
    }
    headers = {\"Content-Type\": \"application/x-www-form-urlencoded\"}

    response = requests.post(url, data=data, headers=headers, timeout=10, verify=False)
    print(f\"Status: {response.status_code}\")
    if response.status_code == 200:
        print(\"✅ 토큰 발급 성공!\")
    else:
        print(f\"❌ 응답: {response.text[:200]}\")
except Exception as e:
    print(f\"❌ 오류: {e}\")
"
'

echo ""
echo "============================================"
echo "테스트 완료"
echo "============================================"