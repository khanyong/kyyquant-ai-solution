-- 키움 계좌 동기화 설정 상태 확인

-- 1. 테이블 제약 조건 확인
SELECT
  'Constraints' as check_type,
  conname as constraint_name,
  contype as constraint_type,
  pg_get_constraintdef(oid) as definition
FROM pg_constraint
WHERE conrelid = 'kw_account_balance'::regclass;

-- 2. 인덱스 확인
SELECT
  'Indexes' as check_type,
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename = 'kw_account_balance';

-- 3. 데이터베이스 함수 확인
SELECT
  'Functions' as check_type,
  proname as function_name,
  prokind as kind,
  provolatile as volatility
FROM pg_proc
WHERE proname IN (
  'sync_kiwoom_account_balance',
  'sync_kiwoom_portfolio',
  'update_account_totals'
);

-- 4. RLS 정책 확인
SELECT
  'RLS Policies' as check_type,
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd as command,
  qual as using_expression
FROM pg_policies
WHERE tablename IN ('kw_account_balance', 'kw_portfolio');

-- 5. 현재 사용자 데이터 확인
SELECT
  'Current User Balance' as check_type,
  *
FROM kw_account_balance
WHERE user_id = auth.uid();

-- 6. 현재 사용자 포트폴리오 확인
SELECT
  'Current User Portfolio' as check_type,
  *
FROM kw_portfolio
WHERE user_id = auth.uid();

-- 7. 프로필 확인
SELECT
  'Profile' as check_type,
  id,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = auth.uid();

-- 8. API 키 확인
SELECT
  'API Keys' as check_type,
  key_type,
  is_active,
  is_test_mode,
  created_at
FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';
