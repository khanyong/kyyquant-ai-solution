# 📊 실시간 거래 시스템 테이블 활용 계획

## 📑 목차
1. [시장 데이터 테이블](#1-시장-데이터-테이블)
2. [신호 및 전략 실행](#2-신호-및-전략-실행)
3. [주문 및 포지션 관리](#3-주문-및-포지션-관리)
4. [계좌 및 설정](#4-계좌-및-설정)
5. [알림 및 로깅](#5-알림-및-로깅)
6. [데이터 흐름도](#6-데이터-흐름도)

---

## 1. 시장 데이터 테이블

### 1.1 market_data (실시간 시세 데이터)

**목적**: 키움 OpenAPI에서 실시간으로 받는 시세 데이터 저장

**활용 방안**:
```typescript
// 1) 실시간 시세 수집 (WebSocket)
kiwoomWebSocket.onPriceUpdate((data) => {
  supabase.from('market_data').insert({
    stock_code: data.stock_code,
    current_price: data.current_price,
    volume: data.volume,
    change_rate: data.change_rate,
    bid_price: data.bid_price,
    ask_price: data.ask_price,
    trading_date: new Date(),
    trading_time: new Date()
  })
})

// 2) 최신 시세 조회 (전략 실행 시)
const latestPrice = await supabase
  .from('market_data')
  .select('*')
  .eq('stock_code', '005930')
  .order('timestamp', { ascending: false })
  .limit(1)
  .single()

// 3) 가격 히스토리 분석
const priceHistory = await supabase
  .from('market_data')
  .select('current_price, timestamp')
  .eq('stock_code', '005930')
  .gte('timestamp', new Date(Date.now() - 24*60*60*1000)) // 최근 24시간
  .order('timestamp', { ascending: true })
```

**데이터 보존 정책**:
- 실시간 데이터: 최근 1일분만 유지
- 일봉 데이터로 집계 후 삭제 (매일 자정)

---

### 1.2 technical_indicators (기술적 지표)

**목적**: 전략 실행에 필요한 기술적 지표 계산 및 저장

**활용 방안**:
```typescript
// 1) 지표 계산 및 저장 (1분, 5분, 일봉 단위)
async function calculateAndSaveIndicators(stockCode: string, timeframe: string) {
  const priceData = await getPriceData(stockCode, timeframe)

  const indicators = {
    stock_code: stockCode,
    timeframe: timeframe,
    ma5: calculateMA(priceData, 5),
    ma20: calculateMA(priceData, 20),
    rsi: calculateRSI(priceData, 14),
    macd: calculateMACD(priceData),
    macd_signal: calculateMACDSignal(priceData),
    bb_upper: calculateBollingerBands(priceData).upper,
    bb_lower: calculateBollingerBands(priceData).lower,
    calculated_at: new Date()
  }

  await supabase.from('technical_indicators').insert(indicators)
}

// 2) 전략 조건 평가 시 사용
const indicators = await supabase
  .from('technical_indicators')
  .select('*')
  .eq('stock_code', '005930')
  .eq('timeframe', '1d')
  .order('calculated_at', { ascending: false })
  .limit(1)
  .single()

// RSI 과매도 체크
if (indicators.rsi < 30) {
  // 매수 신호 생성
}
```

**업데이트 주기**:
- 1분봉: 1분마다
- 5분봉: 5분마다
- 일봉: 장 마감 후 (15:30)

---

## 2. 신호 및 전략 실행

### 2.1 trading_signals (거래 신호)

**목적**: 전략 조건 충족 시 생성되는 매수/매도 신호 저장

**활용 방안**:
```typescript
// 1) 신호 생성 (전략 엔진에서)
async function generateTradingSignal(strategyId: string, stockCode: string) {
  const indicators = await getLatestIndicators(stockCode)
  const marketData = await getLatestMarketData(stockCode)

  // 전략 조건 평가
  const shouldBuy = evaluateStrategy(strategyId, indicators, marketData)

  if (shouldBuy) {
    const signal = {
      strategy_id: strategyId,
      stock_code: stockCode,
      signal_type: 'BUY',
      signal_strength: 'strong',
      confidence_score: 0.85,
      entry_price: marketData.current_price,
      target_price: marketData.current_price * 1.05, // +5%
      stop_loss_price: marketData.current_price * 0.97, // -3%
      position_size: 100,
      risk_reward_ratio: 1.67,
      indicators_snapshot: indicators,
      market_conditions: marketData,
      expiry_time: new Date(Date.now() + 60*60*1000) // 1시간 후 만료
    }

    const { data } = await supabase
      .from('trading_signals')
      .insert(signal)
      .select()
      .single()

    return data
  }
}

// 2) 미실행 신호 조회 및 주문 실행
async function executeUnexecutedSignals() {
  const signals = await supabase
    .from('trading_signals')
    .select('*')
    .eq('executed', false)
    .lt('expiry_time', new Date())
    .order('timestamp', { ascending: true })

  for (const signal of signals.data) {
    await placeOrder(signal)
  }
}

// 3) 신호 성과 추적
const signalPerformance = await supabase
  .from('trading_signals')
  .select('*, kiwoom_orders(*)')
  .eq('strategy_id', strategyId)
  .eq('executed', true)
```

**신호 생명주기**:
1. 생성 (executed: false)
2. 주문 실행 (executed: true, execution_time 기록)
3. 만료 또는 취소 (expiry_time 초과)

---

### 2.2 strategy_execution_logs (전략 실행 로그)

**목적**: 전략의 모든 실행 기록 및 디버깅 정보 저장

**활용 방안**:
```typescript
// 1) 전략 실행 로깅
async function executeStrategy(strategyId: string) {
  const startTime = Date.now()

  try {
    // 전략 실행 로직
    const result = await runStrategy(strategyId)

    // 성공 로그
    await supabase.from('strategy_execution_logs').insert({
      strategy_id: strategyId,
      execution_type: 'SIGNAL_CHECK',
      execution_status: 'SUCCESS',
      action_taken: result.action,
      reason: result.reason,
      market_snapshot: result.marketData,
      indicators_snapshot: result.indicators,
      result: result,
      executed_at: new Date(),
      execution_time_ms: Date.now() - startTime
    })
  } catch (error) {
    // 실패 로그
    await supabase.from('strategy_execution_logs').insert({
      strategy_id: strategyId,
      execution_type: 'SIGNAL_CHECK',
      execution_status: 'FAILED',
      error_message: error.message,
      executed_at: new Date(),
      execution_time_ms: Date.now() - startTime
    })
  }
}

// 2) 전략 성능 분석
const executionStats = await supabase
  .from('strategy_execution_logs')
  .select('execution_status, execution_time_ms')
  .eq('strategy_id', strategyId)
  .gte('executed_at', new Date(Date.now() - 7*24*60*60*1000)) // 최근 7일

const successRate = executionStats.filter(log => log.execution_status === 'SUCCESS').length / executionStats.length
const avgExecutionTime = executionStats.reduce((sum, log) => sum + log.execution_time_ms, 0) / executionStats.length
```

**활용 사례**:
- 전략 디버깅
- 성능 모니터링
- 오류 추적
- 실행 시간 최적화

---

## 3. 주문 및 포지션 관리

### 3.1 kiwoom_orders (키움 주문 정보)

**목적**: 키움 API를 통해 실행된 모든 주문 추적

**활용 방안**:
```typescript
// 1) 주문 실행 및 기록
async function placeOrder(signal: TradingSignal) {
  // 키움 API 주문 실행
  const orderResponse = await kiwoomAPI.placeOrder({
    account_no: userAccount,
    stock_code: signal.stock_code,
    order_type: signal.signal_type,
    order_method: '시장가',
    order_quantity: signal.position_size,
    order_price: signal.entry_price
  })

  // DB에 주문 기록
  const { data } = await supabase.from('kiwoom_orders').insert({
    strategy_id: signal.strategy_id,
    signal_id: signal.id,
    kiwoom_order_no: orderResponse.order_no,
    account_no: userAccount,
    stock_code: signal.stock_code,
    order_type: signal.signal_type,
    order_method: '시장가',
    order_quantity: signal.position_size,
    order_price: signal.entry_price,
    order_status: 'PENDING',
    order_reason: `신호 ID: ${signal.id}, 신뢰도: ${signal.confidence_score}`
  }).select().single()

  // 신호 실행 상태 업데이트
  await supabase
    .from('trading_signals')
    .update({ executed: true, execution_time: new Date() })
    .eq('id', signal.id)

  return data
}

// 2) 실시간 체결 업데이트 (WebSocket)
kiwoomWebSocket.onOrderExecution((execution) => {
  supabase
    .from('kiwoom_orders')
    .update({
      executed_quantity: execution.executed_quantity,
      executed_price: execution.executed_price,
      remaining_quantity: execution.remaining_quantity,
      order_status: execution.status, // 'PARTIAL' or 'FILLED'
      executed_time: new Date()
    })
    .eq('kiwoom_order_no', execution.order_no)
})

// 3) 주문 상태 모니터링
const pendingOrders = await supabase
  .from('kiwoom_orders')
  .select('*')
  .in('order_status', ['PENDING', 'PARTIAL'])
  .order('order_time', { ascending: false })
```

**주문 상태 흐름**:
1. PENDING (주문 접수)
2. PARTIAL (부분 체결)
3. FILLED (전량 체결)
4. CANCELLED (취소)
5. REJECTED (거부)

---

### 3.2 positions (보유 포지션)

**목적**: 현재 보유 중인 주식 포지션 관리 및 손익 추적

**활용 방안**:
```typescript
// 1) 매수 체결 시 포지션 생성/업데이트
kiwoomWebSocket.onOrderFilled((execution) => {
  if (execution.order_type === 'BUY') {
    // 기존 포지션 확인
    const existingPosition = await supabase
      .from('positions')
      .select('*')
      .eq('account_no', execution.account_no)
      .eq('stock_code', execution.stock_code)
      .eq('position_status', 'OPEN')
      .single()

    if (existingPosition.data) {
      // 추가 매수 - 평단가 계산
      const totalQuantity = existingPosition.data.quantity + execution.quantity
      const totalAmount =
        (existingPosition.data.avg_buy_price * existingPosition.data.quantity) +
        (execution.executed_price * execution.quantity)
      const newAvgPrice = totalAmount / totalQuantity

      await supabase
        .from('positions')
        .update({
          quantity: totalQuantity,
          avg_buy_price: newAvgPrice,
          total_buy_amount: totalAmount,
          last_updated: new Date()
        })
        .eq('id', existingPosition.data.id)
    } else {
      // 신규 포지션 생성
      await supabase.from('positions').insert({
        user_id: auth.user.id,
        strategy_id: execution.strategy_id,
        account_no: execution.account_no,
        stock_code: execution.stock_code,
        stock_name: execution.stock_name,
        quantity: execution.quantity,
        available_quantity: execution.quantity,
        avg_buy_price: execution.executed_price,
        total_buy_amount: execution.executed_price * execution.quantity,
        position_status: 'OPEN',
        entry_signal_id: execution.signal_id,
        stop_loss_price: execution.executed_price * 0.97, // -3%
        take_profit_price: execution.executed_price * 1.05, // +5%
        opened_at: new Date()
      })
    }
  }
})

// 2) 실시간 손익 업데이트
async function updatePositionProfitLoss(stockCode: string) {
  const currentPrice = await getLatestPrice(stockCode)

  await supabase.rpc('update_position_pnl', {
    p_stock_code: stockCode,
    p_current_price: currentPrice
  })
}

// 포지션 손익 계산 SQL 함수
CREATE OR REPLACE FUNCTION update_position_pnl(
  p_stock_code varchar,
  p_current_price numeric
)
RETURNS void AS $$
BEGIN
  UPDATE positions
  SET
    current_price = p_current_price,
    current_value = quantity * p_current_price,
    profit_loss = (quantity * p_current_price) - total_buy_amount,
    profit_loss_rate = ((quantity * p_current_price) - total_buy_amount) / total_buy_amount * 100,
    last_updated = NOW()
  WHERE stock_code = p_stock_code
    AND position_status = 'OPEN';
END;
$$ LANGUAGE plpgsql;

// 3) 손절/익절 모니터링
async function monitorPositionRisks() {
  const positions = await supabase
    .from('positions')
    .select('*')
    .eq('position_status', 'OPEN')

  for (const position of positions.data) {
    const currentPrice = await getLatestPrice(position.stock_code)

    // 손절 체크
    if (currentPrice <= position.stop_loss_price) {
      await createSellSignal(position, 'STOP_LOSS')
    }

    // 익절 체크
    if (currentPrice >= position.take_profit_price) {
      await createSellSignal(position, 'TAKE_PROFIT')
    }

    // 트레일링 스탑 체크
    if (position.trailing_stop_percent) {
      const highestPrice = await getHighestPriceSinceEntry(position)
      const trailingStopPrice = highestPrice * (1 - position.trailing_stop_percent / 100)

      if (currentPrice <= trailingStopPrice) {
        await createSellSignal(position, 'TRAILING_STOP')
      }
    }
  }
}

// 4) 매도 체결 시 포지션 종료/부분매도
async function handleSellExecution(execution) {
  const position = await supabase
    .from('positions')
    .select('*')
    .eq('stock_code', execution.stock_code)
    .eq('position_status', 'OPEN')
    .single()

  if (execution.quantity >= position.data.quantity) {
    // 전량 매도 - 포지션 종료
    const realizedPL =
      (execution.executed_price * execution.quantity) -
      (position.data.avg_buy_price * execution.quantity)

    await supabase
      .from('positions')
      .update({
        position_status: 'CLOSED',
        realized_profit_loss: realizedPL,
        closed_at: new Date(),
        exit_signal_id: execution.signal_id
      })
      .eq('id', position.data.id)
  } else {
    // 부분 매도 - 수량 차감
    const partialPL =
      (execution.executed_price * execution.quantity) -
      (position.data.avg_buy_price * execution.quantity)

    await supabase
      .from('positions')
      .update({
        quantity: position.data.quantity - execution.quantity,
        available_quantity: position.data.available_quantity - execution.quantity,
        realized_profit_loss: position.data.realized_profit_loss + partialPL,
        last_updated: new Date()
      })
      .eq('id', position.data.id)
  }
}
```

**포지션 관리 주요 기능**:
- 평단가 자동 계산
- 실시간 손익 업데이트
- 손절/익절 자동 모니터링
- 트레일링 스탑 지원
- 부분 매도 처리

---

## 4. 계좌 및 설정

### 4.1 account_balance (계좌 잔고)

**목적**: 키움 계좌의 실시간 잔고 및 자산 현황 추적

**활용 방안**:
```typescript
// 1) 정기적 잔고 업데이트 (1분마다)
setInterval(async () => {
  const balanceData = await kiwoomAPI.getAccountBalance(userAccount)

  await supabase.from('account_balance').insert({
    user_id: auth.user.id,
    account_no: userAccount,
    total_evaluation: balanceData.total_evaluation,
    total_buy_amount: balanceData.total_buy_amount,
    available_cash: balanceData.available_cash,
    total_profit_loss: balanceData.total_profit_loss,
    total_profit_loss_rate: balanceData.total_profit_loss_rate,
    stock_value: balanceData.stock_value,
    cash_balance: balanceData.cash_balance,
    updated_at: new Date()
  })
}, 60000)

// 2) 주문 가능 금액 확인
async function canPlaceOrder(orderAmount: number) {
  const latestBalance = await supabase
    .from('account_balance')
    .select('available_cash')
    .eq('account_no', userAccount)
    .order('updated_at', { ascending: false })
    .limit(1)
    .single()

  return latestBalance.data.available_cash >= orderAmount
}

// 3) 자산 성과 차트 데이터
const balanceHistory = await supabase
  .from('account_balance')
  .select('updated_at, total_evaluation, total_profit_loss_rate')
  .eq('account_no', userAccount)
  .gte('updated_at', new Date(Date.now() - 30*24*60*60*1000)) // 최근 30일
  .order('updated_at', { ascending: true })
```

**데이터 활용**:
- 실시간 자산 현황 대시보드
- 수익률 차트
- 일일/주간/월간 성과 분석
- 리스크 관리 (일일 손실 한도 체크)

---

### 4.2 system_settings (시스템 설정)

**목적**: 사용자별 자동매매 및 리스크 관리 설정 저장

**활용 방안**:
```typescript
// 1) 초기 설정
async function initializeUserSettings(userId: string) {
  await supabase.from('system_settings').insert({
    user_id: userId,
    auto_trading_enabled: false, // 기본값: 수동
    max_positions: 10,
    max_position_size: 10.00, // 포지션당 최대 10%
    daily_loss_limit: -100000, // 일일 최대 손실 10만원
    use_stop_loss: true,
    default_stop_loss_percent: 3.00,
    alert_on_signal: true,
    alert_on_execution: true,
    alert_channels: ['email', 'push'],
    is_demo_mode: true // 모의투자 모드
  })
}

// 2) 자동매매 활성화 체크
async function isAutoTradingEnabled(userId: string) {
  const settings = await supabase
    .from('system_settings')
    .select('auto_trading_enabled, is_demo_mode')
    .eq('user_id', userId)
    .single()

  return settings.data.auto_trading_enabled && !settings.data.is_demo_mode
}

// 3) 리스크 관리 체크
async function checkRiskLimits(userId: string) {
  const settings = await supabase
    .from('system_settings')
    .select('*')
    .eq('user_id', userId)
    .single()

  // 일일 손실 한도 체크
  const todayPL = await getTodayProfitLoss(userId)
  if (todayPL <= settings.data.daily_loss_limit) {
    await disableAutoTrading(userId)
    await createAlert(userId, 'RISK', 'CRITICAL', '일일 손실 한도 도달 - 자동매매 정지')
    return false
  }

  // 최대 포지션 수 체크
  const openPositions = await getOpenPositionsCount(userId)
  if (openPositions >= settings.data.max_positions) {
    return false
  }

  return true
}
```

**주요 설정 항목**:
- 자동매매 on/off
- 최대 보유 종목 수
- 포지션 사이즈 제한
- 손절 설정
- 알림 설정
- 데모/실전 모드

---

## 5. 알림 및 로깅

### 5.1 alerts (실시간 알림)

**목적**: 중요 이벤트 발생 시 사용자에게 알림 전송

**활용 방안**:
```typescript
// 1) 알림 생성 함수
async function createAlert(
  userId: string,
  alertType: string,
  alertLevel: string,
  message: string,
  relatedId?: string
) {
  const { data } = await supabase
    .from('alerts')
    .insert({
      user_id: userId,
      alert_type: alertType,
      alert_level: alertLevel,
      title: `[${alertType}] ${alertLevel}`,
      message: message,
      related_id: relatedId,
      created_at: new Date()
    })
    .select()
    .single()

  // 즉시 전송
  await sendAlertNotifications(data)

  return data
}

// 2) 알림 전송 (다채널)
async function sendAlertNotifications(alert: Alert) {
  const settings = await getUserSettings(alert.user_id)

  for (const channel of settings.alert_channels) {
    switch (channel) {
      case 'email':
        await sendEmail(alert)
        break
      case 'push':
        await sendPushNotification(alert)
        break
      case 'telegram':
        await sendTelegramMessage(alert)
        break
    }
  }

  // 전송 완료 표시
  await supabase
    .from('alerts')
    .update({
      is_sent: true,
      sent_channels: settings.alert_channels
    })
    .eq('id', alert.id)
}

// 3) 알림 유형별 생성
// 신호 생성 알림
await createAlert(userId, 'SIGNAL', 'INFO',
  `${stockCode} 매수 신호 발생 (신뢰도: ${confidenceScore})`, signalId)

// 주문 체결 알림
await createAlert(userId, 'ORDER', 'INFO',
  `${stockCode} ${orderType} 주문 체결 (수량: ${quantity}, 가격: ${price})`, orderId)

// 손절 알림
await createAlert(userId, 'RISK', 'WARNING',
  `${stockCode} 손절 실행 (손실: ${profitLoss}원)`, positionId)

// 일일 손실 한도 알림
await createAlert(userId, 'SYSTEM', 'CRITICAL',
  '일일 손실 한도 도달 - 자동매매가 정지되었습니다')

// 4) 읽지 않은 알림 조회
const unreadAlerts = await supabase
  .from('alerts')
  .select('*')
  .eq('user_id', userId)
  .eq('is_read', false)
  .order('created_at', { ascending: false })
```

**알림 유형**:
- SIGNAL: 매수/매도 신호 생성
- ORDER: 주문 접수/체결/취소
- POSITION: 포지션 생성/종료
- RISK: 손절/익절, 한도 초과
- SYSTEM: 자동매매 상태 변경, 오류

---

## 6. 데이터 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                   키움 OpenAPI (WebSocket)                   │
│              실시간 시세, 체결, 잔고 데이터 수신               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  market_data 테이블                          │
│              실시간 시세 저장 (1분마다 갱신)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│             technical_indicators 테이블                      │
│          기술적 지표 계산 및 저장 (1분마다)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                 전략 실행 엔진 (n8n)                         │
│        1. strategies 테이블에서 활성 전략 조회                │
│        2. 지표 + 시세로 조건 평가                             │
│        3. 조건 충족 시 신호 생성                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              trading_signals 테이블                          │
│          매수/매도 신호 저장 (executed: false)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                주문 실행 엔진                                 │
│        1. 미실행 신호 조회                                    │
│        2. 리스크 체크 (한도, 포지션 수)                        │
│        3. 키움 API 주문 실행                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              kiwoom_orders 테이블                            │
│          주문 정보 저장 (status: PENDING)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓ (WebSocket 체결 알림)
┌─────────────────────────────────────────────────────────────┐
│         kiwoom_orders 업데이트 (status: FILLED)              │
│              + positions 생성/업데이트                        │
│              + account_balance 업데이트                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│           리스크 모니터링 (1분마다)                           │
│        1. positions에서 보유 종목 조회                        │
│        2. 현재가로 손익 계산                                  │
│        3. 손절/익절 조건 체크                                 │
│        4. 조건 충족 시 매도 신호 생성                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 구현 우선순위

### Phase 1: 데이터 수집 인프라 (1주)
1. ✅ market_data 실시간 수집 (WebSocket)
2. ✅ technical_indicators 계산 엔진
3. ✅ account_balance 정기 업데이트

### Phase 2: 신호 생성 시스템 (1주)
1. ✅ n8n 워크플로우 구성
2. ✅ 전략 조건 평가 엔진
3. ✅ trading_signals 생성 로직

### Phase 3: 주문 실행 시스템 (2주)
1. ✅ 키움 API 주문 실행
2. ✅ kiwoom_orders 관리
3. ✅ positions 자동 업데이트
4. ✅ 체결 WebSocket 연동

### Phase 4: 리스크 관리 (1주)
1. ✅ 손절/익절 자동 모니터링
2. ✅ 일일 손실 한도 체크
3. ✅ 포지션 사이즈 제한
4. ✅ system_settings 적용

### Phase 5: 알림 및 모니터링 (1주)
1. ✅ alerts 생성 및 전송
2. ✅ strategy_execution_logs 분석
3. ✅ 대시보드 UI

---

## 8. 데이터 보존 정책

### 단기 보존 (삭제)
- **market_data**: 1일 후 삭제 (일봉으로 집계)
- **alerts**: 읽음 처리 후 30일

### 중기 보존
- **technical_indicators**: 90일
- **strategy_execution_logs**: 180일

### 장기 보존 (영구)
- **kiwoom_orders**: 모든 주문 기록
- **positions**: 모든 포지션 기록
- **account_balance**: 월말 스냅샷
- **trading_signals**: 실행된 신호

---

## 9. 성능 최적화

### 인덱스 전략
```sql
-- 조회 성능 최적화
CREATE INDEX idx_market_data_stock_time ON market_data(stock_code, timestamp DESC);
CREATE INDEX idx_signals_execution ON trading_signals(strategy_id, executed, timestamp DESC);
CREATE INDEX idx_positions_performance ON positions(account_no, position_status, profit_loss_rate);
```

### 파티셔닝 (대용량 데이터)
```sql
-- market_data 월별 파티셔닝
CREATE TABLE market_data_2025_01 PARTITION OF market_data
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### 캐싱 전략
- 최신 시세: Redis (1초 TTL)
- 기술적 지표: Redis (1분 TTL)
- 계좌 잔고: Redis (10초 TTL)

---

이 계획대로 구현하면 완전한 실시간 자동매매 시스템을 구축할 수 있습니다!
