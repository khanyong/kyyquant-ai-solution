-- RPC 함수 존재 여부 확인
-- 실행: Supabase SQL Editor

-- 1. 모든 public 스키마의 함수 확인
SELECT
  '=== 키움 관련 RPC 함수 ===' as section,
  routine_name,
  routine_type,
  data_type as return_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name LIKE '%kiwoom%'
ORDER BY routine_name;

-- 2. 필요한 함수들이 있는지 확인
SELECT
  '=== 필수 함수 확인 ===' as section,
  CASE
    WHEN EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_schema = 'public' AND routine_name = 'sync_kiwoom_account_balance')
      THEN '✅ sync_kiwoom_account_balance 존재'
    ELSE '❌ sync_kiwoom_account_balance 없음'
  END as balance_func,
  CASE
    WHEN EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_schema = 'public' AND routine_name = 'sync_kiwoom_portfolio')
      THEN '✅ sync_kiwoom_portfolio 존재'
    ELSE '❌ sync_kiwoom_portfolio 없음'
  END as portfolio_func,
  CASE
    WHEN EXISTS (SELECT 1 FROM information_schema.routines WHERE routine_schema = 'public' AND routine_name = 'update_account_totals')
      THEN '✅ update_account_totals 존재'
    ELSE '❌ update_account_totals 없음'
  END as totals_func;
