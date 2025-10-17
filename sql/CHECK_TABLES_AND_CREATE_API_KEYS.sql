-- 현재 테이블 구조 확인 및 user_api_keys 테이블 생성

-- 1. 현재 존재하는 테이블 확인
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('profiles', 'user_api_keys', 'user_profiles')
ORDER BY table_name;

-- 2. profiles 테이블 컬럼 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'profiles'
ORDER BY ordinal_position;

-- 3. user_api_keys 테이블이 없으면 생성
CREATE TABLE IF NOT EXISTS user_api_keys (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  provider varchar(50) NOT NULL,           -- 'kiwoom', 'google', etc.
  key_type varchar(50) NOT NULL,           -- 'app_key', 'app_secret', 'account_number'
  key_name varchar(100) NOT NULL,
  encrypted_value text NOT NULL,           -- Base64 encoded value
  is_test_mode boolean DEFAULT false,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),

  -- 하나의 사용자는 provider별로 같은 key_type을 중복 저장하지 않음
  UNIQUE(user_id, provider, key_type, key_name)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_user_api_keys_user ON user_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_user_api_keys_provider ON user_api_keys(provider);

-- RLS 활성화
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;

-- RLS 정책
DROP POLICY IF EXISTS "Users can view their own API keys" ON user_api_keys;
CREATE POLICY "Users can view their own API keys"
  ON user_api_keys FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage their own API keys" ON user_api_keys;
CREATE POLICY "Users can manage their own API keys"
  ON user_api_keys FOR ALL
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON user_api_keys TO authenticated;
GRANT ALL ON user_api_keys TO service_role;

-- 4. profiles 테이블에 kiwoom_account 컬럼이 없으면 추가
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'profiles'
      AND column_name = 'kiwoom_account'
  ) THEN
    ALTER TABLE profiles ADD COLUMN kiwoom_account varchar(50);
  END IF;
END $$;

-- 5. 확인 쿼리
SELECT
  'user_api_keys 테이블' as status,
  CASE WHEN EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'user_api_keys'
  ) THEN '✅ 존재' ELSE '❌ 없음' END as result
UNION ALL
SELECT
  'profiles.kiwoom_account 컬럼' as status,
  CASE WHEN EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'profiles'
      AND column_name = 'kiwoom_account'
  ) THEN '✅ 존재' ELSE '❌ 없음' END as result;
