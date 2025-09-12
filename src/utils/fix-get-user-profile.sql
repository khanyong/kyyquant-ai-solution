-- get_user_profile 함수 타입 오류 수정

-- 기존 함수 삭제
DROP FUNCTION IF EXISTS get_user_profile(UUID);

-- 수정된 함수 생성 (email 타입을 VARCHAR로 변경)
CREATE OR REPLACE FUNCTION get_user_profile(p_user_id UUID)
RETURNS TABLE(
  user_id UUID,
  email VARCHAR(255),  -- TEXT에서 VARCHAR(255)로 변경
  name VARCHAR(255),   -- TEXT에서 VARCHAR(255)로 변경
  display_name VARCHAR(255),  -- TEXT에서 VARCHAR(255)로 변경
  phone_number VARCHAR(20),
  investor_type VARCHAR(50),
  risk_tolerance VARCHAR(50),
  api_keys_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    u.id,
    u.email::VARCHAR(255),  -- 명시적 타입 캐스팅
    p.name::VARCHAR(255),    -- 명시적 타입 캐스팅
    COALESCE(pe.display_name, p.name)::VARCHAR(255) as display_name,  -- 명시적 타입 캐스팅
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

-- 테스트
DO $$
DECLARE
  v_count INTEGER;
BEGIN
  -- 함수가 제대로 작동하는지 테스트
  SELECT COUNT(*) INTO v_count FROM get_user_profile(auth.uid());
  RAISE NOTICE '✅ get_user_profile 함수 수정 완료. 결과 행 수: %', v_count;
END $$;