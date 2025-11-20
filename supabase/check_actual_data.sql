-- 실제 DB에 데이터가 있는지 확인
-- 실행: Supabase SQL Editor

-- 1. kw_account_balance 테이블 전체 확인 (RLS 무시)
SELECT
  '=== 계좌 잔고 (전체) ===' as section,
  user_id,
  account_number,
  total_cash,
  stock_value,
  total_asset,
  updated_at
FROM kw_account_balance
ORDER BY updated_at DESC
LIMIT 5;

-- 2. kw_portfolio 테이블 전체 확인 (RLS 무시)
SELECT
  '=== 보유 종목 (전체) ===' as section,
  user_id,
  account_number,
  stock_code,
  stock_name,
  quantity,
  updated_at
FROM kw_portfolio
ORDER BY updated_at DESC
LIMIT 5;

-- 3. 특정 사용자 데이터 확인
SELECT
  '=== f912da32 사용자 데이터 ===' as section,
  'kw_account_balance' as table_name,
  COUNT(*) as record_count
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
UNION ALL
SELECT
  '=== f912da32 사용자 데이터 ===' as section,
  'kw_portfolio' as table_name,
  COUNT(*) as record_count
FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
