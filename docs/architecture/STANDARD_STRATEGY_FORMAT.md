# 전략 조건 표준 형식 가이드

## 📋 표준 형식: `left/right`

모든 전략 조건은 **`left` - `operator` - `right`** 형식을 사용합니다.

---

## ✅ 표준 형식 (Standard Format)

### 기본 구조
```json
{
  "left": "컬럼명_또는_지표",
  "operator": "연산자",
  "right": "컬럼명_또는_값"
}
```

### 예시

#### 1. 크로스오버 (지표 간 비교)
```json
{
  "left": "macd",
  "operator": "crossover",
  "right": "macd_signal"
}
```

#### 2. 값 비교 (지표 vs 숫자)
```json
{
  "left": "rsi",
  "operator": "<",
  "right": 30
}
```

#### 3. 가격 vs 지표
```json
{
  "left": "close",
  "operator": ">",
  "right": "sma_20"
}
```

#### 4. 지표 vs 지표
```json
{
  "left": "sma_20",
  "operator": ">",
  "right": "sma_60"
}
```

---

## 🚫 폐기된 형식 (Deprecated)

**사용 금지**:
```json
{
  "indicator": "macd",
  "operator": "cross_above",
  "compareTo": "macd_signal"
}
```

**이유**:
- 프리플라이트 호환성
- 중첩 조건 지원 부족
- 명명 일관성

---

## 🎯 지원 연산자

### 비교 연산자
- `>`, `<`, `>=`, `<=`, `==`, `!=`

### 크로스 연산자
- `crossover` - 상향 돌파 (A가 B를 아래→위로)
- `crossunder` - 하향 돌파 (A가 B를 위→아래로)

### 논리 연산자 (중첩 조건)
- `and` - 모든 조건 만족
- `or` - 하나 이상 만족
- `not` - 조건 반전

---

## 📐 완전한 전략 예시

### Golden Cross (골든크로스)
```json
{
  "indicators": [
    {
      "name": "sma",
      "type": "SMA",
      "params": {"period": 20}
    },
    {
      "name": "sma",
      "type": "SMA",
      "params": {"period": 60}
    }
  ],
  "buyConditions": [
    {
      "left": "sma_20",
      "operator": "crossover",
      "right": "sma_60"
    }
  ],
  "sellConditions": [
    {
      "left": "sma_20",
      "operator": "crossunder",
      "right": "sma_60"
    }
  ]
}
```

### MACD + RSI 복합
```json
{
  "indicators": [
    {
      "name": "macd",
      "type": "MACD",
      "params": {"fast": 12, "slow": 26, "signal": 9}
    },
    {
      "name": "rsi",
      "type": "RSI",
      "params": {"period": 14}
    }
  ],
  "buyConditions": [
    {
      "left": "macd",
      "operator": "crossover",
      "right": "macd_signal"
    },
    {
      "left": "macd",
      "operator": ">",
      "right": 0
    },
    {
      "left": "rsi",
      "operator": "<",
      "right": 60
    }
  ],
  "sellConditions": [
    {
      "left": "macd",
      "operator": "crossunder",
      "right": "macd_signal"
    },
    {
      "left": "rsi",
      "operator": ">",
      "right": 70
    }
  ]
}
```

---

## 🔧 프론트엔드 구현 가이드

### TypeScript 타입 정의
```typescript
// src/types/strategy.ts

export type Operator =
  | '>' | '<' | '>=' | '<=' | '==' | '!='
  | 'crossover' | 'crossunder'
  | 'and' | 'or' | 'not';

export interface Condition {
  left: string | number;
  operator: Operator;
  right: string | number;
}

export interface StrategyConfig {
  indicators: Array<{
    name: string;
    type: string;
    params: Record<string, any>;
  }>;
  buyConditions: Condition[];
  sellConditions: Condition[];
}
```

### 조건 빌더 컴포넌트
```tsx
// src/components/ConditionBuilder.tsx

const ConditionBuilder = ({ condition, onChange }) => {
  return (
    <div className="condition-builder">
      {/* Left */}
      <Select
        value={condition.left}
        onChange={(val) => onChange({ ...condition, left: val })}
        options={availableColumns} // ['close', 'macd', 'rsi', 'sma_20', ...]
      />

      {/* Operator */}
      <Select
        value={condition.operator}
        onChange={(val) => onChange({ ...condition, operator: val })}
        options={[
          { value: '>', label: '>' },
          { value: '<', label: '<' },
          { value: 'crossover', label: '상향 돌파' },
          { value: 'crossunder', label: '하향 돌파' }
        ]}
      />

      {/* Right */}
      {isNumericOperator(condition.operator) ? (
        <Input
          type="number"
          value={condition.right}
          onChange={(val) => onChange({ ...condition, right: parseFloat(val) })}
        />
      ) : (
        <Select
          value={condition.right}
          onChange={(val) => onChange({ ...condition, right: val })}
          options={availableColumns}
        />
      )}
    </div>
  );
};
```

### 저장 전 검증
```typescript
// src/hooks/useStrategy.ts

const validateStrategy = (config: StrategyConfig): string[] => {
  const errors: string[] = [];

  // 1. indicators 필수
  if (!config.indicators || config.indicators.length === 0) {
    errors.push('지표를 최소 1개 이상 추가해주세요');
  }

  // 2. 조건 형식 검증
  const validateConditions = (conditions: Condition[], type: string) => {
    conditions.forEach((cond, idx) => {
      if (!cond.left || !cond.operator || cond.right === undefined) {
        errors.push(`${type} 조건 #${idx + 1}: left, operator, right 필수`);
      }

      // left/right 형식 강제
      if ('indicator' in cond || 'compareTo' in cond) {
        errors.push(
          `${type} 조건 #${idx + 1}: 폐기된 형식입니다. left/right를 사용하세요`
        );
      }
    });
  };

  validateConditions(config.buyConditions, '매수');
  validateConditions(config.sellConditions, '매도');

  return errors;
};
```

### 프리플라이트 호출
```typescript
// src/api/backtest.ts

export const preflightStrategy = async (
  config: StrategyConfig,
  stockCodes: string[],
  dateRange: [string, string]
): Promise<PreflightReport> => {
  const response = await fetch('/api/backtest/preflight', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      strategy_config: config,
      stock_codes: stockCodes,
      date_range: dateRange
    })
  });

  const report = await response.json();

  if (!report.passed) {
    throw new Error(
      '전략 검증 실패:\n' +
      report.errors.map(e => e.message).join('\n')
    );
  }

  return report;
};
```

---

## 🧪 테스트 케이스

### 유효한 조건
```json
[
  {"left": "close", "operator": ">", "right": "sma_20"},
  {"left": "rsi", "operator": "<", "right": 30},
  {"left": "macd", "operator": "crossover", "right": "macd_signal"},
  {"left": "sma_20", "operator": ">", "right": "sma_60"}
]
```

### 무효한 조건 (에러)
```json
[
  {"left": "close", "operator": ">"},  // ❌ right 누락
  {"indicator": "macd"},  // ❌ 폐기된 형식
  {"left": "unknown_col", "operator": ">", "right": 0}  // ❌ 존재하지 않는 컬럼
]
```

---

## 📊 지표명 → 컬럼명 매핑

| 지표명 | 생성 컬럼 |
|--------|----------|
| `sma` | `sma`, `sma_20` (period 기반) |
| `ema` | `ema`, `ema_12` |
| `macd` | `macd`, `macd_signal`, `macd_hist` |
| `rsi` | `rsi` |
| `bollinger_bands` (`bb`) | `bb_upper`, `bb_middle`, `bb_lower` |
| `stochastic` | `stoch_k`, `stoch_d` |
| `atr` | `atr` |

**주의**: `sma` 지표의 경우 `params.period`에 따라 `sma_20`, `sma_60` 등으로 컬럼명이 달라집니다.

---

## 🔄 마이그레이션 체크리스트

### 백엔드 (완료)
- [x] Supabase 스키마 강화 (Phase 1)
- [x] 프리플라이트 2가지 형식 지원
- [x] indicator_columns 표준표
- [x] 템플릿 전략 재생성 (left/right)

### 프론트엔드 (TODO)
- [ ] TypeScript 타입 정의 (`left/right`)
- [ ] 조건 빌더 컴포넌트 수정
- [ ] 저장 전 형식 검증
- [ ] 프리플라이트 API 호출
- [ ] 에러 메시지 UI 표시

### 테스트
- [ ] 템플릿 전략 백테스트 (8개)
- [ ] 사용자 전략 생성 → 저장 → 백테스트
- [ ] 프리플라이트 실패 케이스 (누락 지표)

---

## 📞 문의

형식 관련 질문은 `PHASE_2.5_DEPLOYMENT.md` 참조