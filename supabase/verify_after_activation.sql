-- =====================================================
-- 전략 활성화 후 확인
-- user_id: f912da32-897f-4dbb-9242-3a438e9733a8
-- =====================================================

-- 1. 전략 설정 확인
SELECT
  '=== 1. 전략 설정 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  auto_execute,
  target_stocks,
  universe,
  COALESCE(ARRAY_LENGTH(target_stocks, 1), ARRAY_LENGTH(universe, 1), 0) as stock_count,
  allocated_capital,
  allocated_percent,
  CASE
    WHEN NOT is_active THEN '❌ 전략 비활성화'
    WHEN NOT (auto_trade_enabled OR auto_execute) THEN '❌ 자동매매 꺼짐'
    WHEN COALESCE(ARRAY_LENGTH(target_stocks, 1), ARRAY_LENGTH(universe, 1), 0) = 0 THEN '❌ 종목 없음'
    ELSE '✅ 모든 설정 완료'
  END as status
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
ORDER BY name;

-- 2. strategy_monitoring 업데이트 확인 (워크플로우 실행 여부)
SELECT
  '=== 2. 워크플로우 실행 확인 ===' as section,
  COUNT(*) as monitored_stocks,
  MAX(updated_at) as last_update,
  ROUND(EXTRACT(EPOCH FROM (NOW() - COALESCE(MAX(updated_at), NOW() - INTERVAL '999 days'))) / 60) as minutes_ago,
  STRING_AGG(DISTINCT stock_code, ', ') as stock_codes,
  CASE
    WHEN COUNT(*) = 0 THEN '❌ 아직 워크플로우 미실행 (1-2분 대기)'
    WHEN MAX(updated_at) > NOW() - INTERVAL '5 minutes' THEN '✅ 워크플로우 정상 작동'
    ELSE '⚠️ 워크플로우 지연'
  END as status
FROM strategy_monitoring;

-- 3. 모니터링 중인 종목 점수
SELECT
  '=== 3. 종목별 조건 충족도 ===' as section,
  stock_code,
  stock_name,
  current_price,
  condition_match_score,
  is_near_entry,
  updated_at,
  CASE
    WHEN condition_match_score >= 100 THEN '🔴 100점 → 즉시 매수 신호 발생!'
    WHEN condition_match_score >= 80 THEN '🟡 80-99점 → 매수 대기'
    WHEN condition_match_score >= 50 THEN '🔵 50-79점'
    ELSE '⚪ <50점'
  END as status
FROM strategy_monitoring
ORDER BY condition_match_score DESC;

-- 4. 최근 시그널 발생 여부
SELECT
  '=== 4. 최근 시그널 ===' as section,
  COUNT(*) as signal_count,
  STRING_AGG(stock_code || '(' || signal_type || ')', ', ') as signals,
  MAX(created_at) as last_signal,
  CASE
    WHEN COUNT(*) = 0 THEN '⏳ 시그널 대기 중 (조건 충족 시 자동 발생)'
    ELSE '✅ 시그널 ' || COUNT(*) || '건 발생'
  END as status
FROM trading_signals
WHERE created_at > NOW() - INTERVAL '1 hour';

-- 5. 최근 주문 발생 여부
SELECT
  '=== 5. 최근 주문 ===' as section,
  COUNT(*) as order_count,
  STRING_AGG(stock_code || '(' || order_type || ')', ', ') as orders,
  MAX(created_at) as last_order,
  CASE
    WHEN COUNT(*) = 0 THEN '⏳ 주문 대기 중 (시그널 발생 시 자동 생성)'
    ELSE '✅ 주문 ' || COUNT(*) || '건 발생'
  END as status
FROM orders
WHERE created_at > NOW() - INTERVAL '1 hour';

-- 6. 종합 상태
SELECT
  '=== 6. 🎯 종합 상태 ===' as section,
  (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true AND (auto_trade_enabled OR auto_execute)) as active_strategies,
  (SELECT COUNT(*) FROM strategy_monitoring WHERE updated_at > NOW() - INTERVAL '5 minutes') as monitoring_active,
  (SELECT COALESCE(MAX(condition_match_score), 0) FROM strategy_monitoring) as max_score,
  (SELECT COUNT(*) FROM trading_signals WHERE created_at > NOW() - INTERVAL '1 hour') as signals_1h,
  (SELECT COUNT(*) FROM orders WHERE created_at > NOW() - INTERVAL '1 hour') as orders_1h,
  CASE
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true AND (auto_trade_enabled OR auto_execute)) = 0
      THEN '❌ 활성 전략 없음'
    WHEN (SELECT COUNT(*) FROM strategy_monitoring WHERE updated_at > NOW() - INTERVAL '5 minutes') = 0
      THEN '⏳ 워크플로우 시작 대기 중 (1-2분 소요)'
    WHEN (SELECT COALESCE(MAX(condition_match_score), 0) FROM strategy_monitoring) < 80
      THEN '✅ 정상 작동 (조건 미달 대기)'
    WHEN (SELECT COALESCE(MAX(condition_match_score), 0) FROM strategy_monitoring) >= 80
      THEN '🎉 조건 충족 근접! (' || (SELECT COALESCE(MAX(condition_match_score), 0) FROM strategy_monitoring) || '점)'
    ELSE '✅ 시스템 정상'
  END as overall_status;
