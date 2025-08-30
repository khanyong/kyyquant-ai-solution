-- 모든 트리거 제거하여 문제를 격리
-- Supabase SQL Editor에서 실행

-- 1. 기존 트리거들 모두 제거
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP TRIGGER IF EXISTS sync_email_verification_trigger ON auth.users;

-- 2. 트리거 함수들도 제거 (선택사항)
DROP FUNCTION IF EXISTS public.handle_new_user();
DROP FUNCTION IF EXISTS public.sync_email_verification();

-- 3. 현재 활성화된 트리거 확인
SELECT 
  trigger_name,
  event_object_table,
  action_statement,
  action_timing,
  event_manipulation
FROM information_schema.triggers 
WHERE event_object_schema = 'auth' 
  AND event_object_table = 'users'
ORDER BY trigger_name;

-- 4. 트리거 제거 후 상태 확인
SELECT 'All triggers removed successfully' as status;