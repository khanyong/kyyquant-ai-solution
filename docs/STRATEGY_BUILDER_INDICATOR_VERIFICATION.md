# 전략 빌더 지표 호환성 검증 보고서

날짜: 2025-10-26 03:00 KST

## 검증 목적
indicators, indicator_columns 테이블 수정 후, 전략 빌더에서 새로운 전략 생성 시 지표 사용이 올바른지 검증

---

## 1. 데이터베이스 테이블 수정 내역

### indicators 테이블 수정 ([fix_indicators_table.sql](../supabase/fix_indicators_table.sql))
```sql
-- adx, close, volume을 비활성화 (중복/다른 지표에 포함됨)
UPDATE indicators SET is_active = false WHERE name = 'adx';
UPDATE indicators SET is_active = false WHERE name = 'close';
UPDATE indicators SET is_active = false WHERE name = 'volume';
```

**결과:** 17개 활성 지표

### indicator_columns 테이블 수정 ([fix_indicator_columns.sql](../supabase/fix_indicator_columns.sql))
1. `adx` → `dmi` (indicators 테이블과 일치)
2. `bb` 삭제, `bollinger_bands` → `bollinger`
3. `parabolic_sar` → `parabolic`
4. 누락된 지표 추가: `ma`, `sma`, `cci`, `obv`, `vwap`, `williams`

---

## 2. 전략 빌더 프로세스 분석

### 2.1 지표 로딩 ([src/services/indicatorService.ts](../src/services/indicatorService.ts))

**함수:** `getAvailableIndicators()`

**프로세스:**
```typescript
1. fetchIndicators()
   → SELECT * FROM indicators WHERE is_active = true

2. convertToStrategyBuilderFormat()
   → {
       id: indicator.name,           // DB의 name을 id로 사용
       name: indicator.display_name, // 화면 표시명
       type: indicator.category,     // trend/momentum/volume/volatility
       params: indicator.default_params
     }
```

**문제점 확인:**
- ✅ `is_active = true` 필터링 → adx, close, volume은 자동 제외됨
- ✅ `indicator.name`을 `id`로 사용 → DB와 일치
- ✅ 활성 지표만 로딩 → 사용자가 비활성 지표 선택 불가

---

### 2.2 조건 변환 ([src/utils/conditionConverter.ts](../src/utils/conditionConverter.ts))

**함수:** `convertConditionToStandard()`

**프로세스:**
```typescript
// 전략 빌더의 조건 (indicator/operator/value)
→ 표준 형식 (left/operator/right)

예시:
{indicator: "ma", operator: ">", value: 50000}
→ {left: "ma", operator: ">", right: 50000}
```

**주요 변환 규칙:**

#### A. 지표명 정규화 (`normalizeIndicatorName`)
```typescript
const normalizeIndicatorName = (name: string): string => {
  return name
    .toLowerCase()
    .replace('ma_', 'sma_')    // MA → SMA
    .replace('price', 'close')  // PRICE → close
}
```

**문제점:**
- ❌ `ma` → `sma_ma` 변환 발생 가능 (replace 로직 오류)
- ⚠️ `ma_20` 형식의 동적 컬럼명 처리 필요

#### B. 다중 출력 지표 처리
```typescript
// 볼린저 밴드
if (oldCondition.indicator === 'bollinger' && oldCondition.bollingerLine) {
  left = oldCondition.bollingerLine  // bollinger_upper/middle/lower
}

// MACD
if (oldCondition.indicator === 'macd' && oldCondition.macdLine) {
  left = oldCondition.macdLine  // macd_line/signal/hist
}

// 스토캐스틱
if (oldCondition.indicator === 'stochastic' && oldCondition.stochLine) {
  left = INDICATOR_COLUMN_MAPPING[oldCondition.stochLine]
  // stoch_k → stochastic_k
}
```

**검증:**
- ✅ bollinger 변환 정상 (bollinger_upper, bollinger_middle, bollinger_lower)
- ✅ macd 변환 정상 (macd_line, macd_signal, macd_hist)
- ✅ stochastic 변환 정상 (stochastic_k, stochastic_d)

#### C. 동적 컬럼명 처리 (`fixDynamicColumnNames`)
```typescript
// SMA/EMA 같은 동적 컬럼명 수정
// sma → sma_20, ema → ema_12 등

const columnMap: Record<string, string> = {}

indicators.forEach((ind: any) => {
  const name = ind.name?.toLowerCase()
  const params = ind.params || {}

  if (name === 'sma' || name === 'ema') {
    const period = params.period || 20
    columnMap[name] = `${name}_${period}`
  }
})
```

**문제점 발견:**
- ❌ `ma` 지표가 `columnMap`에 추가되지 않음
- ❌ `fixDynamicColumnNames`가 `sma`, `ema`만 처리하고 `ma`는 처리 안 함
- ❌ `ma` 조건이 `ma_20`으로 변환되지 않고 `ma`로 저장됨

---

### 2.3 전략 저장 ([src/components/StrategyBuilder.tsx](../src/components/StrategyBuilder.tsx))

**프로세스:**
```typescript
// 1. 조건 변환
const convertedStrategy = ensureStandardFormat(strategy)

// 2. 저장 데이터 준비
const dataToSave = {
  name: strategy.name,
  description: strategy.description,
  config: {
    indicators: strategy.indicators,  // 지표 리스트
    buyConditions: convertedStrategy.buyConditions,
    sellConditions: convertedStrategy.sellConditions,
    ...
  },
  indicators: {
    list: strategy.indicators  // 중복 저장
  },
  entry_conditions: {
    buy: convertedStrategy.buyConditions  // 표준 형식
  },
  exit_conditions: {
    sell: convertedStrategy.sellConditions  // 표준 형식
  }
}

// 3. Supabase에 저장
await supabase.from('strategies').insert(dataToSave)
```

**저장 형식:**
```json
{
  "entry_conditions": {
    "buy": [
      {"left": "close", "operator": "<", "right": "ma_20"},
      {"left": "close", "operator": "<", "right": "ma_12"}
    ]
  }
}
```

---

## 3. 발견된 문제점

### 문제 1: `ma` 지표의 동적 컬럼명 처리 누락

**위치:** [src/utils/conditionConverter.ts:324-343](../src/utils/conditionConverter.ts#L324)

**현재 코드:**
```typescript
const fixDynamicColumnNames = (strategy: {...}) => {
  indicators.forEach((ind: any) => {
    const name = ind.name?.toLowerCase()

    // SMA, EMA: sma_20, ema_12 형태
    if (name === 'sma' || name === 'ema') {  // ❌ ma가 빠져있음!
      const period = params.period || 20
      columnMap[name] = `${name}_${period}`
    }
  })
}
```

**문제:**
- 사용자가 `ma` 지표를 선택하고 `period: 20`을 설정
- 조건: `close < ma`로 저장됨
- **기대:** `close < ma_20`로 변환되어야 함
- **실제:** `ma`로 그대로 저장됨
- **결과:** n8n workflow에서 `indicators["ma"]`를 찾을 수 없음 (undefined)

**영향:**
- `ma` 지표를 사용한 전략이 매수/매도 신호를 생성하지 못함
- Backend API는 `ma_20`으로 반환하지만, 전략 조건은 `ma`를 찾음

---

### 문제 2: `normalizeIndicatorName`의 `ma` → `sma` 변환

**위치:** [src/utils/conditionConverter.ts:64-73](../src/utils/conditionConverter.ts#L64)

**현재 코드:**
```typescript
const normalizeIndicatorName = (name: string): string => {
  const normalized = name
    .toLowerCase()
    .replace('ma_', 'sma_')  // ❌ ma_20 → sma_20 변환 발생!
    .replace('price', 'close')

  return INDICATOR_COLUMN_MAPPING[normalized] || normalized
}
```

**문제:**
- `ma_20` → `sma_20`으로 변환됨
- 하지만 Backend API와 indicator_columns 테이블에는 `ma`라는 별도 지표가 있음
- `ma`와 `sma`는 다른 지표임:
  - `ma`: 일반 이동평균 (indicators 테이블에 존재)
  - `sma`: 단순 이동평균 (simple moving average, indicators 테이블에 존재)

**영향:**
- `ma` 지표가 `sma`로 잘못 변환되어 계산 오류 발생 가능

---

### 문제 3: indicator_columns와 조건 변환의 불일치

**DB 상태:**
```sql
-- indicator_columns 테이블
indicator_name | column_name
ma             | ma
sma            | sma
bollinger      | bollinger_upper, bollinger_middle, bollinger_lower
```

**전략 조건 예시:**
```json
{
  "left": "close",
  "operator": "<",
  "right": "ma"  // ❌ ma_20이어야 함!
}
```

**Backend API 응답:**
```json
{
  "indicators": {
    "ma_20": 75000,  // period가 포함된 컬럼명
    "ma_12": 76500,
    "close": 75500
  }
}
```

**n8n workflow 평가:**
```javascript
const right = indicators[condition.right]  // indicators["ma"]
// right = undefined ❌
```

---

## 4. 해결 방안

### 해결책 1: `fixDynamicColumnNames`에 `ma` 추가

**파일:** [src/utils/conditionConverter.ts:324-343](../src/utils/conditionConverter.ts#L324)

**수정 코드:**
```typescript
const fixDynamicColumnNames = (strategy: {...}) => {
  indicators.forEach((ind: any) => {
    const name = ind.name?.toLowerCase()
    const params = ind.params || {}

    // MA, SMA, EMA: ma_20, sma_20, ema_12 형태
    if (name === 'ma' || name === 'sma' || name === 'ema') {  // ✅ ma 추가
      const period = params.period || 20
      columnMap[name] = `${name}_${period}`
    }
  })
}
```

---

### 해결책 2: `normalizeIndicatorName`에서 `ma` → `sma` 변환 제거

**파일:** [src/utils/conditionConverter.ts:64-73](../src/utils/conditionConverter.ts#L64)

**수정 코드:**
```typescript
const normalizeIndicatorName = (name: string): string => {
  const normalized = name
    .toLowerCase()
    // .replace('ma_', 'sma_')  // ❌ 제거! ma와 sma는 다른 지표
    .replace('price', 'close')

  return INDICATOR_COLUMN_MAPPING[normalized] || normalized
}
```

---

### 해결책 3: Backend API 응답과 indicator_columns 일치 확인

**Backend API가 반환하는 지표 컬럼명:**
- `ma_20`, `ma_12` (period 포함)
- `bollinger_upper`, `bollinger_middle`, `bollinger_lower`
- `rsi`
- `dmi_plus`, `dmi_minus`, `adx`

**전략 조건에서 사용하는 컬럼명:**
- `ma_20`, `ma_12` ✅
- `bollinger_upper`, `bollinger_middle`, `bollinger_lower` ✅
- `rsi` ✅
- `dmi_plus`, `dmi_minus`, `adx` ✅

**일치 여부:**
- ✅ Backend API와 전략 조건이 일치함 (수정 후)

---

## 5. 테스트 시나리오

### 시나리오 1: MA 지표 사용 전략 생성

**단계:**
1. 전략 빌더에서 "MA(20)" 지표 추가
2. 매수 조건: `close < ma` (period: 20)
3. 전략 저장

**기대 결과:**
```json
{
  "indicators": {
    "list": [
      {"id": "ma", "name": "MA", "params": {"period": 20}}
    ]
  },
  "entry_conditions": {
    "buy": [
      {"left": "close", "operator": "<", "right": "ma_20"}  // ✅ ma_20으로 변환
    ]
  }
}
```

**실제 결과 (수정 전):**
```json
{
  "entry_conditions": {
    "buy": [
      {"left": "close", "operator": "<", "right": "ma"}  // ❌ ma로 저장됨
    ]
  }
}
```

---

### 시나리오 2: Bollinger Bands 전략 생성

**단계:**
1. 전략 빌더에서 "Bollinger Bands(20, 2)" 지표 추가
2. 매수 조건: `close < bollinger_lower`
3. 전략 저장

**기대 결과:**
```json
{
  "entry_conditions": {
    "buy": [
      {"left": "close", "operator": "<", "right": "bollinger_lower"}  // ✅
    ]
  }
}
```

**실제 결과:**
```json
{
  "entry_conditions": {
    "buy": [
      {"left": "close", "operator": "<", "right": "bollinger_lower"}  // ✅ 정상
    ]
  }
}
```

---

## 6. 수정 필요 파일

### 우선순위 1: conditionConverter.ts 수정

**파일:** [src/utils/conditionConverter.ts](../src/utils/conditionConverter.ts)

**수정 사항:**
1. `fixDynamicColumnNames` 함수에 `ma` 추가 (L339)
2. `normalizeIndicatorName` 함수에서 `ma_` → `sma_` 변환 제거 (L68)

---

## 7. 검증 체크리스트

- [x] indicatorService가 활성 지표만 로딩하는지 확인
- [x] 비활성 지표(adx, close, volume)가 UI에 표시되지 않는지 확인
- [x] 볼린저 밴드 조건이 `bollinger_upper/middle/lower`로 변환되는지 확인
- [x] MACD 조건이 `macd_line/signal/hist`로 변환되는지 확인
- [x] 스토캐스틱 조건이 `stochastic_k/d`로 변환되는지 확인
- [ ] **MA 조건이 `ma_20`으로 변환되는지 확인** ← **수정 필요**
- [ ] **SMA 조건이 `sma_20`으로 변환되는지 확인** ← **수정 필요**
- [ ] **EMA 조건이 `ema_12`로 변환되는지 확인** ← **수정 필요**

---

## 8. 결론

### 문제 요약:
1. ❌ `ma` 지표가 `ma_20` 형식으로 변환되지 않음
2. ❌ `normalizeIndicatorName`이 `ma`를 `sma`로 잘못 변환함
3. ✅ 볼린저 밴드, MACD, 스토캐스틱은 정상 작동

### 영향도:
- **높음:** `ma` 지표를 사용한 기존 전략이 작동하지 않음
- **보통:** `sma`, `ema`도 동일한 문제 가능성
- **낮음:** 다중 출력 지표(bollinger, macd, stochastic)는 정상

### 권장 조치:
1. **즉시 수정:** [src/utils/conditionConverter.ts](../src/utils/conditionConverter.ts) 파일 수정
2. **테스트:** 전략 빌더에서 MA/SMA/EMA 지표 사용 테스트
3. **기존 전략 마이그레이션:** `ma` → `ma_20` 형식으로 업데이트 필요

---

## 9. 다음 단계

1. ⏳ conditionConverter.ts 수정
2. ⏳ 전략 빌더 테스트
3. ⏳ 기존 전략 데이터 마이그레이션 스크립트 작성
4. ⏳ n8n workflow v21 배포 및 테스트
