-- 모든 키움 관련 데이터 확인

-- 1. kw_account_balance 데이터 확인
SELECT 'kw_account_balance' as table_name, COUNT(*) as total_records FROM kw_account_balance;

SELECT * FROM kw_account_balance
ORDER BY updated_at DESC
LIMIT 5;

-- 2. kw_portfolio 데이터 확인
SELECT 'kw_portfolio' as table_name, COUNT(*) as total_records FROM kw_portfolio;

SELECT * FROM kw_portfolio
ORDER BY updated_at DESC
LIMIT 10;

-- 3. 특정 사용자 데이터 확인
SELECT
  'User specific data' as info,
  (SELECT COUNT(*) FROM kw_account_balance WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as balance_count,
  (SELECT COUNT(*) FROM kw_portfolio WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8') as portfolio_count;
