-- 누락된 프로필 생성 및 트리거 문제 해결

-- 1. khanyong.yoo@gmail.com 사용자 정보 확인
SELECT 
  id,
  email,
  created_at,
  email_confirmed_at,
  raw_user_meta_data
FROM auth.users 
WHERE email = 'khanyong.yoo@gmail.com';

-- 2. 해당 사용자의 프로필을 수동으로 생성
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
SELECT 
  u.id,
  u.email,
  COALESCE(u.raw_user_meta_data->>'name', split_part(u.email, '@', 1)) as name,
  u.raw_user_meta_data->>'kiwoom_id' as kiwoom_account,
  COALESCE(u.email_confirmed_at IS NOT NULL, false) as email_verified,
  u.email_confirmed_at,
  u.created_at,
  now() as updated_at
FROM auth.users u
WHERE u.email = 'khanyong.yoo@gmail.com'
  AND NOT EXISTS (
    SELECT 1 FROM profiles p WHERE p.id = u.id
  );

-- 3. 트리거 재생성 (더 안전한 버전)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
BEGIN
  RAISE NOTICE 'Trigger executed for user: % (%)', NEW.id, NEW.email;
  
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
    NEW.id, 
    NEW.email, 
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
    NEW.raw_user_meta_data->>'kiwoom_id',
    COALESCE(NEW.email_confirmed_at IS NOT NULL, false),
    NEW.email_confirmed_at,
    now(),
    now()
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    email_verified = EXCLUDED.email_verified,
    email_verified_at = EXCLUDED.email_verified_at,
    updated_at = now();
    
  RAISE NOTICE 'Profile created/updated for user: %', NEW.id;
  RETURN NEW;
EXCEPTION
  WHEN others THEN
    RAISE WARNING 'Profile creation failed for user %: % (SQLSTATE: %)', NEW.id, SQLERRM, SQLSTATE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 4. 생성 결과 확인
SELECT 
  id,
  email,
  name,
  kiwoom_account,
  email_verified,
  created_at
FROM profiles 
WHERE email = 'khanyong.yoo@gmail.com';

-- 5. 트리거 생성 확인
SELECT 
  trigger_name,
  event_object_table,
  action_timing,
  event_manipulation
FROM information_schema.triggers 
WHERE event_object_schema = 'auth' 
  AND event_object_table = 'users'
  AND trigger_name = 'on_auth_user_created';