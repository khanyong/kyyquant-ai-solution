-- 회원가입 시 자동으로 profiles 테이블에 레코드 생성하는 트리거
-- Supabase SQL Editor에서 실행해주세요

-- 트리거 함수 생성
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, name, kiwoom_account, created_at, updated_at)
  VALUES (
    new.id, 
    new.email, 
    COALESCE(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
    new.raw_user_meta_data->>'kiwoom_id',
    now(),
    now()
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 트리거 생성
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- RLS 정책 확인/생성
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 사용자가 자신의 프로필만 읽을 수 있도록
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);

-- 사용자가 자신의 프로필만 업데이트할 수 있도록  
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

-- 트리거에서 프로필을 INSERT할 수 있도록 (인증된 사용자만)
CREATE POLICY "Enable insert for authenticated users only" ON profiles FOR INSERT 
WITH CHECK (auth.role() = 'authenticated');

-- 관리자는 모든 프로필에 접근 가능
CREATE POLICY "Admin full access" ON profiles FOR ALL 
USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE id = auth.uid() 
    AND (role = 'admin' OR is_admin = true)
  )
);