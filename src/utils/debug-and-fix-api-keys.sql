-- API 키 저장 오류 디버깅 및 수정
-- 1단계: 테이블 존재 확인 및 생성

-- 테이블 확인
DO $$
BEGIN
  RAISE NOTICE '========================================';
  RAISE NOTICE '1. 테이블 확인';
  RAISE NOTICE '========================================';
  
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_api_keys') THEN
    RAISE NOTICE '✅ user_api_keys 테이블이 존재합니다';
  ELSE
    RAISE NOTICE '❌ user_api_keys 테이블이 없습니다. 생성합니다...';
  END IF;
  
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_profiles_extended') THEN
    RAISE NOTICE '✅ user_profiles_extended 테이블이 존재합니다';
  ELSE
    RAISE NOTICE '❌ user_profiles_extended 테이블이 없습니다. 생성합니다...';
  END IF;
END $$;

-- 2단계: 테이블이 없으면 생성
CREATE TABLE IF NOT EXISTS user_api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  provider VARCHAR(50) NOT NULL,
  key_type VARCHAR(50) NOT NULL,
  key_name VARCHAR(100),
  encrypted_value TEXT NOT NULL,
  key_id UUID,
  nonce BYTEA,
  is_active BOOLEAN DEFAULT true,
  is_test_mode BOOLEAN DEFAULT false,
  last_used_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, provider, key_type, key_name)
);

CREATE TABLE IF NOT EXISTS user_profiles_extended (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
  display_name VARCHAR(100),
  phone_number VARCHAR(20),
  birth_date DATE,
  investor_type VARCHAR(50),
  risk_tolerance VARCHAR(50),
  preferred_market VARCHAR(50),
  email_notifications BOOLEAN DEFAULT true,
  sms_notifications BOOLEAN DEFAULT false,
  push_notifications BOOLEAN DEFAULT true,
  two_factor_enabled BOOLEAN DEFAULT false,
  last_password_change TIMESTAMP WITH TIME ZONE,
  default_order_type VARCHAR(20) DEFAULT 'limit',
  default_time_in_force VARCHAR(20) DEFAULT 'day',
  max_daily_trades INTEGER DEFAULT 100,
  current_trading_mode VARCHAR(20) DEFAULT 'test' CHECK (current_trading_mode IN ('test', 'live')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3단계: 뷰 생성
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
  CASE 
    WHEN key_type = 'app_secret' THEN '••••••••'
    WHEN key_type = 'cert_password' THEN '••••••••'
    ELSE SUBSTRING(provider || '_' || key_type, 1, 4) || '••••'
  END as masked_value
FROM user_api_keys;

-- 4단계: RPC 함수 생성 (가장 간단한 버전)
DROP FUNCTION IF EXISTS save_user_api_key CASCADE;
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
BEGIN
  -- 직접 저장 (base64 인코딩)
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
    encode(p_key_value::bytea, 'base64'),
    p_is_test_mode,
    true
  )
  ON CONFLICT (user_id, provider, key_type, key_name) 
  DO UPDATE SET
    encrypted_value = encode(EXCLUDED.encrypted_value::bytea, 'base64'),
    is_test_mode = EXCLUDED.is_test_mode,
    updated_at = NOW()
  RETURNING id INTO v_key_id;
  
  RETURN v_key_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5단계: 삭제 함수
DROP FUNCTION IF EXISTS delete_user_api_key CASCADE;
CREATE OR REPLACE FUNCTION delete_user_api_key(
  p_user_id UUID,
  p_key_id UUID
) RETURNS BOOLEAN AS $$
BEGIN
  DELETE FROM user_api_keys 
  WHERE id = p_key_id AND user_id = p_user_id;
  
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 6단계: 모드 정보 함수
DROP FUNCTION IF EXISTS get_current_mode_info CASCADE;
CREATE OR REPLACE FUNCTION get_current_mode_info(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_result JSON;
BEGIN
  SELECT json_build_object(
    'current_mode', COALESCE(
      (SELECT current_trading_mode FROM user_profiles_extended WHERE user_id = p_user_id),
      'test'
    ),
    'test_ready', EXISTS (
      SELECT 1 FROM user_api_keys 
      WHERE user_id = p_user_id AND is_test_mode = true AND is_active = true
    ),
    'live_ready', EXISTS (
      SELECT 1 FROM user_api_keys 
      WHERE user_id = p_user_id AND is_test_mode = false AND is_active = true
    ),
    'can_switch_to_live', EXISTS (
      SELECT 1 FROM user_api_keys 
      WHERE user_id = p_user_id AND is_test_mode = false AND is_active = true
    )
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7단계: 모드 전환 함수
DROP FUNCTION IF EXISTS switch_trading_mode CASCADE;
CREATE OR REPLACE FUNCTION switch_trading_mode(
  p_user_id UUID,
  p_new_mode VARCHAR(20)
) RETURNS VARCHAR AS $$
BEGIN
  -- 프로필이 없으면 생성
  INSERT INTO user_profiles_extended (user_id, current_trading_mode)
  VALUES (p_user_id, p_new_mode)
  ON CONFLICT (user_id) DO UPDATE
  SET current_trading_mode = p_new_mode,
      updated_at = NOW();
  
  RETURN 'Switched to ' || p_new_mode || ' mode';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8단계: 키움 빠른 설정 함수
DROP FUNCTION IF EXISTS save_kiwoom_keys_set CASCADE;
CREATE OR REPLACE FUNCTION save_kiwoom_keys_set(
  p_user_id UUID,
  p_app_key TEXT,
  p_app_secret TEXT,
  p_account_number TEXT DEFAULT NULL,
  p_cert_password TEXT DEFAULT NULL,
  p_is_test_mode BOOLEAN DEFAULT true,
  p_key_name_suffix VARCHAR(100) DEFAULT NULL
) RETURNS JSON AS $$
DECLARE
  v_key_name VARCHAR(100);
BEGIN
  v_key_name := COALESCE(p_key_name_suffix, CASE WHEN p_is_test_mode THEN '모의투자' ELSE '실전투자' END);
  
  -- App Key 저장
  PERFORM save_user_api_key(p_user_id, 'kiwoom', 'app_key', v_key_name, p_app_key, p_is_test_mode);
  
  -- App Secret 저장
  PERFORM save_user_api_key(p_user_id, 'kiwoom', 'app_secret', v_key_name, p_app_secret, p_is_test_mode);
  
  -- 계좌번호 저장 (선택)
  IF p_account_number IS NOT NULL AND p_account_number != '' THEN
    PERFORM save_user_api_key(p_user_id, 'kiwoom', 'account_number', v_key_name, p_account_number, p_is_test_mode);
  END IF;
  
  RETURN json_build_object(
    'success', true,
    'mode', CASE WHEN p_is_test_mode THEN 'test' ELSE 'live' END,
    'key_name', v_key_name
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9단계: RLS 정책
ALTER TABLE user_api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles_extended ENABLE ROW LEVEL SECURITY;

-- 기존 정책 삭제 후 재생성
DROP POLICY IF EXISTS "Users can view own API keys" ON user_api_keys;
DROP POLICY IF EXISTS "Users can manage own API keys" ON user_api_keys;
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles_extended;
DROP POLICY IF EXISTS "Users can manage own profile" ON user_profiles_extended;

CREATE POLICY "Users can view own API keys" 
  ON user_api_keys FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own API keys" 
  ON user_api_keys FOR ALL 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can view own profile" 
  ON user_profiles_extended FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own profile" 
  ON user_profiles_extended FOR ALL 
  USING (auth.uid() = user_id);

-- 10단계: 권한 부여 (중요!)
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

GRANT ALL ON user_api_keys TO authenticated;
GRANT ALL ON user_profiles_extended TO authenticated;
GRANT SELECT ON user_api_keys_view TO authenticated;

GRANT EXECUTE ON FUNCTION save_user_api_key TO authenticated;
GRANT EXECUTE ON FUNCTION save_user_api_key TO anon;

GRANT EXECUTE ON FUNCTION delete_user_api_key TO authenticated;
GRANT EXECUTE ON FUNCTION get_current_mode_info TO authenticated;
GRANT EXECUTE ON FUNCTION switch_trading_mode TO authenticated;
GRANT EXECUTE ON FUNCTION save_kiwoom_keys_set TO authenticated;

-- 11단계: 함수 확인
DO $$
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '========================================';
  RAISE NOTICE '함수 생성 확인';
  RAISE NOTICE '========================================';
  
  IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'save_user_api_key') THEN
    RAISE NOTICE '✅ save_user_api_key 함수가 생성되었습니다';
  ELSE
    RAISE NOTICE '❌ save_user_api_key 함수가 없습니다';
  END IF;
  
  IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'delete_user_api_key') THEN
    RAISE NOTICE '✅ delete_user_api_key 함수가 생성되었습니다';
  ELSE
    RAISE NOTICE '❌ delete_user_api_key 함수가 없습니다';
  END IF;
  
  IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_current_mode_info') THEN
    RAISE NOTICE '✅ get_current_mode_info 함수가 생성되었습니다';
  ELSE
    RAISE NOTICE '❌ get_current_mode_info 함수가 없습니다';
  END IF;
  
  RAISE NOTICE '';
  RAISE NOTICE '✅ 모든 설정이 완료되었습니다!';
  RAISE NOTICE '========================================';
END $$;

-- 12단계: 테스트
-- 아래 주석을 해제하고 테스트하세요
/*
SELECT save_user_api_key(
  auth.uid(),
  'test_provider',
  'test_key',
  '테스트',
  'TEST_VALUE_123',
  true
);
*/