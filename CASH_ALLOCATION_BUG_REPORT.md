# 💰 현금 할당/회수 로직 버그 보고서

## 🐛 발견된 문제

### 문제 상황
- **total_cash**: 9,782,702원 ✅
- **available_cash**: 0원 ❌

사용자가 전략을 비활성화했는데도 `available_cash`가 0으로 남아있음.

## 🔍 원인 분석

### 1. 전략 할당 시 (EditStrategyDialog.tsx:90-96)

```typescript
const { error: updateError } = await supabase
  .from('strategies')
  .update({
    allocated_capital: allocatedCapital || 0,  // ✅ 전략에 할당
    allocated_percent: allocatedPercent || 0
  })
  .eq('id', strategyId)

// ❌ 문제: kw_account_balance.available_cash를 차감하지 않음!
```

**누락된 로직**:
```typescript
// kw_account_balance.available_cash를 차감해야 함
const { error } = await supabase
  .from('kw_account_balance')
  .update({
    available_cash: available_cash - allocatedCapital
  })
```

### 2. 전략 중지 시 (AutoTradingPanelV2.tsx:187-218)

```typescript
const handleStopStrategy = async (strategyId: string) => {
  // 전략 비활성화
  const { error: strategyError } = await supabase
    .from('strategies')
    .update({
      auto_execute: false,
      auto_trade_enabled: false
      // ❌ allocated_capital을 0으로 초기화하지 않음!
    })
    .eq('id', strategyId)

  // ❌ 문제: kw_account_balance.available_cash를 회수하지 않음!
}
```

**누락된 로직**:
```typescript
// 1. 먼저 현재 할당 금액 조회
const { data: strategy } = await supabase
  .from('strategies')
  .select('allocated_capital')
  .eq('id', strategyId)
  .single()

// 2. allocated_capital을 0으로 초기화
await supabase
  .from('strategies')
  .update({
    auto_execute: false,
    auto_trade_enabled: false,
    allocated_capital: 0,        // ← 추가 필요
    allocated_percent: 0         // ← 추가 필요
  })
  .eq('id', strategyId)

// 3. available_cash에 금액 반환
await supabase
  .from('kw_account_balance')
  .update({
    available_cash: available_cash + strategy.allocated_capital
  })
  .eq('user_id', userId)
```

## 📊 현재 DB 상태

```sql
-- kw_account_balance
total_cash: 9,782,702원
available_cash: 0원         ← 전략 비활성화 후에도 회수 안됨

-- strategies ([템플릿] 볼린저밴드)
is_active: true
allocated_capital: (값 확인 필요)
allocated_percent: 100%
```

## ✅ 해결 방법

### 옵션 1: 임시 해결 (SQL로 수동 복구)

```sql
-- 활성 전략이 없으므로 available_cash = total_cash로 복구
UPDATE kw_account_balance
SET
  available_cash = total_cash,
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
```

### 옵션 2: 프론트엔드 코드 수정 (근본 해결)

#### A. EditStrategyDialog.tsx 수정

```typescript
const handleSave = async () => {
  if (!strategyId) {
    setError('전략 ID가 없습니다.')
    return
  }

  if (allocatedPercent <= 0) {
    setError('할당 비율을 입력해주세요 (0보다 커야 합니다)')
    return
  }

  try {
    setLoading(true)
    setError('')

    // 1. 현재 할당 금액 조회
    const { data: currentStrategy, error: fetchError } = await supabase
      .from('strategies')
      .select('allocated_capital, user_id')
      .eq('id', strategyId)
      .single()

    if (fetchError) throw fetchError

    const previousAllocation = currentStrategy.allocated_capital || 0
    const allocationDiff = allocatedCapital - previousAllocation

    // 2. 계좌 잔고 조회
    const { data: balance, error: balanceError } = await supabase
      .from('kw_account_balance')
      .select('available_cash')
      .eq('user_id', currentStrategy.user_id)
      .order('updated_at', { ascending: false })
      .limit(1)
      .single()

    if (balanceError) throw balanceError

    // 3. 사용 가능 현금 확인
    if (allocationDiff > 0 && balance.available_cash < allocationDiff) {
      setError(`사용 가능한 현금이 부족합니다. (필요: ${allocationDiff.toLocaleString()}원, 가용: ${balance.available_cash.toLocaleString()}원)`)
      return
    }

    // 4. 전략 업데이트
    const { error: updateError } = await supabase
      .from('strategies')
      .update({
        allocated_capital: allocatedCapital || 0,
        allocated_percent: allocatedPercent || 0
      })
      .eq('id', strategyId)

    if (updateError) throw updateError

    // 5. available_cash 업데이트 (차감 또는 반환)
    const { error: cashError } = await supabase
      .from('kw_account_balance')
      .update({
        available_cash: balance.available_cash - allocationDiff,
        updated_at: new Date().toISOString()
      })
      .eq('user_id', currentStrategy.user_id)

    if (cashError) throw cashError

    // 성공
    onSuccess()
    onClose()
  } catch (error: any) {
    console.error('전략 수정 실패:', error)
    setError(`전략 수정 실패: ${error.message}`)
  } finally {
    setLoading(false)
  }
}
```

#### B. AutoTradingPanelV2.tsx 수정

```typescript
const handleStopStrategy = async (strategyId: string) => {
  if (!confirm('정말 이 전략을 중지하시겠습니까?')) {
    return
  }

  try {
    // 1. 현재 전략 할당 금액 조회
    const { data: strategy, error: fetchError } = await supabase
      .from('strategies')
      .select('allocated_capital, user_id')
      .eq('id', strategyId)
      .single()

    if (fetchError) throw fetchError

    const releasedCapital = strategy.allocated_capital || 0

    // 2. 전략 비활성화 및 금액 초기화
    const { error: strategyError } = await supabase
      .from('strategies')
      .update({
        auto_execute: false,
        auto_trade_enabled: false,
        allocated_capital: 0,       // ← 추가
        allocated_percent: 0        // ← 추가
      })
      .eq('id', strategyId)

    if (strategyError) throw strategyError

    // 3. available_cash에 금액 반환
    if (releasedCapital > 0) {
      const { data: balance, error: balanceError } = await supabase
        .from('kw_account_balance')
        .select('available_cash')
        .eq('user_id', strategy.user_id)
        .order('updated_at', { ascending: false })
        .limit(1)
        .single()

      if (balanceError) throw balanceError

      const { error: cashError } = await supabase
        .from('kw_account_balance')
        .update({
          available_cash: balance.available_cash + releasedCapital,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', strategy.user_id)

      if (cashError) throw cashError
    }

    // 4. 연결된 유니버스 비활성화
    const { error: universeError } = await supabase
      .from('strategy_universes')
      .update({ is_active: false })
      .eq('strategy_id', strategyId)

    if (universeError) throw universeError

    // 5. 데이터 새로고침
    loadData()
  } catch (error: any) {
    console.error('전략 중지 실패:', error)
    alert(`전략 중지 실패: ${error.message}`)
  }
}
```

## 🎯 권장 작업 순서

1. **즉시 실행** (임시 복구):
   ```sql
   UPDATE kw_account_balance
   SET available_cash = total_cash
   WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
   ```

2. **프론트엔드 수정**:
   - EditStrategyDialog.tsx 수정 (할당 시 available_cash 차감)
   - AutoTradingPanelV2.tsx 수정 (중지 시 available_cash 회수)

3. **테스트**:
   - 전략 활성화 → available_cash 차감 확인
   - 전략 비활성화 → available_cash 회수 확인
   - 전략 수정 (할당 금액 변경) → available_cash 증감 확인

## 📝 참고사항

- 현재 `kw_account_balance` 테이블의 RLS 정책 확인 필요
- `available_cash` 업데이트 시 트랜잭션 처리 필요 (동시성 제어)
- 추후 PostgreSQL Function으로 로직을 DB에 구현하는 것도 고려
