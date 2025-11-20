-- 포지션과 포트폴리오 데이터 확인

-- 1. 현재 open 상태의 포지션
SELECT
  '=== OPEN POSITIONS ===' as section,
  id,
  user_id,
  stock_code,
  stock_name,
  quantity,
  avg_buy_price,
  position_status,
  strategy_id,
  created_at
FROM positions
WHERE position_status = 'open'
ORDER BY created_at DESC;

-- 2. kw_portfolio 테이블 (키움에서 동기화된 실제 보유 종목)
SELECT
  '=== KW_PORTFOLIO ===' as section,
  id,
  user_id,
  stock_code,
  stock_name,
  quantity,
  avg_price,
  purchase_amount,
  current_price,
  evaluated_amount,
  profit_loss,
  profit_loss_rate,
  updated_at
FROM kw_portfolio
ORDER BY updated_at DESC;

-- 3. positions와 kw_portfolio 비교
SELECT
  '=== COMPARISON ===' as section,
  COALESCE(p.stock_code, kp.stock_code) as stock_code,
  COALESCE(p.stock_name, kp.stock_name) as stock_name,
  p.quantity as positions_qty,
  kp.quantity as kw_portfolio_qty,
  p.avg_buy_price as positions_avg_price,
  kp.avg_price as kw_avg_price,
  p.strategy_id,
  p.position_status
FROM positions p
FULL OUTER JOIN kw_portfolio kp
  ON p.stock_code = kp.stock_code AND p.user_id = kp.user_id
WHERE p.position_status = 'open' OR kp.quantity > 0
ORDER BY COALESCE(p.created_at, kp.updated_at) DESC;

-- 4. 전략별 할당 자본 확인
SELECT
  '=== STRATEGY ALLOCATIONS ===' as section,
  id,
  user_id,
  name,
  allocated_capital,
  is_active,
  auto_execute
FROM strategies
WHERE is_active = true
ORDER BY created_at DESC;

-- 5. LX세미콘 관련 모든 주문
SELECT
  '=== LX세미콘 ORDERS ===' as section,
  id,
  user_id,
  stock_code,
  stock_name,
  order_type,
  quantity,
  order_price,
  executed_quantity,
  executed_price,
  status,
  strategy_id,
  created_at
FROM orders
WHERE stock_code = '067570' OR stock_name LIKE '%LX세미콘%'
ORDER BY created_at DESC;
