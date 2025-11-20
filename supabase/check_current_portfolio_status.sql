-- ============================================================================
-- 현재 포트폴리오 상태 상세 확인
-- ============================================================================

-- 1. kw_portfolio 테이블의 LX세미콘 데이터
SELECT
  '=== kw_portfolio LX세미콘 현황 ===' as section;

SELECT
  user_id,
  account_number,
  stock_code,
  stock_name,
  quantity,
  avg_price,
  purchase_amount,
  current_price,
  evaluated_amount,
  profit_loss,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_update
FROM kw_portfolio
WHERE stock_code = '067570'
ORDER BY updated_at DESC;

-- 2. 모든 보유 종목 현황
SELECT
  '=== 전체 kw_portfolio ===' as section;

SELECT
  stock_code,
  stock_name,
  quantity,
  avg_price,
  purchase_amount,
  profit_loss,
  updated_at
FROM kw_portfolio
ORDER BY updated_at DESC;

-- 3. positions 테이블 확인
SELECT
  '=== positions 테이블 ===' as section;

SELECT
  stock_code,
  stock_name,
  quantity,
  avg_buy_price,
  position_status,
  last_updated
FROM positions
WHERE position_status = 'open'
ORDER BY last_updated DESC;

-- 4. kw_account_balance 최근 업데이트 시간
SELECT
  '=== 계좌 잔고 최근 동기화 시간 ===' as section;

SELECT
  account_number,
  total_cash,
  stock_value,
  total_asset,
  profit_loss,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_update
FROM kw_account_balance
ORDER BY updated_at DESC
LIMIT 5;
