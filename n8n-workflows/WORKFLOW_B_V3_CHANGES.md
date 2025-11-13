# 워크플로우 B v3 변경사항

## 📋 주요 변경 사항 (v2 → v3)

### 문제점
v2에서 키움 Mock API 호출 시 다음 에러 발생:
```
잘못된 요청입니다[1504:해당 URI에서는 지원하는 API ID가 아닙니다.
API ID=ka10005, URI=/api/dostk/order]
```

### 원인
- **잘못된 API 엔드포인트**: `/api/dostk/order` (존재하지 않음)
- **잘못된 API ID**: `ka10005` (지원되지 않음)
- **잘못된 헤더**: `api-id` 대신 `tr_id` 사용해야 함

---

## 🔧 v3에서 수정된 주문 실행 노드

### 1. URL 변경
```diff
- https://mockapi.kiwoom.com/api/dostk/order
+ https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash
```

### 2. Request Body 변경
**Before (v2):**
```json
{
  "stk_cd": "005930",
  "ord_qty": "10",
  "ord_prc": "50000",
  "ord_type": "1",
  "ord_condition": "0"
}
```

**After (v3):**
```json
{
  "CANO": "81101350",           // 계좌번호 앞 8자리
  "ACNT_PRDT_CD": "01",         // 계좌번호 뒤 2자리
  "PDNO": "005930",             // 종목코드
  "ORD_DVSN": "00",             // 00: 지정가, 01: 시장가
  "ORD_QTY": "10",              // 주문수량
  "ORD_UNPR": "50000"           // 주문가격
}
```

### 3. Headers 변경
**Before (v2):**
```json
{
  "Content-Type": "application/json;charset=UTF-8",
  "authorization": "Bearer {token}",
  "api-id": "ka10005"
}
```

**After (v3):**
```json
{
  "Content-Type": "application/json;charset=UTF-8",
  "authorization": "Bearer {access_token}",
  "appkey": "S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU",
  "appsecret": "tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA",
  "tr_id": "VTTC0802U"  // 매수: VTTC0802U, 매도: VTTC0801U
}
```

---

## 📊 TR_ID (거래 ID) 매핑

| 거래 유형 | 모의투자 TR_ID | 실전투자 TR_ID |
|----------|---------------|---------------|
| 매수 | `VTTC0802U` | `TTTC0802U` |
| 매도 | `VTTC0801U` | `TTTC0801U` |

v3에서는 `signal_type`에 따라 자동으로 TR_ID를 선택합니다:
```javascript
signal_type === 'buy' ? 'VTTC0802U' : 'VTTC0801U'
```

---

## 🔑 토큰 발급 API 변경

### URL 변경
```diff
- https://mockapi.kiwoom.com/oauth2/token
+ https://openapivts.koreainvestment.com:29443/oauth2/tokenP
```

### Request Body 필드명 변경
```diff
{
  "grant_type": "client_credentials",
  "appkey": "...",
- "secretkey": "..."
+ "appsecret": "..."
}
```

### 응답 필드 변경
키움증권 API는 `access_token` 필드로 토큰을 반환합니다:

**v2에서 사용 (잘못됨):**
```javascript
$node["키움 토큰 발급"].json.token
```

**v3에서 사용 (올바름):**
```javascript
$node["키움 토큰 발급"].json.access_token
```

### 실제 응답 예시
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

---

## 📝 계좌번호 포맷

키움증권 계좌번호: `81101350-01`

- **CANO**: `81101350` (앞 8자리)
- **ACNT_PRDT_CD**: `01` (뒤 2자리)

현재 v3에서는 하드코딩되어 있습니다. 환경변수로 관리하려면:
```javascript
{
  "CANO": "{{$node['환경변수 설정'].json.KIWOOM_ACCOUNT_NO.substring(0, 8)}}",
  "ACNT_PRDT_CD": "{{$node['환경변수 설정'].json.KIWOOM_ACCOUNT_NO.substring(9, 11)}}"
}
```

---

## 🎯 버전별 비교

| 항목 | v1 | v2 | v3 |
|------|----|----|-----|
| **Rate Limiting** | ❌ 없음 | ✅ 있음 | ✅ 있음 |
| **토큰 대기 시간** | - | 2초 | 3초 |
| **주문 대기 시간** | - | 1초 | 2초 |
| **API 엔드포인트** | ❌ 잘못됨 | ❌ 잘못됨 | ✅ 올바름 |
| **API Headers** | ❌ 잘못됨 | ❌ 잘못됨 | ✅ 올바름 |
| **Request Body** | ❌ 잘못됨 | ❌ 잘못됨 | ✅ 올바름 |

---

## 🚀 v3 사용 방법

### 1. n8n에 Import
```
n8n 대시보드
→ "+" 버튼 (새 워크플로우)
→ "⋮" → "Import from File"
→ auto-trading-workflow-b-v3.json 선택
→ "Save" 클릭
```

### 2. 환경변수 확인
워크플로우의 "환경변수 설정" 노드에서 다음 값들을 확인하세요:
- `KIWOOM_ACCOUNT_NO`: 계좌번호
- `SUPABASE_URL`: Supabase URL
- `SUPABASE_ANON_KEY`: Supabase API Key

### 3. 토큰 발급 노드 확인
"키움 토큰 발급" 노드의 응답 필드명을 확인하세요:
- 응답에 `access_token` 필드가 있는지
- 없다면 `token` 또는 다른 필드명인지

### 4. 테스트 실행
- 수동으로 워크플로우 실행
- 각 노드의 실행 결과 확인
- 특히 "주문 실행" 노드에서 성공 응답이 오는지 확인

---

## ⚠️ 주의사항

### 1. 모의투자 vs 실전투자
현재 v3는 **모의투자 환경**으로 설정되어 있습니다:
```
https://openapivts.koreainvestment.com:29443
```

실전투자로 전환하려면:
- URL: `https://openapi.koreainvestment.com:9443`
- TR_ID: `TTTC0802U` (매수), `TTTC0801U` (매도)

### 2. 보안
워크플로우 JSON에 API Key와 Secret이 하드코딩되어 있습니다:
```json
"appkey": "S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU",
"appsecret": "tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA"
```

프로덕션 환경에서는:
- n8n Credentials로 관리
- 환경변수로 주입
- Supabase Vault 사용

### 3. 계좌번호
현재 하드코딩된 계좌번호: `81101350-01`

다른 계좌 사용 시 수정 필요합니다.

---

## 🧪 테스트 체크리스트

- [ ] 워크플로우 Import 성공
- [ ] 환경변수 설정 확인
- [ ] 토큰 발급 성공 (access_token 받음)
- [ ] 주문 실행 성공 (에러 1504 없음)
- [ ] trading_signals 테이블에 신호 저장됨
- [ ] orders 테이블에 주문 저장됨
- [ ] API 응답이 정상적으로 저장됨

---

## 📚 참고 문서

- 키움증권 Open API 문서
- KiwoomApiService: `src/services/kiwoomApiService.ts`
- 실전 워크플로우: `n8n-workflows/practical-workflow.json`

---

## 📝 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-11-12 | v3 | API 엔드포인트 및 헤더 수정, 올바른 키움 API 사용 | Claude Code |
| 2025-11-12 | v2 | Rate Limiting 추가 (토큰 3초, 주문 2초) | Claude Code |
| 2025-11-12 | v1 | 초기 버전 | - |
