-- =====================================================
-- 자동 매매 테스트: 시그널 발생 → 주문 생성 검증
-- 실행: Supabase SQL Editor
-- =====================================================

-- ============================================================
-- STEP 1: 현재 시스템 상태 확인
-- ============================================================

-- 1-1. 활성 전략 확인
SELECT
  '=== 1. 활성 전략 ===' as section,
  id,
  name,
  user_id,
  is_active,
  entry_conditions,
  position_size_percent,
  max_positions,
  created_at
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- 1-2. 전략의 투자 유니버스 확인
SELECT
  '=== 2. 투자 유니버스 (모니터링 대상) ===' as section,
  s.name as strategy_name,
  iu.stock_code,
  iu.stock_name,
  iu.created_at
FROM investment_universe iu
JOIN strategies s ON s.id = iu.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true
ORDER BY s.name, iu.stock_code;

-- 1-3. 현재 strategy_monitoring 상태 (매수 대기 종목)
SELECT
  '=== 3. 현재 매수 대기 종목 ===' as section,
  sm.id,
  s.name as strategy_name,
  sm.stock_code,
  sm.stock_name,
  sm.current_price,
  sm.condition_match_score,
  sm.is_near_entry,
  sm.conditions_met,
  sm.updated_at,
  CASE
    WHEN sm.condition_match_score >= 100 THEN '✅ 즉시 매수 가능'
    WHEN sm.condition_match_score >= 80 THEN '⏳ 매수 준비 중'
    ELSE '⚠️ 조건 미달'
  END as status
FROM strategy_monitoring sm
JOIN strategies s ON s.id = sm.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY sm.condition_match_score DESC, sm.updated_at DESC;

-- 1-4. 최근 24시간 시그널 현황
SELECT
  '=== 4. 최근 24시간 시그널 ===' as section,
  ts.id,
  s.name as strategy_name,
  ts.stock_code,
  ts.stock_name,
  ts.signal_type,
  ts.signal_strength,
  ts.current_price,
  ts.signal_status,
  ts.order_id,
  ts.created_at,
  EXTRACT(EPOCH FROM (NOW() - ts.created_at)) / 60 as minutes_ago
FROM trading_signals ts
JOIN strategies s ON s.id = ts.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND ts.created_at > NOW() - INTERVAL '24 hours'
ORDER BY ts.created_at DESC
LIMIT 20;

-- 1-5. 최근 주문 현황
SELECT
  '=== 5. 최근 주문 ===' as section,
  o.id,
  o.stock_code,
  o.order_type,
  o.order_status,
  o.quantity,
  o.price,
  o.filled_quantity,
  o.auto_cancel_at,
  o.created_at,
  CASE
    WHEN o.order_status = 'EXECUTED' THEN '✅ 체결 완료'
    WHEN o.order_status = 'SUBMITTED' THEN '⏳ 주문 제출됨'
    WHEN o.order_status = 'PENDING' THEN '⏸️ 대기 중'
    WHEN o.order_status = 'CANCELLED' THEN '❌ 취소됨'
    ELSE o.order_status
  END as status_display,
  CASE
    WHEN o.auto_cancel_at IS NOT NULL AND o.auto_cancel_at > NOW() THEN
      '⏰ ' || EXTRACT(EPOCH FROM (o.auto_cancel_at - NOW())) / 60 || '분 후 자동취소'
    WHEN o.auto_cancel_at IS NOT NULL AND o.auto_cancel_at <= NOW() THEN
      '⚠️ 자동취소 시간 경과'
    ELSE '-'
  END as cancel_info
FROM orders o
WHERE o.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND o.created_at > NOW() - INTERVAL '24 hours'
ORDER BY o.created_at DESC
LIMIT 20;

-- ============================================================
-- STEP 2: 자동매매 파이프라인 상태 진단
-- ============================================================

SELECT
  '=== 6. 자동매매 파이프라인 요약 ===' as section,
  (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) as active_strategies,
  (SELECT COUNT(DISTINCT sm.stock_code) FROM strategy_monitoring sm JOIN strategies s ON s.id = sm.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as monitored_stocks,
  (SELECT COUNT(*) FROM strategy_monitoring sm JOIN strategies s ON s.id = sm.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND sm.condition_match_score >= 100) as ready_to_buy,
  (SELECT COUNT(*) FROM trading_signals ts JOIN strategies s ON s.id = ts.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND ts.created_at > NOW() - INTERVAL '24 hours') as signals_24h,
  (SELECT COUNT(*) FROM orders WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND created_at > NOW() - INTERVAL '24 hours') as orders_24h,
  (SELECT COUNT(*) FROM orders WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND order_status = 'EXECUTED' AND created_at > NOW() - INTERVAL '24 hours') as executed_orders_24h;

-- ============================================================
-- STEP 3: n8n 워크플로우 실행 상태 확인
-- ============================================================

-- 3-1. strategy_monitoring 최근 업데이트 확인 (워크플로우 v7-1 실행 여부)
SELECT
  '=== 7. 조건 모니터링 워크플로우 실행 상태 ===' as section,
  COUNT(*) as total_monitored,
  MAX(updated_at) as last_update,
  EXTRACT(EPOCH FROM (NOW() - MAX(updated_at))) / 60 as minutes_since_update,
  CASE
    WHEN MAX(updated_at) > NOW() - INTERVAL '5 minutes' THEN '✅ 정상 작동 (<5분)'
    WHEN MAX(updated_at) > NOW() - INTERVAL '30 minutes' THEN '⚠️ 지연 (5-30분)'
    ELSE '❌ 워크플로우 중단 (>30분)'
  END as workflow_status
FROM strategy_monitoring sm
JOIN strategies s ON s.id = sm.strategy_id
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- ============================================================
-- STEP 4: 계좌 잔고 및 주문 가능 여부 확인
-- ============================================================

SELECT
  '=== 8. 계좌 잔고 및 주문 가능 여부 ===' as section,
  account_number,
  total_cash,
  available_cash,
  order_cash,
  stock_value,
  total_asset,
  CASE
    WHEN available_cash > 10000000 THEN '✅ 1천만원 이상 (대형 매수 가능)'
    WHEN available_cash > 1000000 THEN '✅ 100만원 이상 (소형 매수 가능)'
    WHEN available_cash > 100000 THEN '⚠️ 10만원 이상 (초소형만 가능)'
    ELSE '❌ 주문 불가 (잔고 부족)'
  END as order_capability,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_sync
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- ============================================================
-- STEP 5: 테스트 시그널 수동 생성 (선택사항)
-- ============================================================

-- 주의: 실제 주문이 발생할 수 있으므로 테스트 환경에서만 사용
-- 이 쿼리는 주석 처리되어 있습니다. 필요시 주석 해제하여 사용하세요.

/*
-- 5-1. 테스트용 매수 시그널 생성
INSERT INTO trading_signals (
  user_id,
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
  signal_status
)
SELECT
  'f912da32-897f-4dbb-9242-3a438e9733a8',
  s.id,
  '005930',
  '삼성전자',
  'BUY',
  'STRONG',
  72000,
  76000,
  68000,
  0.85,
  ARRAY['RSI < 30 (과매도)', '거래량 급증 (2.5배)', '이동평균선 돌파'],
  'PENDING'
FROM strategies s
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true
LIMIT 1
RETURNING id, stock_code, stock_name, signal_type, created_at;
*/

-- ============================================================
-- STEP 6: 자동매매 문제 진단
-- ============================================================

SELECT
  '=== 9. 자동매매 문제 진단 ===' as section,
  CASE
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = 0
      THEN '❌ 문제: 활성 전략 없음 → 전략을 활성화하세요'
    WHEN (SELECT COUNT(*) FROM investment_universe iu JOIN strategies s ON s.id = iu.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND s.is_active = true) = 0
      THEN '❌ 문제: 투자 유니버스 비어있음 → 모니터링할 종목을 추가하세요'
    WHEN (SELECT MAX(updated_at) FROM strategy_monitoring sm JOIN strategies s ON s.id = sm.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') < NOW() - INTERVAL '30 minutes'
      THEN '❌ 문제: 조건 모니터링 워크플로우 중단 → n8n workflow-v7-1을 확인하세요'
    WHEN (SELECT COUNT(*) FROM strategy_monitoring sm JOIN strategies s ON s.id = sm.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND sm.condition_match_score >= 100) > 0
      AND (SELECT COUNT(*) FROM trading_signals ts JOIN strategies s ON s.id = ts.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND ts.created_at > NOW() - INTERVAL '5 minutes') = 0
      THEN '❌ 문제: 조건 충족 종목 있지만 시그널 미발생 → n8n workflow-v7-2를 확인하세요'
    WHEN (SELECT COUNT(*) FROM trading_signals WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND signal_status = 'PENDING' AND created_at > NOW() - INTERVAL '5 minutes') > 0
      AND (SELECT COUNT(*) FROM orders WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND created_at > NOW() - INTERVAL '5 minutes') = 0
      THEN '❌ 문제: 시그널 있지만 주문 미생성 → workflow-v7-2의 주문 생성 로직 확인'
    WHEN (SELECT available_cash FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' ORDER BY updated_at DESC LIMIT 1) < 100000
      THEN '⚠️ 주의: 잔고 부족 (10만원 미만) → 계좌에 입금이 필요합니다'
    ELSE '✅ 정상: 모든 구성요소 작동 중'
  END as diagnosis,
  CASE
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = 0
      THEN '전략 페이지에서 전략을 활성화하세요'
    WHEN (SELECT COUNT(*) FROM investment_universe iu JOIN strategies s ON s.id = iu.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND s.is_active = true) = 0
      THEN '전략 설정에서 투자 유니버스 종목을 추가하세요'
    WHEN (SELECT MAX(updated_at) FROM strategy_monitoring sm JOIN strategies s ON s.id = sm.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') < NOW() - INTERVAL '30 minutes'
      THEN 'n8n에서 workflow-v7-1-condition-monitoring이 Active 상태인지 확인'
    ELSE '시그널 발생 대기 중 (시장 조건이 매수 조건을 충족할 때까지 대기)'
  END as recommendation;

-- ============================================================
-- STEP 7: 실시간 모니터링 뷰 (계속 새로고침하여 사용)
-- ============================================================

SELECT
  '=== 10. 실시간 대시보드 ===' as section,
  'Active Strategies: ' || (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) as stat1,
  'Monitored Stocks: ' || (SELECT COUNT(*) FROM strategy_monitoring sm JOIN strategies s ON s.id = sm.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as stat2,
  'Ready to Buy (Score 100): ' || (SELECT COUNT(*) FROM strategy_monitoring sm JOIN strategies s ON s.id = sm.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND sm.condition_match_score >= 100) as stat3,
  'Signals Today: ' || (SELECT COUNT(*) FROM trading_signals ts JOIN strategies s ON s.id = ts.strategy_id WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND ts.created_at > CURRENT_DATE) as stat4,
  'Orders Today: ' || (SELECT COUNT(*) FROM orders WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND created_at > CURRENT_DATE) as stat5,
  'Available Cash: ₩' || TO_CHAR((SELECT available_cash FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' ORDER BY updated_at DESC LIMIT 1), 'FM999,999,999') as stat6;
