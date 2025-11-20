-- ============================================================================
-- LX세미콘 종목 마스터 등록 및 positions 동기화
-- ============================================================================

-- 1단계: kw_stock_master에 LX세미콘이 있는지 확인
SELECT
  '=== kw_stock_master에 LX세미콘 존재 여부 ===' as section;

SELECT *
FROM kw_stock_master
WHERE stock_code = '067570';

-- 2단계: LX세미콘이 없으면 등록
INSERT INTO kw_stock_master (
  stock_code,
  stock_name,
  market,
  sector_name
)
VALUES (
  '067570',
  'LX세미콘',
  'KOSPI',  -- LX세미콘은 코스피 상장
  '전기전자'
)
ON CONFLICT (stock_code) DO UPDATE
SET
  stock_name = EXCLUDED.stock_name,
  market = EXCLUDED.market,
  sector_name = EXCLUDED.sector_name,
  updated_at = NOW();

-- 3단계: 등록 확인
SELECT
  '=== LX세미콘 등록 확인 ===' as section;

SELECT *
FROM kw_stock_master
WHERE stock_code = '067570';

-- 4단계: LX세미콘 주문 내역에서 strategy_id 확인
SELECT
  '=== LX세미콘 주문 내역 ===' as section;

SELECT
  id,
  user_id,
  stock_code,
  stock_name,
  strategy_id,
  order_type,
  quantity,
  order_price,
  executed_quantity,
  status,
  created_at
FROM orders
WHERE (stock_code = '067570' OR stock_name LIKE '%LX세미콘%')
ORDER BY created_at DESC;

-- 5단계: kw_portfolio → positions 동기화
-- strategy_id는 주문 내역에서 가져오거나, 없으면 활성 전략 중 첫번째 사용

WITH lx_order AS (
  -- LX세미콘 체결된 주문에서 strategy_id 가져오기
  SELECT
    user_id,
    strategy_id,
    stock_code
  FROM orders
  WHERE (stock_code = '067570' OR stock_name LIKE '%LX세미콘%')
    AND status IN ('EXECUTED', 'PARTIAL')
    AND strategy_id IS NOT NULL
  ORDER BY created_at DESC
  LIMIT 1
),
default_strategy AS (
  -- 만약 주문 내역이 없으면 활성 전략 중 첫번째 사용
  SELECT
    id as strategy_id,
    user_id
  FROM strategies
  WHERE is_active = true
    AND user_id IN (SELECT DISTINCT user_id FROM kw_portfolio)
  ORDER BY created_at
  LIMIT 1
),
kw_with_strategy AS (
  SELECT
    kp.*,
    COALESCE(lo.strategy_id, ds.strategy_id) as strategy_id
  FROM kw_portfolio kp
  LEFT JOIN lx_order lo ON kp.stock_code = lo.stock_code AND kp.user_id = lo.user_id
  LEFT JOIN default_strategy ds ON kp.user_id = ds.user_id
  WHERE kp.quantity > 0
)
SELECT
  '=== 동기화할 데이터 미리보기 ===' as section,
  user_id,
  strategy_id,
  stock_code,
  stock_name,
  quantity,
  avg_price as avg_buy_price,
  purchase_amount as total_buy_amount
FROM kw_with_strategy;

-- 6단계: 실제 INSERT 수행
WITH lx_order AS (
  SELECT
    user_id,
    strategy_id,
    stock_code
  FROM orders
  WHERE (stock_code = '067570' OR stock_name LIKE '%LX세미콘%')
    AND status IN ('EXECUTED', 'PARTIAL')
    AND strategy_id IS NOT NULL
  ORDER BY created_at DESC
  LIMIT 1
),
default_strategy AS (
  SELECT
    id as strategy_id,
    user_id
  FROM strategies
  WHERE is_active = true
    AND user_id IN (SELECT DISTINCT user_id FROM kw_portfolio)
  ORDER BY created_at
  LIMIT 1
)

INSERT INTO positions (
  user_id,
  strategy_id,
  account_no,
  stock_code,
  stock_name,
  quantity,
  available_quantity,
  avg_buy_price,
  current_price,
  total_buy_amount,
  current_value,
  profit_loss,
  profit_loss_rate,
  position_status,
  opened_at,
  last_updated
)
SELECT
  kp.user_id,
  COALESCE(lo.strategy_id, ds.strategy_id) as strategy_id,
  kp.account_number,
  kp.stock_code,
  kp.stock_name,
  kp.quantity,
  kp.available_quantity,
  kp.avg_price,
  kp.current_price,
  kp.purchase_amount,
  kp.evaluated_amount,
  kp.profit_loss,
  kp.profit_loss_rate,
  'open'::varchar as position_status,
  NOW() as opened_at,
  kp.updated_at as last_updated
FROM kw_portfolio kp
LEFT JOIN lx_order lo ON kp.stock_code = lo.stock_code AND kp.user_id = lo.user_id
LEFT JOIN default_strategy ds ON kp.user_id = ds.user_id
WHERE kp.quantity > 0
ON CONFLICT (account_no, stock_code, strategy_id)
DO UPDATE SET
  quantity = EXCLUDED.quantity,
  available_quantity = EXCLUDED.available_quantity,
  avg_buy_price = EXCLUDED.avg_buy_price,
  current_price = EXCLUDED.current_price,
  total_buy_amount = EXCLUDED.total_buy_amount,
  current_value = EXCLUDED.current_value,
  profit_loss = EXCLUDED.profit_loss,
  profit_loss_rate = EXCLUDED.profit_loss_rate,
  position_status = EXCLUDED.position_status,
  last_updated = EXCLUDED.last_updated;

-- 7단계: 동기화 결과 확인
SELECT
  '=== 동기화 후 positions ===' as section;

SELECT
  p.user_id,
  p.stock_code,
  p.stock_name,
  p.quantity,
  p.avg_buy_price,
  p.total_buy_amount,
  p.current_value,
  p.profit_loss,
  p.profit_loss_rate,
  p.position_status,
  p.strategy_id,
  s.name as strategy_name
FROM positions p
LEFT JOIN strategies s ON p.strategy_id = s.id
WHERE p.position_status = 'open'
ORDER BY p.last_updated DESC;

-- 8단계: 전략별 투자 금액 집계 확인
SELECT
  '=== 전략별 투자 현황 ===' as section;

SELECT
  s.id as strategy_id,
  s.user_id,
  s.name as strategy_name,
  s.allocated_capital as 할당자본,
  COUNT(p.id) as 보유종목수,
  COALESCE(SUM(p.total_buy_amount), 0) as 총매입금액,
  COALESCE(SUM(p.current_value), 0) as 총평가금액,
  COALESCE(SUM(p.profit_loss), 0) as 총손익,
  CASE
    WHEN COALESCE(SUM(p.total_buy_amount), 0) > 0
    THEN ROUND((COALESCE(SUM(p.profit_loss), 0)::decimal / SUM(p.total_buy_amount)::decimal) * 100, 2)
    ELSE 0
  END as 수익률
FROM strategies s
LEFT JOIN positions p ON s.id = p.strategy_id AND p.position_status = 'open'
WHERE s.is_active = true
GROUP BY s.id, s.name, s.allocated_capital, s.user_id
ORDER BY s.user_id, s.created_at;
