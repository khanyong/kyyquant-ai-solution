# 📋 키움증권 REST API 발급 완벽 가이드

## 🎯 목차
1. [API 신청 전 준비사항](#1-api-신청-전-준비사항)
2. [키움증권 REST API 신청](#2-키움증권-rest-api-신청)
3. [API Key 발급 및 설정](#3-api-key-발급-및-설정)
4. [API 테스트](#4-api-테스트)
5. [프로젝트 환경 설정](#5-프로젝트-환경-설정)

---

## 1. API 신청 전 준비사항

### ✅ 필수 준비물
- **키움증권 계좌** (실전투자 또는 모의투자)
- **키움증권 홈페이지 회원가입**
- **공동인증서** (구 공인인증서)
- **키움 영웅문S 설치** (선택사항)

### 📱 계좌 개설이 필요한 경우
1. 키움증권 홈페이지: https://www.kiwoom.com
2. 비대면 계좌개설 가능 (신분증 필요)
3. 계좌 개설 후 즉시 API 신청 가능

---

## 2. 키움증권 REST API 신청

### 🔗 Step 1: OpenAPI+ 사이트 접속
```
https://openapi.kiwoom.com
```

### 📝 Step 2: 회원가입 및 로그인
1. **[회원가입]** 클릭
2. 키움증권 계좌번호로 인증
3. 개인정보 입력
4. 이메일 인증 완료

### 🚀 Step 3: API 서비스 신청
1. 로그인 후 **[My Page]** → **[API 서비스 신청]**
2. 서비스 선택:
   ```
   ✅ REST API
   ✅ WebSocket (실시간 시세)
   ```
3. 이용 목적 선택:
   - 개인 투자용
   - 알고리즘 트레이딩
   - 포트폴리오 관리

### 💳 Step 4: 서비스 결제
- **모의투자**: 무료
- **실전투자**: 
  - 기본: 월 3,300원 (VAT 포함)
  - 프리미엄: 월 11,000원 (VAT 포함)
  
> 💡 **TIP**: 먼저 모의투자로 테스트 후 실전투자로 전환 권장

---

## 3. API Key 발급 및 설정

### 🔑 Step 1: APP Key 생성
1. **[My Page]** → **[APP 관리]**
2. **[신규 APP 등록]** 클릭
3. APP 정보 입력:
   ```
   APP 이름: auto_stock_trading
   APP 설명: 자동매매 시스템
   Callback URL: http://localhost:3000 (개발용)
   서비스: REST API, WebSocket
   ```

### 📋 Step 2: Key 정보 확인
발급받은 정보:
```
APP Key: PSED....(32자리)
APP Secret: 7Zz5....(32자리)
계좌번호: 12345678-01
```

> ⚠️ **주의**: APP Secret은 최초 1회만 표시됩니다. 반드시 안전하게 저장하세요!

### 🔐 Step 3: 보안 설정
1. **IP 화이트리스트 설정** (선택)
   - 접속 허용 IP 등록
   - 개발: 0.0.0.0/0 (모든 IP)
   - 운영: 특정 서버 IP만

2. **API 권한 설정**
   ```
   ✅ 시세 조회
   ✅ 잔고 조회
   ✅ 주문 (실전투자시)
   ✅ 주문 취소
   ```

---

## 4. API 테스트

### 🧪 Step 1: 토큰 발급 테스트
```bash
# PowerShell 또는 Command Prompt에서 실행
curl -X POST "https://openapi.kiwoom.com:9443/oauth2/token" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "grant_type=client_credentials" ^
  -d "appkey=YOUR_APP_KEY" ^
  -d "appsecret=YOUR_APP_SECRET"
```

### ✅ 정상 응답 예시:
```json
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

### 📊 Step 2: 시세 조회 테스트
```bash
# 삼성전자(005930) 현재가 조회
curl -X GET "https://openapi.kiwoom.com:9443/uapi/domestic-stock/v1/quotations/inquire-price" ^
  -H "authorization: Bearer YOUR_ACCESS_TOKEN" ^
  -H "appkey: YOUR_APP_KEY" ^
  -H "appsecret: YOUR_APP_SECRET" ^
  -H "tr_id: FHKST01010100" ^
  -d "fid_cond_mrkt_div_code=J" ^
  -d "fid_input_iscd=005930"
```

---

## 5. 프로젝트 환경 설정

### 🔧 Step 1: 환경 변수 설정
`.env` 파일 생성:
```env
# 키움증권 REST API
KIWOOM_APP_KEY=YOUR_APP_KEY_HERE
KIWOOM_APP_SECRET=YOUR_APP_SECRET_HERE
KIWOOM_ACCOUNT_NO=12345678-01
KIWOOM_IS_DEMO=true  # 모의투자: true, 실전투자: false

# API URL
KIWOOM_API_URL=https://openapi.kiwoom.com:9443
KIWOOM_WS_URL=ws://openapi.kiwoom.com:9443

# 토큰 관리
KIWOOM_TOKEN_EXPIRES_IN=86400
```

### 📦 Step 2: 필요 패키지 설치
```bash
# Python 패키지
pip install requests websocket-client python-dotenv

# Node.js 패키지 (N8N용)
npm install axios ws dotenv
```

### 🧪 Step 3: 연결 테스트 스크립트
`test_kiwoom_api.py` 생성:
```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    """액세스 토큰 발급"""
    url = f"{os.getenv('KIWOOM_API_URL')}/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "appkey": os.getenv('KIWOOM_APP_KEY'),
        "appsecret": os.getenv('KIWOOM_APP_SECRET')
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✅ 토큰 발급 성공!")
        return token
    else:
        print(f"❌ 토큰 발급 실패: {response.text}")
        return None

def get_current_price(token, stock_code="005930"):
    """현재가 조회"""
    url = f"{os.getenv('KIWOOM_API_URL')}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": os.getenv('KIWOOM_APP_KEY'),
        "appsecret": os.getenv('KIWOOM_APP_SECRET'),
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        price = data['output']['stck_prpr']
        print(f"✅ {stock_code} 현재가: {price:,}원")
        return price
    else:
        print(f"❌ 시세 조회 실패: {response.text}")
        return None

if __name__ == "__main__":
    print("🚀 키움증권 REST API 테스트 시작\n")
    
    # 1. 토큰 발급
    token = get_access_token()
    
    if token:
        # 2. 시세 조회
        print("\n📊 시세 조회 테스트")
        get_current_price(token, "005930")  # 삼성전자
        get_current_price(token, "000660")  # SK하이닉스
        
    print("\n✨ 테스트 완료!")
```

### ▶️ Step 4: 테스트 실행
```bash
python test_kiwoom_api.py
```

---

## 📌 주요 API 엔드포인트

### 시세 조회
- 현재가: `/uapi/domestic-stock/v1/quotations/inquire-price`
- 호가: `/uapi/domestic-stock/v1/quotations/inquire-asking-price`
- 일봉: `/uapi/domestic-stock/v1/quotations/inquire-daily-price`

### 주문/매매
- 주문: `/uapi/domestic-stock/v1/trading/order-cash`
- 주문취소: `/uapi/domestic-stock/v1/trading/order-cancel`
- 정정: `/uapi/domestic-stock/v1/trading/order-modify`

### 계좌 조회
- 잔고: `/uapi/domestic-stock/v1/trading/inquire-balance`
- 체결내역: `/uapi/domestic-stock/v1/trading/inquire-daily-ccld`

---

## 🆘 문제 해결

### ❌ 인증 실패
- APP Key/Secret 확인
- IP 화이트리스트 확인
- 서비스 만료 여부 확인

### ❌ 시세 조회 실패
- 장 운영시간 확인 (09:00 ~ 15:30)
- 종목코드 형식 확인 (6자리)
- tr_id 코드 확인

### ❌ 주문 실패
- 계좌 잔고 확인
- 주문 가능 시간 확인
- 모의투자/실전투자 구분

---

## 📞 고객센터
- 키움증권 고객센터: 1544-9000
- OpenAPI 기술지원: openapi@kiwoom.com
- 운영시간: 평일 09:00 ~ 18:00

---

## 🎉 완료!
이제 키움증권 REST API를 사용할 준비가 되었습니다.
N8N과 연동하여 자동매매 시스템을 구축하세요!