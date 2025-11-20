-- 모든 대기중인 주문 확인 (user_id 필터 없이)

SELECT
  id,
  user_id,
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
WHERE status IN ('PENDING', 'PARTIAL')
ORDER BY created_at DESC
LIMIT 10;
