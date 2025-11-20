-- =====================================================
-- allocated_capital 즉시 수정
-- =====================================================
-- 문제: allocated_percent는 50%인데 allocated_capital이 0
-- 해결: available_cash 기준으로 allocated_capital 계산
-- =====================================================

-- STEP 1: 현재 상태 확인
SELECT
  '=== 1. 현재 전략 상태 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  allocated_percent,
  allocated_capital,
  TO_CHAR(allocated_capital, 'FM999,999,999') || '원' as allocated_display
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY is_active DESC, name;

-- STEP 2: 계좌 잔고 확인
SELECT
  '=== 2. 계좌 잔고 ===' as section,
  total_cash,
  TO_CHAR(total_cash, 'FM999,999,999') || '원' as total_display,
  available_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_display,
  deposit,
  TO_CHAR(deposit, 'FM999,999,999') || '원' as deposit_display
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- STEP 3: allocated_capital 계산 및 업데이트
UPDATE strategies
SET
  allocated_capital = (
    SELECT
      CASE
        WHEN COALESCE(available_cash, total_cash, deposit, 0) > 0
        THEN ROUND(COALESCE(available_cash, total_cash, deposit) * allocated_percent / 100)
        ELSE 0
      END
    FROM kw_account_balance
    WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    ORDER BY updated_at DESC
    LIMIT 1
  ),
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
  AND allocated_percent > 0;

-- STEP 4: available_cash 차감
UPDATE kw_account_balance
SET
  available_cash = total_cash - (
    SELECT COALESCE(SUM(allocated_capital), 0)
    FROM strategies
    WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
      AND is_active = true
  ),
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- STEP 5: 결과 확인
SELECT
  '=== 5. 수정 후 전략 상태 ===' as section,
  name,
  is_active,
  allocated_percent,
  allocated_capital,
  TO_CHAR(allocated_capital, 'FM999,999,999') || '원' as allocated_display
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- STEP 6: 수정 후 계좌 잔고
SELECT
  '=== 6. 수정 후 계좌 잔고 ===' as section,
  total_cash,
  TO_CHAR(total_cash, 'FM999,999,999') || '원' as total_display,
  available_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_display,
  CASE
    WHEN available_cash + (SELECT COALESCE(SUM(allocated_capital), 0) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = total_cash
    THEN '✅ 금액 일치'
    ELSE '❌ 금액 불일치'
  END as validation
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;
