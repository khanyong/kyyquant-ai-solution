-- 대기중인 주문 확인

SELECT
  id,
  stock_code,
  stock_name,
  order_type,
  quantity,
  order_price,
  executed_quantity,
  status,
  kiwoom_order_no,
  created_at,
  updated_at
FROM orders
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND status IN ('PENDING', 'PARTIAL')
ORDER BY created_at DESC;
