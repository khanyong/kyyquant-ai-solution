# 전략별 자금 할당 가이드

## 개요

각 전략에 서로 다른 자금을 할당하여 보유 잔고를 세분화하고 리스크를 분산할 수 있습니다.

## 자금 할당 방식

### 1. 할당 자금 (allocated_capital)
정확한 금액을 원 단위로 지정합니다.

**예시:**
```typescript
{
  name: "RSI 전략",
  allocated_capital: 3000000,  // 3,000,000원
  positionSize: 50,            // 할당 자금의 50% = 1,500,000원
  maxPositions: 2
}
```

### 2. 할당 비율 (allocated_percent)
전체 계좌 잔고 대비 비율(%)로 지정합니다.

**예시:**
```typescript
{
  name: "골든크로스",
  allocated_percent: 30,  // 계좌 잔고의 30%
  positionSize: 20,       // 할당 자금의 20%
  maxPositions: 5
}
```

## 사용 예시

### 예시 1: 총 계좌 잔고 10,000,000원

```typescript
// 전략 A: 보수적 (30%)
{
  name: "보수적 전략",
  allocated_percent: 30,     // 3,000,000원
  positionSize: 10,          // 종목당 300,000원
  maxPositions: 10           // 최대 10종목
}

// 전략 B: 공격적 (50%)
{
  name: "공격적 전략",
  allocated_percent: 50,     // 5,000,000원
  positionSize: 25,          // 종목당 1,250,000원
  maxPositions: 4            // 최대 4종목
}

// 전략 C: 분산형 (20%)
{
  name: "분산 전략",
  allocated_percent: 20,     // 2,000,000원
  positionSize: 5,           // 종목당 100,000원
  maxPositions: 20           // 최대 20종목
}

// 총 할당: 100% (10,000,000원)
```

### 예시 2: 고정 금액 할당

```typescript
// 전략 A: 3백만원
{
  name: "단기 매매",
  allocated_capital: 3000000,
  positionSize: 50,
  maxPositions: 2
}

// 전략 B: 5백만원
{
  name: "중기 투자",
  allocated_capital: 5000000,
  positionSize: 20,
  maxPositions: 5
}

// 전략 C: 2백만원
{
  name: "장기 보유",
  allocated_capital: 2000000,
  positionSize: 100,
  maxPositions: 1
}
```

## 자금 할당 규칙

### ✅ 권장 사항
1. **총 할당 비율은 80-100%** 사이 유지
2. **단일 전략에 50% 이상 집중 지양**
3. **최소 3개 이상 전략 분산**
4. **할당 방식 통일** (자금 또는 비율 중 하나)

### ⚠️ 제한 사항
1. **총 할당 비율 100% 초과 불가**
2. **할당 자금이 계좌 잔고 초과 불가**
3. **음수 값 불가**

## UI 사용법

### 1. 전략 생성/수정 시

**자동매매** 탭 → **전략 만들기** → **리스크 관리** 섹션:

```
💰 전략별 자금 할당
┌────────────────────────────┬────────────────────────────┐
│ 할당 자금 (원)              │ 할당 비율 (%)              │
│ [    3,000,000    ] 원     │ [      30      ] %         │
└────────────────────────────┴────────────────────────────┘

ℹ️ 자금 할당 방식:
• 할당 자금: 정확한 금액 지정 (예: 3,000,000원)
• 할당 비율: 계좌 잔고의 일정 비율 (예: 30%)
• 포지션 크기는 할당된 자금 내에서 계산됩니다
```

### 2. 모니터링 화면

**모니터링** 탭에서 전략별 할당 현황 확인:

```
💰 전략별 자금 할당
┌─────────────────────────────────┐
│ RSI 전략                        │
│ 3,000,000원  30%                │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ 골든크로스                       │
│ 5,000,000원  50%                │
└─────────────────────────────────┘
```

## 프로그래밍 API

### 자금 할당 검증

```typescript
import { validateCapitalAllocation } from '@/utils/capitalAllocationValidator'

const strategies = [
  { name: "전략A", allocated_percent: 30, is_active: true },
  { name: "전략B", allocated_percent: 50, is_active: true },
  { name: "전략C", allocated_percent: 30, is_active: true }
]

const result = validateCapitalAllocation(strategies, 10000000)

if (!result.isValid) {
  console.error("할당 오류:", result.errors)
}
// result.totalPercent: 110 (초과!)
// result.errors: ["전체 할당 비율이 110%로 100%를 초과합니다."]
```

### 균등 배분

```typescript
import { autoAllocateEqual } from '@/utils/capitalAllocationValidator'

const strategies = [
  { name: "전략A", is_active: true },
  { name: "전략B", is_active: true },
  { name: "전략C", is_active: true }
]

const allocated = autoAllocateEqual(strategies)
// 각 전략에 33.33% 자동 할당
```

### 비율 ↔ 자금 변환

```typescript
import {
  convertPercentToCapital,
  convertCapitalToPercent
} from '@/utils/capitalAllocationValidator'

// 비율 → 자금
const withCapital = convertPercentToCapital(strategies, 10000000)

// 자금 → 비율
const withPercent = convertCapitalToPercent(strategies, 10000000)
```

### 사용 가능 자금 계산

```typescript
import { calculateAvailableCapital } from '@/utils/capitalAllocationValidator'

const strategy = {
  allocated_capital: 3000000,
  allocated_percent: 30
}

const available = calculateAvailableCapital(strategy, 10000000)
// 3,000,000원 (allocated_capital 우선)
```

## n8n 워크플로우 연동

n8n에서 매수 주문 시 전략별 할당 자금을 기준으로 계산:

```javascript
// n8n Function 노드
const strategy = $input.item.json.strategy
const accountBalance = 10000000

// 사용 가능 자금 계산
let availableCapital = 0
if (strategy.allocated_capital > 0) {
  availableCapital = strategy.allocated_capital
} else if (strategy.allocated_percent > 0) {
  availableCapital = accountBalance * strategy.allocated_percent / 100
}

// 포지션 크기 적용
const orderAmount = availableCapital * strategy.positionSize / 100

return {
  json: {
    ...strategy,
    available_capital: availableCapital,
    order_amount: orderAmount
  }
}
```

## DB 스키마

```sql
-- strategies 테이블
ALTER TABLE strategies
ADD COLUMN allocated_capital DECIMAL(15, 2) DEFAULT 0,
ADD COLUMN allocated_percent DECIMAL(5, 2) DEFAULT 0;

-- 전략별 자금 할당 통계 뷰
CREATE VIEW strategy_capital_allocation AS
SELECT
  user_id,
  COUNT(*) as total_strategies,
  COUNT(*) FILTER (WHERE is_active = true) as active_strategies,
  SUM(allocated_capital) FILTER (WHERE is_active = true) as total_allocated_capital,
  SUM(allocated_percent) FILTER (WHERE is_active = true) as total_allocated_percent,
  100 - COALESCE(SUM(allocated_percent) FILTER (WHERE is_active = true), 0) as remaining_percent
FROM strategies
GROUP BY user_id;
```

## 마이그레이션

```bash
# Supabase SQL Editor에서 실행
\i supabase/migrations/add_strategy_capital_allocation.sql
```

## 참고 자료

- [전략 빌더 사용법](./STRATEGY_BUILDER_GUIDE.md)
- [리스크 관리 가이드](./RISK_MANAGEMENT_GUIDE.md)
- [n8n 워크플로우 설정](./N8N_SETUP_GUIDE.md)
