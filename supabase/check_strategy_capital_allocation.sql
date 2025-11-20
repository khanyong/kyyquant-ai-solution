-- =====================================================
-- 전략별 자본 배분 및 매매 한도 확인
-- 목적: 활성 전략이 할당받은 금액 내에서만 매매하는지 검증
-- 실행: Supabase SQL Editor
-- =====================================================

-- ============================================================
-- STEP 1: 현재 계좌 상태
-- ============================================================

SELECT
  '=== 계좌 전체 현황 ===' as section,
  account_number,
  TO_CHAR(total_cash, 'FM999,999,999') || '원' as total_cash,
  TO_CHAR(available_cash, 'FM999,999,999') || '원' as available_cash,
  TO_CHAR(stock_value, 'FM999,999,999') || '원' as stock_value,
  TO_CHAR(total_asset, 'FM999,999,999') || '원' as total_asset,
  TO_CHAR(profit_loss, 'FM999,999,999') || '원' as profit_loss,
  TO_CHAR(profit_loss_rate, 'FM999.99') || '%' as profit_loss_rate,
  updated_at
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC
LIMIT 1;

-- ============================================================
-- STEP 2: 활성 전략 및 자본 배분 현황
-- ============================================================

SELECT
  '=== 활성 전략 자본 배분 ===' as section,
  s.id,
  s.name as strategy_name,
  s.is_active,
  s.position_size_percent,
  s.max_positions,
  s.max_investment_per_stock,
  -- 계좌 잔고 기준 실제 사용 가능 금액 계산
  ROUND((SELECT available_cash FROM kw_account_balance
         WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
         ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100) as allocated_cash,
  TO_CHAR(
    ROUND((SELECT available_cash FROM kw_account_balance
           WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
           ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100),
    'FM999,999,999'
  ) || '원' as allocated_cash_display,
  -- 종목당 최대 투자금액 (배분 금액 / max_positions)
  CASE
    WHEN s.max_investment_per_stock IS NOT NULL THEN s.max_investment_per_stock
    ELSE ROUND(
      (SELECT available_cash FROM kw_account_balance
       WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
       ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100 / GREATEST(s.max_positions, 1)
    )
  END as max_per_stock,
  TO_CHAR(
    CASE
      WHEN s.max_investment_per_stock IS NOT NULL THEN s.max_investment_per_stock
      ELSE ROUND(
        (SELECT available_cash FROM kw_account_balance
         WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
         ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100 / GREATEST(s.max_positions, 1)
      )
    END,
    'FM999,999,999'
  ) || '원' as max_per_stock_display,
  s.created_at
FROM strategies s
WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND s.is_active = true
ORDER BY s.created_at DESC;

-- ============================================================
-- STEP 3: 전략별 현재 사용 중인 자본
-- ============================================================

WITH strategy_usage AS (
  SELECT
    s.id as strategy_id,
    s.name as strategy_name,
    s.position_size_percent,
    s.max_positions,
    s.max_investment_per_stock,
    -- 할당 금액
    ROUND((SELECT available_cash FROM kw_account_balance
           WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
           ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100) as allocated_amount,
    -- 현재 보유 종목 수
    (SELECT COUNT(DISTINCT stock_code)
     FROM kw_portfolio kp
     WHERE kp.user_id = s.user_id
       AND kp.quantity > 0) as current_positions,
    -- 현재 보유 주식 평가액 (전략별 분리 불가능하므로 전체)
    (SELECT COALESCE(SUM(quantity * current_price), 0)
     FROM kw_portfolio kp
     WHERE kp.user_id = s.user_id
       AND kp.quantity > 0) as current_stock_value,
    -- 대기중인 주문 금액
    (SELECT COALESCE(SUM(quantity * price), 0)
     FROM orders o
     WHERE o.user_id = s.user_id
       AND o.order_status IN ('PENDING', 'SUBMITTED')
       AND o.order_type = 'BUY') as pending_buy_amount
  FROM strategies s
  WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    AND s.is_active = true
)
SELECT
  '=== 전략별 자본 사용 현황 ===' as section,
  strategy_name,
  TO_CHAR(allocated_amount, 'FM999,999,999') || '원' as allocated_budget,
  current_positions || '/' || max_positions as positions_used,
  TO_CHAR(current_stock_value, 'FM999,999,999') || '원' as stock_value_held,
  TO_CHAR(pending_buy_amount, 'FM999,999,999') || '원' as pending_orders,
  TO_CHAR(current_stock_value + pending_buy_amount, 'FM999,999,999') || '원' as total_committed,
  TO_CHAR(allocated_amount - (current_stock_value + pending_buy_amount), 'FM999,999,999') || '원' as remaining_budget,
  ROUND((current_stock_value + pending_buy_amount)::NUMERIC / NULLIF(allocated_amount, 0) * 100, 2) || '%' as usage_rate,
  CASE
    WHEN current_stock_value + pending_buy_amount > allocated_amount THEN '❌ 한도 초과!'
    WHEN current_stock_value + pending_buy_amount > allocated_amount * 0.9 THEN '⚠️ 90% 이상 사용'
    WHEN current_stock_value + pending_buy_amount > allocated_amount * 0.7 THEN '⏳ 70% 이상 사용'
    ELSE '✅ 정상'
  END as status
FROM strategy_usage;

-- ============================================================
-- STEP 4: 최근 주문들이 한도를 준수했는지 검증
-- ============================================================

WITH order_validation AS (
  SELECT
    o.id,
    o.stock_code,
    o.stock_name,
    o.order_type,
    o.quantity,
    o.price,
    o.quantity * o.price as order_amount,
    s.name as strategy_name,
    s.position_size_percent,
    s.max_investment_per_stock,
    -- 종목당 최대 허용 금액
    CASE
      WHEN s.max_investment_per_stock IS NOT NULL THEN s.max_investment_per_stock
      ELSE ROUND(
        (SELECT available_cash FROM kw_account_balance
         WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
         ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100 / GREATEST(s.max_positions, 1)
      )
    END as max_allowed_per_stock,
    o.order_status,
    o.created_at
  FROM orders o
  LEFT JOIN trading_signals ts ON ts.order_id = o.id
  LEFT JOIN strategies s ON s.id = ts.strategy_id
  WHERE o.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    AND o.created_at > NOW() - INTERVAL '7 days'
    AND o.order_type = 'BUY'
)
SELECT
  '=== 최근 주문 한도 준수 검증 ===' as section,
  stock_code,
  stock_name,
  strategy_name,
  TO_CHAR(order_amount, 'FM999,999,999') || '원' as order_amount,
  TO_CHAR(max_allowed_per_stock, 'FM999,999,999') || '원' as max_allowed,
  TO_CHAR(order_amount - max_allowed_per_stock, 'FM999,999,999') || '원' as difference,
  ROUND(order_amount::NUMERIC / NULLIF(max_allowed_per_stock, 0) * 100, 2) || '%' as usage_percent,
  CASE
    WHEN order_amount > max_allowed_per_stock THEN '❌ 한도 초과'
    WHEN order_amount > max_allowed_per_stock * 0.95 THEN '⚠️ 95% 이상'
    ELSE '✅ 정상'
  END as validation_status,
  order_status,
  created_at
FROM order_validation
ORDER BY created_at DESC
LIMIT 20;

-- ============================================================
-- STEP 5: 포지션 수 제한 검증
-- ============================================================

WITH position_check AS (
  SELECT
    s.name as strategy_name,
    s.max_positions,
    -- 현재 보유 종목 수
    (SELECT COUNT(DISTINCT stock_code)
     FROM kw_portfolio kp
     WHERE kp.user_id = s.user_id
       AND kp.quantity > 0) as current_positions,
    -- 대기중인 매수 주문 종목 수 (체결되면 추가될 포지션)
    (SELECT COUNT(DISTINCT stock_code)
     FROM orders o
     WHERE o.user_id = s.user_id
       AND o.order_status IN ('PENDING', 'SUBMITTED')
       AND o.order_type = 'BUY') as pending_positions
  FROM strategies s
  WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    AND s.is_active = true
)
SELECT
  '=== 포지션 수 제한 검증 ===' as section,
  strategy_name,
  current_positions || '개 보유' as current,
  pending_positions || '개 대기' as pending,
  (current_positions + pending_positions) || '/' || max_positions as total_positions,
  CASE
    WHEN current_positions + pending_positions > max_positions THEN '❌ 포지션 수 초과!'
    WHEN current_positions + pending_positions = max_positions THEN '⚠️ 최대 포지션 도달'
    ELSE '✅ 정상 (' || (max_positions - current_positions - pending_positions) || '개 여유)'
  END as status
FROM position_check;

-- ============================================================
-- STEP 6: 다음 주문 시 사용 가능한 금액 계산
-- ============================================================

WITH next_order_budget AS (
  SELECT
    s.id as strategy_id,
    s.name as strategy_name,
    s.position_size_percent,
    s.max_positions,
    s.max_investment_per_stock,
    -- 전략에 할당된 총 금액
    ROUND((SELECT available_cash FROM kw_account_balance
           WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
           ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100) as allocated_amount,
    -- 이미 사용 중인 금액 (보유 주식 + 대기 주문)
    (SELECT COALESCE(SUM(quantity * current_price), 0)
     FROM kw_portfolio kp
     WHERE kp.user_id = s.user_id
       AND kp.quantity > 0) +
    (SELECT COALESCE(SUM(quantity * price), 0)
     FROM orders o
     WHERE o.user_id = s.user_id
       AND o.order_status IN ('PENDING', 'SUBMITTED')
       AND o.order_type = 'BUY') as used_amount,
    -- 현재 포지션 수
    (SELECT COUNT(DISTINCT stock_code)
     FROM kw_portfolio kp
     WHERE kp.user_id = s.user_id
       AND kp.quantity > 0) +
    (SELECT COUNT(DISTINCT stock_code)
     FROM orders o
     WHERE o.user_id = s.user_id
       AND o.order_status IN ('PENDING', 'SUBMITTED')
       AND o.order_type = 'BUY') as current_positions,
    -- 종목당 최대 금액
    CASE
      WHEN s.max_investment_per_stock IS NOT NULL THEN s.max_investment_per_stock
      ELSE ROUND(
        (SELECT available_cash FROM kw_account_balance
         WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
         ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100 / GREATEST(s.max_positions, 1)
      )
    END as max_per_stock
  FROM strategies s
  WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    AND s.is_active = true
)
SELECT
  '=== 다음 주문 가능 금액 ===' as section,
  strategy_name,
  TO_CHAR(allocated_amount, 'FM999,999,999') || '원' as total_allocated,
  TO_CHAR(used_amount, 'FM999,999,999') || '원' as already_used,
  TO_CHAR(allocated_amount - used_amount, 'FM999,999,999') || '원' as remaining,
  current_positions || '/' || max_positions as positions,
  TO_CHAR(max_per_stock, 'FM999,999,999') || '원' as max_per_new_stock,
  CASE
    WHEN current_positions >= max_positions THEN '❌ 포지션 수 한도 도달 (추가 매수 불가)'
    WHEN allocated_amount - used_amount < max_per_stock * 0.1 THEN '❌ 잔여 예산 부족 (10% 미만)'
    WHEN allocated_amount - used_amount < max_per_stock THEN
      '⚠️ 부분 매수 가능 (' || TO_CHAR(allocated_amount - used_amount, 'FM999,999,999') || '원)'
    ELSE '✅ 전액 매수 가능 (' || TO_CHAR(LEAST(max_per_stock, allocated_amount - used_amount), 'FM999,999,999') || '원)'
  END as next_order_status,
  -- 실제 다음 주문 시 사용 가능한 금액
  LEAST(max_per_stock, allocated_amount - used_amount) as available_for_next_order,
  TO_CHAR(LEAST(max_per_stock, allocated_amount - used_amount), 'FM999,999,999') || '원' as available_display
FROM next_order_budget;

-- ============================================================
-- STEP 7: 자본 배분 시뮬레이션 (예시 주문)
-- ============================================================

WITH simulation AS (
  SELECT
    s.name as strategy_name,
    -- 가상 주문: 삼성전자 @ 72,000원
    72000 as example_price,
    -- 종목당 최대 금액으로 살 수 있는 수량
    FLOOR(
      CASE
        WHEN s.max_investment_per_stock IS NOT NULL THEN s.max_investment_per_stock
        ELSE ROUND(
          (SELECT available_cash FROM kw_account_balance
           WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
           ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100 / GREATEST(s.max_positions, 1)
        )
      END / 72000
    ) as max_quantity,
    -- 실제 주문 금액
    FLOOR(
      CASE
        WHEN s.max_investment_per_stock IS NOT NULL THEN s.max_investment_per_stock
        ELSE ROUND(
          (SELECT available_cash FROM kw_account_balance
           WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
           ORDER BY updated_at DESC LIMIT 1) * s.position_size_percent / 100 / GREATEST(s.max_positions, 1)
        )
      END / 72000
    ) * 72000 as order_amount
  FROM strategies s
  WHERE s.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    AND s.is_active = true
)
SELECT
  '=== 주문 시뮬레이션 (삼성전자 @ 72,000원) ===' as section,
  strategy_name,
  '005930 삼성전자' as stock,
  TO_CHAR(example_price, 'FM999,999') || '원' as price,
  max_quantity || '주' as quantity,
  TO_CHAR(order_amount, 'FM999,999,999') || '원' as total_order_amount,
  '✅ 이 금액으로 주문 생성됨' as expected_behavior
FROM simulation;

-- ============================================================
-- STEP 8: 종합 진단 및 권장사항
-- ============================================================

SELECT
  '=== 자본 배분 종합 진단 ===' as section,
  CASE
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) = 0
      THEN '❌ 활성 전략 없음'
    WHEN (SELECT COUNT(*) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true AND position_size_percent IS NULL)
      THEN '❌ position_size_percent 미설정'
    WHEN (SELECT SUM(position_size_percent) FROM strategies WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND is_active = true) > 100
      THEN '❌ 전략 배분 합계 > 100% (과다 배분)'
    ELSE '✅ 설정 정상'
  END as configuration_status,
  CASE
    WHEN EXISTS (
      SELECT 1 FROM orders o
      LEFT JOIN trading_signals ts ON ts.order_id = o.id
      LEFT JOIN strategies s ON s.id = ts.strategy_id
      WHERE o.user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
        AND o.created_at > NOW() - INTERVAL '7 days'
        AND o.order_type = 'BUY'
        AND o.quantity * o.price > COALESCE(s.max_investment_per_stock, 999999999)
    ) THEN '❌ 한도 초과 주문 발견'
    ELSE '✅ 모든 주문이 한도 내'
  END as order_compliance,
  CASE
    WHEN (
      SELECT COUNT(DISTINCT stock_code)
      FROM kw_portfolio
      WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
        AND quantity > 0
    ) + (
      SELECT COUNT(DISTINCT stock_code)
      FROM orders
      WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
        AND order_status IN ('PENDING', 'SUBMITTED')
        AND order_type = 'BUY'
    ) > (
      SELECT COALESCE(MIN(max_positions), 0)
      FROM strategies
      WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
        AND is_active = true
    ) THEN '❌ 포지션 수 초과'
    ELSE '✅ 포지션 수 정상'
  END as position_compliance,
  CASE
    WHEN (SELECT available_cash FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' ORDER BY updated_at DESC LIMIT 1) < 100000
      THEN '⚠️ 계좌 잔고 부족 (<10만원)'
    ELSE '✅ 잔고 충분'
  END as balance_status;

-- ============================================================
-- STEP 9: 권장사항
-- ============================================================

SELECT
  '=== 📋 권장사항 ===' as section,
  '1. 전략 배분 합계가 100%를 넘지 않도록 설정' as tip1,
  '2. max_investment_per_stock을 명시적으로 설정하여 한 종목에 과도한 집중 방지' as tip2,
  '3. 포지션 수(max_positions)를 적절히 분산하여 리스크 관리' as tip3,
  '4. 주문 전 잔여 예산 확인 로직이 n8n workflow-v7-2에 구현되어 있는지 확인' as tip4,
  '5. 실시간으로 STEP 6 쿼리를 모니터링하여 예산 소진 상황 추적' as tip5;
