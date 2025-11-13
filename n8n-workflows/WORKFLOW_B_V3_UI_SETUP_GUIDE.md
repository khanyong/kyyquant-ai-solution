# 워크플로우 B v3 - UI 설정 가이드 (최종 해결책)

## 🔍 문제 원인

n8n에서 HTTP Request 노드의 Body를 "JSON" 형식으로 지정하고 `JSON.stringify()`를 사용하면, 표현식이 문자열 리터럴로 변환되어 평가되지 않습니다.

**잘못된 방식:**
```javascript
={{JSON.stringify({ appkey: $node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY })}}
```

**결과:**
```json
{
  "appkey": "$node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY"
}
```
표현식이 문자열로 전송됩니다!

---

## ✅ 올바른 설정 방법

### 방법 1: "Using Fields Below" 사용 (권장)

이 방법이 가장 안전하고 직관적입니다.

#### 1️⃣ 키움 토큰 발급 노드

**URL:**
```
https://openapivts.koreainvestment.com:29443/oauth2/tokenP
```

**Method:** POST

**Headers:**
| Name | Value | Type |
|------|-------|------|
| `Content-Type` | `application/json;charset=UTF-8` | Fixed |

**Body Parameters:**
- **Specify Body:** 드롭다운에서 **"Using Fields Below"** 선택
- **Add Parameter** 클릭하여 다음 필드 추가:

| Name | Value | Type |
|------|-------|------|
| `grant_type` | `client_credentials` | Fixed |
| `appkey` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY}}` | Expression |
| `appsecret` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_SECRET}}` | Expression |

**Options → Batching:**
- Batch Size: `1`
- Batch Interval: `3000` ms

---

#### 2️⃣ 주문 실행 노드

**URL:**
```
https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash
```

**Method:** POST

**Headers:**
| Name | Value | Type |
|------|-------|------|
| `Content-Type` | `application/json;charset=UTF-8` | Fixed |
| `authorization` | `={{\"Bearer \" + $node[\"키움 토큰 발급\"].json.access_token}}` | Expression |
| `appkey` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY}}` | Expression |
| `appsecret` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_SECRET}}` | Expression |
| `tr_id` | `={{$json.signal_type === 'buy' ? 'VTTC0802U' : 'VTTC0801U'}}` | Expression |

**Body Parameters:**
- **Specify Body:** 드롭다운에서 **"Using Fields Below"** 선택
- **Add Parameter** 클릭하여 다음 필드 추가:

| Name | Value | Type |
|------|-------|------|
| `CANO` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_ACCOUNT_NO.substring(0, 8)}}` | Expression |
| `ACNT_PRDT_CD` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_ACCOUNT_NO.substring(9, 11)}}` | Expression |
| `PDNO` | `={{$json.stock_code}}` | Expression |
| `ORD_DVSN` | `={{$json.order_method === 'MARKET' ? '01' : '00'}}` | Expression |
| `ORD_QTY` | `10` | Fixed |
| `ORD_UNPR` | `={{String($json.order_price || 0)}}` | Expression |

**Options → Batching:**
- Batch Size: `1`
- Batch Interval: `2000` ms

---

### 방법 2: JSON 형식 사용 (고급)

"Using Fields Below" 대신 JSON 포맷을 직접 작성하려면:

#### 키움 토큰 발급 노드 Body

**Specify Body:** "JSON" 선택

**JSON Body:**
```json
={
  "grant_type": "client_credentials",
  "appkey": {{$node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY}},
  "appsecret": {{$node['환경변수 설정'].item(0).json.KIWOOM_APP_SECRET}}
}
```

⚠️ **주의:**
- `={{ }}` 표현식 안에서 JSON 객체 리터럴을 사용
- `JSON.stringify()` 사용하지 않음
- 각 필드 값은 `{{ }}` 안에서 직접 참조

---

## 🧪 테스트 방법

### 1단계: 환경변수 설정 노드 테스트

1. "환경변수 설정" 노드만 선택
2. **Execute node** 클릭
3. 출력 확인:

```json
{
  "SUPABASE_URL": "https://...",
  "SUPABASE_ANON_KEY": "eyJ...",
  "KIWOOM_APP_KEY": "iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk",
  "KIWOOM_APP_SECRET": "9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA",
  "KIWOOM_ACCOUNT_NO": "81101350-01"
}
```

✅ 모든 값이 제대로 출력되는지 확인

---

### 2단계: 키움 토큰 발급 노드 테스트

1. "환경변수 설정" → "키움 토큰 발급" 노드까지 선택
2. **Execute node** 클릭
3. 요청 본문 확인 (n8n UI에서 "Executed Workflows" → "Details" → "Parameters" 확인):

```json
{
  "grant_type": "client_credentials",
  "appkey": "iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk",
  "appsecret": "9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA"
}
```

✅ 값들이 실제 문자열로 치환되어 있어야 함 (표현식이 평가됨)

4. 응답 확인:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

✅ `access_token` 필드가 존재하고 JWT 토큰이 반환되어야 함

---

## 🐛 트러블슈팅

### 문제 1: 표현식이 문자열로 전송됨

**증상:**
```json
{
  "appkey": "$node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY"
}
```

**원인:**
- Body에서 "JSON" 형식 사용 시 `JSON.stringify()` 사용
- 또는 Field Type이 "Fixed"로 설정됨

**해결:**
- **방법 A:** "Using Fields Below"로 변경하고 각 필드를 Expression 타입으로 설정
- **방법 B:** JSON 형식 사용 시 `JSON.stringify()` 제거하고 객체 리터럴 사용

---

### 문제 2: 환경변수 노드가 비어있음

**증상:**
"환경변수 설정" 노드 실행 시 출력이 비어있거나 에러 발생

**원인:**
n8n Set 노드가 올바르게 구성되지 않음

**해결:**
1. "환경변수 설정" 노드 클릭
2. **Mode:** "Manual" 또는 "Automatically Map"
3. **Add Value** → **String** 클릭하여 다음 추가:

| Name | Value |
|------|-------|
| `SUPABASE_URL` | `https://hznkyaomtrpzcayayayh.supabase.co` |
| `SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `KIWOOM_APP_KEY` | `iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk` |
| `KIWOOM_APP_SECRET` | `9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA` |
| `KIWOOM_ACCOUNT_NO` | `81101350-01` |

⚠️ **또는** 환경변수에서 가져오기:
| Name | Value | Type |
|------|-------|------|
| `KIWOOM_APP_KEY` | `={{$env.KIWOOM_APP_KEY \|\| 'iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk'}}` | Expression |

---

### 문제 3: 403 Forbidden (유효하지 않은 AppKey)

**원인:**
- 키움증권에서 발급받은 AppKey가 만료되었거나 잘못됨
- 현재 사용 중인 키: `iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk`

**해결:**
1. 키움증권 Open API 포털에서 새 키 발급:
   - https://apiportal.koreainvestment.com
   - 모의투자 신청
   - AppKey/AppSecret 발급
2. "환경변수 설정" 노드의 값 업데이트
3. 또는 n8n 환경변수 설정:
   ```bash
   # Docker .env 파일
   KIWOOM_APP_KEY=새로_발급받은_키
   KIWOOM_APP_SECRET=새로_발급받은_시크릿
   ```

---

### 문제 4: 429 Too Many Requests

**원인:**
API 호출이 너무 빠르게 연속으로 발생

**해결:**
Options → Batching 설정 확인:
- 토큰 발급: Batch Interval `3000` ms (3초)
- 주문 실행: Batch Interval `2000` ms (2초)

필요시 값을 더 늘릴 것 (예: 5000ms)

---

## 📋 완전한 체크리스트

### ✅ 환경변수 설정 노드
- [ ] Set 노드 타입 사용
- [ ] 5개 값 모두 설정 (SUPABASE_URL, SUPABASE_ANON_KEY, KIWOOM_APP_KEY, KIWOOM_APP_SECRET, KIWOOM_ACCOUNT_NO)
- [ ] 노드 실행 시 모든 값이 출력됨

### ✅ 키움 토큰 발급 노드
- [ ] URL: `https://openapivts.koreainvestment.com:29443/oauth2/tokenP`
- [ ] Method: POST
- [ ] Header: `Content-Type: application/json;charset=UTF-8`
- [ ] Body: "Using Fields Below" 또는 올바른 JSON 형식
- [ ] `grant_type`, `appkey`, `appsecret` 필드 설정
- [ ] Expression 필드는 Type을 "Expression"으로 설정
- [ ] Batching: 3000ms
- [ ] 실행 시 `access_token` 반환됨

### ✅ 주문 실행 노드
- [ ] URL: `https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash`
- [ ] Method: POST
- [ ] Headers: `Content-Type`, `authorization`, `appkey`, `appsecret`, `tr_id`
- [ ] Body: "Using Fields Below" 또는 올바른 JSON 형식
- [ ] `CANO`, `ACNT_PRDT_CD`, `PDNO`, `ORD_DVSN`, `ORD_QTY`, `ORD_UNPR` 필드 설정
- [ ] Batching: 2000ms
- [ ] 실행 시 에러 없이 성공

---

## 🎯 최종 확인

전체 워크플로우를 수동으로 실행하고:

1. **환경변수 설정** → 5개 값 출력 확인
2. **키움 토큰 발급** → `access_token` 반환 확인
3. **주문 실행** → 성공 응답 확인 (rt_cd: "0")

모든 노드가 성공하면 자동 실행 (스케줄 트리거) 활성화!

---

**이 가이드를 따르면 JSON 파싱 에러와 표현식 평가 문제를 모두 해결할 수 있습니다!** 🎉
