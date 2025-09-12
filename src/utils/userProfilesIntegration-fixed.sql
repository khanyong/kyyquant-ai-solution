-- 기존 profiles 테이블과 새로운 테이블들의 통합 뷰
-- profiles 테이블의 실제 구조에 맞게 수정됨

-- 0. profiles 테이블에 누락된 컬럼 추가 (필요시)
DO $$ 
BEGIN
  -- kiwoom_account 컬럼이 없으면 추가
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'profiles' 
    AND column_name = 'kiwoom_account'
  ) THEN
    ALTER TABLE profiles ADD COLUMN kiwoom_account VARCHAR(50);
  END IF;
END $$;

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

-- 3. 간소화된 프로필 뷰 (거래 계좌 제외)
CREATE OR REPLACE VIEW user_profile_summary AS
SELECT 
  u.id as user_id,
  u.email,
  COALESCE(pe.display_name, p.name, u.email) as display_name,
  p.name as profile_name,
  pe.phone_number,
  pe.investor_type,
  pe.risk_tolerance,
  pe.preferred_market,
  pe.email_notifications,
  pe.sms_notifications,
  pe.push_notifications,
  pe.two_factor_enabled,
  p.created_at,
  pe.updated_at
FROM auth.users u
LEFT JOIN profiles p ON p.id = u.id
LEFT JOIN user_profiles_extended pe ON pe.user_id = u.id;

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
  
  -- kiwoom_account 정보가 있으면 API 키로 마이그레이션
  INSERT INTO user_api_keys (
    user_id,
    provider,
    key_type,
    key_name,
    encrypted_value,
    is_test_mode,
    is_active
  )
  SELECT 
    p.id,
    'kiwoom',
    'account_number',
    '레거시 계좌',
    encode(p.kiwoom_account::bytea, 'base64'), -- 간단한 인코딩
    false,
    true
  FROM profiles p
  WHERE p.kiwoom_account IS NOT NULL
    AND p.kiwoom_account != ''
    AND NOT EXISTS (
      SELECT 1 FROM user_api_keys ak 
      WHERE ak.user_id = p.id 
        AND ak.provider = 'kiwoom'
        AND ak.key_type = 'account_number'
    );
END;
$$ LANGUAGE plpgsql;

-- 5. RLS 정책 (뷰에 대한)
-- Supabase에서 뷰는 기본적으로 security_invoker를 사용
ALTER VIEW user_complete_profile SET (security_barrier = true);
ALTER VIEW user_api_status SET (security_barrier = true);
ALTER VIEW user_profile_summary SET (security_barrier = true);

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

-- 트리거가 이미 존재하면 삭제 후 재생성
DROP TRIGGER IF EXISTS after_profile_created ON profiles;
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
          'key_name', key_name,
          'is_active', is_active,
          'is_test_mode', is_test_mode
        )
      )
      FROM user_api_keys
      WHERE user_id = p_user_id
    ),
    'summary', (
      SELECT row_to_json(ps.*)
      FROM user_profile_summary ps
      WHERE ps.user_id = p_user_id
    )
  ) INTO v_result;
  
  RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. 간단한 프로필 조회 함수
CREATE OR REPLACE FUNCTION get_user_profile(p_user_id UUID)
RETURNS TABLE(
  user_id UUID,
  email TEXT,
  name TEXT,
  display_name TEXT,
  phone_number VARCHAR(20),
  investor_type VARCHAR(50),
  risk_tolerance VARCHAR(50),
  api_keys_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    u.id,
    u.email,
    p.name,
    COALESCE(pe.display_name, p.name) as display_name,
    pe.phone_number,
    pe.investor_type,
    pe.risk_tolerance,
    (SELECT COUNT(*) FROM user_api_keys WHERE user_api_keys.user_id = u.id)
  FROM auth.users u
  LEFT JOIN profiles p ON p.id = u.id
  LEFT JOIN user_profiles_extended pe ON pe.user_id = u.id
  WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE '✅ User profiles integration completed successfully!';
  RAISE NOTICE '📌 Views created: user_complete_profile, user_api_status, user_profile_summary';
  RAISE NOTICE '📌 Run migrate_existing_profiles() to migrate existing data';
  RAISE NOTICE '📌 Test with: SELECT * FROM user_complete_profile WHERE user_id = auth.uid()';
END $$;