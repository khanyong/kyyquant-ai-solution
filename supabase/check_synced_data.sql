-- 키움 계좌 동기화 후 데이터 확인

-- ========================================
-- 1. 계좌 잔고 데이터 확인
-- ========================================
SELECT
  '계좌 잔고' as data_type,
  id,
  user_id,
  account_number,
  total_cash,
  available_cash,
  order_cash,
  total_asset,
  stock_value,
  profit_loss,
  profit_loss_rate,
  updated_at,
  created_at
FROM kw_account_balance
WHERE user_id = auth.uid()
ORDER BY updated_at DESC;

-- ========================================
-- 2. 포트폴리오 데이터 확인
-- ========================================
SELECT
  '보유 종목' as data_type,
  id,
  user_id,
  account_number,
  stock_code,
  stock_name,
  quantity,
  available_quantity,
  avg_price,
  current_price,
  purchase_amount,
  evaluated_amount,
  profit_loss,
  profit_loss_rate,
  updated_at,
  created_at
FROM kw_portfolio
WHERE user_id = auth.uid()
ORDER BY evaluated_amount DESC;

-- ========================================
-- 3. 레코드 수 확인
-- ========================================
SELECT
  '데이터 개수' as check_type,
  'kw_account_balance' as table_name,
  COUNT(*) as count
FROM kw_account_balance
WHERE user_id = auth.uid()

UNION ALL

SELECT
  '데이터 개수',
  'kw_portfolio',
  COUNT(*)
FROM kw_portfolio
WHERE user_id = auth.uid();

-- ========================================
-- 4. 최근 업데이트 시간 확인
-- ========================================
SELECT
  'kw_account_balance' as table_name,
  MAX(updated_at) as last_updated,
  NOW() as current_time,
  EXTRACT(EPOCH FROM (NOW() - MAX(updated_at))) as seconds_ago
FROM kw_account_balance
WHERE user_id = auth.uid()

UNION ALL

SELECT
  'kw_portfolio',
  MAX(updated_at),
  NOW(),
  EXTRACT(EPOCH FROM (NOW() - MAX(updated_at)))
FROM kw_portfolio
WHERE user_id = auth.uid();

-- ========================================
-- 예상 결과
-- ========================================

/*
✅ 동기화 성공한 경우:
1. 계좌 잔고: 1개 이상의 레코드
2. 포트폴리오: 0개 이상의 레코드 (보유 종목이 있으면)
3. updated_at이 최근 시간 (방금 전)

❌ 데이터가 없는 경우:
1. count = 0
2. last_updated = NULL
→ Edge Function이 성공했지만 데이터베이스에 저장 안 됨
→ RLS 정책 또는 함수 내부 문제
*/
