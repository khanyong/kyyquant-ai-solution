-- ============================================================================
-- 동기화 결과 확인
-- ============================================================================

-- 1. kw_portfolio 현재 상태
SELECT
  '=== kw_portfolio 현황 ===' as section;

SELECT
  stock_code,
  stock_name,
  quantity,
  avg_price,
  purchase_amount,
  profit_loss,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_update
FROM kw_portfolio
ORDER BY updated_at DESC;

-- 2. kw_account_balance 현재 상태
SELECT
  '=== kw_account_balance 현황 ===' as section;

SELECT
  account_number,
  total_cash,
  stock_value,
  total_asset,
  profit_loss,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_update
FROM kw_account_balance
ORDER BY updated_at DESC;

-- 3. positions 현재 상태
SELECT
  '=== positions 현황 ===' as section;

SELECT
  stock_code,
  stock_name,
  quantity,
  position_status,
  last_updated
FROM positions
WHERE position_status = 'open'
ORDER BY last_updated DESC;
