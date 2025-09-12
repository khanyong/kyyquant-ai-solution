-- RPC 함수 404 오류 빠른 수정
-- save_user_api_key 함수가 없어서 발생하는 오류 해결

-- 1. 간단한 save_user_api_key 함수 (base64 인코딩만 사용)
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
  v_encrypted_value TEXT;
BEGIN
  -- 간단한 base64 인코딩
  v_encrypted_value := encode(p_key_value::bytea, 'base64');
  
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

-- 2. delete_user_api_key 함수
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

-- 3. get_current_mode_info 함수 (간단 버전)
CREATE OR REPLACE FUNCTION get_current_mode_info(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_result JSON;
  v_current_mode VARCHAR(20);
  v_test_count INTEGER;
  v_live_count INTEGER;
BEGIN
  -- 현재 모드 확인
  SELECT current_trading_mode INTO v_current_mode
  FROM user_profiles_extended
  WHERE user_id = p_user_id;
  
  IF v_current_mode IS NULL THEN
    v_current_mode := 'test';
  END IF;
  
  -- 키 개수 확인
  SELECT 
    COUNT(*) FILTER (WHERE is_test_mode = true) as test_count,
    COUNT(*) FILTER (WHERE is_test_mode = false) as live_count
  INTO v_test_count, v_live_count
  FROM user_api_keys
  WHERE user_id = p_user_id AND is_active = true;
  
  -- 결과 조합
  SELECT json_build_object(
    'current_mode', v_current_mode,
    'test_ready', v_test_count > 0,
    'live_ready', v_live_count > 0,
    'can_switch_to_live', v_live_count > 0
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. switch_trading_mode 함수
CREATE OR REPLACE FUNCTION switch_trading_mode(
  p_user_id UUID,
  p_new_mode VARCHAR(20)
)
RETURNS VARCHAR AS $$
DECLARE
  v_result VARCHAR(100);
BEGIN
  -- 모드 유효성 검사
  IF p_new_mode NOT IN ('test', 'live') THEN
    RAISE EXCEPTION 'Invalid mode. Use "test" or "live"';
  END IF;
  
  -- 모드 업데이트
  UPDATE user_profiles_extended
  SET 
    current_trading_mode = p_new_mode,
    updated_at = NOW()
  WHERE user_id = p_user_id;
  
  -- 프로필이 없으면 생성
  IF NOT FOUND THEN
    INSERT INTO user_profiles_extended (user_id, current_trading_mode)
    VALUES (p_user_id, p_new_mode)
    ON CONFLICT (user_id) DO UPDATE
    SET current_trading_mode = p_new_mode;
  END IF;
  
  v_result := 'Switched to ' || p_new_mode || ' mode';
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. save_kiwoom_keys_set 함수
CREATE OR REPLACE FUNCTION save_kiwoom_keys_set(
  p_user_id UUID,
  p_app_key TEXT,
  p_app_secret TEXT,
  p_account_number TEXT DEFAULT NULL,
  p_cert_password TEXT DEFAULT NULL,
  p_is_test_mode BOOLEAN DEFAULT true,
  p_key_name_suffix VARCHAR(100) DEFAULT NULL
)
RETURNS JSON AS $$
DECLARE
  v_key_name VARCHAR(100);
  v_result JSON;
  v_app_key_id UUID;
  v_app_secret_id UUID;
BEGIN
  -- 키 이름 설정
  v_key_name := CASE 
    WHEN p_key_name_suffix IS NOT NULL THEN p_key_name_suffix
    WHEN p_is_test_mode THEN '모의투자'
    ELSE '실전투자'
  END;
  
  -- App Key 저장
  SELECT save_user_api_key(
    p_user_id,
    'kiwoom',
    'app_key',
    v_key_name,
    p_app_key,
    p_is_test_mode
  ) INTO v_app_key_id;
  
  -- App Secret 저장
  SELECT save_user_api_key(
    p_user_id,
    'kiwoom',
    'app_secret',
    v_key_name,
    p_app_secret,
    p_is_test_mode
  ) INTO v_app_secret_id;
  
  -- 계좌번호 저장 (선택사항)
  IF p_account_number IS NOT NULL AND p_account_number != '' THEN
    PERFORM save_user_api_key(
      p_user_id,
      'kiwoom',
      'account_number',
      v_key_name,
      p_account_number,
      p_is_test_mode
    );
  END IF;
  
  -- 결과 반환
  SELECT json_build_object(
    'success', true,
    'mode', CASE WHEN p_is_test_mode THEN 'test' ELSE 'live' END,
    'key_name', v_key_name
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 권한 부여
GRANT EXECUTE ON FUNCTION save_user_api_key TO authenticated;
GRANT EXECUTE ON FUNCTION delete_user_api_key TO authenticated;
GRANT EXECUTE ON FUNCTION get_current_mode_info TO authenticated;
GRANT EXECUTE ON FUNCTION switch_trading_mode TO authenticated;
GRANT EXECUTE ON FUNCTION save_kiwoom_keys_set TO authenticated;

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ RPC functions created successfully!';
  RAISE NOTICE '📌 All 404 errors should be resolved now';
END $$;