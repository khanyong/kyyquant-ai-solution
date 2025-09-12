-- 사용자 API 키 안전 저장을 위한 테이블 (pgsodium 암호화 버전)
-- 주의: 00-prerequisites-fixed.sql을 먼저 실행해야 합니다!
-- 주의: Supabase 대시보드에서 pgsodium extension을 활성화해야 합니다!

-- pgsodium 확장 확인 (이미 활성화되어 있으면 오류 무시)
CREATE EXTENSION IF NOT EXISTS pgsodium;

-- 1. 사용자 API 키 테이블 (pgsodium 암호화)
CREATE TABLE IF NOT EXISTS user_api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- API 제공자 정보
  provider VARCHAR(50) NOT NULL, -- 'kiwoom', 'korea_investment', 'ebest', etc.
  key_type VARCHAR(50) NOT NULL, -- 'app_key', 'app_secret', 'account_number', 'cert_password'
  key_name VARCHAR(100), -- 사용자가 지정한 이름 (예: "모의투자용", "실전투자용")
  
  -- 암호화된 키 값 (pgsodium)
  encrypted_value TEXT NOT NULL,
  key_id UUID, -- pgsodium key reference
  nonce BYTEA, -- pgsodium nonce for decryption
  
  -- 메타데이터
  is_active BOOLEAN DEFAULT true,
  is_test_mode BOOLEAN DEFAULT false, -- 모의투자용인지
  last_used_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE, -- API 키 만료일
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, provider, key_type, key_name)
);

-- 2. API 키 저장 함수 (pgsodium 암호화)
CREATE OR REPLACE FUNCTION save_user_api_key(
  p_user_id UUID,
  p_provider VARCHAR(50),
  p_key_type VARCHAR(50),
  p_key_name VARCHAR(100),
  p_key_value TEXT,
  p_is_test_mode BOOLEAN DEFAULT false
) RETURNS UUID AS $$
DECLARE
  v_key_id UUID;
  v_key_uuid UUID;
  v_nonce BYTEA;
  v_encrypted_value BYTEA;
BEGIN
  -- 암호화 키 생성
  v_key_uuid := pgsodium.create_key(
    name := p_user_id::TEXT || '_' || p_provider || '_' || p_key_type,
    key_type := 'aead-det'
  );
  
  -- Nonce 생성
  v_nonce := pgsodium.crypto_aead_det_noncegen();
  
  -- 값 암호화
  v_encrypted_value := pgsodium.crypto_aead_det_encrypt(
    message := p_key_value::BYTEA,
    additional := (p_provider || '_' || p_key_type)::BYTEA,
    key_uuid := v_key_uuid,
    nonce := v_nonce
  );
  
  -- API 키 저장
  INSERT INTO user_api_keys (
    user_id,
    provider,
    key_type,
    key_name,
    encrypted_value,
    key_id,
    nonce,
    is_test_mode,
    is_active
  ) VALUES (
    p_user_id,
    p_provider,
    p_key_type,
    p_key_name,
    encode(v_encrypted_value, 'base64'),
    v_key_uuid,
    v_nonce,
    p_is_test_mode,
    true
  )
  ON CONFLICT (user_id, provider, key_type, key_name) 
  DO UPDATE SET
    encrypted_value = EXCLUDED.encrypted_value,
    key_id = EXCLUDED.key_id,
    nonce = EXCLUDED.nonce,
    is_test_mode = EXCLUDED.is_test_mode,
    updated_at = NOW()
  RETURNING id INTO v_key_id;
  
  RETURN v_key_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. API 키 조회 함수 (pgsodium 복호화)
CREATE OR REPLACE FUNCTION get_user_api_key(
  p_user_id UUID,
  p_provider VARCHAR(50),
  p_key_type VARCHAR(50),
  p_key_name VARCHAR(100) DEFAULT NULL
) RETURNS TEXT AS $$
DECLARE
  v_encrypted_value TEXT;
  v_key_uuid UUID;
  v_nonce BYTEA;
  v_decrypted_value BYTEA;
BEGIN
  -- 암호화된 값과 키 정보 조회
  SELECT encrypted_value, key_id, nonce 
  INTO v_encrypted_value, v_key_uuid, v_nonce
  FROM user_api_keys
  WHERE user_id = p_user_id 
    AND provider = p_provider 
    AND key_type = p_key_type
    AND (p_key_name IS NULL OR key_name = p_key_name)
    AND is_active = true
  LIMIT 1;
  
  IF v_encrypted_value IS NULL THEN
    RETURN NULL;
  END IF;
  
  -- 복호화
  v_decrypted_value := pgsodium.crypto_aead_det_decrypt(
    ciphertext := decode(v_encrypted_value, 'base64'),
    additional := (p_provider || '_' || p_key_type)::BYTEA,
    key_uuid := v_key_uuid,
    nonce := v_nonce
  );
  
  -- 사용 시간 업데이트
  UPDATE user_api_keys 
  SET last_used_at = NOW() 
  WHERE user_id = p_user_id 
    AND provider = p_provider 
    AND key_type = p_key_type
    AND (p_key_name IS NULL OR key_name = p_key_name);
  
  RETURN convert_from(v_decrypted_value, 'UTF8');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. 간단한 버전 (pgsodium secretbox 사용 - 더 간단함)
CREATE OR REPLACE FUNCTION save_user_api_key_simple(
  p_user_id UUID,
  p_provider VARCHAR(50),
  p_key_type VARCHAR(50),
  p_key_name VARCHAR(100),
  p_key_value TEXT,
  p_is_test_mode BOOLEAN DEFAULT false
) RETURNS UUID AS $$
DECLARE
  v_key_id UUID;
  v_encrypted_value TEXT;
BEGIN
  -- 간단한 secretbox 암호화 (자동 키 관리)
  v_encrypted_value := encode(
    pgsodium.crypto_secretbox(
      p_key_value::BYTEA,
      pgsodium.crypto_secretbox_noncegen(),
      pgsodium.crypto_secretbox_keygen()
    ),
    'base64'
  );
  
  -- API 키 저장
  INSERT INTO user_api_keys (
    user_id,
    provider,
    key_type,
    key_name,
    encrypted_value,
    is_test_mode,
    is_active
  ) VALUES (
    p_user_id,
    p_provider,
    p_key_type,
    p_key_name,
    v_encrypted_value,
    p_is_test_mode,
    true
  )
  ON CONFLICT (user_id, provider, key_type, key_name) 
  DO UPDATE SET
    encrypted_value = EXCLUDED.encrypted_value,
    is_test_mode = EXCLUDED.is_test_mode,
    updated_at = NOW()
  RETURNING id INTO v_key_id;
  
  RETURN v_key_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. 사용자 API 키 목록 조회 (복호화 없이)
CREATE OR REPLACE VIEW user_api_keys_view AS
SELECT 
  id,
  user_id,
  provider,
  key_type,
  key_name,
  is_active,
  is_test_mode,
  last_used_at,
  expires_at,
  created_at,
  updated_at,
  -- 키 값은 마스킹 처리
  CASE 
    WHEN key_type = 'app_secret' THEN '••••••••'
    WHEN key_type = 'cert_password' THEN '••••••••'
    ELSE SUBSTRING(provider || '_' || key_type, 1, 4) || '••••'
  END as masked_value
FROM user_api_keys;

-- 6. API 키 삭제 함수
CREATE OR REPLACE FUNCTION delete_user_api_key(
  p_user_id UUID,
  p_key_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
  v_key_uuid UUID;
BEGIN
  -- pgsodium 키 ID 조회
  SELECT key_id INTO v_key_uuid
  FROM user_api_keys 
  WHERE id = p_key_id AND user_id = p_user_id;
  
  -- API 키 삭제
  DELETE FROM user_api_keys 
  WHERE id = p_key_id AND user_id = p_user_id;
  
  -- pgsodium 키도 삭제 (있는 경우)
  IF v_key_uuid IS NOT NULL THEN
    PERFORM pgsodium.delete_key(v_key_uuid);
  END IF;
  
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. 사용자 프로필 확장 테이블
CREATE TABLE IF NOT EXISTS user_profiles_extended (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  
  -- 기본 정보
  display_name VARCHAR(100),
  phone_number VARCHAR(20),
  birth_date DATE,
  
  -- 투자 정보
  investor_type VARCHAR(50), -- 'beginner', 'intermediate', 'advanced', 'professional'
  risk_tolerance VARCHAR(50), -- 'conservative', 'moderate', 'aggressive'
  preferred_market VARCHAR(50), -- 'kospi', 'kosdaq', 'both'
  
  -- 알림 설정
  email_notifications BOOLEAN DEFAULT true,
  sms_notifications BOOLEAN DEFAULT false,
  push_notifications BOOLEAN DEFAULT true,
  
  -- 보안 설정
  two_factor_enabled BOOLEAN DEFAULT false,
  last_password_change TIMESTAMP WITH TIME ZONE,
  
  -- 거래 설정
  default_order_type VARCHAR(20) DEFAULT 'limit', -- 'market', 'limit'
  default_time_in_force VARCHAR(20) DEFAULT 'day', -- 'day', 'gtc', 'ioc'
  max_daily_trades INTEGER DEFAULT 100,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. RLS 정책
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles_extended ENABLE ROW LEVEL SECURITY;

-- API 키 정책
CREATE POLICY "Users can view own API keys" 
  ON user_api_keys FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own API keys" 
  ON user_api_keys FOR ALL 
  USING (auth.uid() = user_id);

-- 프로필 정책
CREATE POLICY "Users can view own profile" 
  ON user_profiles_extended FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own profile" 
  ON user_profiles_extended FOR ALL 
  USING (auth.uid() = user_id);

-- 9. 인덱스
CREATE INDEX IF NOT EXISTS idx_user_api_keys_user_id ON user_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_user_api_keys_provider ON user_api_keys(provider);
CREATE INDEX IF NOT EXISTS idx_user_profiles_extended_user_id ON user_profiles_extended(user_id);

-- 10. 트리거
CREATE TRIGGER update_user_api_keys_updated_at
  BEFORE UPDATE ON user_api_keys
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_user_profiles_extended_updated_at
  BEFORE UPDATE ON user_profiles_extended
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

-- 11. 테스트 함수 (pgsodium이 제대로 작동하는지 확인)
CREATE OR REPLACE FUNCTION test_pgsodium()
RETURNS TEXT AS $$
DECLARE
  v_test_key UUID;
  v_test_encrypted BYTEA;
  v_test_nonce BYTEA;
  v_test_decrypted BYTEA;
BEGIN
  -- 테스트 키 생성
  v_test_key := pgsodium.create_key(
    name := 'test_key_' || gen_random_uuid()::TEXT,
    key_type := 'aead-det'
  );
  
  -- Nonce 생성
  v_test_nonce := pgsodium.crypto_aead_det_noncegen();
  
  -- 암호화
  v_test_encrypted := pgsodium.crypto_aead_det_encrypt(
    message := 'Hello pgsodium!'::BYTEA,
    additional := 'test'::BYTEA,
    key_uuid := v_test_key,
    nonce := v_test_nonce
  );
  
  -- 복호화
  v_test_decrypted := pgsodium.crypto_aead_det_decrypt(
    ciphertext := v_test_encrypted,
    additional := 'test'::BYTEA,
    key_uuid := v_test_key,
    nonce := v_test_nonce
  );
  
  -- 테스트 키 삭제
  PERFORM pgsodium.delete_key(v_test_key);
  
  RETURN convert_from(v_test_decrypted, 'UTF8');
END;
$$ LANGUAGE plpgsql;

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ User API Keys schema with pgsodium created successfully!';
  RAISE NOTICE '🔐 Using pgsodium for secure encryption';
  RAISE NOTICE '📌 Test with: SELECT test_pgsodium();';
  RAISE NOTICE '📌 Expected result: "Hello pgsodium!"';
END $$;