# 워크플로우 B v3 - UI에서 수정하는 방법

JSON 파싱 에러가 계속 발생하는 경우, n8n UI에서 직접 수정하는 것이 가장 빠릅니다.

## 🔧 수정 방법

### 1. 키움 토큰 발급 노드 수정

1. **노드 클릭** → "키움 토큰 발급" 노드 선택
2. **Body Parameters** 섹션
3. **Specify Body** 드롭다운에서 **"Using Fields Below"** 선택
4. **Add Parameter** 클릭하여 다음 필드 추가:

| Name | Value |
|------|-------|
| `grant_type` | `client_credentials` |
| `appkey` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY}}` |
| `appsecret` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_SECRET}}` |

### 2. 주문 실행 노드 수정

1. **노드 클릭** → "주문 실행" 노드 선택
2. **Body Parameters** 섹션
3. **Specify Body** 드롭다운에서 **"Using Fields Below"** 선택
4. **Add Parameter** 클릭하여 다음 필드 추가:

| Name | Value |
|------|-------|
| `CANO` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_ACCOUNT_NO.substring(0, 8)}}` |
| `ACNT_PRDT_CD` | `={{$node['환경변수 설정'].item(0).json.KIWOOM_ACCOUNT_NO.substring(9, 11)}}` |
| `PDNO` | `={{$json.stock_code}}` |
| `ORD_DVSN` | `={{$json.order_method === 'MARKET' ? '01' : '00'}}` |
| `ORD_QTY` | `10` |
| `ORD_UNPR` | `={{String($json.order_price \|\| 0)}}` |

---

## 🎯 대체 방법: 하드코딩된 값으로 테스트

환경변수가 작동하지 않는 경우, 임시로 하드코딩된 값을 사용하여 테스트:

### 키움 토큰 발급 노드

```json
{
  "grant_type": "client_credentials",
  "appkey": "iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk",
  "appsecret": "9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA"
}
```

n8n UI에서:
1. **Specify Body** → **"JSON"** 선택
2. 위 JSON을 직접 붙여넣기 (표현식 없이)

### 주문 실행 노드

**Headers:**
- `appkey`: `iQ4uqUvLr7IAXTnOv1a7_156IHhIu9l8aiXiBDbSsSk`
- `appsecret`: `9uBOq4tEp_DQO1-L6jBiGrFVD7yr-FeSZRQXFd2wmUA`

**Body:**
```json
{
  "CANO": "81101350",
  "ACNT_PRDT_CD": "01",
  "PDNO": "={{$json.stock_code}}",
  "ORD_DVSN": "={{$json.order_method === 'MARKET' ? '01' : '00'}}",
  "ORD_QTY": "10",
  "ORD_UNPR": "={{String($json.order_price || 0)}}"
}
```

---

## 🐛 트러블슈팅

### 문제: 환경변수가 undefined

**원인:**
- n8n 환경변수가 설정되지 않음
- 워크플로우의 "환경변수 설정" 노드가 실행되지 않음

**해결:**
1. n8n 컨테이너 환경변수 확인:
   ```bash
   docker exec n8n env | grep KIWOOM
   ```

2. 워크플로우의 "환경변수 설정" 노드 수동 실행하여 출력 확인

3. 임시로 하드코딩된 값 사용 (위 참고)

### 문제: JSON 파싱 에러 계속 발생

**해결:**
1. **Specify Body**를 **"JSON"**에서 **"Using Fields Below"**로 변경
2. 각 필드를 개별적으로 설정
3. 표현식에서 따옴표 이스케이핑 제거

---

## 📝 완성된 워크플로우 설정

### 키움 토큰 발급 노드

**URL:** `https://openapivts.koreainvestment.com:29443/oauth2/tokenP`

**Method:** POST

**Headers:**
- `Content-Type`: `application/json;charset=UTF-8`

**Body (Using Fields Below):**
- `grant_type`: `client_credentials` (Plain text)
- `appkey`: `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY}}` (Expression)
- `appsecret`: `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_SECRET}}` (Expression)

**Options:**
- Batching: Batch Size `1`, Batch Interval `3000` ms

---

### 주문 실행 노드

**URL:** `https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash`

**Method:** POST

**Headers:**
- `Content-Type`: `application/json;charset=UTF-8`
- `authorization`: `={{"Bearer " + $json.access_token}}` (Expression)
- `appkey`: `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_KEY}}` (Expression)
- `appsecret`: `={{$node['환경변수 설정'].item(0).json.KIWOOM_APP_SECRET}}` (Expression)
- `tr_id`: `={{$json.signal_type === 'buy' ? 'VTTC0802U' : 'VTTC0801U'}}` (Expression)

**Body (Using Fields Below):**
- `CANO`: `={{$node['환경변수 설정'].item(0).json.KIWOOM_ACCOUNT_NO.substring(0, 8)}}` (Expression)
- `ACNT_PRDT_CD`: `={{$node['환경변수 설정'].item(0).json.KIWOOM_ACCOUNT_NO.substring(9, 11)}}` (Expression)
- `PDNO`: `={{$json.stock_code}}` (Expression)
- `ORD_DVSN`: `={{$json.order_method === 'MARKET' ? '01' : '00'}}` (Expression)
- `ORD_QTY`: `10` (Plain text)
- `ORD_UNPR`: `={{String($json.order_price || 0)}}` (Expression)

**Options:**
- Batching: Batch Size `1`, Batch Interval `2000` ms

---

## 🚀 빠른 테스트

1. **"환경변수 설정" 노드만 실행**
   - 출력에서 `KIWOOM_APP_KEY`, `KIWOOM_APP_SECRET`, `KIWOOM_ACCOUNT_NO` 확인
   - 값이 제대로 나오는지 확인

2. **"키움 토큰 발급" 노드까지 실행**
   - `access_token` 필드가 있는지 확인
   - 에러 없이 성공하는지 확인

3. **전체 워크플로우 실행**
   - 모든 노드가 순서대로 성공하는지 확인

---

이 가이드를 따라 n8n UI에서 직접 수정하면 JSON 파싱 에러를 피할 수 있습니다!
