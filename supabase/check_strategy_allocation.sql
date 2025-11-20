-- 전략 할당 및 실제 투자 현황 확인

-- 1. 활성 전략 목록
SELECT
  id,
  name,
  allocated_capital,
  is_active
FROM strategies
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND is_active = true
ORDER BY created_at;

-- 2. LX세미콘 주문이 어느 전략인지 확인
SELECT
  o.id,
  o.stock_code,
  o.stock_name,
  o.strategy_id,
  s.name as strategy_name,
  o.quantity,
  o.order_price,
  o.status
FROM orders o
LEFT JOIN strategies s ON o.strategy_id = s.id
WHERE o.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND (o.stock_code = '067570' OR o.stock_name LIKE '%LX세미콘%')
ORDER BY o.created_at DESC
LIMIT 5;

-- 3. 체결된 주문의 전략별 합계
SELECT
  s.name as strategy_name,
  COUNT(*) as order_count,
  SUM(o.quantity * o.order_price) as total_invested
FROM orders o
JOIN strategies s ON o.strategy_id = s.id
WHERE o.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND o.status IN ('EXECUTED', 'PARTIAL')
GROUP BY s.id, s.name
ORDER BY s.name;
