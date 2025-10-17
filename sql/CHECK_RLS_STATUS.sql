-- RLS 상태 확인 및 강제 비활성화

-- 1. 현재 RLS 상태
SELECT
  tablename,
  rowsecurity as rls_enabled,
  CASE
    WHEN rowsecurity = true THEN '❌ RLS 활성화됨 - 비활성화 필요'
    ELSE '✅ RLS 비활성화됨'
  END as status
FROM pg_tables
WHERE tablename IN ('kw_account_balance', 'kw_portfolio', 'user_profiles');

-- 2. 강제 비활성화
ALTER TABLE IF EXISTS kw_account_balance DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS kw_portfolio DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS user_profiles DISABLE ROW LEVEL SECURITY;

-- 3. 재확인
SELECT
  tablename,
  rowsecurity as rls_enabled,
  CASE
    WHEN rowsecurity = false THEN '✅ RLS 비활성화 성공'
    ELSE '❌ 여전히 활성화됨'
  END as status
FROM pg_tables
WHERE tablename IN ('kw_account_balance', 'kw_portfolio', 'user_profiles');
