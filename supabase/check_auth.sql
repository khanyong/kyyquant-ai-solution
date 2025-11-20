-- 현재 인증 상태 확인
SELECT
  auth.uid() as current_user_id,
  CASE
    WHEN auth.uid() IS NULL THEN '❌ 로그인되지 않음 - RLS 컨텍스트에서 실행 필요'
    ELSE '✅ 로그인됨'
  END as auth_status;

-- 모든 사용자 확인 (서비스 역할로 실행)
SELECT
  id,
  email,
  created_at
FROM auth.users
ORDER BY created_at DESC
LIMIT 5;
