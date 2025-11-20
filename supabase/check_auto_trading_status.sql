-- 자동 매매 상태 진단
-- 실행: Supabase SQL Editor

-- 1. 활성화된 전략 확인
SELECT
  '=== 활성화된 자동매매 전략 ===' as section,
  id,
  user_id,
  strategy_name,
  stock_code,
  stock_name,
  is_active,
  max_investment_per_stock,
  created_at,
  updated_at
FROM strategy_monitoring
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
ORDER BY created_at DESC;

-- 2. 최근 발생한 시그널 확인 (24시간 이내)
SELECT
  '=== 최근 24시간 시그널 ===' as section,
  id,
  strategy_id,
  stock_code,
  stock_name,
  signal_type,
  signal_strength,
  current_price,
  target_price,
  stop_loss,
  confidence,
  reasons,
  created_at,
  EXTRACT(EPOCH FROM (NOW() - created_at)) / 60 as minutes_ago
FROM trading_signals
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 10;

-- 3. 시그널에 대응하는 주문 확인
SELECT
  '=== 시그널 → 주문 매칭 ===' as section,
  ts.id as signal_id,
  ts.stock_code,
  ts.signal_type,
  ts.created_at as signal_time,
  o.id as order_id,
  o.order_type,
  o.order_status,
  o.quantity,
  o.price,
  o.created_at as order_time,
  EXTRACT(EPOCH FROM (o.created_at - ts.created_at)) as seconds_delay,
  CASE
    WHEN o.id IS NULL THEN '❌ 주문 미생성'
    WHEN EXTRACT(EPOCH FROM (o.created_at - ts.created_at)) < 60 THEN '✅ 즉시 주문 생성 (<1분)'
    ELSE '⚠️ 지연 주문'
  END as order_status_check
FROM trading_signals ts
LEFT JOIN orders o ON ts.stock_code = o.stock_code
  AND ts.user_id = o.user_id
  AND ABS(EXTRACT(EPOCH FROM (o.created_at - ts.created_at))) < 300  -- 5분 이내
WHERE ts.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND ts.created_at > NOW() - INTERVAL '24 hours'
ORDER BY ts.created_at DESC
LIMIT 10;

-- 4. 주문 실행 상태
SELECT
  '=== 주문 실행 상태 ===' as section,
  id,
  stock_code,
  order_type,
  order_status,
  quantity,
  price,
  filled_quantity,
  average_filled_price,
  created_at,
  updated_at,
  CASE
    WHEN order_status = 'EXECUTED' THEN '✅ 체결 완료'
    WHEN order_status = 'SUBMITTED' THEN '⏳ 주문 제출됨'
    WHEN order_status = 'PENDING' THEN '⏸️ 대기 중'
    WHEN order_status = 'CANCELLED' THEN '❌ 취소됨'
    ELSE order_status
  END as status_emoji
FROM orders
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC
LIMIT 10;

-- 5. 전체 자동매매 파이프라인 요약
SELECT
  '=== 자동매매 파이프라인 요약 ===' as section,
  (SELECT COUNT(*) FROM strategy_monitoring WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) as active_strategies,
  (SELECT COUNT(*) FROM trading_signals WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND created_at > NOW() - INTERVAL '24 hours') as signals_24h,
  (SELECT COUNT(*) FROM orders WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND created_at > NOW() - INTERVAL '24 hours') as orders_24h,
  (SELECT COUNT(*) FROM orders WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND order_status = 'EXECUTED' AND created_at > NOW() - INTERVAL '24 hours') as executed_orders_24h,
  CASE
    WHEN (SELECT COUNT(*) FROM strategy_monitoring WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = 0
      THEN '❌ 활성 전략 없음'
    WHEN (SELECT COUNT(*) FROM trading_signals WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND created_at > NOW() - INTERVAL '24 hours') = 0
      THEN '⚠️ 시그널 미발생 (24시간)'
    WHEN (SELECT COUNT(*) FROM orders WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND created_at > NOW() - INTERVAL '24 hours') = 0
      THEN '❌ 주문 미생성'
    ELSE '✅ 정상 작동 중'
  END as pipeline_status;

-- 6. 현재 계좌 잔고 (주문 가능 여부 확인)
SELECT
  '=== 계좌 잔고 상태 ===' as section,
  account_number,
  total_cash,
  available_cash,
  stock_value,
  total_asset,
  CASE
    WHEN available_cash > 1000000 THEN '✅ 주문 가능 (100만원 이상)'
    WHEN available_cash > 100000 THEN '⚠️ 잔고 부족 (10~100만원)'
    ELSE '❌ 주문 불가 (10만원 미만)'
  END as order_availability,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_sync
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;
