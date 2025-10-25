# 종목명 표시 문제 디버깅 가이드

## 🔴 발견된 문제

`kw_price_current` 테이블의 `stock_name` 컬럼에 **종목코드가 그대로 저장**됨

```javascript
// 실제 데이터
{code: '331660', name: '331660'}  // ← 종목명 아닌 종목코드
{code: '222670', name: '222670'}
```

## 🔍 원인 분석

### 1. n8n 워크플로우의 로직

**신호 생성 노드** (Line 227):
```javascript
const stockName = kiwoomResponse.stk_nm || stockCode;
```

- `stk_nm` 필드가 비어있으면 `stockCode`로 fallback
- 결과: 종목코드가 `stock_name`에 저장됨

### 2. 키움 API 응답 구조 문제

**가능성 1**: 호가 조회 API는 종목명을 제공하지 않음

키움 REST API 엔드포인트 확인 필요:
- `/uapi/domestic-stock/v1/quotations/inquire-asking-price` ← 현재 사용 중
- `/uapi/domestic-stock/v1/quotations/inquire-price` ← 시세 조회 (종목명 포함?)

**가능성 2**: Mock API 사용 중

v19 워크플로우에서:
```javascript
"url": "https://mockapi.kiwoom.com/oauth2/token"
```

Mock API는 실제 데이터를 제공하지 않을 수 있음.

## ✅ 해결 방법

### 방법 1: 키움 API 엔드포인트 확인 및 변경

**현재 사용 중인 API**:
```
GET /uapi/domestic-stock/v1/quotations/inquire-asking-price
```

**응답 필드 확인**:
- `stk_nm` 또는 `hts_kor_isnm` 필드 존재 여부
- 실제 응답 예시 필요

**대안 API**:
```
GET /uapi/domestic-stock/v1/quotations/inquire-price
Parameters: FID_INPUT_ISCD={종목코드}
```

응답 예시:
```json
{
  "output": {
    "stk_nm": "삼성전자",          // ← 종목명
    "stck_prpr": "70000",          // 현재가
    "prdy_vrss": "+500",           // 전일대비
    "prdy_ctrt": "0.72"            // 전일대비율
  }
}
```

### 방법 2: 별도 종목명 조회 API 호출

n8n 워크플로우에 노드 추가:

1. **종목 마스터 조회 API 호출**
   ```
   GET /uapi/domestic-stock/v1/quotations/search-stock-info
   ```

2. **Supabase kw_stock_master 테이블 활용**
   - 1회만 전체 종목 마스터 다운로드
   - n8n에서 조인하여 사용

### 방법 3: 현재가 조회 API로 변경

**수정 위치**: n8n 워크플로우 "호가 조회" 노드

**Before**:
```json
{
  "method": "GET",
  "url": "https://openapi.kiwoom.com:9443/uapi/domestic-stock/v1/quotations/inquire-asking-price",
  "qs": {
    "fid_cond_mrkt_div_code": "J",
    "fid_input_iscd": "{{$json.stock_code}}"
  }
}
```

**After**:
```json
{
  "method": "GET",
  "url": "https://openapi.kiwoom.com:9443/uapi/domestic-stock/v1/quotations/inquire-price",
  "qs": {
    "fid_cond_mrkt_div_code": "J",
    "fid_input_iscd": "{{$json.stock_code}}"
  },
  "headers": {
    "tr_id": "FHKST01010100"
  }
}
```

**응답 파싱 수정**:
```javascript
// 신호 생성 노드
const stockName = kiwoomResponse.output?.stk_nm
  || kiwoomResponse.stk_nm
  || stockCode;
```

## 🧪 테스트 방법

### 1. n8n 실행 로그 확인

1. n8n Dashboard → "자동매매 모니터링 v19"
2. Executions 탭
3. 최근 실행 선택
4. "호가 조회" 노드의 Output 확인
5. `stk_nm` 필드 값 확인

### 2. 키움 API 직접 테스트

```bash
# PowerShell
$token = "YOUR_ACCESS_TOKEN"
$appKey = "YOUR_APP_KEY"
$appSecret = "YOUR_APP_SECRET"

curl -X GET "https://openapi.kiwoom.com:9443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd=005930" `
  -H "authorization: Bearer $token" `
  -H "appkey: $appKey" `
  -H "appsecret: $appSecret" `
  -H "tr_id: FHKST01010100"
```

### 3. Supabase에서 최신 데이터 확인

```sql
-- v19 실행 후 최신 데이터 확인
SELECT
  stock_code,
  stock_name,
  current_price,
  updated_at
FROM kw_price_current
WHERE updated_at > NOW() - INTERVAL '10 minutes'
ORDER BY updated_at DESC
LIMIT 10;
```

**예상 결과**:
```
stock_code | stock_name | current_price | updated_at
-----------|------------|---------------|------------------
005930     | 삼성전자   | 70000         | 2025-10-24 13:45:00
```

## 📝 다음 단계

1. **n8n 실행 로그에서 키움 API 응답 확인**
2. **`stk_nm` 필드 존재 여부 확인**
3. **필드가 없으면 API 엔드포인트 변경**
4. **Mock API 사용 중이면 실제 API로 변경**

## 🔧 긴급 임시 조치

테스트를 위해 주요 종목만 수동 업데이트:

```sql
-- supabase/manual_update_stock_names.sql 실행
UPDATE kw_price_current
SET stock_name = CASE stock_code
  WHEN '005930' THEN '삼성전자'
  WHEN '000660' THEN 'SK하이닉스'
  -- ... (10개 종목)
END;
```

프론트엔드를 새로고침하면 해당 종목들은 정상 표시됨.
