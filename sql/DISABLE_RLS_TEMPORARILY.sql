-- RLS 일시 비활성화 (개발 중)
-- 나중에 다시 활성화할 것

-- 1. 현재 RLS 상태 확인
SELECT
  schemaname,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables
WHERE tablename IN ('kw_account_balance', 'kw_portfolio');

-- 2. RLS 비활성화
ALTER TABLE kw_account_balance DISABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio DISABLE ROW LEVEL SECURITY;

-- 3. 비활성화 확인
SELECT
  schemaname,
  tablename,
  rowsecurity as rls_enabled,
  CASE
    WHEN rowsecurity = false THEN '✅ RLS 비활성화됨'
    ELSE '❌ 아직 활성화됨'
  END as status
FROM pg_tables
WHERE tablename IN ('kw_account_balance', 'kw_portfolio');

-- 4. 테스트 쿼리 (이제 작동해야 함)
SELECT
  'Account Balance Test' as test_name,
  COUNT(*) as count
FROM kw_account_balance;

SELECT
  'Portfolio Test' as test_name,
  COUNT(*) as count
FROM kw_portfolio;
