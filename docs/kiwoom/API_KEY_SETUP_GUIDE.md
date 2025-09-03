# 📌 키움증권 API 키 설정 가이드

## 🔑 API 키 입력 위치

### 1. `.env` 파일 위치
```
D:\Dev\auto_stock\.env
```

### 2. 현재 설정된 키 (예시 값)
```env
# ===== 키움증권 API 설정 =====
KIWOOM_APP_KEY=여기에_실제_APP_KEY_입력
KIWOOM_APP_SECRET=여기에_실제_APP_SECRET_입력
KIWOOM_ACCOUNT_NO=여기에_계좌번호_입력
KIWOOM_IS_DEMO=true  # 모의투자: true, 실전: false
```

## 📋 API 키 발급 방법

### OpenAPI+ (실시간 거래용)
1. **키움증권 홈페이지 접속**
   - https://www.kiwoom.com/
   
2. **OpenAPI 신청**
   - 로그인 → OpenAPI → 사용신청
   - 모의투자 신청 (테스트용)
   - 실전투자 신청 (실거래용)

3. **계좌번호 확인**
   - KOA Studio 실행
   - 로그인 후 계좌번호 확인

### REST API (클라우드/자동화용)
1. **한국투자증권 개발자센터**
   - https://apiportal.koreainvestment.com/
   
2. **회원가입 및 앱 등록**
   - 회원가입 → 마이페이지
   - 앱 등록 → APP KEY, APP SECRET 발급
   
3. **API 키 종류**
   - 모의투자용 키 (테스트)
   - 실전투자용 키 (실거래)

## ⚙️ 설정 방법

### 방법 1: 직접 편집
```bash
# .env 파일 열기
notepad .env

# 다음 항목 수정
KIWOOM_APP_KEY=PS123456-7890-abcd-efgh-ijklmnopqrst
KIWOOM_APP_SECRET=1234567890abcdefghijklmnopqrstuvwxyz=
KIWOOM_ACCOUNT_NO=12345678-01
```

### 방법 2: 자동 설정 스크립트
```bash
cd backend
python setup_api_keys.py
```

### 방법 3: 환경 변수 설정
```powershell
# Windows PowerShell
$env:KIWOOM_APP_KEY="your_app_key"
$env:KIWOOM_APP_SECRET="your_app_secret"
$env:KIWOOM_ACCOUNT_NO="your_account"
```

## 🔍 API URL 설정

### 모의투자
```env
# OpenAPI+ 모의투자
KIWOOM_IS_DEMO=true

# REST API 모의투자
KIWOOM_API_URL=https://openapivts.koreainvestment.com:29443
```

### 실전투자
```env
# OpenAPI+ 실전
KIWOOM_IS_DEMO=false

# REST API 실전
KIWOOM_API_URL=https://openapi.koreainvestment.com:9443
```

## ✅ 설정 확인

### 1. 테스트 스크립트 실행
```bash
cd backend
python test_api_connection.py
```

### 2. 예상 출력
```
[SUCCESS] REST API 키 확인됨
[SUCCESS] OpenAPI+ 계좌 확인됨
[SUCCESS] API 연결 테스트 통과
```

## ⚠️ 주의사항

1. **API 키 보안**
   - `.env` 파일을 절대 Git에 커밋하지 마세요
   - API 키를 외부에 노출하지 마세요

2. **계좌번호 형식**
   - 일반: 12345678-01
   - 모의: 12345678-01 (동일 형식)

3. **API 제한**
   - REST API: 초당 20회
   - OpenAPI+: 초당 5회 (조회), 초당 2회 (주문)

## 🆘 문제 해결

### API 키가 작동하지 않을 때
1. 키 발급 후 10분 대기 (활성화 시간)
2. 모의/실전 구분 확인
3. IP 등록 여부 확인 (REST API)

### 계좌번호를 모를 때
1. KOA Studio 실행
2. 로그인 → 계좌 정보 확인
3. 또는 키움증권 HTS에서 확인

## 📞 지원

- 키움증권 고객센터: 1544-9000
- 한국투자증권 API 지원: 1544-5000
- 개발자 포럼: https://apiportal.koreainvestment.com/community