# 키움증권 API 정보

## 🔑 모의투자 계정 정보

### API 키
- **App Key**: `iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk`
- **Secret Key**: `9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA`

### 계좌 정보
- **계좌번호**: `81101350`
- **계좌 유형**: 모의투자 (Demo)

## ⚙️ 환경 변수 설정

`.env` 파일에 다음과 같이 설정:

```bash
# 키움증권 API 설정 (모의투자)
KIWOOM_APP_KEY=iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk
KIWOOM_APP_SECRET=9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA
KIWOOM_ACCOUNT_NO=81101350
KIWOOM_IS_DEMO=true
```

## 📌 주의사항

1. **모의투자 환경**: 현재 설정은 모의투자용입니다
2. **실전 전환 시**:
   - 실전 App Key/Secret 발급 필요
   - `KIWOOM_IS_DEMO=false`로 변경
   - 실제 계좌번호로 변경

3. **API 제한사항**:
   - 1초당 최대 5회 호출
   - 1분당 최대 100회 호출
   - 동시 접속 제한 있음

## 🔗 관련 URL

- 키움증권 OpenAPI+: https://apiplus.kiwoom.com
- 개발 가이드: https://apiplus.kiwoom.com/howto/index
- KIS Developers: https://apiportal.koreainvestment.com

## 📝 테스트 방법

```bash
# API 연결 테스트
curl http://192.168.50.150:8080/api/market/test

# 계좌 정보 조회
curl http://192.168.50.150:8080/api/account/info

# 주식 목록 조회
curl http://192.168.50.150:8080/api/market/stocks
```

## ⚠️ 보안 주의

- API 키를 절대 공개 저장소에 커밋하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있어야 합니다
- 프로덕션 환경에서는 환경 변수로 관리하세요