-- 키움 계좌 동기화 후 데이터 확인

-- 1. 계좌 잔고 확인
SELECT
  '계좌 잔고' as table_name,
  id,
  user_id,
  account_number,
  total_cash,
  available_cash,
  order_cash,
  total_asset,
  stock_value,
  profit_loss,
  profit_loss_rate,
  updated_at
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- 2. 보유 종목 확인
SELECT
  '보유 종목' as table_name,
  id,
  user_id,
  account_number,
  stock_code,
  stock_name,
  quantity,
  available_quantity,
  avg_price,
  current_price,
  purchase_amount,
  evaluated_amount,
  profit_loss,
  profit_loss_rate,
  updated_at
FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY evaluated_amount DESC;

-- 3. 요약 통계
SELECT
  (SELECT COUNT(*) FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as balance_count,
  (SELECT COUNT(*) FROM kw_portfolio WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as portfolio_count,
  (SELECT MAX(updated_at) FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as last_balance_update,
  (SELECT MAX(updated_at) FROM kw_portfolio WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as last_portfolio_update;

-- 4. 최근 동기화 내역 (있다면)
SELECT
  table_name,
  COUNT(*) as record_count,
  MAX(updated_at) as last_update
FROM (
  SELECT 'kw_account_balance' as table_name, updated_at FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  UNION ALL
  SELECT 'kw_portfolio' as table_name, updated_at FROM kw_portfolio WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
) combined
GROUP BY table_name;
