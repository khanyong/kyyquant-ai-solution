# 자동매매 탭 설계 문서

## UI 구조

```
┌─────────────────────────────────────────────────────┐
│  자동매매                                              │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌───────────────────────────────────────────┐      │
│  │ 1. 전략 선택                                │      │
│  │   [드롭다운: 전략 선택...]                   │      │
│  │   선택된 전략: [분할] RSI 3단계 매수매도       │      │
│  │   매수조건: RSI < 35, 28, 22               │      │
│  │   매도조건: 없음                            │      │
│  └───────────────────────────────────────────┘      │
│                                                       │
│  ┌───────────────────────────────────────────┐      │
│  │ 2. 투자유니버스 선택 (다중 선택 가능)        │      │
│  │   ☑ 기본필터 (446개 종목)                  │      │
│  │   ☐ 대형주 필터 (120개 종목)               │      │
│  │   ☐ 성장주 필터 (89개 종목)                │      │
│  │   [+ 새 필터 만들기]                        │      │
│  └───────────────────────────────────────────┘      │
│                                                       │
│  ┌───────────────────────────────────────────┐      │
│  │ 3. 자동매매 설정                            │      │
│  │   포지션 크기: [1,000,000] 원               │      │
│  │   최대 보유 종목: [5] 개                    │      │
│  │   손절라인: [-5] %                          │      │
│  │   목표수익: [10] %                          │      │
│  └───────────────────────────────────────────┘      │
│                                                       │
│  [자동매매 시작]  [중지]                             │
│                                                       │
├─────────────────────────────────────────────────────┤
│  활성 자동매매 현황                                    │
├─────────────────────────────────────────────────────┤
│  전략명        │ 유니버스 │ 상태  │ 마지막실행 │ 신호  │
│  RSI 3단계    │ 2개      │ 🟢활성 │ 1분 전    │ 3개   │
│  볼린저밴드    │ 1개      │ 🟢활성 │ 2분 전    │ 0개   │
└─────────────────────────────────────────────────────┘
```

## 데이터 흐름

### 자동매매 시작 버튼 클릭 시:

```typescript
async function startAutoTrading() {
  // 1. 전략 업데이트 (auto_execute = true)
  await supabase
    .from('strategies')
    .update({
      auto_execute: true,
      auto_trade_enabled: true,
      is_active: true
    })
    .eq('id', selectedStrategyId);

  // 2. 선택된 투자유니버스들과 연결
  const connections = selectedFilters.map(filterId => ({
    strategy_id: selectedStrategyId,
    investment_filter_id: filterId,
    is_active: true
  }));

  await supabase
    .from('strategy_universes')
    .upsert(connections, {
      onConflict: 'strategy_id,investment_filter_id'
    });

  // 3. 성공 메시지
  toast.success('자동매매가 시작되었습니다!');
}
```

### 자동매매 중지 버튼 클릭 시:

```typescript
async function stopAutoTrading() {
  // 1. 전략 비활성화
  await supabase
    .from('strategies')
    .update({
      auto_execute: false,
      auto_trade_enabled: false
    })
    .eq('id', selectedStrategyId);

  // 2. 연결된 유니버스 비활성화
  await supabase
    .from('strategy_universes')
    .update({ is_active: false })
    .eq('strategy_id', selectedStrategyId);

  toast.success('자동매매가 중지되었습니다.');
}
```

## 3. Realtime 업데이트

```typescript
// 자동매매 상태 실시간 모니터링
useEffect(() => {
  const channel = supabase
    .channel('auto_trading_status')
    .on('postgres_changes', {
      event: 'UPDATE',
      schema: 'public',
      table: 'strategies',
      filter: `auto_execute=eq.true`
    }, (payload) => {
      // 자동매매 상태 업데이트
      updateAutoTradingStatus(payload.new);
    })
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}, []);
```

## 4. 활성 자동매매 현황 조회

```typescript
async function fetchActiveAutoTrading() {
  const { data, error } = await supabase
    .rpc('get_active_strategies_with_universe');

  // 전략별로 그룹화
  const grouped = data.reduce((acc, item) => {
    if (!acc[item.strategy_id]) {
      acc[item.strategy_id] = {
        strategy_id: item.strategy_id,
        strategy_name: item.strategy_name,
        universes: [],
        last_executed: item.last_signal_at
      };
    }
    acc[item.strategy_id].universes.push({
      filter_id: item.filter_id,
      filter_name: item.filter_name,
      stocks_count: item.filtered_stocks.length
    });
    return acc;
  }, {});

  return Object.values(grouped);
}
```

## 5. 안전장치

### 중복 실행 방지
```typescript
async function validateBeforeStart() {
  // 이미 활성화된 같은 전략이 있는지 체크
  const { data: existing } = await supabase
    .from('strategies')
    .select('id, name')
    .eq('id', selectedStrategyId)
    .eq('auto_execute', true)
    .single();

  if (existing) {
    return confirm('이미 활성화된 전략입니다. 재시작하시겠습니까?');
  }
  return true;
}
```

### 최대 동시 실행 제한
```typescript
async function checkMaxConcurrent() {
  const { count } = await supabase
    .from('strategies')
    .select('*', { count: 'exact', head: true })
    .eq('auto_execute', true)
    .eq('is_active', true);

  const MAX_CONCURRENT = 5;
  if (count >= MAX_CONCURRENT) {
    throw new Error(`최대 ${MAX_CONCURRENT}개까지만 동시 실행 가능합니다.`);
  }
}
```

## 6. 모니터링 대시보드

```typescript
// 실시간 신호 카운트
const { data: signals } = await supabase
  .from('trading_signals')
  .select('*')
  .eq('strategy_id', strategyId)
  .gte('created_at', new Date(Date.now() - 24*60*60*1000).toISOString())
  .order('created_at', { ascending: false });

// 신호 통계
const stats = {
  total: signals.length,
  buy: signals.filter(s => s.signal_type === 'BUY').length,
  sell: signals.filter(s => s.signal_type === 'SELL').length,
  lastSignal: signals[0]?.created_at
};
```

## 7. 에러 처리

```typescript
try {
  await startAutoTrading();
} catch (error) {
  if (error.code === '23505') {
    toast.error('이미 같은 조합이 활성화되어 있습니다.');
  } else if (error.code === '23503') {
    toast.error('존재하지 않는 전략 또는 필터입니다.');
  } else {
    toast.error('자동매매 시작 중 오류 발생: ' + error.message);
  }
}
```
