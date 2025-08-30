-- Profiles 테이블 스키마 확인 및 수정
-- Supabase SQL Editor에서 실행

-- 1. 기존 테이블 확인
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'profiles'
ORDER BY ordinal_position;

-- 2. Profiles 테이블이 없다면 생성
CREATE TABLE IF NOT EXISTS profiles (
  id uuid REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email text UNIQUE,
  name text,
  kiwoom_account text,
  role text DEFAULT 'user',
  is_admin boolean DEFAULT false,
  is_approved boolean DEFAULT false,
  approval_status text DEFAULT 'pending',
  email_verified boolean DEFAULT false,
  email_verified_at timestamptz,
  avatar_url text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- 3. 누락된 컬럼들 추가 (에러 발생 시 해당 컬럼은 이미 존재)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email text UNIQUE;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS name text;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS kiwoom_account text;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now();
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS role text DEFAULT 'user';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_admin boolean DEFAULT false;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_approved boolean DEFAULT false;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS approval_status text DEFAULT 'pending';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verified boolean DEFAULT false;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email_verified_at timestamptz;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS avatar_url text;

-- 4. RLS 정책 설정
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 (에러 무시)
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles; 
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON profiles;
DROP POLICY IF EXISTS "Admin full access" ON profiles;

-- 새 정책 생성
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Enable insert for service role" ON profiles FOR INSERT WITH CHECK (true);
CREATE POLICY "Admin full access" ON profiles FOR ALL USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE id = auth.uid() 
    AND (role = 'admin' OR is_admin = true)
  )
);

-- 5. 트리거 재생성 (더 안전한 버전)
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (
    id, 
    email, 
    name, 
    kiwoom_account,
    created_at, 
    updated_at
  )
  VALUES (
    new.id, 
    new.email, 
    COALESCE(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
    new.raw_user_meta_data->>'kiwoom_id',
    now(),
    now()
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    updated_at = now();
  RETURN new;
EXCEPTION
  WHEN others THEN
    -- 에러 발생 시 로그만 남기고 계속 진행
    RAISE WARNING 'Error creating profile for user %: %', new.id, SQLERRM;
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 트리거 재생성
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();