-- 모의투자/실전투자 듀얼 모드 API 키 관리 시스템

-- 1. 사용자의 현재 거래 모드 저장 (profiles_extended에 추가)
ALTER TABLE user_profiles_extended 
ADD COLUMN IF NOT EXISTS current_trading_mode VARCHAR(20) DEFAULT 'test' CHECK (current_trading_mode IN ('test', 'live'));

-- 2. API 키 세트 조회 함수 (모의/실전 구분)
CREATE OR REPLACE FUNCTION get_user_api_keys_by_mode(
  p_user_id UUID,
  p_provider VARCHAR(50),
  p_is_test_mode BOOLEAN
)
RETURNS TABLE(
  key_type VARCHAR(50),
  key_name VARCHAR(100),
  decrypted_value TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    ak.key_type,
    ak.key_name,
    get_user_api_key(p_user_id, p_provider, ak.key_type, ak.key_name) as decrypted_value
  FROM user_api_keys ak
  WHERE ak.user_id = p_user_id
    AND ak.provider = p_provider
    AND ak.is_test_mode = p_is_test_mode
    AND ak.is_active = true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. 현재 모드에 따른 API 키 자동 선택
CREATE OR REPLACE FUNCTION get_active_api_keys(
  p_user_id UUID,
  p_provider VARCHAR(50)
)
RETURNS TABLE(
  key_type VARCHAR(50),
  key_name VARCHAR(100),
  decrypted_value TEXT,
  is_test_mode BOOLEAN
) AS $$
DECLARE
  v_current_mode VARCHAR(20);
BEGIN
  -- 현재 거래 모드 확인
  SELECT current_trading_mode INTO v_current_mode
  FROM user_profiles_extended
  WHERE user_id = p_user_id;
  
  -- 기본값은 test 모드
  IF v_current_mode IS NULL THEN
    v_current_mode := 'test';
  END IF;
  
  -- 현재 모드에 맞는 키 반환
  RETURN QUERY
  SELECT 
    ak.key_type,
    ak.key_name,
    get_user_api_key(p_user_id, p_provider, ak.key_type, ak.key_name) as decrypted_value,
    ak.is_test_mode
  FROM user_api_keys ak
  WHERE ak.user_id = p_user_id
    AND ak.provider = p_provider
    AND ak.is_test_mode = (v_current_mode = 'test')
    AND ak.is_active = true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. 거래 모드 전환 함수
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
  
  -- 실전 모드로 전환시 실전 키 존재 확인
  IF p_new_mode = 'live' THEN
    IF NOT EXISTS (
      SELECT 1 FROM user_api_keys 
      WHERE user_id = p_user_id 
        AND is_test_mode = false 
        AND is_active = true
    ) THEN
      RAISE EXCEPTION 'No live API keys found. Please add live keys first.';
    END IF;
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
    VALUES (p_user_id, p_new_mode);
  END IF;
  
  v_result := 'Switched to ' || p_new_mode || ' mode';
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. API 키 상태 대시보드 뷰
CREATE OR REPLACE VIEW user_api_keys_dashboard AS
SELECT 
  u.id as user_id,
  u.email,
  pe.current_trading_mode,
  -- 모의투자 키 상태
  (
    SELECT COUNT(*) 
    FROM user_api_keys 
    WHERE user_id = u.id 
      AND is_test_mode = true 
      AND is_active = true
  ) as test_keys_count,
  -- 실전투자 키 상태
  (
    SELECT COUNT(*) 
    FROM user_api_keys 
    WHERE user_id = u.id 
      AND is_test_mode = false 
      AND is_active = true
  ) as live_keys_count,
  -- 키움 모의투자 준비 상태
  EXISTS (
    SELECT 1 FROM user_api_keys
    WHERE user_id = u.id
      AND provider = 'kiwoom'
      AND key_type IN ('app_key', 'app_secret')
      AND is_test_mode = true
      AND is_active = true
    GROUP BY provider
    HAVING COUNT(DISTINCT key_type) >= 2
  ) as kiwoom_test_ready,
  -- 키움 실전투자 준비 상태
  EXISTS (
    SELECT 1 FROM user_api_keys
    WHERE user_id = u.id
      AND provider = 'kiwoom'
      AND key_type IN ('app_key', 'app_secret')
      AND is_test_mode = false
      AND is_active = true
    GROUP BY provider
    HAVING COUNT(DISTINCT key_type) >= 2
  ) as kiwoom_live_ready
FROM auth.users u
LEFT JOIN user_profiles_extended pe ON pe.user_id = u.id;

-- 6. 통합 API 키 입력 헬퍼 함수
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
  v_account_id UUID;
  v_cert_id UUID;
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
    SELECT save_user_api_key(
      p_user_id,
      'kiwoom',
      'account_number',
      v_key_name,
      p_account_number,
      p_is_test_mode
    ) INTO v_account_id;
  END IF;
  
  -- 인증서 비밀번호 저장 (선택사항)
  IF p_cert_password IS NOT NULL AND p_cert_password != '' THEN
    SELECT save_user_api_key(
      p_user_id,
      'kiwoom',
      'cert_password',
      v_key_name,
      p_cert_password,
      p_is_test_mode
    ) INTO v_cert_id;
  END IF;
  
  -- 결과 반환
  SELECT json_build_object(
    'success', true,
    'mode', CASE WHEN p_is_test_mode THEN 'test' ELSE 'live' END,
    'key_name', v_key_name,
    'keys_saved', json_build_object(
      'app_key', v_app_key_id IS NOT NULL,
      'app_secret', v_app_secret_id IS NOT NULL,
      'account_number', v_account_id IS NOT NULL,
      'cert_password', v_cert_id IS NOT NULL
    )
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. 현재 활성 키 정보 조회
CREATE OR REPLACE FUNCTION get_current_mode_info(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_result JSON;
  v_current_mode VARCHAR(20);
  v_test_ready BOOLEAN;
  v_live_ready BOOLEAN;
BEGIN
  -- 현재 모드 확인
  SELECT current_trading_mode INTO v_current_mode
  FROM user_profiles_extended
  WHERE user_id = p_user_id;
  
  IF v_current_mode IS NULL THEN
    v_current_mode := 'test';
  END IF;
  
  -- 준비 상태 확인
  SELECT 
    kiwoom_test_ready,
    kiwoom_live_ready
  INTO v_test_ready, v_live_ready
  FROM user_api_keys_dashboard
  WHERE user_id = p_user_id;
  
  -- 결과 조합
  SELECT json_build_object(
    'current_mode', v_current_mode,
    'test_ready', COALESCE(v_test_ready, false),
    'live_ready', COALESCE(v_live_ready, false),
    'can_switch_to_live', COALESCE(v_live_ready, false),
    'active_keys', (
      SELECT json_agg(
        json_build_object(
          'provider', provider,
          'key_type', key_type,
          'key_name', key_name
        )
      )
      FROM user_api_keys
      WHERE user_id = p_user_id
        AND is_test_mode = (v_current_mode = 'test')
        AND is_active = true
    )
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. RLS 정책 업데이트
CREATE POLICY "Users can view own dashboard" 
  ON user_api_keys_dashboard FOR SELECT 
  USING (auth.uid() = user_id);

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ Dual-mode API key system created successfully!';
  RAISE NOTICE '📌 Test with: SELECT get_current_mode_info(auth.uid());';
  RAISE NOTICE '📌 Switch mode: SELECT switch_trading_mode(auth.uid(), ''live'');';
END $$;