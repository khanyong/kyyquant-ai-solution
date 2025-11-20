-- =====================================================
-- available_cash 임시 복구
-- =====================================================
-- 문제: 전략 비활성화 시 할당 금액이 회수되지 않아
--       available_cash = 0으로 남아있음
--
-- 해결: available_cash를 total_cash로 복구
--       (현재 활성 전략이 1개뿐이고, 미체결 주문 없음)
-- =====================================================

-- STEP 1: 현재 상태 확인
SELECT
  '=== 1. 현재 계좌 상태 ===' as section,
  account_number,
  total_cash,
  TO_CHAR(total_cash, 'FM999,999,999') || '원' as total_display,
  available_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_display,
  order_cash,
  TO_CHAR(order_cash, 'FM999,999,999') || '원' as order_display,
  CASE
    WHEN available_cash = 0 AND total_cash > 0 THEN '❌ 회수 안됨'
    WHEN available_cash = total_cash THEN '✅ 정상'
    ELSE '⚠️ 확인 필요'
  END as status
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- STEP 2: 활성 전략 확인
SELECT
  '=== 2. 활성 전략 ===' as section,
  name,
  is_active,
  allocated_percent,
  allocated_capital,
  TO_CHAR(allocated_capital, 'FM999,999,999') || '원' as allocated_display
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- STEP 3: 미체결 주문 확인
SELECT
  '=== 3. 미체결 주문 ===' as section,
  COUNT(*) as pending_order_count,
  COALESCE(SUM(order_price * order_quantity), 0) as total_pending_amount,
  TO_CHAR(COALESCE(SUM(order_price * order_quantity), 0), 'FM999,999,999') || '원' as total_pending_display,
  CASE
    WHEN COUNT(*) = 0 THEN '✅ 미체결 주문 없음 (복구 안전)'
    ELSE '⚠️ 미체결 주문 있음 (복구 주의)'
  END as safety
FROM orders
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND order_status IN ('PENDING', 'PARTIAL');

-- STEP 4: 복구 실행
-- 주의: 미체결 주문이 있는 경우 실행하지 마세요!
UPDATE kw_account_balance
SET
  available_cash = total_cash - COALESCE(order_cash, 0),
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- STEP 5: 복구 결과 확인
SELECT
  '=== 5. 복구 후 상태 ===' as section,
  account_number,
  total_cash,
  TO_CHAR(total_cash, 'FM999,999,999') || '원' as total_display,
  available_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_display,
  order_cash,
  TO_CHAR(order_cash, 'FM999,999,999') || '원' as order_display,
  CASE
    WHEN available_cash > 0 THEN '✅ 복구 완료'
    ELSE '❌ 여전히 0원'
  END as status,
  updated_at,
  ROUND(EXTRACT(EPOCH FROM (NOW() - updated_at))) as seconds_ago
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- STEP 6: 활성 전략에 금액 재할당 (필요한 경우)
-- 현재 [템플릿] 볼린저밴드가 100% 할당되어 있음
UPDATE strategies
SET
  allocated_capital = (
    SELECT available_cash * allocated_percent / 100
    FROM kw_account_balance
    WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    ORDER BY updated_at DESC
    LIMIT 1
  ),
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
  AND allocated_percent > 0;

-- STEP 7: 최종 확인
SELECT
  '=== 7. 최종 확인 ===' as section,
  s.name,
  s.allocated_percent || '%' as allocation_percent,
  s.allocated_capital as allocated_capital,
  TO_CHAR(s.allocated_capital, 'FM999,999,999') || '원' as allocated_display,
  kb.available_cash as remaining_cash,
  TO_CHAR(kb.available_cash, 'FM999,999,999') || '원' as remaining_display,
  kb.total_cash as total_cash,
  TO_CHAR(kb.total_cash, 'FM999,999,999') || '원' as total_display,
  CASE
    WHEN s.allocated_capital + kb.available_cash = kb.total_cash THEN '✅ 금액 일치'
    ELSE '❌ 금액 불일치'
  END as validation
FROM strategies s
CROSS JOIN (
  SELECT total_cash, available_cash
  FROM kw_account_balance
  WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  ORDER BY updated_at DESC
  LIMIT 1
) kb
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true;
