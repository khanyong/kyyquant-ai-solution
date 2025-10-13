# 자동매매 탭 리팩토링 계획

## 현재 → 목표

### 현재 (Before):
```typescript
// 로컬 상태, 하드코딩
const [strategies, setStrategies] = useState<TradingStrategy[]>(exampleStrategies)
```

### 목표 (After):
```typescript
// Supabase 연동, 실시간 업데이트
const [strategies, setStrategies] = useState([])
const [filters, setFilters] = useState([])

// Supabase에서 실제 전략 로드
const loadStrategies = async () => {
  const { data } = await supabase
    .from('strategies')
    .select('*')
    .order('created_at', { ascending: false })
  setStrategies(data)
}
```

## 수정 단계

### 1단계: UI 수정 (가장 중요!)

#### 기존 UI:
```
[스위치] 자동매매 ON/OFF
[테이블] 개별 전략 목록 (종목코드 하나씩)
```

#### 새 UI:
```
┌──────────────────────────────────────┐
│ 1. 전략 선택                          │
│   [드롭다운] 저장된 전략 선택...       │
│   선택: [분할] RSI 3단계 매수매도       │
├──────────────────────────────────────┤
│ 2. 투자유니버스 선택 (다중)            │
│   ☑ 기본필터 (446개)                  │
│   ☐ 대형주필터 (120개)                │
│   [+ 새 필터]                         │
├──────────────────────────────────────┤
│ 3. 자동매매 설정                      │
│   포지션 크기: [1,000,000]원           │
│   최대 종목: [5]개                    │
├──────────────────────────────────────┤
│ [자동매매 시작] [중지]                 │
└──────────────────────────────────────┘

활성 자동매매:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
전략명         │유니버스│상태│신호
RSI 3단계      │2개    │🟢  │3개
볼린저밴드     │1개    │🟢  │0개
```

### 2단계: Supabase 연동 로직

```typescript
// 전략 목록 로드
const loadStrategies = async () => {
  const { data, error } = await supabase
    .from('strategies')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('전략 로드 실패:', error);
    return;
  }

  setStrategies(data);
};

// 투자유니버스 목록 로드
const loadFilters = async () => {
  const { data, error } = await supabase
    .from('kw_investment_filters')
    .select('id, name, filtered_stocks_count')
    .eq('is_active', true)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('필터 로드 실패:', error);
    return;
  }

  setFilters(data);
};

// 자동매매 시작
const startAutoTrading = async () => {
  if (!selectedStrategyId || selectedFilterIds.length === 0) {
    toast.error('전략과 투자유니버스를 선택해주세요');
    return;
  }

  try {
    // 1. 전략 auto_execute 활성화
    const { error: strategyError } = await supabase
      .from('strategies')
      .update({
        auto_execute: true,
        auto_trade_enabled: true,
        is_active: true
      })
      .eq('id', selectedStrategyId);

    if (strategyError) throw strategyError;

    // 2. 선택된 투자유니버스들과 연결
    const connections = selectedFilterIds.map(filterId => ({
      strategy_id: selectedStrategyId,
      investment_filter_id: filterId,
      is_active: true
    }));

    const { error: connectError } = await supabase
      .from('strategy_universes')
      .upsert(connections, {
        onConflict: 'strategy_id,investment_filter_id'
      });

    if (connectError) throw connectError;

    toast.success('자동매매가 시작되었습니다!');

    // 활성 자동매매 목록 새로고침
    loadActiveAutoTrading();

  } catch (error) {
    console.error('자동매매 시작 실패:', error);
    toast.error('자동매매 시작 중 오류 발생');
  }
};

// 자동매매 중지
const stopAutoTrading = async (strategyId: string) => {
  try {
    // 1. 전략 비활성화
    const { error: strategyError } = await supabase
      .from('strategies')
      .update({
        auto_execute: false,
        auto_trade_enabled: false
      })
      .eq('id', strategyId);

    if (strategyError) throw strategyError;

    // 2. 연결된 유니버스 비활성화
    const { error: connectError } = await supabase
      .from('strategy_universes')
      .update({ is_active: false })
      .eq('strategy_id', strategyId);

    if (connectError) throw connectError;

    toast.success('자동매매가 중지되었습니다');
    loadActiveAutoTrading();

  } catch (error) {
    console.error('자동매매 중지 실패:', error);
    toast.error('자동매매 중지 중 오류 발생');
  }
};

// 활성 자동매매 목록 조회
const loadActiveAutoTrading = async () => {
  const { data, error } = await supabase
    .rpc('get_active_strategies_with_universe');

  if (error) {
    console.error('활성 자동매매 조회 실패:', error);
    return;
  }

  // 전략별로 그룹화
  const grouped = data.reduce((acc: any, item: any) => {
    if (!acc[item.strategy_id]) {
      acc[item.strategy_id] = {
        strategy_id: item.strategy_id,
        strategy_name: item.strategy_name,
        universes: [],
        entry_conditions: item.entry_conditions,
        exit_conditions: item.exit_conditions
      };
    }
    acc[item.strategy_id].universes.push({
      filter_id: item.filter_id,
      filter_name: item.filter_name
    });
    return acc;
  }, {});

  setActiveAutoTrading(Object.values(grouped));
};
```

### 3단계: Realtime 업데이트

```typescript
useEffect(() => {
  // 자동매매 상태 실시간 모니터링
  const channel = supabase
    .channel('auto_trading_monitor')
    .on('postgres_changes', {
      event: 'UPDATE',
      schema: 'public',
      table: 'strategies',
      filter: 'auto_execute=eq.true'
    }, (payload) => {
      console.log('전략 상태 변경:', payload);
      loadActiveAutoTrading();
    })
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'trading_signals'
    }, (payload) => {
      console.log('새 신호 생성:', payload);
      // 신호 카운트 업데이트
      updateSignalCount(payload.new);
    })
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}, []);
```

### 4단계: 신호 모니터링

```typescript
// 최근 24시간 신호 조회
const loadRecentSignals = async (strategyId: string) => {
  const { data, error } = await supabase
    .from('trading_signals')
    .select('*')
    .eq('strategy_id', strategyId)
    .gte('created_at', new Date(Date.now() - 24*60*60*1000).toISOString())
    .order('created_at', { ascending: false });

  if (error) {
    console.error('신호 조회 실패:', error);
    return [];
  }

  return data;
};

// 신호 통계
const calculateSignalStats = (signals: any[]) => {
  return {
    total: signals.length,
    buy: signals.filter(s => s.signal_type === 'BUY').length,
    sell: signals.filter(s => s.signal_type === 'SELL').length,
    lastSignal: signals[0]?.created_at || null
  };
};
```

## 파일 구조

```
src/
├── components/
│   └── trading/
│       ├── AutoTradingPanel.tsx (전체 UI)
│       ├── StrategySelector.tsx (전략 선택)
│       ├── UniverseSelector.tsx (투자유니버스 선택)
│       ├── ActiveTradingList.tsx (활성 자동매매 목록)
│       └── SignalMonitor.tsx (신호 모니터링)
└── services/
    └── autoTradingService.ts (Supabase 연동 로직)
```

## 구현 순서

1. ✅ Supabase 테이블 구조 확인 (완료)
2. ✅ RPC Function 생성 (완료)
3. ✅ n8n 워크플로우 생성 (완료)
4. ⏭️ AutoTradingPanel.tsx 리팩토링
5. ⏭️ Supabase 연동 로직 추가
6. ⏭️ Realtime 업데이트 추가
7. ⏭️ 테스트 및 디버깅

## 핵심 변경사항

### Before:
- 로컬 상태 관리
- 하드코딩된 전략
- 개별 종목 선택
- n8n 연동 없음

### After:
- Supabase 연동
- 실제 저장된 전략 사용
- 투자유니버스 (여러 종목) 선택
- n8n 자동 실행
- 실시간 신호 모니터링
