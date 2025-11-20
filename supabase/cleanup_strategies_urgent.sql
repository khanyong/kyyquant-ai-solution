-- =====================================================
-- 긴급: 전략 정리 (is_active 31개 → 1개)
-- =====================================================
-- 문제: is_active = true가 31개나 되어 시스템 혼란
-- 해결: 실제 사용 중인 전략 1개만 남기고 모두 비활성화
-- =====================================================

-- STEP 1: 현재 상태 확인
SELECT
  '=== 1. 전체 전략 통계 ===' as section,
  COUNT(*) as total_strategies,
  COUNT(CASE WHEN is_active = true THEN 1 END) as active_strategies,
  COUNT(CASE WHEN auto_trade_enabled = true THEN 1 END) as auto_trade_enabled_count,
  COUNT(CASE WHEN auto_execute = true THEN 1 END) as auto_execute_count
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- STEP 2: 실제 사용 중인 전략 확인
SELECT
  '=== 2. 실제 사용 중인 전략 ===' as section,
  id,
  name,
  is_active,
  auto_trade_enabled,
  auto_execute,
  allocated_percent,
  allocated_capital,
  COALESCE(ARRAY_LENGTH(target_stocks, 1), 0) as stock_count,
  updated_at
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND (
    auto_trade_enabled = true
    OR auto_execute = true
    OR allocated_percent > 0
    OR allocated_capital > 0
  )
ORDER BY updated_at DESC;

-- STEP 3: 모든 전략 비활성화 (안전하게)
UPDATE strategies
SET
  is_active = false,
  auto_trade_enabled = false,
  auto_execute = false,
  allocated_capital = 0,
  allocated_percent = 0,
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- STEP 4: [템플릿] 볼린저밴드 1개만 활성화
UPDATE strategies
SET
  is_active = true,
  auto_trade_enabled = true,
  auto_execute = true,
  allocated_percent = 50,
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND name = '[템플릿] 볼린저밴드';

-- STEP 5: allocated_capital 계산
UPDATE strategies
SET
  allocated_capital = (
    SELECT
      CASE
        WHEN COALESCE(available_cash, total_cash, deposit, 0) > 0
        THEN ROUND(COALESCE(available_cash, total_cash, deposit) * 50 / 100)
        ELSE 0
      END
    FROM kw_account_balance
    WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    ORDER BY updated_at DESC
    LIMIT 1
  ),
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND name = '[템플릿] 볼린저밴드';

-- STEP 6: available_cash 차감
UPDATE kw_account_balance
SET
  available_cash = COALESCE(total_cash, deposit, 0) - (
    SELECT COALESCE(SUM(allocated_capital), 0)
    FROM strategies
    WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
      AND is_active = true
  ),
  updated_at = NOW()
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- STEP 7: 최종 결과 확인
SELECT
  '=== 7. 정리 후 활성 전략 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  auto_execute,
  allocated_percent,
  allocated_capital,
  TO_CHAR(allocated_capital, 'FM999,999,999') || '원' as allocated_display,
  ARRAY_TO_STRING(target_stocks, ', ') as target_stocks_display
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- STEP 8: 계좌 잔고 확인
SELECT
  '=== 8. 계좌 잔고 ===' as section,
  total_cash,
  TO_CHAR(total_cash, 'FM999,999,999') || '원' as total_display,
  available_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_display,
  (SELECT SUM(allocated_capital) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) as total_allocated,
  TO_CHAR(
    (SELECT SUM(allocated_capital) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true),
    'FM999,999,999'
  ) || '원' as allocated_display,
  CASE
    WHEN available_cash + (SELECT COALESCE(SUM(allocated_capital), 0) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = COALESCE(total_cash, deposit, 0)
    THEN '✅ 금액 일치'
    ELSE '❌ 금액 불일치'
  END as validation
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- STEP 9: 전체 통계 (정리 후)
SELECT
  '=== 9. 정리 후 전체 통계 ===' as section,
  COUNT(*) as total_strategies,
  COUNT(CASE WHEN is_active = true THEN 1 END) as active_strategies,
  COUNT(CASE WHEN auto_trade_enabled = true THEN 1 END) as auto_trade_enabled_count,
  '✅ 정리 완료! 이제 UI를 새로고침하세요.' as next_step
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
