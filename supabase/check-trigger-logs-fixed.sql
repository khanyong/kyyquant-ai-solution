-- 트리거 로그 확인 및 문제 진단 (수정버전)

-- 1. 최신 사용자 정보 확인
SELECT 
  id,
  email,
  created_at,
  email_confirmed_at,
  raw_user_meta_data
FROM auth.users 
ORDER BY created_at DESC 
LIMIT 3;

-- 2. 현재 트리거 상태 재확인
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

-- 3. 트리거 함수 상태 확인
SELECT 
  routine_name,
  routine_type,
  security_type
FROM information_schema.routines 
WHERE routine_schema = 'public' 
  AND routine_name = 'handle_new_user';

-- 4. 수동 트리거 함수 먼저 생성
CREATE OR REPLACE FUNCTION public.handle_new_user_manual(
  user_id uuid,
  user_email text,
  user_meta jsonb,
  email_confirmed timestamptz,
  user_created timestamptz
)
RETURNS void AS $$
BEGIN
  RAISE NOTICE 'Manual function called for user: % (%)', user_id, user_email;
  
  INSERT INTO public.profiles (
    id, 
    email, 
    name, 
    kiwoom_account,
    email_verified,
    email_verified_at,
    created_at, 
    updated_at
  )
  VALUES (
    user_id, 
    user_email, 
    COALESCE(user_meta->>'name', split_part(user_email, '@', 1)),
    user_meta->>'kiwoom_id',
    COALESCE(email_confirmed IS NOT NULL, false),
    email_confirmed,
    user_created,
    now()
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    updated_at = now();
    
  RAISE NOTICE 'Profile created manually for user: %', user_id;
EXCEPTION
  WHEN others THEN
    RAISE WARNING 'Manual profile creation failed for user %: % (SQLSTATE: %)', user_id, SQLERRM, SQLSTATE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. 수동으로 최신 사용자에 대해 트리거 함수 실행
DO $$
DECLARE
  latest_user RECORD;
BEGIN
  -- 최신 사용자 선택
  SELECT id, email, raw_user_meta_data, email_confirmed_at, created_at
  INTO latest_user
  FROM auth.users 
  ORDER BY created_at DESC 
  LIMIT 1;
  
  IF latest_user.id IS NOT NULL THEN
    RAISE NOTICE 'Manual trigger test for user: % (%)', latest_user.id, latest_user.email;
    
    -- 트리거 함수 직접 호출 시뮬레이션
    PERFORM public.handle_new_user_manual(
      latest_user.id, 
      latest_user.email, 
      latest_user.raw_user_meta_data,
      latest_user.email_confirmed_at,
      latest_user.created_at
    );
  END IF;
END $$;

-- 6. profiles 상태 확인
SELECT 
  id,
  email,
  name,
  created_at
FROM profiles 
ORDER BY created_at DESC 
LIMIT 5;