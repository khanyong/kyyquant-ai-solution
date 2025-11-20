-- =====================================================
-- 실제로 활성화된 전략 확인
-- user_id: f912da32-897f-4dbb-9242-3a438e9733a8
-- =====================================================

-- 모든 전략 상태 확인
SELECT
  '=== 전체 전략 상태 ===' as section,
  name,
  is_active,
  auto_trade_enabled,
  auto_execute,
  allocated_percent,
  allocated_capital,
  target_stocks,
  universe,
  created_at,
  updated_at,
  CASE
    WHEN is_active = true THEN '✅ 활성화'
    ELSE '❌ 비활성화'
  END as status
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY is_active DESC, updated_at DESC;

-- 활성화된 전략만
SELECT
  '=== 활성화된 전략만 ===' as section,
  name,
  auto_trade_enabled,
  auto_execute,
  allocated_percent,
  COALESCE(ARRAY_LENGTH(target_stocks, 1), ARRAY_LENGTH(universe, 1), 0) as stock_count
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
ORDER BY name;
