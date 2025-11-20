-- ============================================================================
-- LX세미콘 손절 후 수동 업데이트
-- ============================================================================
-- 키움 HTS에서 LX세미콘을 모두 매도한 후, DB를 수동으로 업데이트
-- ============================================================================

-- 1단계: 현재 상태 확인
SELECT '=== 업데이트 전 kw_portfolio ===' as section;
SELECT * FROM kw_portfolio WHERE stock_code = '067570';

SELECT '=== 업데이트 전 계좌 잔고 ===' as section;
SELECT
  account_number,
  total_cash,
  stock_value,
  total_asset,
  profit_loss
FROM kw_account_balance
WHERE account_number = '8112-5100';

-- 2단계: kw_portfolio에서 LX세미콘 삭제
DELETE FROM kw_portfolio WHERE stock_code = '067570';

-- 3단계: 계좌 잔고 재계산 및 업데이트
-- LX세미콘 매도 후 현금 증가, 주식 평가액 감소

-- 먼저 현재 보유 종목의 총 평가액 계산
WITH current_stocks AS (
  SELECT
    COALESCE(SUM(evaluated_amount), 0) as total_stock_value,
    COALESCE(SUM(profit_loss), 0) as total_profit_loss,
    COALESCE(SUM(purchase_amount), 0) as total_purchase
  FROM kw_portfolio
  WHERE account_number = '8112-5100'
)
UPDATE kw_account_balance ab
SET
  stock_value = cs.total_stock_value,
  profit_loss = cs.total_profit_loss,
  profit_loss_rate = CASE
    WHEN cs.total_purchase > 0 THEN (cs.total_profit_loss::decimal / cs.total_purchase::decimal) * 100
    ELSE 0
  END,
  -- total_cash는 그대로 유지 (실제 HTS에서 확인 필요)
  -- LX세미콘 매도금액을 더해야 하지만, 정확한 체결가를 모르므로 일단 유지
  total_asset = total_cash + cs.total_stock_value,
  updated_at = NOW()
FROM current_stocks cs
WHERE ab.account_number = '8112-5100';

-- 4단계: 업데이트 후 확인
SELECT '=== 업데이트 후 kw_portfolio ===' as section;
SELECT
  stock_code,
  stock_name,
  quantity,
  avg_price,
  purchase_amount,
  evaluated_amount,
  profit_loss
FROM kw_portfolio
WHERE account_number = '8112-5100'
ORDER BY updated_at DESC;

SELECT '=== 업데이트 후 계좌 잔고 ===' as section;
SELECT
  account_number,
  total_cash,
  stock_value,
  total_asset,
  profit_loss,
  profit_loss_rate,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) as seconds_since_update
FROM kw_account_balance
WHERE account_number = '8112-5100';

-- 5단계: positions 테이블도 정리 (만약 있다면)
SELECT '=== positions 테이블 정리 ===' as section;
DELETE FROM positions WHERE stock_code = '067570';

SELECT '=== 정리 후 positions ===' as section;
SELECT
  stock_code,
  stock_name,
  quantity,
  position_status
FROM positions
WHERE position_status = 'open'
ORDER BY last_updated DESC;

-- 참고: LX세미콘 매도 체결가를 아신다면 아래 쿼리로 total_cash를 업데이트하세요
-- UPDATE kw_account_balance
-- SET
--   total_cash = total_cash + [매도체결금액],
--   total_asset = total_cash + stock_value,
--   updated_at = NOW()
-- WHERE account_number = '8112-5100';
