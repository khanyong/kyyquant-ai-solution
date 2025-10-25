# n8n Workflow v21 생성 가이드

자동매매 시스템에 **기술적 지표 계산** 기능을 추가한 v21 workflow를 생성합니다.

## 🎯 주요 변경사항

### v20 → v21 차이점

**v20 (현재)**:
```javascript
const indicators = {
  close: estimatedPrice,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: selVolume + buyVolume
};
// ❌ ma_20, bollinger_lower, rsi 등 미계산!
```

**v21 (목표)**:
```javascript
const indicators = {
  close: estimatedPrice,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: selVolume + buyVolume,
  ma_20: 75000,              // ✅ 백엔드에서 계산
  ma_12: 76500,              // ✅ 백엔드에서 계산
  bollinger_upper: 78000,    // ✅ 백엔드에서 계산
  bollinger_middle: 75000,   // ✅ 백엔드에서 계산
  bollinger_lower: 72000,    // ✅ 백엔드에서 계산
  rsi: 45.5                  // ✅ 백엔드에서 계산
};
```

---

## 📋 v21 Workflow 생성 단계

### 1단계: v20 복사하여 v21 생성

1. n8n에서 "auto-trading-with-capital-validation-v20" workflow 열기
2. "Save As" → "auto-trading-with-capital-validation-v21"로 저장
3. Description 수정: "지표 계산 기능 추가 (백엔드 API 연동)"

### 2단계: 새 노드 추가 위치 확인

```
[활성 전략 조회]
    ↓
[종목별 분리]
    ↓
[키움 호가 조회]
    ↓
[🆕 지표 계산] ← 여기에 새 노드 추가!
    ↓
[조건 체크 및 신호 생성]
    ↓
[신호 저장]
```

### 3단계: "지표 계산" HTTP Request 노드 생성

**Node Settings**:
- **Name**: `지표 계산`
- **Node Type**: HTTP Request
- **Method**: POST
- **URL**: `http://localhost:8000/api/indicators/calculate`
- **Authentication**: None
- **Body Content Type**: JSON

**Request Body** (Code 탭에서 작성):
```javascript
const stockCode = $input.item.json._original_stock_code;
const entryConditions = $input.item.json._original_entry_conditions;

// 전략 조건에서 필요한 지표 추출
function extractRequiredIndicators(conditions) {
  const indicators = new Set();

  if (conditions && conditions.buy) {
    for (const condition of conditions.buy) {
      // right 값이 지표 이름인 경우
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

console.log('📊 Required indicators:', requiredIndicators);

// 지표별로 요청 형식 변환
const indicatorRequests = requiredIndicators.map(indicator => {
  // ma_20 → {name: "ma", params: {period: 20}}
  if (indicator.startsWith('ma_')) {
    const period = parseInt(indicator.split('_')[1]);
    return {
      name: 'ma',
      params: { period: period }
    };
  }

  // bollinger_lower, bollinger_upper 등 → {name: "bollinger", params: {period: 20}}
  if (indicator.startsWith('bollinger_')) {
    return {
      name: 'bollinger',
      params: { period: 20, std_dev: 2 }
    };
  }

  // rsi → {name: "rsi", params: {period: 14}}
  if (indicator === 'rsi') {
    return {
      name: 'rsi',
      params: { period: 14 }
    };
  }

  // 기타 지표
  return {
    name: indicator,
    params: {}
  };
});

// 중복 제거 (bollinger는 한 번만 계산)
const uniqueIndicators = [];
const seen = new Set();

for (const req of indicatorRequests) {
  const key = `${req.name}_${JSON.stringify(req.params)}`;
  if (!seen.has(key)) {
    uniqueIndicators.push(req);
    seen.add(key);
  }
}

return {
  stock_code: stockCode,
  indicators: uniqueIndicators,
  days: 60
};
```

**Options**:
- Response Format: JSON
- Timeout: 30000 (30초)
- Retry on Fail: Yes (2회)

### 4단계: "조건 체크 및 신호 생성" 노드 수정

기존 노드의 Code를 수정합니다:

```javascript
const kiwoomData = $input.first().json;  // 키움 호가 조회 결과
const calculatedIndicators = $input.last().json;  // 지표 계산 결과

console.log('🔄 조건 체크 시작');
console.log('📦 Kiwoom data:', kiwoomData);
console.log('📊 Calculated indicators:', calculatedIndicators);

// 원본 데이터 복원
const originalData = {
  stock_code: kiwoomData._original_stock_code,
  strategy_id: kiwoomData._original_strategy_id,
  strategy_name: kiwoomData._original_strategy_name,
  entry_conditions: kiwoomData._original_entry_conditions,
  exit_conditions: kiwoomData._original_exit_conditions
};

// 키움 호가 데이터에서 현재가 정보 추출
const selPrice = parseInt(kiwoomData['(최우선)매도호가'] || 0);
const buyPrice = parseInt(kiwoomData['(최우선)매수호가'] || 0);
const selVolume = parseInt(kiwoomData['매도호가수량1'] || 0);
const buyVolume = parseInt(kiwoomData['매수호가수량1'] || 0);
const estimatedPrice = (selPrice + buyPrice) / 2;

// 지표 통합: 키움 데이터 + 백엔드 계산 결과
const indicators = {
  close: estimatedPrice,
  sel_price: selPrice,
  buy_price: buyPrice,
  volume: selVolume + buyVolume,
  ...calculatedIndicators.indicators  // ✅ 백엔드에서 계산된 지표 추가!
};

console.log('📊 Final indicators:', indicators);

// 매수 조건 체크
function checkConditions(conditions, indicators) {
  if (!conditions || conditions.length === 0) return false;

  for (const condition of conditions) {
    const leftValue = indicators[condition.left] || 0;
    const rightValue = typeof condition.right === 'string'
      ? (indicators[condition.right] || 0)
      : condition.right;

    console.log(`🔍 Checking: ${condition.left}(${leftValue}) ${condition.operator} ${condition.right}(${rightValue})`);

    let result = false;

    switch (condition.operator) {
      case '>':
        result = leftValue > rightValue;
        break;
      case '<':
        result = leftValue < rightValue;
        break;
      case '>=':
        result = leftValue >= rightValue;
        break;
      case '<=':
        result = leftValue <= rightValue;
        break;
      case '==':
      case '=':
        result = leftValue == rightValue;
        break;
      default:
        result = false;
    }

    console.log(`   → ${result ? '✅ PASS' : '❌ FAIL'}`);

    if (!result) return false;  // AND 조건이므로 하나라도 실패하면 false
  }

  return true;
}

const buySignal = checkConditions(originalData.entry_conditions.buy, indicators);

console.log(`🎯 Buy signal: ${buySignal ? '✅ BUY' : '❌ NO SIGNAL'}`);

if (buySignal) {
  return {
    signal_type: 'buy',
    stock_code: originalData.stock_code,
    strategy_id: originalData.strategy_id,
    strategy_name: originalData.strategy_name,
    price: estimatedPrice,
    indicators: indicators,
    generated_at: new Date().toISOString()
  };
} else {
  return null;  // 신호 없음
}
```

### 5단계: 노드 연결 수정

기존:
```
[키움 호가 조회] → [조건 체크 및 신호 생성]
```

변경:
```
[키움 호가 조회] → [지표 계산]
                  ↓
[조건 체크 및 신호 생성] (입력 2개: 키움 데이터 + 지표 데이터)
```

**중요**: "조건 체크 및 신호 생성" 노드 설정
- Input mode: "Combine"
- Combine By: "Combine All"
- Include Other Fields: "All"

### 6단계: 테스트

1. **Manual Execution** 버튼 클릭
2. 각 노드의 실행 결과 확인:
   - ✅ "지표 계산" 노드: `{"stock_code": "005930", "indicators": {"ma_20": 75000, ...}}`
   - ✅ "조건 체크 및 신호 생성" 노드: 통합된 indicators 객체 확인
3. 콘솔 로그 확인:
   - `📊 Required indicators: ["ma_20", "ma_12", "bollinger_lower", ...]`
   - `📊 Final indicators: {close: 75500, ma_20: 75000, ...}`
   - `🔍 Checking: close(75500) < ma_20(75000)` → PASS/FAIL

### 7단계: 저장 및 활성화

1. **Save** 버튼 클릭
2. **Activate** 토글 켜기
3. v20 workflow **Deactivate** (비활성화)

---

## 🔧 백엔드 서버 준비

v21 workflow가 작동하려면 백엔드 서버가 실행 중이어야 합니다:

```bash
cd d:\Dev\auto_stock\backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**API 테스트**:
```bash
curl -X POST http://localhost:8000/api/indicators/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "005930",
    "indicators": [
      {"name": "ma", "params": {"period": 20}},
      {"name": "ma", "params": {"period": 12}},
      {"name": "bollinger", "params": {"period": 20}},
      {"name": "rsi", "params": {"period": 14}}
    ],
    "days": 60
  }'
```

**기대 응답**:
```json
{
  "stock_code": "005930",
  "indicators": {
    "ma_20": 75000.5,
    "ma_12": 76500.3,
    "bollinger_upper": 78000,
    "bollinger_middle": 75000,
    "bollinger_lower": 72000,
    "rsi": 45.5,
    "close": 75500
  },
  "calculated_at": "2025-10-26T15:30:00"
}
```

---

## 📊 전략 조건 확인

v21이 올바르게 작동하려면 전략 조건이 수정되어 있어야 합니다:

### "나의 전략 7"
```json
{
  "buy": [
    { "left": "close", "operator": "<", "right": "ma_20" },  // ✅
    { "left": "close", "operator": "<", "right": "ma_12" }   // ✅
  ]
}
```

### "[분할] 볼린저밴드 2단계 매수"
```json
{
  "buy": [
    { "left": "close", "operator": "<", "right": "bollinger_lower" },  // ✅
    { "left": "rsi", "operator": "<", "right": 45 }                    // ✅
  ]
}
```

전략 조건 수정이 안 되어 있다면 `d:\Dev\auto_stock\supabase\fix_strategy_conditions.sql` 실행!

---

## ✅ 완료 체크리스트

- [ ] Supabase: indicators/indicator_columns 테이블 정리 완료
- [ ] Supabase: 전략 조건 수정 완료 (ma_20, ma_12 등)
- [ ] 백엔드: `/api/indicators/calculate` API 테스트 성공
- [ ] n8n: v21 workflow 생성 및 "지표 계산" 노드 추가
- [ ] n8n: "조건 체크 및 신호 생성" 노드 수정
- [ ] n8n: 노드 연결 및 설정 확인
- [ ] n8n: Manual execution 테스트 성공
- [ ] n8n: v21 활성화, v20 비활성화
- [ ] 실전: 매수 신호 발생 확인!

---

## 🐛 트러블슈팅

### 문제 1: "지표 계산" 노드에서 404 에러
**원인**: 백엔드 서버가 실행되지 않음
**해결**: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` 실행

### 문제 2: "No historical data found for XXX"
**원인**: kw_price_daily 테이블에 해당 종목의 과거 데이터 없음
**해결**: 해당 종목의 일봉 데이터를 kw_price_daily에 추가

### 문제 3: 여전히 매수 신호가 안 나옴
**원인**: 전략 조건이 너무 엄격함
**해결**:
1. Manual execution으로 indicators 값 확인
2. 실제 조건 체크 로그 확인: `🔍 Checking: close(75500) < ma_20(75000)` → FAIL
3. 전략 조건 완화 또는 투자유니버스 확대

### 문제 4: bollinger_lower 값이 계산 안 됨
**원인**: indicators 테이블의 bollinger output_columns 불일치
**해결**: `d:\Dev\auto_stock\supabase\fix_indicator_columns.sql` 재실행

---

## 📝 다음 단계

v21이 성공적으로 작동하면:
1. **등락률 계산** 추가 (0% 문제 해결)
2. **휴일 필터링** 추가 (공휴일 제외)
3. **매도 신호** 로직 추가
4. **자본 검증** 강화

---

**문서 작성일**: 2025-10-26
**작성자**: Claude Code
**버전**: 1.0
