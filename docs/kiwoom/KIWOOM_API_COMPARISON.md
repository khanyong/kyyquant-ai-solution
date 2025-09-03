# 🔍 키움증권 OpenAPI+ vs REST API 비교 및 설정 가이드

## 📊 API 종류 비교

### 1. OpenAPI+ (기존)
- **방식**: COM/OCX 기반 (Windows 전용)
- **연결**: 키움 서버와 직접 연결
- **실시간**: 지원 (초당 수십건)
- **환경**: Windows + Python/C#/VB 등
- **인증**: 로그인 창 통한 공동인증서 인증

### 2. REST API (신규)
- **방식**: HTTP/HTTPS 기반 (OS 무관)
- **연결**: RESTful API 호출
- **실시간**: WebSocket 별도 필요
- **환경**: 모든 OS + 모든 언어
- **인증**: APP Key/Secret 토큰 방식

---

## 🔑 APP Key/Secret 공통 사용 여부

### ✅ **답변: 같은 APP Key/Secret 사용 가능!**

OpenAPI+용으로 발급받은 APP Key와 Secret은 REST API에서도 **그대로 사용 가능**합니다.

단, 다음을 확인하세요:

1. **서비스 신청 확인**
   - https://openapi.kiwoom.com 로그인
   - My Page → 서비스 관리
   - 확인 항목:
     ```
     ✅ OpenAPI+ (이미 신청됨)
     ❓ REST API (확인 필요)
     ❓ WebSocket (실시간 필요시)
     ```

2. **REST API 추가 신청 방법**
   ```
   1. My Page → 서비스 관리
   2. "REST API" 추가 신청
   3. 기존 APP에 권한 추가
   4. 즉시 사용 가능 (같은 Key 사용)
   ```

---

## 🔧 기존 APP Key/Secret 확인 방법

### Windows에서 확인 (OpenAPI+ 설치된 경우)
```python
# check_kiwoom_keys.py
import win32com.client

# OpenAPI+ 연결
kiwoom = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")

# 로그인 후
if kiwoom.CommConnect() == 0:
    # KOA Studio에서 확인하거나
    # 키움 홈페이지에서 확인
    print("https://openapi.kiwoom.com 에서 확인")
```

### 웹에서 확인
1. https://openapi.kiwoom.com 접속
2. 로그인
3. My Page → APP 관리
4. APP Key 확인 (Secret은 재발급만 가능)

---

## 🚀 REST API 즉시 테스트

### 1. 기존 Key로 테스트
```bash
# .env 파일 수정
KIWOOM_APP_KEY=기존_OpenAPI+_APP_KEY
KIWOOM_APP_SECRET=기존_OpenAPI+_APP_SECRET
KIWOOM_ACCOUNT_NO=계좌번호-01
KIWOOM_IS_DEMO=true
KIWOOM_API_URL=https://openapi.kiwoom.com:9443
```

### 2. 테스트 실행
```bash
python test_kiwoom_api.py
```

### 3. 예상 결과

#### ✅ REST API 권한이 있는 경우:
```
✅ 토큰 발급 성공!
✅ 시세 조회 성공!
```

#### ❌ REST API 권한이 없는 경우:
```
❌ 토큰 발급 실패
   상태코드: 401
   응답: {"error": "unauthorized_client"}
```
→ REST API 서비스 추가 신청 필요

---

## 📝 프로젝트별 선택 가이드

### 🖥️ Windows 전용 자동매매
**OpenAPI+ 선택**
- 장점: 빠른 실시간 데이터, 안정성
- 단점: Windows 전용, 복잡한 설정
- 용도: HTS 연동, 고빈도 매매

### ☁️ 클라우드/웹 기반 자동매매
**REST API 선택**
- 장점: OS 무관, 간단한 연동, N8N 지원
- 단점: 실시간 제한, API 호출 제한
- 용도: 웹서비스, 클라우드 배포

### 🔄 하이브리드 (본 프로젝트 추천)
**REST API + WebSocket**
- REST API: 주문, 조회, 전략 실행
- WebSocket: 실시간 시세 (필요시)
- N8N: 자동화 워크플로우
- Supabase: 데이터 저장

---

## ⚡ 빠른 설정 (기존 Key 사용)

### Step 1: REST API 권한 확인/추가
```
https://openapi.kiwoom.com
→ My Page 
→ 서비스 관리 
→ REST API 신청 (없는 경우)
```

### Step 2: 환경 설정
```bash
# .env 파일
KIWOOM_APP_KEY=PSEDxxxxxx  # 기존 KEY
KIWOOM_APP_SECRET=7Zz5xxxx  # 기존 SECRET
KIWOOM_ACCOUNT_NO=12345678-01
KIWOOM_API_URL=https://openapi.kiwoom.com:9443
```

### Step 3: 테스트
```bash
python test_kiwoom_api.py
```

---

## 🎯 결론

1. **기존 OpenAPI+ APP Key/Secret 그대로 사용 가능**
2. **REST API 서비스만 추가 신청**하면 됨 (같은 계정에서)
3. **N8N + Supabase 연동**에는 REST API가 적합
4. 필요시 WebSocket도 추가하여 실시간 데이터 수신

---

## 📞 추가 도움

- 서비스 추가 문의: openapi@kiwoom.com
- 기술 지원: 1544-9000
- 문서: `docs/키움 REST API 문서.xlsx`