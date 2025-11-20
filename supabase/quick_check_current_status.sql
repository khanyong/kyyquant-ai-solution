-- 현재 상태 빠른 확인
-- user_id: f912da32-897f-4dbb-9242-3a438e9733a8

-- 1. 계좌 잔고
SELECT
  'Current Balance' as check_type,
  TO_CHAR(total_cash, 'FM999,999,999') || '원' as total_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_cash
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- 2. 활성 전략
SELECT
  'Active Strategies' as check_type,
  COUNT(*) as count,
  STRING_AGG(name, ', ') as strategy_names,
  SUM(position_size_percent) as total_allocation_percent
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true;

-- 3. 전략 상세
SELECT
  name,
  position_size_percent || '%' as allocation,
  max_positions,
  TO_CHAR(max_investment_per_stock, 'FM999,999,999') || '원' as max_per_stock,
  is_active
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY is_active DESC, created_at DESC;
