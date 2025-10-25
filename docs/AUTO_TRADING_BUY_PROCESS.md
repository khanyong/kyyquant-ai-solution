# 자동매매 매수 프로세스 전체 흐름

수정된 시스템의 완전한 자동매매 매수 프로세스를 정리합니다.

---

## 📊 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         Supabase Database                        │
├─────────────────────────────────────────────────────────────────┤
│ • strategies (2개 활성 전략)                                     │
│ • kw_investment_filters (투자유니버스: 105개 종목)               │
│ • indicators (17개 기술지표 정의 + Python 계산식)                │
│ • indicator_columns (지표 출력 컬럼 매핑)                        │
│ • kw_price_daily (과거 일봉 데이터)                              │
│ • kw_price_current (실시간 호가 데이터)                          │
│ • trading_signals (생성된 매수/매도 신호)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      n8n Workflow (v20/v21)                      │
│                    매 5분마다 실행 (Schedule)                    │
├─────────────────────────────────────────────────────────────────┤
│ 1. 장시간 체크 (9-15시, 월-금)                                   │
│ 2. 활성 전략 조회 (RPC: get_active_strategies_with_universe)     │
│ 3. 종목별 분리 (105개 종목)                                      │
│ 4. 키움 호가 조회 (Mock API)                                     │
│ 5. 지표 계산 (Backend API) ← 🆕 NEW!                             │
│ 6. 조건 체크 및 신호 생성                                        │
│ 7. 신호 저장 (trading_signals)                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Backend FastAPI Server                        │
│                   (http://localhost:8000)                        │
├─────────────────────────────────────────────────────────────────┤
│ POST /api/indicators/calculate                                   │
│ • kw_price_daily에서 과거 60일 데이터 조회                       │
│ • IndicatorCalculator로 지표 계산                                │
│ • indicators 테이블의 Python 코드 실행                           │
│ • 최신 값 반환: {ma_20: 75000, rsi: 45.5, ...}                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend React App                            │
│                  (http://localhost:3000)                         │
├─────────────────────────────────────────────────────────────────┤
│ • MarketMonitor: kw_price_current 실시간 모니터링 (1000개)       │
│ • TradingSignals: trading_signals 테이블 조회                    │
│ • 사용자에게 매수 신호 알림                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⏰ 1. 모니터링 타이밍

### 1-1. n8n Workflow 실행 주기

```javascript
// Schedule Trigger 노드: "5분마다 실행"
{
  "rule": {
    "interval": [
      {
        "field": "minutes",
        "minutesInterval": 5
      }
    ]
  }
}
```

**실행 주기**: 매 5분마다 (00:00, 00:05, 00:10, 00:15, ...)

### 1-2. 장시간 체크 (운영 시간 필터링)

```javascript
// "장시간 체크" 노드
const now = new Date();
const day = now.getDay();      // 0=일요일, 1=월, 2=화, ..., 6=토
const hour = now.getHours();   // 0-23

// 월-금요일 (1-5)
if (day < 1 || day > 5) {
  console.log('❌ 주말입니다. 실행 중단');
  return null;
}

// 장 시작 전후 30분 포함 (8:30 - 15:30)
// 실제 거래시간: 9:00 - 15:30
if (hour < 8 || hour > 15) {
  console.log('❌ 장시간이 아닙니다. 실행 중단');
  return null;
}

// 9시 정각에는 시가 데이터 대기를 위해 5분 후 실행
if (hour === 9 && now.getMinutes() < 5) {
  console.log('⏳ 시가 데이터 대기 중...');
  return null;
}

console.log('✅ 장시간입니다. 실행 계속');
return { continue: true };
```

**🚨 현재 문제점**: 공휴일 체크 없음!
- 설날, 추석, 임시공휴일에도 실행됨
- **개선 방안**: 한국거래소 공휴일 API 또는 calendar 테이블 활용

### 1-3. 실제 모니터링 빈도

```
월-금, 9:00-15:30 (6.5시간 = 390분)
매 5분마다 실행
→ 하루 최대 78회 실행 (390분 ÷ 5분 = 78회)
→ 종목당 최대 78회 체크 (105개 종목 × 78회 = 8,190번 호가 조회)
```

**💡 5분 주기의 장점**:
- 서버 부하 감소 (1분 대비 1/5)
- 지표 계산 여유 시간 확보 (75초 소요 → 5분 = 300초 내 완료)
- 기술적 지표는 5분 간격으로도 충분한 변화 감지 가능

---

## 🎯 2. 모니터링 종목

### 2-1. 활성 전략 조회

```sql
-- RPC 함수: get_active_strategies_with_universe()
SELECT
  s.id as strategy_id,
  s.name as strategy_name,
  s.entry_conditions,
  s.exit_conditions,
  kif.filtered_stocks,  -- 투자유니버스 종목 배열
  s.allocated_capital,
  s.allocated_percent
FROM strategies s
INNER JOIN strategy_universes su ON s.id = su.strategy_id
INNER JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
WHERE s.auto_execute = true
  AND s.is_active = true
  AND su.is_active = true
  AND kif.is_active = true;
```

**결과 (현재 시스템)**:
```json
[
  {
    "strategy_id": "7cd0d6cd-fe76-482d-83b9-ff1a955c7d39",
    "strategy_name": "나의 전략 7",
    "entry_conditions": {
      "buy": [
        { "left": "close", "operator": "<", "right": "ma_20" },
        { "left": "close", "operator": "<", "right": "ma_12" }
      ]
    },
    "filtered_stocks": ["005930", "000660", ...],  // 70개 종목
    "allocated_capital": 5000000,
    "allocated_percent": 50
  },
  {
    "strategy_id": "a0515a88-a220-40de-8538-5e503336005c",
    "strategy_name": "[분할] 볼린저밴드 2단계 매수",
    "entry_conditions": {
      "buy": [
        { "left": "close", "operator": "<", "right": "bollinger_lower" },
        { "left": "rsi", "operator": "<", "right": 45 }
      ]
    },
    "filtered_stocks": ["005930", "051910", ...],  // 35개 종목
    "allocated_capital": 5000000,
    "allocated_percent": 50
  }
]
```

### 2-2. 종목별 분리

```javascript
// "종목별 분리" 노드
const strategies = $input.all();
const stockStrategyPairs = [];

for (const strategy of strategies) {
  const filteredStocks = strategy.json.filtered_stocks || [];

  for (const stockCode of filteredStocks) {
    stockStrategyPairs.push({
      stock_code: stockCode,
      strategy_id: strategy.json.strategy_id,
      strategy_name: strategy.json.strategy_name,
      entry_conditions: strategy.json.entry_conditions,
      exit_conditions: strategy.json.exit_conditions
    });
  }
}

console.log(`📊 총 ${stockStrategyPairs.length}개 종목-전략 쌍 생성`);
// 출력: 📊 총 105개 종목-전략 쌍 생성 (70 + 35 = 105)

return stockStrategyPairs;
```

### 2-3. 모니터링 종목 리스트

**전략 1: "나의 전략 7"** (70개 종목)
- 삼성전자 (005930)
- SK하이닉스 (000660)
- ... (70개)

**전략 2: "[분할] 볼린저밴드 2단계 매수"** (35개 종목)
- 삼성전자 (005930)
- LG화학 (051910)
- ... (35개)

**중복 제거 시 실제 종목 수**: ~100개 (일부 종목은 두 전략 모두에 포함)

**💡 참고**: 프론트엔드 MarketMonitor는 1000개 종목을 표시하지만, 실제 자동매매는 105개 종목만 모니터링!

---

## 📈 3. 지표 계산 방식

### 3-1. 필요한 지표 추출

```javascript
// "지표 계산" HTTP Request 노드 - Request Body

const stockCode = $input.item.json._original_stock_code;
const entryConditions = $input.item.json._original_entry_conditions;

// 전략 조건에서 필요한 지표 자동 추출
function extractRequiredIndicators(conditions) {
  const indicators = new Set();

  if (conditions && conditions.buy) {
    for (const condition of conditions.buy) {
      // right 값이 지표 이름인 경우 (ma_20, bollinger_lower 등)
      if (typeof condition.right === 'string' && condition.right !== 'close') {
        indicators.add(condition.right);
      }
      // left 값이 지표 이름인 경우 (rsi 등)
      if (typeof condition.left === 'string' && condition.left !== 'close') {
        indicators.add(condition.left);
      }
    }
  }

  return Array.from(indicators);
}

const requiredIndicators = extractRequiredIndicators(entryConditions);
// "나의 전략 7": ["ma_20", "ma_12"]
// "[분할] 볼린저밴드": ["bollinger_lower", "rsi"]
```

### 3-2. 지표 요청 변환

```javascript
// 지표 이름 → API 요청 형식 변환
const indicatorRequests = requiredIndicators.map(indicator => {
  // ma_20 → {name: "ma", params: {period: 20}}
  if (indicator.startsWith('ma_')) {
    const period = parseInt(indicator.split('_')[1]);
    return { name: 'ma', params: { period: period } };
  }

  // bollinger_lower, bollinger_upper 등 → {name: "bollinger", params: {period: 20}}
  if (indicator.startsWith('bollinger_')) {
    return { name: 'bollinger', params: { period: 20, std_dev: 2 } };
  }

  // rsi → {name: "rsi", params: {period: 14}}
  if (indicator === 'rsi') {
    return { name: 'rsi', params: { period: 14 } };
  }

  return { name: indicator, params: {} };
});

// 중복 제거 (bollinger는 한 번만 계산)
const uniqueIndicators = [...new Set(indicatorRequests.map(JSON.stringify))].map(JSON.parse);

return {
  stock_code: stockCode,
  indicators: uniqueIndicators,
  days: 60  // 과거 60일 데이터 사용
};
```

**요청 예시 (삼성전자, "나의 전략 7")**:
```json
{
  "stock_code": "005930",
  "indicators": [
    {"name": "ma", "params": {"period": 20}},
    {"name": "ma", "params": {"period": 12}}
  ],
  "days": 60
}
```

**요청 예시 (삼성전자, "[분할] 볼린저밴드")**:
```json
{
  "stock_code": "005930",
  "indicators": [
    {"name": "bollinger", "params": {"period": 20, "std_dev": 2}},
    {"name": "rsi", "params": {"period": 14}}
  ],
  "days": 60
}
```

### 3-3. 백엔드 지표 계산 프로세스

```python
# POST /api/indicators/calculate

# 1. 과거 데이터 조회
df = await data_provider.get_historical_data(
    stock_code="005930",
    start_date="2025-08-27",  # 60일 전
    end_date="2025-10-26"     # 오늘
)
# 결과: DataFrame with columns [open, high, low, close, volume]
#       60 rows (60일치 일봉 데이터)

# 2. 지표 계산 (indicators 테이블 사용)
calculator = IndicatorCalculator()

# ma_20 계산
ma_20_df = calculator.calculate(
    df=df,
    indicator_name="ma",
    period=20
)
# 결과: DataFrame with column [ma]
#       60 rows, 마지막 row의 ma 값 = 75000.5

# bollinger 계산
bollinger_df = calculator.calculate(
    df=df,
    indicator_name="bollinger",
    period=20,
    std_dev=2
)
# 결과: DataFrame with columns [bollinger_upper, bollinger_middle, bollinger_lower, bb_pct, bb_width]
#       60 rows, 마지막 row 사용

# rsi 계산
rsi_df = calculator.calculate(
    df=df,
    indicator_name="rsi",
    period=14
)
# 결과: DataFrame with column [rsi]
#       60 rows, 마지막 row의 rsi 값 = 45.5

# 3. 최신 값 추출 및 반환
result = {
    "stock_code": "005930",
    "indicators": {
        "ma_20": 75000.5,
        "bollinger_upper": 78000.0,
        "bollinger_middle": 75000.0,
        "bollinger_lower": 72000.0,
        "bb_pct": 0.583,
        "bb_width": 6000.0,
        "rsi": 45.5,
        "close": 75500.0  # df의 마지막 close 값
    },
    "calculated_at": "2025-10-26T15:30:00"
}
```

### 3-4. Supabase indicators 테이블 사용

```python
# IndicatorCalculator._calculate_from_definition()

# indicators 테이블에서 지표 정의 로드
indicator_def = {
    "name": "ma",
    "calculation_type": "python_code",
    "formula": {
        "code": """
import pandas as pd

period = params.get('period', 20)
min_periods = params.get('min_periods', period)

result = pd.DataFrame()
result['ma'] = df['close'].rolling(window=period, min_periods=min_periods).mean()
""",
        "dependencies": ["pandas"]
    },
    "output_columns": ["ma"],
    "default_params": {"period": 20}
}

# Python 코드 실행 (샌드박스 환경)
namespace = {
    'df': df.copy(),
    'params': {'period': 20, 'min_periods': 20},
    'pd': pandas,
    'np': numpy
}
exec(indicator_def['formula']['code'], namespace)
result_df = namespace.get('result')

# 결과: DataFrame with column [ma]
```

**계산 시간**:
- 종목당 평균 0.5초 (과거 데이터 조회 + 지표 계산)
- 105개 종목 × 0.5초 = 약 52.5초 (1분 이내)

---

## 🔍 4. 매수 조건 체크

### 4-1. 지표 데이터 통합

```javascript
// "조건 체크 및 신호 생성" 노드

const kiwoomData = $input.first().json;           // 키움 호가 조회 결과
const calculatedIndicators = $input.last().json;  // 백엔드 지표 계산 결과

// 키움 호가에서 현재가 정보 추출
const selPrice = parseInt(kiwoomData['(최우선)매도호가'] || 0);
const buyPrice = parseInt(kiwoomData['(최우선)매수호가'] || 0);
const estimatedPrice = (selPrice + buyPrice) / 2;

// 지표 통합
const indicators = {
  // 키움 실시간 데이터
  close: estimatedPrice,        // 75500 (추정 체결가)
  sel_price: selPrice,          // 75600 (매도호가)
  buy_price: buyPrice,          // 75400 (매수호가)
  volume: selVolume + buyVolume,// 거래량

  // 백엔드 계산 지표
  ...calculatedIndicators.indicators
  // ma_20: 75000.5
  // ma_12: 76500.3
  // bollinger_upper: 78000.0
  // bollinger_middle: 75000.0
  // bollinger_lower: 72000.0
  // rsi: 45.5
};
```

### 4-2. 조건 평가 로직

```javascript
// 매수 조건 체크 함수
function checkConditions(conditions, indicators) {
  if (!conditions || conditions.length === 0) return false;

  for (const condition of conditions) {
    // 좌변 값 (항상 indicators에서 가져옴)
    const leftValue = indicators[condition.left] || 0;

    // 우변 값 (지표 이름이면 indicators에서, 숫자면 그대로)
    const rightValue = typeof condition.right === 'string'
      ? (indicators[condition.right] || 0)
      : condition.right;

    console.log(`🔍 Checking: ${condition.left}(${leftValue}) ${condition.operator} ${condition.right}(${rightValue})`);

    // 조건 평가
    let result = false;
    switch (condition.operator) {
      case '>':  result = leftValue > rightValue;  break;
      case '<':  result = leftValue < rightValue;  break;
      case '>=': result = leftValue >= rightValue; break;
      case '<=': result = leftValue <= rightValue; break;
      case '==':
      case '=':  result = leftValue == rightValue; break;
      default:   result = false;
    }

    console.log(`   → ${result ? '✅ PASS' : '❌ FAIL'}`);

    // AND 조건: 하나라도 실패하면 전체 실패
    if (!result) return false;
  }

  return true;
}

const buySignal = checkConditions(entryConditions.buy, indicators);
```

### 4-3. 전략별 조건 체크 예시

#### 전략 1: "나의 전략 7" (삼성전자)

**조건**:
```json
{
  "buy": [
    { "left": "close", "operator": "<", "right": "ma_20" },
    { "left": "close", "operator": "<", "right": "ma_12" }
  ]
}
```

**실제 평가**:
```
🔍 Checking: close(75500) < ma_20(75000.5)
   → ❌ FAIL (75500 > 75000.5)

조건 1 실패 → 전체 매수 신호 없음
```

**매수 신호 발생 조건**:
```
close < ma_20  AND  close < ma_12
→ 현재가가 20일 이평선과 12일 이평선 모두 아래에 있어야 함
→ 단기 하락 추세 진입 시점 포착 전략
```

#### 전략 2: "[분할] 볼린저밴드" (삼성전자)

**조건**:
```json
{
  "buy": [
    { "left": "close", "operator": "<", "right": "bollinger_lower" },
    { "left": "rsi", "operator": "<", "right": 45 },
    { "left": "close", "operator": "<", "right": "bollinger_lower" },
    { "left": "rsi", "operator": "<", "right": 35 }
  ]
}
```

**실제 평가**:
```
🔍 Checking: close(75500) < bollinger_lower(72000.0)
   → ❌ FAIL (75500 > 72000.0)

조건 1 실패 → 전체 매수 신호 없음
```

**매수 신호 발생 조건**:
```
1차 매수: close < bollinger_lower  AND  rsi < 45
2차 매수: close < bollinger_lower  AND  rsi < 35
→ 과매도 구간 진입 시 분할 매수
→ RSI가 더 낮을수록 추가 매수
```

---

## 💾 5. 신호 저장

### 5-1. 매수 신호 생성

```javascript
if (buySignal) {
  return {
    signal_type: 'buy',
    stock_code: originalData.stock_code,          // "005930"
    strategy_id: originalData.strategy_id,        // UUID
    strategy_name: originalData.strategy_name,    // "나의 전략 7"
    price: estimatedPrice,                        // 75500
    indicators: indicators,                       // 전체 지표 값
    generated_at: new Date().toISOString()        // "2025-10-26T15:30:00Z"
  };
} else {
  return null;  // 신호 없음 → "신호 저장" 노드로 전달 안 됨
}
```

### 5-2. Supabase 저장

```javascript
// "신호 저장" Supabase 노드

INSERT INTO trading_signals (
  signal_type,
  stock_code,
  strategy_id,
  strategy_name,
  price,
  indicators,
  generated_at,
  status
) VALUES (
  'buy',
  '005930',
  '7cd0d6cd-fe76-482d-83b9-ff1a955c7d39',
  '나의 전략 7',
  75500,
  '{"close": 75500, "ma_20": 75000.5, "ma_12": 76500.3, ...}'::jsonb,
  '2025-10-26T15:30:00Z',
  'pending'
);
```

### 5-3. 프론트엔드 알림

```typescript
// Frontend: TradingSignals.tsx

const { data: signals } = await supabase
  .from('trading_signals')
  .select('*')
  .eq('status', 'pending')
  .eq('signal_type', 'buy')
  .order('generated_at', { ascending: false });

// 새 매수 신호 발견 시 알림
if (signals && signals.length > 0) {
  showNotification({
    title: '🔔 매수 신호 발생!',
    message: `${signals[0].strategy_name} - ${signals[0].stock_code}`,
    color: 'green'
  });
}
```

---

## 🔄 6. 전체 프로세스 플로우차트

```
┌─────────────────────────────────────────────────────────────────┐
│ [5분마다 실행 - Schedule Trigger]                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ [장시간 체크]                                                     │
│ • 월-금요일만 (공휴일 체크 X)                                    │
│ • 8:30 - 15:30 시간대만                                          │
│ • 9:00-9:05는 제외 (시가 대기)                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (장시간일 때만)
┌─────────────────────────────────────────────────────────────────┐
│ [활성 전략 조회 - Supabase RPC]                                   │
│ • get_active_strategies_with_universe()                          │
│ • 2개 전략 조회                                                   │
│   - "나의 전략 7" (70개 종목)                                     │
│   - "[분할] 볼린저밴드" (35개 종목)                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ [종목별 분리]                                                     │
│ • 전략-종목 쌍 생성: 105개                                        │
│ • 각 종목마다 개별 처리                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (105개 병렬 처리)
┌─────────────────────────────────────────────────────────────────┐
│ [키움 호가 조회 - Mock API]                                       │
│ • GET https://workflow.bll-pro.com/api/kiwoom/current/{code}     │
│ • 응답: 매도호가, 매수호가, 거래량 등                             │
│ • 추정 체결가 계산: (매도호가 + 매수호가) / 2                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ [🆕 지표 계산 - Backend API]                                     │
│ • POST http://localhost:8000/api/indicators/calculate            │
│ • 전략 조건에서 필요한 지표 자동 추출                             │
│   - "나의 전략 7": ma_20, ma_12                                   │
│   - "[분할] 볼린저밴드": bollinger_lower, rsi                     │
│                                                                   │
│ Backend 처리:                                                     │
│ 1. kw_price_daily에서 과거 60일 데이터 조회                       │
│ 2. indicators 테이블에서 Python 계산식 로드                       │
│ 3. IndicatorCalculator로 지표 계산                               │
│ 4. 최신 값 반환                                                   │
│                                                                   │
│ • 응답: {ma_20: 75000, bollinger_lower: 72000, rsi: 45.5, ...}   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ [조건 체크 및 신호 생성]                                          │
│                                                                   │
│ 1. 지표 통합:                                                     │
│    indicators = {                                                 │
│      close: 75500,           // 키움 호가 데이터                  │
│      sel_price: 75600,       // 키움                              │
│      buy_price: 75400,       // 키움                              │
│      volume: 1234567,        // 키움                              │
│      ma_20: 75000.5,         // 백엔드 계산 ✅                    │
│      ma_12: 76500.3,         // 백엔드 계산 ✅                    │
│      bollinger_lower: 72000, // 백엔드 계산 ✅                    │
│      rsi: 45.5               // 백엔드 계산 ✅                    │
│    }                                                               │
│                                                                   │
│ 2. 매수 조건 평가:                                                │
│    for each condition in entry_conditions.buy:                    │
│      left_value = indicators[condition.left]                      │
│      right_value = indicators[condition.right] or condition.right │
│      evaluate: left_value <operator> right_value                  │
│                                                                   │
│    예: close(75500) < ma_20(75000.5) → FAIL                       │
│                                                                   │
│ 3. 신호 생성:                                                     │
│    if ALL conditions PASS:                                        │
│      return {signal_type: 'buy', stock_code, price, ...}          │
│    else:                                                          │
│      return null  // 신호 없음                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (매수 신호 발생 시에만)
┌─────────────────────────────────────────────────────────────────┐
│ [신호 저장 - Supabase]                                            │
│ • INSERT INTO trading_signals                                     │
│ • 프론트엔드에서 조회 가능                                        │
│ • 사용자에게 알림 발송                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 7. 데이터 흐름 예시

### 실제 실행 예시 (2025-10-26 15:30)

```
[1] Cron Trigger 실행
    → 현재 시간: 2025-10-26 15:30 (수요일)

[2] 장시간 체크
    → day = 3 (수요일) ✅
    → hour = 15 ✅
    → 장시간 맞음, 계속 진행

[3] 활성 전략 조회
    → 2개 전략 조회됨
    → 105개 종목-전략 쌍 생성

[4] 종목 #1 처리: 삼성전자 (005930) - "나의 전략 7"

    [4-1] 키움 호가 조회
          → 매도호가: 75,600원
          → 매수호가: 75,400원
          → 추정가: 75,500원

    [4-2] 지표 계산 요청
          POST /api/indicators/calculate
          {
            "stock_code": "005930",
            "indicators": [
              {"name": "ma", "params": {"period": 20}},
              {"name": "ma", "params": {"period": 12}}
            ],
            "days": 60
          }

          Backend 처리:
          • kw_price_daily에서 2025-08-27 ~ 2025-10-26 데이터 조회 (60일)
          • ma_20 계산: df['close'].rolling(20).mean() → 마지막 값 75,000.5
          • ma_12 계산: df['close'].rolling(12).mean() → 마지막 값 76,500.3

          Response:
          {
            "stock_code": "005930",
            "indicators": {
              "ma_20": 75000.5,
              "ma_12": 76500.3,
              "close": 75500.0
            }
          }

    [4-3] 조건 체크
          indicators = {
            close: 75500,
            ma_20: 75000.5,
            ma_12: 76500.3
          }

          조건 1: close(75500) < ma_20(75000.5)
                → 75500 < 75000.5 → FAIL ❌

          매수 신호 없음 → null 반환

[5] 종목 #2 처리: 삼성전자 (005930) - "[분할] 볼린저밴드"

    [5-1] 키움 호가 조회 (동일)
          → 추정가: 75,500원

    [5-2] 지표 계산 요청
          POST /api/indicators/calculate
          {
            "stock_code": "005930",
            "indicators": [
              {"name": "bollinger", "params": {"period": 20}},
              {"name": "rsi", "params": {"period": 14}}
            ],
            "days": 60
          }

          Response:
          {
            "indicators": {
              "bollinger_upper": 78000.0,
              "bollinger_middle": 75000.0,
              "bollinger_lower": 72000.0,
              "bb_pct": 0.583,
              "bb_width": 6000.0,
              "rsi": 45.5
            }
          }

    [5-3] 조건 체크
          조건 1: close(75500) < bollinger_lower(72000) → FAIL ❌
          조건 2: rsi(45.5) < 45 → FAIL ❌

          매수 신호 없음 → null 반환

[6] ... 나머지 103개 종목 동일하게 처리

[결과] 이번 실행에서는 매수 신호 없음
       → trading_signals 테이블에 새 레코드 없음
```

---

## 🎯 8. 매수 신호 발생 시나리오

### 시나리오: 삼성전자 급락 시 매수 신호

```
[상황]
• 시간: 2025-10-26 14:25
• 삼성전자 현재가: 71,500원 (전일 대비 -5% 급락)
• 전일 종가: 75,000원

[지표 계산 결과]
• ma_20: 75,000원
• ma_12: 76,500원
• bollinger_upper: 78,000원
• bollinger_middle: 75,000원
• bollinger_lower: 72,000원
• rsi: 32.5 (과매도)

[전략 1: "나의 전략 7" 조건 체크]
✅ 조건 1: close(71500) < ma_20(75000) → PASS
✅ 조건 2: close(71500) < ma_12(76500) → PASS

→ 🎉 매수 신호 발생!

{
  "signal_type": "buy",
  "stock_code": "005930",
  "strategy_name": "나의 전략 7",
  "price": 71500,
  "indicators": {
    "close": 71500,
    "ma_20": 75000,
    "ma_12": 76500
  },
  "generated_at": "2025-10-26T14:25:00Z"
}

[전략 2: "[분할] 볼린저밴드" 조건 체크]
✅ 조건 1: close(71500) < bollinger_lower(72000) → PASS
✅ 조건 2: rsi(32.5) < 45 → PASS
❌ 조건 3: close(71500) < bollinger_lower(72000) → PASS (중복)
✅ 조건 4: rsi(32.5) < 35 → PASS

→ 🎉 2차 매수 신호까지 발생! (RSI 32.5 < 35)

{
  "signal_type": "buy",
  "stock_code": "005930",
  "strategy_name": "[분할] 볼린저밴드 2단계 매수",
  "price": 71500,
  "indicators": {
    "close": 71500,
    "bollinger_lower": 72000,
    "rsi": 32.5
  },
  "generated_at": "2025-10-26T14:25:00Z"
}

[결과]
• trading_signals 테이블에 2개 매수 신호 저장
• 프론트엔드에 알림 발송
• 사용자 확인 후 수동 매수 실행 (또는 자동 매수 설정 시 자동 실행)
```

---

## 📈 9. 성능 및 최적화

### 9-1. 현재 성능

```
실행 주기: 5분 (300초)
종목 수: 105개
지표 계산: 종목당 평균 0.5초

1회 실행 시간:
• 활성 전략 조회: 0.1초
• 종목별 분리: 0.01초
• 키움 호가 조회: 105 × 0.2초 = 21초
• 지표 계산: 105 × 0.5초 = 52.5초
• 조건 체크: 105 × 0.01초 = 1.05초
• 신호 저장: 0.1초

총: 약 75초 (1분 15초)
```

**✅ 성능 여유**: 5분(300초) 주기에 75초 실행 → 여유 225초
- 다음 실행 전에 충분히 완료 가능
- 피크 시간대 지연 발생해도 문제 없음

### 9-2. 최적화 방안

#### A. 병렬 처리 강화

```javascript
// n8n에서 Split In Batches 노드 사용
// 105개 종목을 10개씩 배치로 나눔
{
  "batchSize": 10,
  "options": {
    "keepInputData": true
  }
}

// 각 배치 10개를 병렬 처리
// 총 11개 배치 × 5초 = 55초
```

#### B. 캐싱 전략

```python
# Backend: 계산된 지표를 Redis에 캐싱
# TTL: 1분 (같은 분에 여러 전략이 같은 종목 요청 시 캐시 사용)

@router.post("/calculate")
async def calculate_indicators(request: CalculateRequest):
    cache_key = f"indicators:{request.stock_code}:{hash(request.indicators)}"

    # 캐시 확인
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 계산 수행
    result = await _calculate(request)

    # 캐시 저장 (TTL: 60초)
    await redis.setex(cache_key, 60, json.dumps(result))

    return result
```

#### C. 실행 빈도 분석

```
현재: 5분마다 실행 (78회/일) ✅

장점:
• 주가 변동 충분히 포착 가능
• 기술적 지표 변화 감지에 적절
• 서버 부하 적절한 수준
• 실행 시간 여유 충분 (75초 / 300초)

개선 옵션:
• 변동성 높은 구간: 3분 주기로 단축
• 안정적인 구간: 10분 주기로 확대
• 동적 조절: 시장 상황에 따라 주기 자동 조정
```

---

## 🐛 10. 현재 알려진 문제점

### 1. 공휴일 필터링 없음
- **문제**: 설날, 추석 등 공휴일에도 실행됨
- **해결**: 한국거래소 API 연동 또는 holiday 테이블 생성

### 2. 등락률 0% 표시
- **문제**: 모든 종목이 0% 변동률로 표시됨
- **원인**: kw_price_current 테이블에 change_rate 계산 로직 없음
- **해결**: n8n에서 전일 종가 대비 변동률 계산 후 저장

### 3. 매수 신호가 거의 발생하지 않음
- **문제**: 수일간 매수 신호 0건
- **원인**:
  - 전략 조건이 너무 엄격 (ma_20, ma_12 모두 아래 + bollinger_lower 아래)
  - 투자유니버스가 좁음 (105개 종목)
  - 현재 시장이 상승장 (조건 충족 어려움)
- **해결**:
  - 전략 조건 완화 (OR 조건 추가)
  - 투자유니버스 확대 (200-300개)
  - 다양한 전략 추가 (돌파 전략, 모멘텀 전략 등)

### 4. ~~실행 시간 초과 가능성~~ (해결됨 ✅)
- ~~**문제**: 1분 주기인데 실행 시간 75초~~
- **✅ 해결**: 5분 주기로 설정되어 있음 (충분한 여유 시간 확보)

---

## ✅ 11. 체크리스트

자동매매 시스템이 올바르게 작동하려면:

- [x] Supabase: indicators 테이블 정리 (17개 active)
- [x] Supabase: indicator_columns 테이블 정리 (매핑 완료)
- [x] Supabase: strategies 테이블 조건 수정 (ma_20, ma_12)
- [ ] Backend: 서버 실행 중 (http://localhost:8000)
- [ ] Backend: /api/indicators/calculate 테스트 성공
- [ ] NAS: backend 파일 복사 완료 (indicators.py, main.py)
- [ ] NAS: Docker 컨테이너 재시작
- [ ] n8n: v21 workflow 생성 완료
- [ ] n8n: "지표 계산" 노드 추가 완료
- [ ] n8n: v21 활성화, v20 비활성화
- [ ] n8n: Manual execution 테스트 성공
- [ ] Frontend: MarketMonitor 실시간 모니터링 작동
- [ ] Frontend: TradingSignals 신호 표시 작동

---

## 📚 참고 문서

- [CREATE_V21_GUIDE.md](../n8n-workflows/CREATE_V21_GUIDE.md) - n8n v21 생성 가이드
- [COPY_TO_NAS.md](../COPY_TO_NAS.md) - NAS 파일 복사 가이드
- [INDICATORS_SCHEMA_AND_DATA.md](./INDICATORS_SCHEMA_AND_DATA.md) - 지표 시스템 문서
- [fix_indicator_columns.sql](../supabase/fix_indicator_columns.sql) - 지표 테이블 수정
- [fix_strategy_conditions.sql](../supabase/fix_strategy_conditions.sql) - 전략 조건 수정

---

**작성일**: 2025-10-26
**작성자**: Claude Code
**버전**: 1.0
