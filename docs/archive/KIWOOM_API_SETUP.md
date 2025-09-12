# 키움증권 API 설정 가이드

## 1. API 키 발급

1. [한국투자증권 OpenAPI](https://apiportal.koreainvestment.com) 접속
2. 회원가입 및 로그인
3. 마이페이지 → API 신청
4. 앱 생성 및 API 키 발급
   - 앱 키 (App Key)
   - 앱 시크릿 (App Secret)

## 2. 환경 변수 설정

### backend/.env 파일 생성
```bash
cd backend
cp .env.example .env
```

### 실제 API 키 입력
```env
# 키움증권 API 설정
KIWOOM_APP_KEY=발급받은_앱_키
KIWOOM_APP_SECRET=발급받은_앱_시크릿
KIWOOM_ACCOUNT=계좌번호(하이픈없이)

# 모의투자/실전투자 선택
# 모의투자: https://openapivts.koreainvestment.com:29443
# 실전투자: https://openapi.koreainvestment.com:9443
KIWOOM_API_URL=https://openapivts.koreainvestment.com:29443
```

## 3. API 연동 테스트

```bash
cd backend
python test_kiwoom_real_api.py
```

## 4. 주의사항

- **모의투자 먼저 테스트**: 실전투자 전에 모의투자 환경에서 충분히 테스트
- **API 호출 제한**: 초당 20회, 분당 1000회 제한
- **토큰 유효기간**: 24시간 (자동 갱신 로직 구현됨)
- **시장 운영시간**: 평일 09:00 ~ 15:30 (정규시장)

## 5. 문제 해결

### 인증 실패
- App Key와 App Secret 확인
- API URL이 올바른지 확인 (모의/실전)
- API 사용 승인 상태 확인

### 데이터 조회 실패
- 종목코드 형식 확인 (6자리)
- 날짜 형식 확인 (YYYYMMDD)
- 계좌번호 확인

### 참고 문서
- [한국투자증권 OpenAPI 개발가이드](https://apiportal.koreainvestment.com/apiservice/oauth2)
- [REST API 레퍼런스](https://apiportal.koreainvestment.com/apiservice/)