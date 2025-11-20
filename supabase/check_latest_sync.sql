-- 최신 동기화 데이터 확인

-- 1. 계좌 잔고 최신 데이터
SELECT
  '계좌 잔고' as data_type,
  total_cash,
  available_cash,
  stock_value,
  total_asset,
  profit_loss,
  updated_at,
  NOW() - updated_at as seconds_ago
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- 2. 포트폴리오 최신 데이터
SELECT
  '포트폴리오' as data_type,
  stock_code,
  stock_name,
  quantity,
  avg_price,
  current_price,
  evaluated_amount,
  profit_loss,
  profit_loss_rate,
  updated_at,
  NOW() - updated_at as seconds_ago
FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC;
