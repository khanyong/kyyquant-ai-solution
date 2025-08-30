-- 개선된 프로필 생성 트리거
-- 문제점을 해결한 안전한 버전

-- 1. 개선된 프로필 생성 함수
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
BEGIN
  -- 프로필 생성 (중복 방지)
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
    
  RETURN NEW;
EXCEPTION
  WHEN others THEN
    -- 에러 발생 시에도 사용자 생성은 계속 진행
    RAISE WARNING 'Profile creation failed for user %: %', NEW.id, SQLERRM;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. 이메일 인증 상태 동기화 함수 (안전한 버전)
CREATE OR REPLACE FUNCTION public.sync_email_verification()
RETURNS trigger AS $$
BEGIN
  -- 프로필이 존재하는 경우에만 업데이트
  UPDATE public.profiles 
  SET 
    email_verified = COALESCE(NEW.email_confirmed_at IS NOT NULL, false),
    email_verified_at = NEW.email_confirmed_at,
    updated_at = now()
  WHERE id = NEW.id;
  
  -- 프로필이 없다면 생성
  IF NOT FOUND THEN
    INSERT INTO public.profiles (
      id, 
      email, 
      name,
      email_verified,
      email_verified_at,
      created_at, 
      updated_at
    )
    VALUES (
      NEW.id, 
      NEW.email, 
      split_part(NEW.email, '@', 1),
      COALESCE(NEW.email_confirmed_at IS NOT NULL, false),
      NEW.email_confirmed_at,
      now(),
      now()
    )
    ON CONFLICT (id) DO NOTHING;
  END IF;
  
  RETURN NEW;
EXCEPTION
  WHEN others THEN
    RAISE WARNING 'Email verification sync failed for user %: %', NEW.id, SQLERRM;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. 트리거 생성
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

CREATE TRIGGER sync_email_verification_trigger
  AFTER UPDATE OF email_confirmed_at ON auth.users
  FOR EACH ROW 
  WHEN (OLD.email_confirmed_at IS DISTINCT FROM NEW.email_confirmed_at)
  EXECUTE FUNCTION public.sync_email_verification();

-- 4. 트리거 생성 확인
SELECT 
  trigger_name,
  event_object_table,
  action_timing,
  event_manipulation
FROM information_schema.triggers 
WHERE event_object_schema = 'auth' 
  AND event_object_table = 'users'
ORDER BY trigger_name;