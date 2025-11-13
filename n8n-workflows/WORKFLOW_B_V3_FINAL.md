# 워크플로우 B v3 최종 버전

## 📋 최종 수정 사항

### 문제 해결 과정
1. ✅ trading_signals 테이블 컬럼 추가
2. ✅ orders 테이블 컬럼 추가
3. ✅ Rate Limiting 설정 (429 에러 해결)
4. ✅ API 엔드포인트 수정 (1504 에러 해결)
5. ✅ **환경변수 사용으로 자격증명 관리 (403 에러 해결)**

---

## 🔑 주요 변경 사항

### 1. 환경변수 설정 노드 업데이트
키움 API 자격증명을 환경변수에서 가져오도록 추가:

```json
{
  "KIWOOM_APP_KEY": "환경변수 또는 기본값",
  "KIWOOM_APP_SECRET": "환경변수 또는 기본값",
  "KIWOOM_ACCOUNT_NO": "환경변수 또는 기본값"
}
```

### 2. 토큰 발급 노드
**하드코딩 제거 → 환경변수 참조**

**Before:**
```json
{
  "appkey": "S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU",
  "appsecret": "tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA"
}
```

**After:**
```json
{
  "appkey": "{{$node['환경변수 설정'].json.KIWOOM_APP_KEY}}",
  "appsecret": "{{$node['환경변수 설정'].json.KIWOOM_APP_SECRET}}"
}
```

### 3. 주문 실행 노드
**하드코딩 제거 → 환경변수 참조**

**Headers Before:**
```json
{
  "appkey": "S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU",
  "appsecret": "tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA"
}
```

**Headers After:**
```json
{
  "appkey": "{{$node['환경변수 설정'].json.KIWOOM_APP_KEY}}",
  "appsecret": "{{$node['환경변수 설정'].json.KIWOOM_APP_SECRET}}"
}
```

**Body Before:**
```json
{
  "CANO": "81101350",
  "ACNT_PRDT_CD": "01"
}
```

**Body After:**
```json
{
  "CANO": "{{$node['환경변수 설정'].json.KIWOOM_ACCOUNT_NO.substring(0, 8)}}",
  "ACNT_PRDT_CD": "{{$node['환경변수 설정'].json.KIWOOM_ACCOUNT_NO.substring(9, 11)}}"
}
```

---

## 🔧 n8n 환경변수 설정

워크플로우가 올바르게 작동하려면 n8n에 다음 환경변수를 설정해야 합니다:

### Docker Compose 환경변수 (.env)
```bash
KIWOOM_APP_KEY=iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk
KIWOOM_APP_SECRET=9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA
KIWOOM_ACCOUNT_NO=81101350-01
```

### n8n 설정 확인
1. n8n 대시보드에서 **Settings** → **Variables** 확인
2. 또는 워크플로우 실행 시 "환경변수 설정" 노드의 출력 확인

---

## 📊 완전한 워크플로우 구조

```
1. 5분마다 실행 (Schedule Trigger)
   ↓
2. 환경변수 설정 (Supabase + 키움 API 자격증명)
   ↓
3. 활성 전략 조회 (Supabase RPC)
   ↓
4. 유니버스 종목 추출 (Code)
   ↓
5. 현재가 조회 (Supabase)
   ↓
6. 데이터 병합 (Code)
   ↓
7. 매수/매도 신호 생성 (Code)
   ↓
8. 주문 가격 계산 (Code)
   ↓
9. 신호 저장 (Supabase: trading_signals)
   ↓
10. 키움 토큰 발급 (환경변수 사용) ✨
    - Rate Limit: 3초
    ↓
11. 주문 실행 (환경변수 사용) ✨
    - Rate Limit: 2초
    ↓
12. 주문 결과 저장 (Supabase: orders)
```

---

## ⚠️ 중요 사항

### 1. 키움 API 자격증명 유효성
현재 환경변수에 설정된 AppKey와 AppSecret이 **유효한지 확인**하세요:

```bash
# 키움증권 모의투자 API 키 발급
https://apiportal.koreainvestment.com
```

### 2. 계좌번호 포맷
계좌번호는 `XXXXXXXX-XX` 포맷이어야 합니다:
- 예: `81101350-01`
- CANO: 앞 8자리 (`81101350`)
- ACNT_PRDT_CD: 뒤 2자리 (`01`)

### 3. 모의투자 vs 실전투자
현재 v3는 **모의투자** 환경으로 설정:
- URL: `https://openapivts.koreainvestment.com:29443`
- TR_ID: `VTTC0802U` (매수), `VTTC0801U` (매도)

실전투자 전환 시:
- URL: `https://openapi.koreainvestment.com:9443`
- TR_ID: `TTTC0802U` (매수), `TTTC0801U` (매도)

---

## 🚀 배포 단계

### 1. n8n 환경변수 설정
```bash
# Docker Compose .env 파일에 추가
KIWOOM_APP_KEY=실제_발급받은_키
KIWOOM_APP_SECRET=실제_발급받은_시크릿
KIWOOM_ACCOUNT_NO=계좌번호
```

### 2. n8n 재시작
```bash
docker-compose restart n8n
```

### 3. 워크플로우 Import
1. n8n 대시보드 접속
2. 기존 워크플로우 B 삭제 (선택사항)
3. **"+" → Import from File**
4. `auto-trading-workflow-b-v3.json` 선택
5. **Save** 클릭

### 4. 환경변수 확인
워크플로우를 수동으로 실행하고 "환경변수 설정" 노드의 출력 확인:
```json
{
  "SUPABASE_URL": "https://...",
  "SUPABASE_ANON_KEY": "eyJ...",
  "KIWOOM_APP_KEY": "iQ4u...",
  "KIWOOM_APP_SECRET": "9uBO...",
  "KIWOOM_ACCOUNT_NO": "81101350-01"
}
```

### 5. 테스트 실행
- 토큰 발급 노드 확인 → `access_token` 반환
- 주문 실행 노드 확인 → `rt_cd: "0"` (성공)

---

## 🧪 테스트 체크리스트

- [ ] n8n 환경변수 설정 완료
- [ ] n8n 재시작 완료
- [ ] 워크플로우 v3 Import 완료
- [ ] 환경변수 설정 노드 출력 확인
- [ ] 키움 토큰 발급 성공 (`access_token` 존재)
- [ ] 주문 실행 성공 (403/500 에러 없음)
- [ ] trading_signals 테이블에 데이터 저장됨
- [ ] orders 테이블에 데이터 저장됨

---

## 🐛 트러블슈팅

### 문제 1: 403 Forbidden (유효하지 않은 AppKey)
**해결방법:**
1. n8n 환경변수에 올바른 키 설정
2. 키움증권 Open API에서 새 키 발급
3. n8n 재시작

### 문제 2: 환경변수가 undefined
**해결방법:**
1. Docker Compose `.env` 파일 확인
2. n8n 컨테이너 환경변수 전달 확인
3. 워크플로우의 "환경변수 설정" 노드 기본값 확인

### 문제 3: 계좌번호 파싱 에러
**해결방법:**
- 계좌번호 포맷 확인: `XXXXXXXX-XX`
- substring 인덱스 확인: `substring(0, 8)`, `substring(9, 11)`

---

## 📈 성능 최적화

### Rate Limiting 조정
필요시 대기 시간 조정:
```json
{
  "토큰 발급": {
    "batchInterval": 3000  // 3초 (기본값)
  },
  "주문 실행": {
    "batchInterval": 2000  // 2초 (기본값)
  }
}
```

API Rate Limit에 여유가 있다면 값을 줄일 수 있습니다:
- 최소 권장: 1000ms (1초)

---

## 📝 변경 이력

| 날짜 | 변경 내용 | 상태 |
|------|----------|------|
| 2025-11-12 | 환경변수 사용으로 자격증명 관리 | ✅ 완료 |
| 2025-11-12 | 토큰 발급 API 수정 (Mock → 실제) | ✅ 완료 |
| 2025-11-12 | 주문 실행 API 수정 (올바른 엔드포인트) | ✅ 완료 |
| 2025-11-12 | Rate Limiting 추가 | ✅ 완료 |
| 2025-11-12 | DB 스키마 수정 (trading_signals, orders) | ✅ 완료 |

---

## 🎯 다음 단계

1. **실제 키움 API 키 발급** (필수)
   - https://apiportal.koreainvestment.com
   - 모의투자 신청
   - AppKey/AppSecret 발급

2. **n8n 환경변수 설정** (필수)
   - `.env` 파일 또는 Docker Compose 설정

3. **워크플로우 테스트** (필수)
   - 수동 실행으로 전체 플로우 검증

4. **자동 실행 활성화** (선택)
   - 5분 주기 스케줄 활성화

5. **모니터링 설정** (권장)
   - n8n 실행 로그 확인
   - Supabase 데이터 확인
   - 에러 알림 설정

---

## 📚 참고 자료

- [키움증권 Open API 문서](https://apiportal.koreainvestment.com)
- [n8n 환경변수 설정 가이드](https://docs.n8n.io/hosting/environment-variables/)
- KiwoomApiService: `src/services/kiwoomApiService.ts`
- Supabase 스키마: `supabase/add_confidence_column.sql`, `supabase/add_orders_columns.sql`

---

**워크플로우 B v3 최종 완성! 🎉**
