-- RLS 정책 확인
-- 실행: Supabase SQL Editor

-- 1. kw_account_balance 테이블의 RLS 정책
SELECT
  '=== kw_account_balance RLS 정책 ===' as section,
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename = 'kw_account_balance';

-- 2. kw_portfolio 테이블의 RLS 정책
SELECT
  '=== kw_portfolio RLS 정책 ===' as section,
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename = 'kw_portfolio';

-- 3. RLS 활성화 여부 확인
SELECT
  '=== RLS 활성화 상태 ===' as section,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('kw_account_balance', 'kw_portfolio');

-- 4. 실제 데이터 조회 (user_id 필터 없이)
SELECT
  '=== 실제 데이터 샘플 ===' as section,
  user_id,
  account_number,
  total_cash,
  updated_at
FROM kw_account_balance
ORDER BY updated_at DESC
LIMIT 3;
