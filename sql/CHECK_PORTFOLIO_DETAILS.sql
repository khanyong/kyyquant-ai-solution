-- 보유 종목 상세 확인
SELECT
  stock_code,
  stock_name,
  quantity,
  avg_price,
  current_price,
  evaluated_amount,
  profit_loss,
  created_at,
  updated_at
FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC;
