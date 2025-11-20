-- =====================================================
-- 설정 완료 후 최종 확인
-- =====================================================

-- 1. 계좌 잔고 확인
SELECT
  '=== 1. 계좌 잔고 ===' as section,
  account_number,
  total_cash,
  available_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_display,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_ago
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- 2. 활성 전략 확인
SELECT
  '=== 2. 활성 전략 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  auto_execute,
  allocated_percent,
  target_stocks,
  ARRAY_LENGTH(target_stocks, 1) as stock_count,
  updated_at
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- 3. 비활성 전략 확인 (제대로 꺼졌는지)
SELECT
  '=== 3. 비활성 전략 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  allocated_percent
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = false
ORDER BY name;

-- 4. 5분 후 확인: strategy_monitoring 테이블 업데이트 여부
SELECT
  '=== 4. 워크플로우 실행 확인 (5분 후 실행) ===' as section,
  COUNT(*) as monitored_stocks,
  MAX(updated_at) as last_update,
  ROUND(EXTRACT(EPOCH FROM (NOW() - COALESCE(MAX(updated_at), NOW() - INTERVAL '999 days'))) / 60) as minutes_ago,
  STRING_AGG(DISTINCT stock_code, ', ') as stocks,
  CASE
    WHEN COUNT(*) = 0 THEN '⏳ 아직 워크플로우 시작 전 (1-2분 대기)'
    WHEN MAX(updated_at) > NOW() - INTERVAL '5 minutes' THEN '✅ 워크플로우 정상 작동 중'
    ELSE '⚠️ 워크플로우 지연'
  END as status
FROM strategy_monitoring;

-- 5. 예상 할당 금액 계산
SELECT
  '=== 5. 예상 할당 금액 ===' as section,
  s.name,
  s.allocated_percent || '%' as allocation,
  kb.available_cash,
  TO_CHAR(kb.available_cash, 'FM999,999,999') || '원' as balance_display,
  ROUND(kb.available_cash * s.allocated_percent / 100) as allocated_amount,
  TO_CHAR(ROUND(kb.available_cash * s.allocated_percent / 100), 'FM999,999,999') || '원' as allocated_display,
  CASE
    WHEN kb.available_cash = 0 THEN '⚠️ 잔고 0원 (계좌 동기화 필요)'
    WHEN kb.available_cash < 100000 THEN '⚠️ 잔고 부족 (10만원 미만)'
    ELSE '✅ 정상'
  END as status
FROM strategies s
CROSS JOIN (
  SELECT available_cash
  FROM kw_account_balance
  WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  ORDER BY updated_at DESC
  LIMIT 1
) kb
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true;

-- 6. 다음 단계 안내
SELECT
  '=== 6. 📋 다음 단계 ===' as section,
  '1. 1-2분 대기 후 이 SQL을 다시 실행하여 strategy_monitoring 확인' as step1,
  '2. n8n 대시보드에서 workflow-v7-1 실행 로그 확인' as step2,
  '3. 조건 충족 시 자동으로 시그널 및 주문 발생' as step3,
  '4. UI에서 실시간 모니터링' as step4;
