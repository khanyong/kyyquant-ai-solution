-- =====================================================
-- 현금 할당 및 회수 로직 확인
-- =====================================================

-- 1. 현재 계좌 잔고 상태
SELECT
  '=== 1. 계좌 잔고 현황 ===' as section,
  account_number,
  total_cash,
  TO_CHAR(total_cash, 'FM999,999,999') || '원' as total_display,
  available_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_display,
  order_cash,
  TO_CHAR(order_cash, 'FM999,999,999') || '원' as order_display,
  deposit,
  substitute_money,
  total_asset,
  updated_at,
  ROUND(EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60) as minutes_ago
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- 2. 전략별 할당 금액
SELECT
  '=== 2. 전략별 할당 상태 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  allocated_percent,
  allocated_capital,
  TO_CHAR(allocated_capital, 'FM999,999,999') || '원' as allocated_display,
  COALESCE(ARRAY_LENGTH(target_stocks, 1), 0) as stock_count,
  updated_at
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY is_active DESC, updated_at DESC;

-- 3. 활성 전략의 총 할당 금액 계산
SELECT
  '=== 3. 활성 전략 총 할당 ===' as section,
  COUNT(*) as active_strategy_count,
  SUM(allocated_percent) as total_allocated_percent,
  SUM(allocated_capital) as total_allocated_capital,
  TO_CHAR(SUM(allocated_capital), 'FM999,999,999') || '원' as total_allocated_display
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- 4. 예상 available_cash 계산
SELECT
  '=== 4. 예상 사용가능 현금 ===' as section,
  kb.total_cash,
  TO_CHAR(kb.total_cash, 'FM999,999,999') || '원' as total_display,
  COALESCE(SUM(s.allocated_capital), 0) as allocated_to_strategies,
  TO_CHAR(COALESCE(SUM(s.allocated_capital), 0), 'FM999,999,999') || '원' as allocated_display,
  kb.total_cash - COALESCE(SUM(s.allocated_capital), 0) as expected_available_cash,
  TO_CHAR(kb.total_cash - COALESCE(SUM(s.allocated_capital), 0), 'FM999,999,999') || '원' as expected_available_display,
  kb.available_cash as actual_available_cash,
  TO_CHAR(kb.available_cash, 'FM999,999,999') || '원' as actual_available_display,
  CASE
    WHEN kb.available_cash = (kb.total_cash - COALESCE(SUM(s.allocated_capital), 0)) THEN '✅ 정상'
    ELSE '❌ 불일치 (회수 로직 없음?)'
  END as status
FROM (
  SELECT total_cash, available_cash
  FROM kw_account_balance
  WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  ORDER BY updated_at DESC
  LIMIT 1
) kb
CROSS JOIN (
  SELECT COALESCE(SUM(allocated_capital), 0) as allocated_capital
  FROM strategies
  WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    AND is_active = true
) s;

-- 5. 전략 활성화/비활성화 이력 (updated_at 기준)
SELECT
  '=== 5. 전략 변경 이력 (최근 10개) ===' as section,
  name,
  is_active,
  allocated_percent,
  allocated_capital,
  TO_CHAR(allocated_capital, 'FM999,999,999') || '원' as allocated_display,
  updated_at,
  ROUND(EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60) as minutes_ago
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 10;

-- 6. 진단: available_cash = 0 원인
SELECT
  '=== 6. 진단 결과 ===' as section,
  CASE
    WHEN kb.available_cash = 0 AND kb.total_cash > 0 THEN
      '❌ 문제: total_cash는 있지만 available_cash = 0'
    WHEN kb.available_cash = kb.total_cash THEN
      '✅ 정상: 모든 현금이 사용 가능'
    WHEN kb.available_cash < kb.total_cash THEN
      '⚠️ 일부 현금 사용 중 (주문 또는 전략 할당)'
    ELSE
      '⚠️ 알 수 없는 상태'
  END as diagnosis,
  CASE
    WHEN kb.available_cash = 0 AND active_count > 0 THEN
      '전략을 비활성화 했지만 allocated_capital이 회수되지 않음'
    WHEN kb.available_cash = 0 AND active_count = 0 THEN
      '활성 전략이 없는데도 available_cash = 0 (동기화 필요)'
    ELSE
      '정상 범위'
  END as possible_cause,
  '1. 계좌 동기화 버튼 클릭 또는 2. available_cash 수동 업데이트 필요' as solution
FROM (
  SELECT total_cash, available_cash
  FROM kw_account_balance
  WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  ORDER BY updated_at DESC
  LIMIT 1
) kb
CROSS JOIN (
  SELECT COUNT(*) as active_count
  FROM strategies
  WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    AND is_active = true
) s;

-- 7. 임시 해결책: available_cash를 total_cash로 업데이트
-- (주의: 실제 주문이 있는 경우 실행하면 안됨!)
SELECT
  '=== 7. 임시 해결책 SQL (확인 후 실행) ===' as section,
  '아래 SQL을 복사하여 실행하면 available_cash를 total_cash로 설정합니다.' as instruction,
  '주의: 실제 미체결 주문이 있는 경우 실행하지 마세요!' as warning;

-- 실행할 SQL (주석 해제 후 실행):
-- UPDATE kw_account_balance
-- SET
--   available_cash = total_cash,
--   updated_at = NOW()
-- WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
