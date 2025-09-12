-- 기존 profiles 테이블과 새로운 테이블들의 통합 뷰

-- 1. 통합 사용자 정보 뷰
CREATE OR REPLACE VIEW user_complete_profile AS
SELECT 
  -- Auth 정보
  u.id as user_id,
  u.email,
  
  -- 기본 프로필 (profiles 테이블)
  p.name,
  p.kiwoom_account as legacy_kiwoom_account,
  p.created_at as member_since,
  
  -- 확장 프로필 (user_profiles_extended 테이블)
  pe.display_name,
  pe.phone_number,
  pe.birth_date,
  pe.investor_type,
  pe.risk_tolerance,
  pe.preferred_market,
  pe.email_notifications,
  pe.sms_notifications,
  pe.push_notifications,
  pe.two_factor_enabled,
  
  -- API 키 요약 (user_api_keys 테이블)
  (
    SELECT COUNT(*) 
    FROM user_api_keys 
    WHERE user_id = u.id AND is_active = true
  ) as active_api_keys_count,
  
  -- 거래 계좌 요약 (user_trading_accounts_secure 테이블)
  (
    SELECT COUNT(*) 
    FROM user_trading_accounts_secure 
    WHERE user_id = u.id AND is_connected = true
  ) as connected_accounts_count,
  
  -- 계정 상태
  CASE 
    WHEN pe.two_factor_enabled THEN 'secured'
    WHEN pe.user_id IS NOT NULL THEN 'active'
    ELSE 'basic'
  END as account_status
  
FROM auth.users u
LEFT JOIN profiles p ON p.id = u.id  -- 기존 profiles와 연결
LEFT JOIN user_profiles_extended pe ON pe.user_id = u.id
WHERE u.deleted_at IS NULL;

-- 2. 사용자 API 키 상태 뷰
CREATE OR REPLACE VIEW user_api_status AS
SELECT 
  u.id as user_id,
  u.email,
  p.name,
  ak.provider,
  ak.key_type,
  ak.key_name,
  ak.is_test_mode,
  ak.is_active,
  ak.last_used_at,
  CASE 
    WHEN ak.expires_at < NOW() THEN 'expired'
    WHEN ak.expires_at < NOW() + INTERVAL '30 days' THEN 'expiring_soon'
    ELSE 'valid'
  END as key_status
FROM auth.users u
LEFT JOIN profiles p ON p.id = u.id
LEFT JOIN user_api_keys ak ON ak.user_id = u.id
WHERE ak.id IS NOT NULL;

-- 3. 사용자 거래 계좌 상태 뷰
CREATE OR REPLACE VIEW user_trading_status AS
SELECT 
  u.id as user_id,
  u.email,
  p.name,
  ta.account_type,
  ta.account_number,
  ta.account_name,
  ta.is_connected,
  ta.is_active,
  ta.current_balance,
  ta.available_balance,
  ta.allow_auto_trading,
  CASE 
    WHEN ta.token_expires_at < NOW() THEN 'token_expired'
    WHEN ta.is_connected = false THEN 'disconnected'
    WHEN ta.is_active = false THEN 'inactive'
    ELSE 'ready'
  END as account_status
FROM auth.users u
LEFT JOIN profiles p ON p.id = u.id
LEFT JOIN user_trading_accounts_secure ta ON ta.user_id = u.id
WHERE ta.id IS NOT NULL;

-- 4. 마이그레이션 함수 (기존 profiles 데이터를 새 테이블로)
CREATE OR REPLACE FUNCTION migrate_existing_profiles() RETURNS void AS $$
BEGIN
  -- 기존 profiles에서 user_profiles_extended로 데이터 마이그레이션
  INSERT INTO user_profiles_extended (
    user_id,
    display_name,
    email_notifications,
    sms_notifications,
    push_notifications
  )
  SELECT 
    p.id,
    p.name,
    true,  -- 기본값
    false, -- 기본값
    true   -- 기본값
  FROM profiles p
  WHERE NOT EXISTS (
    SELECT 1 FROM user_profiles_extended pe 
    WHERE pe.user_id = p.id
  );
  
  -- 기존 kiwoom_account 정보를 user_trading_accounts_secure로 마이그레이션
  INSERT INTO user_trading_accounts_secure (
    user_id,
    account_type,
    account_number,
    account_name,
    broker,
    is_active
  )
  SELECT 
    p.id,
    'real', -- 기본값 (나중에 사용자가 수정 가능)
    p.kiwoom_account,
    p.name || '의 키움계좌',
    'kiwoom',
    false -- 초기에는 비활성
  FROM profiles p
  WHERE p.kiwoom_account IS NOT NULL
    AND p.kiwoom_account != ''
    AND NOT EXISTS (
      SELECT 1 FROM user_trading_accounts_secure ta 
      WHERE ta.user_id = p.id 
        AND ta.account_number = p.kiwoom_account
    );
END;
$$ LANGUAGE plpgsql;

-- 5. RLS 정책 (뷰에 대한)
ALTER VIEW user_complete_profile SET (security_invoker = true);
ALTER VIEW user_api_status SET (security_invoker = true);
ALTER VIEW user_trading_status SET (security_invoker = true);

-- 6. 인덱스 추가 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_profiles_id ON profiles(id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_extended_user_id ON user_profiles_extended(user_id);

-- 7. 트리거: profiles 생성 시 user_profiles_extended도 자동 생성
CREATE OR REPLACE FUNCTION create_extended_profile() 
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_profiles_extended (
    user_id,
    display_name,
    email_notifications,
    sms_notifications,
    push_notifications
  ) VALUES (
    NEW.id,
    NEW.name,
    true,
    false,
    true
  ) ON CONFLICT (user_id) DO NOTHING;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_profile_created
  AFTER INSERT ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION create_extended_profile();

-- 8. Helper 함수: 전체 사용자 정보 조회
CREATE OR REPLACE FUNCTION get_user_full_profile(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
  v_result JSON;
BEGIN
  SELECT json_build_object(
    'basic_profile', (
      SELECT row_to_json(p.*) 
      FROM profiles p 
      WHERE p.id = p_user_id
    ),
    'extended_profile', (
      SELECT row_to_json(pe.*) 
      FROM user_profiles_extended pe 
      WHERE pe.user_id = p_user_id
    ),
    'api_keys', (
      SELECT json_agg(
        json_build_object(
          'provider', provider,
          'key_type', key_type,
          'is_active', is_active,
          'is_test_mode', is_test_mode
        )
      )
      FROM user_api_keys
      WHERE user_id = p_user_id
    ),
    'trading_accounts', (
      SELECT json_agg(
        json_build_object(
          'account_type', account_type,
          'account_number', account_number,
          'is_connected', is_connected,
          'is_active', is_active
        )
      )
      FROM user_trading_accounts_secure
      WHERE user_id = p_user_id
    )
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 실행 예시:
-- SELECT migrate_existing_profiles(); -- 기존 데이터 마이그레이션
-- SELECT * FROM user_complete_profile WHERE user_id = 'your-user-id';
-- SELECT get_user_full_profile('your-user-id');