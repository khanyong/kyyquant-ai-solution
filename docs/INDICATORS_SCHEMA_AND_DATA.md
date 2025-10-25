# Indicators 테이블 스키마 및 데이터 문서

> 생성일: 2025-10-26
>
> 이 문서는 자동매매 시스템에서 사용하는 기술적 지표(indicators)의 전체 구조와 데이터를 정리한 것입니다.

---

## 📋 목차

1. [indicators 테이블 스키마](#indicators-테이블-스키마)
2. [indicator_columns 테이블 스키마](#indicator_columns-테이블-스키마)
3. [indicators 테이블 전체 데이터](#indicators-테이블-전체-데이터)
4. [indicator_columns 테이블 전체 데이터](#indicator_columns-테이블-전체-데이터)
5. [매핑 관계 분석](#매핑-관계-분석)
6. [발견된 문제점](#발견된-문제점)
7. [해결 방안](#해결-방안)

---

## indicators 테이블 스키마

### 테이블 구조

| 컬럼명 | 데이터 타입 | Nullable | 기본값 | 설명 |
|--------|-----------|----------|--------|------|
| `id` | uuid | NO | gen_random_uuid() | 지표 고유 ID |
| `name` | text | NO | - | 지표 이름 (예: ma, bollinger, rsi) |
| `display_name` | text | NO | - | 화면 표시용 이름 |
| `description` | text | YES | - | 지표 설명 |
| `category` | text | YES | - | 지표 카테고리 (trend, momentum, volatility, volume, price) |
| `calculation_type` | text | NO | - | 계산 방식 (python_code) |
| `formula` | jsonb | YES | - | Python 계산 코드 |
| `default_params` | jsonb | YES | - | 기본 파라미터 (예: {"period": 14}) |
| `required_data` | ARRAY | YES | - | 필요한 입력 데이터 (예: ["close", "high", "low"]) |
| `output_columns` | ARRAY | YES | - | 출력 컬럼명 (예: ["bollinger_upper", "bollinger_middle", "bollinger_lower"]) |
| `is_active` | boolean | YES | true | 활성화 여부 |
| `created_at` | timestamp with time zone | YES | now() | 생성 시간 |
| `updated_at` | timestamp with time zone | YES | now() | 수정 시간 |

### 주요 특징

- **calculation_type**: 모든 지표가 `python_code` 방식으로 계산됨
- **formula**: Python 코드가 JSON 형태로 저장됨
- **output_columns**: 각 지표가 출력하는 컬럼명 배열 (예: RSI는 ["rsi"], 볼린저밴드는 ["bollinger_upper", "bollinger_middle", "bollinger_lower"])

---

## indicator_columns 테이블 스키마

### 테이블 구조

| 컬럼명 | 데이터 타입 | Nullable | 기본값 | 설명 |
|--------|-----------|----------|--------|------|
| `id` | uuid | NO | gen_random_uuid() | 컬럼 고유 ID |
| `indicator_name` | text | NO | - | 지표 이름 (indicators.name과 매핑) |
| `indicator_version` | text | YES | '1.0.0' | 지표 버전 |
| `column_name` | text | NO | - | 출력 컬럼명 |
| `column_type` | text | YES | 'numeric' | 컬럼 데이터 타입 |
| `column_description` | text | YES | - | 컬럼 설명 |
| `output_order` | integer | YES | 0 | 출력 순서 |
| `is_primary` | boolean | YES | false | 주요 컬럼 여부 |
| `is_active` | boolean | YES | true | 활성화 여부 |
| `created_at` | timestamp with time zone | YES | now() | 생성 시간 |

### 주요 특징

- **indicator_name**: indicators 테이블의 `name`과 매핑되어야 하지만, 실제로는 일부 불일치 존재
- **output_order**: 컬럼 출력 순서 정의
- **is_primary**: 해당 지표의 메인 출력 컬럼 표시

---

## indicators 테이블 전체 데이터

### 1. ADX (추세강도)

```json
{
  "id": "06230327-36bb-477e-89ac-30c7bbec9375",
  "name": "adx",
  "display_name": "ADX (추세강도)",
  "category": "trend",
  "calculation_type": "python_code",
  "default_params": {
    "period": 14,
    "realtime": false
  },
  "required_data": ["high", "low", "close"],
  "output_columns": ["adx"]
}
```

### 2. ATR (변동성)

```json
{
  "id": "e1d325ff-72e0-4e0a-bb4f-6f6648a963c9",
  "name": "atr",
  "display_name": "ATR (변동성)",
  "category": "volatility",
  "calculation_type": "python_code",
  "default_params": {
    "period": 14
  },
  "required_data": ["high", "low", "close"],
  "output_columns": ["atr"]
}
```

### 3. Bollinger Bands (볼린저밴드) ⚠️

```json
{
  "id": "085d1011-0dcc-4275-931c-cf13cfed0546",
  "name": "bollinger",
  "display_name": "볼린저밴드",
  "category": "volatility",
  "calculation_type": "python_code",
  "default_params": {
    "std": 2,
    "period": 20
  },
  "required_data": ["close"],
  "output_columns": ["bollinger_upper", "bollinger_middle", "bollinger_lower"]
}
```

**⚠️ 주의**: Python 코드에서는 실제로 `bb_upper`, `bb_middle`, `bb_lower`로 반환됨 (불일치!)

### 4. CCI

```json
{
  "id": "8a17526a-4911-4592-a94d-13a03914ff66",
  "name": "cci",
  "display_name": "CCI",
  "category": "momentum",
  "calculation_type": "python_code",
  "default_params": {
    "period": 20
  },
  "required_data": ["high", "low", "close"],
  "output_columns": ["cci"]
}
```

### 5. Close (종가)

```json
{
  "id": "9e30ddab-8545-4b8e-a5f7-944f9c50f15a",
  "name": "close",
  "display_name": "종가",
  "category": "price",
  "calculation_type": "python_code",
  "default_params": {},
  "required_data": ["close"],
  "output_columns": ["close"]
}
```

### 6. DMI (+DI/-DI)

```json
{
  "id": "3413aed3-aa71-4aa7-a0d6-b5cba7847666",
  "name": "dmi",
  "display_name": "DMI (+DI/-DI)",
  "category": "trend",
  "calculation_type": "python_code",
  "default_params": {
    "period": 14,
    "realtime": false
  },
  "required_data": ["high", "low", "close"],
  "output_columns": ["dmi_plus_di", "dmi_minus_di"]
}
```

### 7. EMA (지수이동평균)

```json
{
  "id": "56de95eb-dc98-41a7-81a8-b009880574d1",
  "name": "ema",
  "display_name": "EMA (지수이동평균)",
  "category": "trend",
  "calculation_type": "python_code",
  "default_params": {
    "period": 20
  },
  "required_data": ["close"],
  "output_columns": ["ema"]
}
```

### 8. Ichimoku (일목균형표)

```json
{
  "id": "cad24fc5-5eaf-4412-93ac-86e9eaf00567",
  "name": "ichimoku",
  "display_name": "일목균형표",
  "category": "trend",
  "calculation_type": "python_code",
  "default_params": {
    "kijun": 26,
    "chikou": 26,
    "senkou": 52,
    "tenkan": 9
  },
  "required_data": ["high", "low", "close"],
  "output_columns": [
    "ichimoku_tenkan",
    "ichimoku_kijun",
    "ichimoku_senkou_a",
    "ichimoku_senkou_b",
    "ichimoku_chikou"
  ]
}
```

### 9. MA (이동평균) ⚠️

```json
{
  "id": "de564d7d-7971-4391-93fa-c98299045d28",
  "name": "ma",
  "display_name": "MA (이동평균)",
  "category": "trend",
  "calculation_type": "python_code",
  "default_params": {
    "period": 20
  },
  "required_data": ["close"],
  "output_columns": ["ma"]
}
```

**⚠️ 주의**: period 파라미터에 따라 `ma_20`, `ma_60` 등으로 동적 생성

### 10. MACD

```json
{
  "id": "134ecf94-fcec-4b75-81ef-05ef498750ad",
  "name": "macd",
  "display_name": "MACD",
  "category": "momentum",
  "calculation_type": "python_code",
  "default_params": {
    "fast": 12,
    "slow": 26,
    "signal": 9
  },
  "required_data": ["close"],
  "output_columns": ["macd_line", "macd_signal", "macd_hist"]
}
```

### 11. OBV (누적거래량)

```json
{
  "id": "6b00f0bf-4c9c-449c-af57-a1eda583560b",
  "name": "obv",
  "display_name": "OBV (누적거래량)",
  "category": "volume",
  "calculation_type": "python_code",
  "default_params": {},
  "required_data": ["close", "volume"],
  "output_columns": ["obv"]
}
```

### 12. Parabolic SAR

```json
{
  "id": "9d77589a-d47a-412d-9642-2a6f476a3f4b",
  "name": "parabolic",
  "display_name": "Parabolic SAR",
  "category": "trend",
  "calculation_type": "python_code",
  "default_params": {
    "af_max": 0.2,
    "af_step": 0.02,
    "af_start": 0.02
  },
  "required_data": ["high", "low", "close"],
  "output_columns": ["psar", "psar_trend"]
}
```

### 13. Price (현재가)

```json
{
  "id": "f4b06a71-2873-44ac-ac92-e79c0913bb99",
  "name": "price",
  "display_name": "현재가",
  "category": "price",
  "calculation_type": "python_code",
  "default_params": {},
  "required_data": ["close"],
  "output_columns": ["price"]
}
```

### 14. RSI

```json
{
  "id": "d8a7ee68-f0da-4923-a559-34d057dc1eba",
  "name": "rsi",
  "display_name": "RSI",
  "category": "momentum",
  "calculation_type": "python_code",
  "default_params": {
    "period": 14
  },
  "required_data": ["close"],
  "output_columns": ["rsi"]
}
```

### 15. SMA (단순이동평균)

```json
{
  "id": "8e24101c-52a7-4284-842e-78cc4c7016e1",
  "name": "sma",
  "display_name": "SMA (단순이동평균)",
  "category": "trend",
  "calculation_type": "python_code",
  "default_params": {
    "period": 20
  },
  "required_data": ["close"],
  "output_columns": ["sma"]
}
```

### 16. Stochastic (스토캐스틱)

```json
{
  "id": "a0680872-8c2a-498c-ad02-ccfc8107ecc7",
  "name": "stochastic",
  "display_name": "스토캐스틱",
  "category": "momentum",
  "calculation_type": "python_code",
  "default_params": {
    "d": 3,
    "k": 14
  },
  "required_data": ["high", "low", "close"],
  "output_columns": ["stochastic_k", "stochastic_d"]
}
```

### 17. Volume (거래량)

```json
{
  "id": "7ec6bc16-f15a-4eb0-9bb0-a7a0d2fa6d11",
  "name": "volume",
  "display_name": "거래량",
  "category": "volume",
  "calculation_type": "python_code",
  "default_params": {},
  "required_data": ["volume"],
  "output_columns": ["volume"]
}
```

### 18. Volume MA (거래량 이동평균)

```json
{
  "id": "856c5cc5-379a-4dd2-89a2-f6ee33ebb800",
  "name": "volume_ma",
  "display_name": "거래량 이동평균",
  "category": "volume",
  "calculation_type": "python_code",
  "default_params": {
    "period": 20
  },
  "required_data": ["volume"],
  "output_columns": ["volume_ma"]
}
```

### 19. VWAP (거래량가중평균)

```json
{
  "id": "7aa38326-5e0d-42d0-b77e-614674f4ebd2",
  "name": "vwap",
  "display_name": "VWAP (거래량가중평균)",
  "category": "volume",
  "calculation_type": "python_code",
  "default_params": {},
  "required_data": ["high", "low", "close", "volume"],
  "output_columns": ["vwap"]
}
```

### 20. Williams %R

```json
{
  "id": "001526d7-70dc-4a36-aca1-fef548d6a54e",
  "name": "williams",
  "display_name": "Williams %R",
  "category": "momentum",
  "calculation_type": "python_code",
  "default_params": {
    "period": 14,
    "realtime": false
  },
  "required_data": ["high", "low", "close"],
  "output_columns": ["williams_r"]
}
```

---

## indicator_columns 테이블 전체 데이터

### ADX (adx)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| adx | numeric | ✅ true | 1 | Average Directional Index (trend strength) |
| plus_di | numeric | false | 2 | Positive Directional Indicator |
| minus_di | numeric | false | 3 | Negative Directional Indicator |

### ATR (atr)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| atr | numeric | ✅ true | 1 | Average True Range (volatility) |
| atr_pct | numeric | false | 2 | ATR as percentage of close |

### Bollinger Bands (bb) ⚠️

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| bb_upper | numeric | false | 1 | Upper band |
| bb_middle | numeric | ✅ true | 2 | Middle band |
| bb_lower | numeric | false | 3 | Lower band |

**⚠️ 주의**: indicator_name이 `bb`로 저장됨 (indicators 테이블에서는 `bollinger`)

### Bollinger Bands (bollinger_bands)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| bb_upper | numeric | false | 1 | Upper band (SMA + std_dev * multiplier) |
| bb_middle | numeric | ✅ true | 2 | Middle band (SMA) |
| bb_lower | numeric | false | 3 | Lower band (SMA - std_dev * multiplier) |
| bb_width | numeric | false | 4 | Band width (upper - lower) |
| bb_pct | numeric | false | 5 | Price position within bands (0-1) |

### EMA (ema)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| ema | numeric | ✅ true | 1 | Exponential moving average value |

### Ichimoku (ichimoku)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| ichimoku_tenkan | numeric | false | 1 | 전환선 (Conversion Line): 최근 9일간 최고가와 최저가의 평균 |
| ichimoku_kijun | numeric | false | 2 | 기준선 (Base Line): 최근 26일간 최고가와 최저가의 평균 |
| ichimoku_senkou_a | numeric | false | 3 | 선행스팬 A (Leading Span A) |
| ichimoku_senkou_b | numeric | false | 4 | 선행스팬 B (Leading Span B) |
| ichimoku_chikou | numeric | false | 5 | 후행스팬 (Lagging Span) |

### MACD (macd)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| macd_line | numeric | ✅ true | 1 | MACD line (fast EMA - slow EMA) |
| macd_signal | numeric | false | 2 | Signal line (EMA of MACD) |
| macd_hist | numeric | false | 3 | Histogram (MACD - Signal) |

### Parabolic SAR (parabolic_sar)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| psar | numeric | ✅ true | 1 | Parabolic SAR value |
| psar_trend | numeric | false | 2 | Trend direction (1=up, -1=down) |

### Price (price)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| open | numeric | false | 1 | Opening price |
| high | numeric | false | 2 | High price |
| low | numeric | false | 3 | Low price |
| close | numeric | ✅ true | 4 | Closing price |
| volume | numeric | false | 5 | Trading volume |
| trade_date | numeric | false | 6 | Trading date |

### RSI (rsi)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| rsi | numeric | ✅ true | 1 | Relative Strength Index (0-100) |

### Stochastic (stochastic)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| stochastic_k | numeric | ✅ true | 1 | %K line (fast stochastic) |
| stochastic_d | numeric | false | 2 | %D line (slow stochastic, SMA of %K) |

### Volume MA (volume_ma)

| column_name | column_type | is_primary | output_order | description |
|-------------|-------------|------------|--------------|-------------|
| volume_ma | numeric | ✅ true | 1 | Volume moving average |
| volume_ratio | numeric | false | 2 | Current volume / MA |

---

## 매핑 관계 분석

### ✅ 정상 매핑

| indicators.name | indicator_columns.indicator_name | 상태 |
|----------------|----------------------------------|------|
| rsi | rsi | ✅ 일치 |
| macd | macd | ✅ 일치 |
| ichimoku | ichimoku | ✅ 일치 |
| adx | adx | ✅ 일치 |
| atr | atr | ✅ 일치 |
| ema | ema | ✅ 일치 |
| stochastic | stochastic | ✅ 일치 |
| volume_ma | volume_ma | ✅ 일치 |

### ❌ 매핑 불일치 또는 누락

| indicators.name | indicator_columns.indicator_name | 상태 | 비고 |
|----------------|----------------------------------|------|------|
| **bollinger** | bb, bollinger_bands | ⚠️ 불일치 | indicator_columns에 2가지 이름으로 존재 |
| **ma** | ❌ 없음 | ❌ 누락 | indicator_columns에 데이터 없음 |
| **close** | ❌ 없음 | ❌ 누락 | price 카테고리에 close 컬럼은 있음 |
| **volume** | ❌ 없음 | ❌ 누락 | price 카테고리에 volume 컬럼은 있음 |
| **sma** | ❌ 없음 | ❌ 누락 | indicator_columns에 데이터 없음 |
| **dmi** | ❌ 없음 | ❌ 누락 | indicator_columns에 데이터 없음 |
| **cci** | ❌ 없음 | ❌ 누락 | indicator_columns에 데이터 없음 |
| **obv** | ❌ 없음 | ❌ 누락 | indicator_columns에 데이터 없음 |
| **parabolic** | parabolic_sar | ⚠️ 불일치 | 이름이 다름 |
| **price** | price | ✅ 일치 | close 컬럼 포함 |
| **vwap** | ❌ 없음 | ❌ 누락 | indicator_columns에 데이터 없음 |
| **williams** | ❌ 없음 | ❌ 누락 | indicator_columns에 데이터 없음 |

---

## 발견된 문제점

### 🚨 1. 테이블 간 데이터 불일치

**심각도**: 🔴 **치명적**

- **indicators** 테이블에는 20개 지표가 정의되어 있음
- **indicator_columns** 테이블에는 13개 지표만 매핑되어 있음
- **7개 지표 누락**: ma, sma, close, volume, dmi, cci, obv, vwap, williams

### 🚨 2. 컬럼명 불일치

**심각도**: 🔴 **치명적**

#### Bollinger Bands

- **indicators.output_columns**: `["bollinger_upper", "bollinger_middle", "bollinger_lower"]`
- **Python formula 실제 반환**: `{'bollinger_upper': ..., 'bollinger_middle': ..., 'bollinger_lower': ...}`
- **indicator_columns**: `bb_upper`, `bb_middle`, `bb_lower`
- **결과**: 전략에서 `bollinger_lower`를 참조하면 매핑 실패

#### Parabolic SAR

- **indicators.name**: `parabolic`
- **indicator_columns.indicator_name**: `parabolic_sar`
- **결과**: JOIN 시 매핑 실패

### 🚨 3. n8n 워크플로우에서 지표 미계산

**심각도**: 🔴 **치명적**

현재 n8n v20 워크플로우는:

```javascript
const indicators = {
  close: estimatedPrice,        // ✅ 계산됨 (호가 기반)
  sel_price: selPrice,          // ✅ 계산됨 (호가)
  buy_price: buyPrice,          // ✅ 계산됨 (호가)
  volume: selVolume + buyVolume // ✅ 계산됨 (호가 거래량)
};
```

**문제점:**
- ❌ **과거 데이터 미조회**: `kw_price_daily` 테이블에서 과거 가격 데이터를 가져오지 않음
- ❌ **Python 지표 계산 미실행**: indicators 테이블의 Python 코드를 실행하지 않음
- ❌ **ma, bollinger, rsi 등 모든 기술적 지표 미계산**

### 🚨 4. 전략 조건 불만족

**심각도**: 🔴 **치명적**

#### 전략 1: "나의 전략 7"

```json
{
  "buy": [
    { "left": "close", "operator": "<", "right": 20 },  // ❌ ma_20을 의도했으나 숫자 20으로 저장됨
    { "left": "close", "operator": "<", "right": 12 }   // ❌ ma_12를 의도했으나 숫자 12로 저장됨
  ]
}
```

**문제**:
- `right` 값이 문자열 `"ma_20"` 대신 숫자 `20`으로 저장됨
- n8n에서 `indicators["ma_20"]`이 `0` 또는 `undefined` → 항상 조건 불만족

#### 전략 2: "[분할] 볼린저밴드 2단계 매수"

```json
{
  "buy": [
    { "left": "close", "operator": "<", "right": "bollinger_lower" },
    { "left": "rsi", "operator": "<", "right": 45 }
  ]
}
```

**문제**:
- `indicators["bollinger_lower"]`가 계산되지 않음 → `0` 또는 `undefined`
- `indicators["rsi"]`가 계산되지 않음 → `0` 또는 `undefined`
- 결과: 항상 조건 불만족

---

## 해결 방안

### 🎯 단계별 해결 계획

#### Phase 1: 데이터 정합성 확보 (긴급)

1. **indicator_columns 테이블에 누락된 지표 데이터 추가**

```sql
-- ma (이동평균) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description, output_order, is_primary)
VALUES
  ('ma', 'ma', 'numeric', 'Moving Average', 1, true);

-- sma (단순이동평균) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description, output_order, is_primary)
VALUES
  ('sma', 'sma', 'numeric', 'Simple Moving Average', 1, true);

-- close (종가) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description, output_order, is_primary)
VALUES
  ('close', 'close', 'numeric', 'Closing price', 1, true);

-- volume (거래량) 추가
INSERT INTO indicator_columns (indicator_name, column_name, column_type, column_description, output_order, is_primary)
VALUES
  ('volume', 'volume', 'numeric', 'Trading volume', 1, true);

-- 나머지 누락 지표들도 추가...
```

2. **bollinger 지표 이름 통일**

```sql
-- bollinger_bands를 bollinger로 통일 (옵션 1)
UPDATE indicator_columns
SET indicator_name = 'bollinger'
WHERE indicator_name IN ('bb', 'bollinger_bands');

-- 또는 indicators 테이블을 indicator_columns에 맞춤 (옵션 2)
UPDATE indicators
SET name = 'bollinger_bands'
WHERE name = 'bollinger';
```

#### Phase 2: Backend API 구축 (필수)

**FastAPI 엔드포인트 생성**: `/api/indicators/calculate`

```python
@app.post("/api/indicators/calculate")
async def calculate_indicators(request: IndicatorRequest):
    """
    지표 계산 API

    Request:
    {
      "stock_code": "005930",
      "indicators": [
        {"name": "ma", "params": {"period": 20}},
        {"name": "bollinger", "params": {"period": 20, "std": 2}},
        {"name": "rsi", "params": {"period": 14}}
      ],
      "lookback_days": 60  # 과거 데이터 조회 기간
    }

    Response:
    {
      "stock_code": "005930",
      "timestamp": "2025-10-26T10:00:00Z",
      "indicators": {
        "ma": 75000,
        "bollinger_upper": 78000,
        "bollinger_middle": 75000,
        "bollinger_lower": 72000,
        "rsi": 45.5,
        "close": 75500,
        "volume": 1000000
      }
    }
    """
    # 1. kw_price_daily에서 과거 데이터 조회
    # 2. indicators 테이블에서 formula 가져오기
    # 3. Python exec()로 formula 실행
    # 4. 계산 결과 반환
```

#### Phase 3: n8n 워크플로우 개선 (필수)

**n8n v21 워크플로우 생성**:

1. **"지표 계산" 노드 추가** (Backend API 호출)
   - 위치: "키움 호가 조회" 노드와 "조건 체크 및 신호 생성" 노드 사이
   - 역할: Backend API로 지표 계산 요청

```javascript
// n8n "지표 계산" 노드 코드
const stockCode = $json._original_stock_code;
const strategyId = $json._original_strategy_id;
const entryConditions = $json._original_entry_conditions;

// 전략에서 필요한 지표 추출
const requiredIndicators = [];
if (entryConditions && entryConditions.buy) {
  entryConditions.buy.forEach(cond => {
    if (cond.left !== 'close' && cond.left !== 'volume') {
      requiredIndicators.push(cond.left);
    }
    if (typeof cond.right === 'string' && cond.right !== 'close') {
      requiredIndicators.push(cond.right);
    }
  });
}

// Backend API 호출
const response = await fetch(`${BACKEND_URL}/api/indicators/calculate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    stock_code: stockCode,
    indicators: [...new Set(requiredIndicators)].map(ind => ({
      name: ind.replace(/_\d+$/, ''), // ma_20 → ma
      params: { period: parseInt(ind.match(/\d+$/)?.[0] || 20) }
    })),
    lookback_days: 60
  })
});

const calculatedIndicators = await response.json();

return {
  ...$json,
  calculated_indicators: calculatedIndicators.indicators
};
```

2. **"조건 체크 및 신호 생성" 노드 수정**

```javascript
// 기존 호가 기반 지표
const indicators = {
  close: estimatedPrice,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: selVolume + buyVolume,
  // 🆕 계산된 기술적 지표 추가
  ...item.calculated_indicators
};

// 이제 ma_20, bollinger_lower, rsi 등 사용 가능!
```

#### Phase 4: 전략 데이터 수정 (긴급)

```sql
-- "나의 전략 7" 조건 수정
UPDATE strategies
SET entry_conditions = '{
  "buy": [
    {
      "id": "ind_1760307674840",
      "left": "close",
      "type": "buy",
      "right": "ma_20",
      "operator": "<",
      "combineWith": "AND"
    },
    {
      "id": "ind_1760307688706",
      "left": "close",
      "type": "buy",
      "right": "ma_12",
      "operator": "<",
      "combineWith": "AND"
    }
  ]
}'::jsonb
WHERE id = '7cd0d6cd-fe76-482d-83b9-ff1a955c7d39';
```

---

## 검증 쿼리

### 전체 매핑 상태 확인

```sql
SELECT
  i.name as indicator_name,
  i.output_columns as defined_outputs,
  CASE
    WHEN COUNT(ic.column_name) = 0 THEN '❌ 누락'
    WHEN i.name != ic.indicator_name THEN '⚠️ 이름 불일치'
    ELSE '✅ 정상'
  END as mapping_status,
  array_agg(ic.column_name ORDER BY ic.output_order) as actual_columns
FROM indicators i
LEFT JOIN indicator_columns ic ON i.name = ic.indicator_name
WHERE i.is_active = true
GROUP BY i.id, i.name, i.output_columns, ic.indicator_name
ORDER BY mapping_status DESC, i.name;
```

### 전략이 사용하는 지표 확인

```sql
WITH strategy_indicators AS (
  SELECT DISTINCT
    s.id,
    s.name,
    jsonb_array_elements(entry_conditions->'buy')->>'left' as indicator_left,
    jsonb_array_elements(entry_conditions->'buy')->>'right' as indicator_right
  FROM strategies s
  WHERE s.is_active = true
)
SELECT
  si.name as strategy_name,
  si.indicator_left,
  si.indicator_right,
  i1.name as left_exists_in_indicators,
  i2.name as right_exists_in_indicators,
  CASE
    WHEN i1.name IS NULL THEN '❌ left 지표 없음'
    WHEN i2.name IS NULL AND si.indicator_right !~ '^\d+$' THEN '❌ right 지표 없음'
    ELSE '✅ 정상'
  END as validation_status
FROM strategy_indicators si
LEFT JOIN indicators i1 ON si.indicator_left = i1.name
LEFT JOIN indicators i2 ON si.indicator_right = i2.name
ORDER BY si.name, validation_status DESC;
```

---

## 참고사항

### 지표 계산 순서

1. **기본 가격 데이터** (price): open, high, low, close, volume
2. **이동평균** (ma, ema, sma): 가격 데이터 기반
3. **변동성 지표** (bollinger, atr): 이동평균 및 가격 데이터 기반
4. **모멘텀 지표** (rsi, macd, stochastic): 가격 변화 기반
5. **추세 지표** (adx, dmi, ichimoku, parabolic): 고급 계산

### 데이터 의존성

```
kw_price_daily (과거 60일)
    ↓
price (open, high, low, close, volume)
    ↓
ma, ema, sma
    ↓
bollinger, atr, rsi, macd, stochastic
    ↓
adx, dmi, ichimoku
```

---

**마지막 업데이트**: 2025-10-26
**작성자**: Claude Code
**버전**: 1.0.0
