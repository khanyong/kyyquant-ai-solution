# kw_price_current 테이블 종목명 표시 수정 가이드

## 🔴 문제점
- 화면에 종목명 대신 종목코드가 표시됨
- `kw_stock_master` 테이블에 11개 종목만 있어 조인 실패
- 등락률이 모두 0%로 표시됨

## ✅ 해결 방법

### 1. Supabase에서 stock_name 컬럼 추가

```sql
-- supabase/add_stock_name_to_kw_price_current.sql 실행
ALTER TABLE kw_price_current
ADD COLUMN IF NOT EXISTS stock_name VARCHAR(100);
```

### 2. n8n 워크플로우 수정

**파일**: `auto-trading-with-capital-validation-v18.json`

#### 📍 수정 위치: "Supabase에 시세 저장" 노드

**현재 코드** (line 293 근처):
```json
{
  "jsonBody": "={\n  \"stock_code\": {{JSON.stringify($json.stock_code)}},\n  \"current_price\": {{$json.current_price}},\n  \"change_price\": {{$json.change_price}},\n  \"change_rate\": {{$json.change_rate}},\n  \"volume\": {{$json.volume || 0}},\n  \"high_52w\": {{$json.sel_price || 0}},\n  \"low_52w\": {{$json.buy_price || 0}},\n  \"market_cap\": 0\n}"
}
```

**수정 후**:
```json
{
  "jsonBody": "={\n  \"stock_code\": {{JSON.stringify($json.stock_code)}},\n  \"stock_name\": {{JSON.stringify($json.stock_name || $json.stock_code)}},\n  \"current_price\": {{$json.current_price}},\n  \"change_price\": {{$json.change_price}},\n  \"change_rate\": {{$json.change_rate}},\n  \"volume\": {{$json.volume || 0}},\n  \"high_52w\": {{$json.sel_price || 0}},\n  \"low_52w\": {{$json.buy_price || 0}},\n  \"market_cap\": 0\n}"
}
```

**변경사항**: `\"stock_name\": {{JSON.stringify($json.stock_name || $json.stock_code)}},` 추가

### 3. stock_name 필드 확인

n8n 워크플로우의 "신호 생성" 노드(line 227)에서 이미 `stock_name`을 추출하고 있습니다:

```javascript
// 종목명은 종목코드로 대체 (키움 API에서 제공하지 않음)
const stockName = kiwoomResponse.stk_nm || stockCode;
```

**주의**: 주석에는 "제공하지 않음"이라고 되어 있지만, 실제로는 `stk_nm` 필드가 있습니다.

### 4. 키움 API 응답 구조

키움 REST API `/uapi/domestic-stock/v1/quotations/inquire-asking-price` 응답:

```json
{
  "output": {
    "stk_nm": "삼성전자",        // ← 종목명
    "stck_prpr": "70000",       // 현재가
    "sel_fpr_bid": "70100",     // 매도호가
    "buy_fpr_bid": "69900",     // 매수호가
    "sel_fpr_req": "1000",      // 매도호가 잔량
    "buy_fpr_req": "2000"       // 매수호가 잔량
  }
}
```

## 📝 적용 순서

1. **Supabase에서 SQL 실행**
   ```bash
   # Supabase Dashboard > SQL Editor에서 실행
   supabase/add_stock_name_to_kw_price_current.sql
   ```

2. **n8n 워크플로우 수정**
   - n8n Dashboard 접속
   - "자동매매 모니터링 v18" 워크플로우 열기
   - "Supabase에 시세 저장" HTTP Request 노드 찾기
   - `jsonBody`에 `stock_name` 필드 추가
   - 저장 및 활성화

3. **MarketMonitor.tsx 수정** (선택사항)
   - `kw_stock_master` 조인 로직 제거 가능
   - `stock_name`을 직접 사용

## 🧪 테스트

1. n8n 워크플로우 수동 실행
2. Supabase에서 데이터 확인:
   ```sql
   SELECT stock_code, stock_name, current_price, change_rate
   FROM kw_price_current
   ORDER BY updated_at DESC
   LIMIT 10;
   ```
3. 화면에서 종목명 정상 표시 확인

## 🎯 예상 결과

- ✅ 종목명 정상 표시 (예: "삼성전자", "SK하이닉스")
- ✅ 등락률 계산 정상화 (현재 0%로 고정된 문제 해결)
- ✅ 상승/하락 종목 수 정상 집계
