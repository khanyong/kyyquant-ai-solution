# 등락률 계산 문제 해결 가이드

## 🔴 문제 상황

**증상**: 모든 종목의 등락률이 0.00%로 표시
- 상승 종목: 0개
- 하락 종목: 0개
- 보합 종목: 1000개 (전체)

## 🔍 원인 분석

n8n 워크플로우의 "등락가/률 계산" 노드에서:

```javascript
// kw_price_daily에서 최근 종가 조회 (전일 종가)
const response = await fetch(
  `${supabaseUrl}/rest/v1/kw_price_daily?stock_code=eq.${stockCode}&select=close&order=trade_date.desc&limit=1`,
  ...
);

const data = await response.json();
const previousClose = data && data.length > 0 ? parseFloat(data[0].close) : currentPrice;

// 등락가 및 등락률 계산
const changePrice = currentPrice - previousClose;
const changeRate = previousClose > 0 ? ((changePrice / previousClose) * 100) : 0;
```

**문제점**:
1. `kw_price_daily` 테이블에 데이터가 없음
2. 조회 실패 시 `previousClose = currentPrice`로 설정
3. 결과: `changePrice = 0`, `changeRate = 0`

## ✅ 해결 방법

### 방법 1: 키움 API에서 직접 전일 종가 가져오기 (권장)

키움 REST API 응답에는 전일 대비 정보가 포함되어 있습니다:

**키움 API 응답 구조**:
```json
{
  "output": {
    "stk_nm": "삼성전자",
    "stck_prpr": "70000",           // 현재가
    "prdy_vrss": "+500",            // 전일 대비
    "prdy_vrss_sign": "2",          // 전일 대비 부호 (1: 상한, 2: 상승, 3: 보합, 4: 하한, 5: 하락)
    "prdy_ctrt": "0.72",            // 전일 대비율
    "stck_oprc": "69800",           // 시가
    "stck_hgpr": "70500",           // 고가
    "stck_lwpr": "69500",           // 저가
    "acml_vol": "12345678"          // 누적 거래량
  }
}
```

**n8n 수정 코드**:
```javascript
// 신호 생성 노드에서 등락률 직접 계산
const item = $input.item.json;
const kiwoomResponse = item;

// 현재가
const currentPrice = parseFloat(kiwoomResponse.stck_prpr || 0);

// 전일 대비 (키움 API에서 직접 제공)
const priceChange = parseFloat(kiwoomResponse.prdy_vrss || 0);
const changeRateRaw = parseFloat(kiwoomResponse.prdy_ctrt || 0);

// 전일 대비 부호 (2: 상승, 5: 하락, 3: 보합)
const sign = kiwoomResponse.prdy_vrss_sign || '3';
const changePrice = (sign === '5') ? -Math.abs(priceChange) : priceChange;
const changeRate = (sign === '5') ? -Math.abs(changeRateRaw) : changeRateRaw;

return {
  ...item,
  current_price: currentPrice,
  change_price: changePrice,
  change_rate: changeRate,
  stock_name: kiwoomResponse.stk_nm || item.stock_code
};
```

### 방법 2: kw_price_daily 테이블 채우기

일봉 데이터를 수집하여 `kw_price_daily` 테이블에 저장:

```sql
-- kw_price_daily 테이블 확인
SELECT * FROM kw_price_daily
WHERE stock_code = '005930'
ORDER BY trade_date DESC
LIMIT 5;
```

별도의 n8n 워크플로우로 일봉 데이터 수집 필요.

## 📝 적용 순서 (방법 1)

### 1. n8n 워크플로우 수정

**파일**: `auto-trading-with-capital-validation-v18.json`

**수정 대상 노드**: "신호 생성" 또는 "등락가/률 계산" 노드

**현재 로직**:
- `kw_price_daily` 테이블에서 전일 종가 조회
- 조회 실패 시 0으로 설정

**수정 후 로직**:
- 키움 API 응답의 `prdy_vrss`, `prdy_ctrt` 사용
- `prdy_vrss_sign`으로 상승/하락 구분

### 2. 수정할 JSON 위치

1. n8n Dashboard 열기
2. "자동매매 모니터링 v18" 워크플로우 편집
3. "신호 생성" 노드 찾기 (Code 노드)
4. JavaScript 코드 수정:

```javascript
// 기존 코드에 추가
const currentPrice = parseFloat(kiwoomResponse.stck_prpr || 0);
const changePrice = parseFloat(kiwoomResponse.prdy_vrss || 0);
const changeRate = parseFloat(kiwoomResponse.prdy_ctrt || 0);
const sign = kiwoomResponse.prdy_vrss_sign || '3';

// 부호 처리
const adjustedChangePrice = (sign === '5') ? -Math.abs(changePrice) : changePrice;
const adjustedChangeRate = (sign === '5') ? -Math.abs(changeRate) : changeRate;
```

### 3. Supabase에 저장하는 부분 수정

"Supabase에 시세 저장" 노드의 jsonBody:

```json
{
  "stock_code": "{{JSON.stringify($json.stock_code)}}",
  "stock_name": "{{JSON.stringify($json.stock_name || $json.stock_code)}}",
  "current_price": "{{$json.current_price}}",
  "change_price": "{{$json.change_price}}",
  "change_rate": "{{$json.change_rate}}",
  "volume": "{{$json.volume || 0}}",
  "high_52w": "{{$json.sel_price || 0}}",
  "low_52w": "{{$json.buy_price || 0}}",
  "market_cap": 0
}
```

## 🧪 테스트

1. n8n 워크플로우 수동 실행
2. Supabase에서 확인:
   ```sql
   SELECT
     stock_code,
     stock_name,
     current_price,
     change_price,
     change_rate,
     updated_at
   FROM kw_price_current
   WHERE change_rate != 0
   ORDER BY ABS(change_rate) DESC
   LIMIT 10;
   ```

## 🎯 예상 결과

- ✅ 상승 종목 정상 집계
- ✅ 하락 종목 정상 집계
- ✅ 등락률 실제 값 표시 (예: +2.35%, -1.87%)
- ✅ 보합 종목만 0% 표시

## 📌 참고: 키움 API 부호 코드

```
prdy_vrss_sign (전일 대비 부호)
1: 상한가
2: 상승
3: 보합
4: 하한가
5: 하락
```
