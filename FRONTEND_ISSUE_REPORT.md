# 프론트엔드 이슈 보고서

## 🐛 발견된 문제

### 1. **전략 활성화/비활성화 토글 기능 없음**

**현재 상태:**
- ✅ 전략 "중지" 버튼만 존재 ([StrategyCard.tsx:213-221](d:\Dev\auto_stock\src\components\trading\StrategyCard.tsx#L213-L221))
- ✅ "중지" 버튼은 `auto_trade_enabled`와 `auto_execute`만 false로 변경
- ❌ **`is_active` 컬럼을 변경하는 UI 없음**

**문제점:**
- 사용자가 UI에서 전략을 활성화/비활성화할 방법이 없음
- 현재 5개 전략이 모두 `is_active = true`인 이유는:
  - 전략 생성 시 기본값이 `true`거나
  - 한 번 활성화하면 비활성화할 방법이 없음

**코드 분석:**

```typescript
// StrategyCard.tsx - "중지" 버튼만 존재
<Button
  size="small"
  startIcon={<Stop />}
  onClick={onStop}
  variant="outlined"
  color="error"
>
  중지
</Button>

// AutoTradingPanelV2.tsx:187-218 - 중지 로직
const handleStopStrategy = async (strategyId: string) => {
  // 전략 비활성화
  const { error: strategyError } = await supabase
    .from('strategies')
    .update({
      auto_execute: false,
      auto_trade_enabled: false
      // ❌ is_active는 변경하지 않음!
    })
    .eq('id', strategyId)

  // ...
}
```

### 2. **`allocated_percent` 업데이트 누락**

**현재 상태:**
- [EditStrategyDialog.tsx:90-96](d:\Dev\auto_stock\src\components\trading\EditStrategyDialog.tsx#L90-L96)에서 `allocated_percent` 업데이트 코드 존재
- ✅ 코드 자체는 정상

**문제점:**
- UI에서 50% 입력 후 저장했지만 DB에 반영 안 됨
- 가능한 원인:
  1. Dialog가 실제로 호출되지 않음
  2. 다른 화면에서 전략 설정 중 (EditStrategyDialog를 안 씀)
  3. 저장 후 즉시 다른 값으로 덮어씀

**확인 필요:**
```typescript
// EditStrategyDialog.tsx:75-100
const handleSave = async () => {
  // ... validation ...

  const { error: updateError } = await supabase
    .from('strategies')
    .update({
      allocated_capital: allocatedCapital || 0,
      allocated_percent: allocatedPercent || 0  // ✅ 코드는 존재
    })
    .eq('id', strategyId)

  // ...
}
```

### 3. **투자 유니버스 설정 누락**

**현재 상태:**
- 모든 활성 전략의 `target_stocks` 및 `universe`가 NULL 또는 빈 배열
- `stock_count = 0`

**문제점:**
- 전략이 모니터링할 종목이 없어서 시그널 발생 불가
- UI에서 투자 유니버스를 설정하는 화면이 누락되었거나 작동하지 않음

## ✅ 해결 방법

### 해결책 1: 전략 활성화/비활성화 토글 추가 (권장)

**StrategyCard.tsx 또는 전략 목록 화면에 추가:**

```typescript
import { Switch, FormControlLabel } from '@mui/material'

// 전략 카드에 토글 추가
<FormControlLabel
  control={
    <Switch
      checked={isActive}
      onChange={handleToggleActive}
      color="primary"
    />
  }
  label="전략 활성화"
/>

// 핸들러
const handleToggleActive = async (event: React.ChangeEvent<HTMLInputElement>) => {
  const newActive = event.target.checked

  try {
    const { error } = await supabase
      .from('strategies')
      .update({ is_active: newActive })
      .eq('id', strategyId)

    if (error) throw error

    // UI 새로고침
    onRefresh()
  } catch (error) {
    console.error('전략 활성화 상태 변경 실패:', error)
  }
}
```

### 해결책 2: "중지" 버튼을 "활성화/비활성화" 토글로 변경

```typescript
// AutoTradingPanelV2.tsx의 handleStopStrategy 수정
const handleStopStrategy = async (strategyId: string, currentActive: boolean) => {
  const newActive = !currentActive

  try {
    const { error } = await supabase
      .from('strategies')
      .update({
        is_active: newActive,
        auto_execute: newActive,
        auto_trade_enabled: newActive
      })
      .eq('id', strategyId)

    if (error) throw error
    loadData()
  } catch (error) {
    console.error('전략 상태 변경 실패:', error)
  }
}
```

### 해결책 3: 투자 유니버스 설정 UI 추가

전략 설정 Dialog에 투자 유니버스 입력 필드 추가:

```typescript
// EditStrategyDialog.tsx에 추가
const [targetStocks, setTargetStocks] = useState<string[]>([])

// UI
<TextField
  label="모니터링 종목 (쉼표로 구분)"
  placeholder="005930,000660,035420"
  value={targetStocks.join(',')}
  onChange={(e) => setTargetStocks(e.target.value.split(',').map(s => s.trim()))}
  fullWidth
/>

// 저장 시
const { error } = await supabase
  .from('strategies')
  .update({
    allocated_capital: allocatedCapital || 0,
    allocated_percent: allocatedPercent || 0,
    target_stocks: targetStocks  // 추가
  })
  .eq('id', strategyId)
```

## 📊 현재 DB 상태 (문제 상황)

```sql
-- 5개 전략 모두 is_active = true
-- 하지만 UI에서 비활성화할 방법이 없음

SELECT name, is_active, auto_trade_enabled, allocated_percent, target_stocks
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 결과:
-- [분할] MACD+RSI 복합 전략    | true | false | 0.00  | NULL
-- [분할] RSI 3단계 매수매도     | true | false | 0.00  | NULL
-- [분할] 볼린저밴드 2단계 매수  | true | false | 30.00 | NULL
-- [템플릿] 골든크로스          | true | false | 0.00  | NULL
-- [템플릿] 볼린저밴드          | true | true  | 50.00 | NULL
```

## 🎯 우선순위

1. **HIGH**: 전략 활성화/비활성화 토글 추가
2. **HIGH**: 투자 유니버스 설정 UI 추가
3. **MEDIUM**: allocated_percent가 왜 저장 안 되는지 디버깅

## 📝 권장 작업

1. `StrategyCard.tsx`에 활성화 토글 추가
2. `EditStrategyDialog.tsx`에 투자 유니버스 입력 필드 추가
3. 전략 목록 화면에서 한눈에 활성화 상태를 볼 수 있도록 표시
