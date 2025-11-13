# 워크플로우 B v4 최종 수정 사항

## 🎯 v4에서 수정된 내용

### 1. 환경변수 설정 노드 (환경변수 설정)

**변경 전 (v3):**
```json
{
  "KIWOOM_APP_KEY": "={{$env.KIWOOM_APP_KEY || 'iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk'}}",
  "KIWOOM_APP_SECRET": "={{$env.KIWOOM_APP_SECRET || '9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA'}}"
}
```

**변경 후 (v4):**
```json
{
  "KIWOOM_APP_KEY": "={{$env.KIWOOM_APP_KEY || 'S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'}}",
  "KIWOOM_APP_SECRET": "={{$env.KIWOOM_APP_SECRET || 'tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'}}"
}
```

**이유:**
- v38 워크플로우에서 작동 확인된 Mock API 자격증명 사용
- 실제 키움증권 API가 아닌 Mock API 사용

---

### 2. 키움 토큰 발급 노드 (키움 토큰 발급)

**변경 전 (v3):**
```json
{
  "url": "https://openapivts.koreainvestment.com:29443/oauth2/tokenP",
  "jsonBody": "={{JSON.stringify({
    grant_type: 'client_credentials',
    appkey: $node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY,
    appsecret: $node['환경변수 설정'].item(0).json.KIWOOM_APP_SECRET
  })}}"
}
```

**변경 후 (v4):**
```json
{
  "url": "https://mockapi.kiwoom.com/oauth2/token",
  "jsonBody": "={{ {
    grant_type: 'client_credentials',
    appkey: $node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY,
    secretkey: $node['환경변수 설정'].item(0).json.KIWOOM_APP_SECRET
  } }}"
}
```

**주요 변경:**
1. **URL 변경**: 실제 키움증권 API → Mock API
2. **필드명 변경**: `appsecret` → `secretkey`
3. **JSON.stringify() 제거**: `={{JSON.stringify({...})}}` → `={{ {...} }}`
   - JSON.stringify()를 사용하면 표현식이 문자열로 변환되어 평가되지 않음

**토큰 응답 필드:**
- Mock API는 `.token` 필드로 반환
- 실제 키움 API는 `.access_token` 필드로 반환

---

### 3. 주문 실행 노드 (주문 실행)

**변경 전 (v3):**
```json
{
  "url": "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash",
  "headers": {
    "authorization": "={{\"Bearer \" + $node[\"키움 토큰 발급\"].json.access_token}}",
    "appkey": "={{$node[\"환경변수 설정\"].item(0).json.KIWOOM_APP_KEY}}",
    "appsecret": "={{$node[\"환경변수 설정\"].item(0).json.KIWOOM_APP_SECRET}}",
    "tr_id": "={{$json.signal_type === 'buy' ? 'VTTC0802U' : 'VTTC0801U'}}"
  },
  "jsonBody": "={{JSON.stringify({
    CANO: $node['환경변수 설정'].item(0).json.KIWOOM_ACCOUNT_NO.substring(0, 8),
    ACNT_PRDT_CD: $node['환경변수 설정'].item(0).json.KIWOOM_ACCOUNT_NO.substring(9, 11),
    PDNO: $json.stock_code,
    ORD_DVSN: $json.order_method === 'MARKET' ? '01' : '00',
    ORD_QTY: '10',
    ORD_UNPR: String($json.order_price || 0)
  })}}"
}
```

**변경 후 (v4):**
```json
{
  "url": "https://mockapi.kiwoom.com/api/dostk/order",
  "headers": {
    "authorization": "={{\"Bearer \" + $node[\"키움 토큰 발급\"].json.token}}",
    "appkey": "={{$node[\"환경변수 설정\"].item(0).json.KIWOOM_APP_KEY}}",
    "secretkey": "={{$node[\"환경변수 설정\"].item(0).json.KIWOOM_APP_SECRET}}",
    "api-id": "={{$node['주문 가격 계산'].item(0).json.signal_type === 'buy' ? 'ka10005' : 'ka10006'}}"
  },
  "jsonBody": "={{ {
    stk_cd: $node['주문 가격 계산'].item(0).json.stock_code,
    ord_qty: '10',
    ord_prc: String($node['주문 가격 계산'].item(0).json.order_price || 0),
    ord_type: $node['주문 가격 계산'].item(0).json.order_method === 'MARKET' ? '1' : '0',
    ord_condition: '0'
  } }}"
}
```

**주요 변경:**
1. **URL 변경**: 실제 키움증권 주문 API → Mock API
2. **Headers 변경**:
   - `.access_token` → `.token` (토큰 필드명)
   - `appsecret` → `secretkey` (헤더명)
   - `tr_id` → `api-id` (헤더명)
   - TR_ID 값: `VTTC0802U`/`VTTC0801U` → `ka10005`/`ka10006`
3. **Body 필드 변경** (실제 키움 API → Mock API):
   - `CANO`, `ACNT_PRDT_CD` → 제거 (Mock API는 불필요)
   - `PDNO` → `stk_cd` (종목코드)
   - `ORD_DVSN` → `ord_type` (주문유형: `00`/`01` → `0`/`1`)
   - `ORD_QTY` → `ord_qty` (주문수량)
   - `ORD_UNPR` → `ord_prc` (주문가격)
   - `ord_condition` 추가 (주문조건)
4. **데이터 참조 변경**:
   - `$json.stock_code` → `$node['주문 가격 계산'].item(0).json.stock_code`
   - 이유: "키움 토큰 발급" 노드를 통과하면서 "주문 가격 계산" 노드의 데이터가 `$json`으로 전달되지 않음
5. **JSON.stringify() 제거**: 표현식 평가를 위해

---

### 4. 주문 결과 저장 노드 (주문 결과 저장)

**변경 전 (v3):**
```json
{
  "jsonBody": "={
    \"strategy_id\": {{JSON.stringify($node[\"주문 가격 계산\"].json.strategy_id)}},
    \"stock_code\": {{JSON.stringify($node[\"주문 가격 계산\"].json.stock_code)}},
    ...
  }"
}
```

**변경 후 (v4):**
```json
{
  "jsonBody": "={
    \"strategy_id\": {{JSON.stringify($node[\"주문 가격 계산\"].item(0).json.strategy_id)}},
    \"stock_code\": {{JSON.stringify($node[\"주문 가격 계산\"].item(0).json.stock_code)}},
    ...
  }"
}
```

**주요 변경:**
- `$node["노드명"].json` → `$node["노드명"].item(0).json`
- 이유: 노드 참조 시 배열 인덱스 명시 필요

---

## 🔍 왜 Mock API를 사용하나요?

1. **.env 파일의 키가 Mock API 키였음**
   - `KIWOOM_APP_KEY=S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU`
   - 이 키는 실제 키움증권 API가 아닌 Mock API 전용

2. **다른 워크플로우(v38)가 Mock API로 작동 중**
   - 사용자 확인: "다른 워크플로우에 이미 작동하고 있는 키값이다"
   - v38 워크플로우를 확인한 결과 Mock API 사용

3. **403 에러의 원인**
   - 실제 키움증권 API URL(`openapivts.koreainvestment.com`)에 Mock API 키를 사용
   - 키가 유효하지 않다는 에러 발생

---

## 📊 API 비교표

| 항목 | Mock API (v4) | 실제 키움증권 API (v3) |
|------|---------------|----------------------|
| **토큰 발급 URL** | `https://mockapi.kiwoom.com/oauth2/token` | `https://openapivts.koreainvestment.com:29443/oauth2/tokenP` |
| **주문 실행 URL** | `https://mockapi.kiwoom.com/api/dostk/order` | `https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash` |
| **토큰 Body 필드** | `secretkey` | `appsecret` |
| **토큰 응답 필드** | `.token` | `.access_token` |
| **주문 헤더** | `api-id` | `tr_id` |
| **주문 헤더 (키)** | `secretkey` | `appsecret` |
| **주문 API ID** | `ka10005` (매수), `ka10006` (매도) | `VTTC0802U` (매수), `VTTC0801U` (매도) |
| **주문 Body 필드** | `stk_cd`, `ord_qty`, `ord_prc`, `ord_type`, `ord_condition` | `CANO`, `ACNT_PRDT_CD`, `PDNO`, `ORD_DVSN`, `ORD_QTY`, `ORD_UNPR` |

---

## ✅ v4 체크리스트

- [x] 환경변수 노드: Mock API 자격증명으로 변경
- [x] 토큰 발급 노드: Mock API URL 및 `secretkey` 사용
- [x] 토큰 발급 노드: JSON.stringify() 제거
- [x] 주문 실행 노드: Mock API URL 사용
- [x] 주문 실행 노드: `.token` 필드 참조
- [x] 주문 실행 노드: Mock API Body 필드 사용
- [x] 주문 실행 노드: `$node['주문 가격 계산']` 참조
- [x] 주문 결과 저장 노드: `.item(0)` 추가

---

## 🚀 배포 방법

### 1. n8n에 Import

1. n8n 대시보드 접속
2. **"+" → "Import from File"**
3. `auto-trading-workflow-b-v4.json` 선택
4. **"Save"** 클릭

### 2. 환경변수 확인

워크플로우를 수동으로 실행하고 "환경변수 설정" 노드의 출력 확인:

```json
{
  "SUPABASE_URL": "https://hznkyaomtrpzcayayayh.supabase.co",
  "SUPABASE_ANON_KEY": "eyJ...",
  "KIWOOM_APP_KEY": "S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU",
  "KIWOOM_APP_SECRET": "tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA",
  "KIWOOM_ACCOUNT_NO": "81101350-01"
}
```

### 3. 테스트 실행

1. **"키움 토큰 발급" 노드 확인**
   - 출력에 `token` 필드가 있는지 확인
   - 에러 없이 성공하는지 확인

2. **"주문 실행" 노드 확인**
   - Mock API 응답이 정상적으로 반환되는지 확인
   - 에러 없이 성공하는지 확인

3. **"주문 결과 저장" 노드 확인**
   - Supabase `orders` 테이블에 데이터가 저장되는지 확인

---

## 🐛 알려진 제약사항

### Mock API 사용 시

1. **실제 주문 실행되지 않음**
   - Mock API는 실제 매매가 실행되지 않는 테스트 환경

2. **실전 전환 시 수정 필요**
   - 실제 키움증권 API로 전환하려면:
     - 키움증권 Open API 포털에서 새 키 발급
     - URL 변경 (Mock → 실제)
     - Body 필드 변경 (Mock 형식 → 실제 형식)
     - 헤더 필드명 변경 (`secretkey` → `appsecret`, `api-id` → `tr_id`)
     - 토큰 응답 필드 변경 (`.token` → `.access_token`)

---

## 📚 참고 문서

- Mock API 워크플로우: `auto-trading-with-capital-validation-v38.json`
- v3 변경사항: `WORKFLOW_B_V3_CHANGES.md`
- UI 설정 가이드: `WORKFLOW_B_V3_UI_SETUP_GUIDE.md`

---

**워크플로우 B v4 완성! 🎉**

이제 Mock API를 사용하여 안전하게 테스트할 수 있습니다.
