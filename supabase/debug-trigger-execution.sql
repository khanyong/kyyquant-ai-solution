-- 트리거 실행 상태 디버깅

-- 1. 트리거가 생성되었는지 확인
SELECT 
  trigger_name,
  event_object_table,
  action_statement,
  action_timing,
  event_manipulation,
  action_condition
FROM information_schema.triggers 
WHERE event_object_schema = 'auth' 
  AND event_object_table = 'users'
ORDER BY trigger_name;

-- 2. 함수가 존재하는지 확인
SELECT 
  routine_name,
  routine_type,
  security_type
FROM information_schema.routines 
WHERE routine_schema = 'public' 
  AND routine_name IN ('handle_new_user', 'sync_email_verification');

-- 3. 최근 생성된 사용자 확인
SELECT 
  id,
  email,
  created_at,
  email_confirmed_at,
  raw_user_meta_data
FROM auth.users 
ORDER BY created_at DESC 
LIMIT 5;

-- 4. profiles 테이블 현재 상태 확인
SELECT 
  id,
  email,
  name,
  kiwoom_account,
  email_verified,
  created_at
FROM profiles 
ORDER BY created_at DESC 
LIMIT 10;

-- 5. PostgreSQL 로그에서 WARNING 메시지 확인 (가능한 경우)
-- Supabase 대시보드의 Logs 섹션에서 확인하세요

-- 6. 수동으로 트리거 함수 테스트
-- 최신 사용자 ID로 수동 실행 테스트
DO $$
DECLARE
  latest_user_id uuid;
  latest_user_email text;
  latest_user_meta jsonb;
BEGIN
  -- 최신 사용자 정보 가져오기
  SELECT id, email, raw_user_meta_data
  INTO latest_user_id, latest_user_email, latest_user_meta
  FROM auth.users 
  ORDER BY created_at DESC 
  LIMIT 1;
  
  IF latest_user_id IS NOT NULL THEN
    RAISE NOTICE 'Testing with user: % (%)', latest_user_id, latest_user_email;
    
    -- 수동으로 프로필 생성 시도
    INSERT INTO public.profiles (
      id, 
      email, 
      name, 
      kiwoom_account,
      email_verified,
      created_at, 
      updated_at
    )
    VALUES (
      latest_user_id, 
      latest_user_email, 
      COALESCE(latest_user_meta->>'name', split_part(latest_user_email, '@', 1)),
      latest_user_meta->>'kiwoom_id',
      false,
      now(),
      now()
    )
    ON CONFLICT (id) DO UPDATE SET
      email = EXCLUDED.email,
      updated_at = now();
      
    RAISE NOTICE 'Profile creation attempt completed';
  ELSE
    RAISE NOTICE 'No users found';
  END IF;
END $$;