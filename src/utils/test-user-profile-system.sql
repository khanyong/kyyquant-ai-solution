-- 사용자 프로필 시스템 통합 테스트
-- 모든 기능이 제대로 작동하는지 확인합니다

-- ============================================
-- 1. 기본 테스트 정보 출력
-- ============================================
DO $$
DECLARE
  v_user_id UUID;
BEGIN
  -- 현재 사용자 ID 가져오기
  v_user_id := auth.uid();
  
  RAISE NOTICE '';
  RAISE NOTICE '========================================';
  RAISE NOTICE '사용자 프로필 시스템 테스트 시작';
  RAISE NOTICE '========================================';
  RAISE NOTICE '현재 사용자 ID: %', COALESCE(v_user_id::TEXT, 'NOT LOGGED IN');
  RAISE NOTICE '테스트 시간: %', NOW();
  RAISE NOTICE '';
END $$;

-- ============================================
-- 2. 기존 데이터 마이그레이션 (필요시)
-- ============================================
DO $$
BEGIN
  RAISE NOTICE '----------------------------------------';
  RAISE NOTICE '2. 기존 데이터 마이그레이션 실행';
  RAISE NOTICE '----------------------------------------';
  
  -- 마이그레이션 실행
  PERFORM migrate_existing_profiles();
  
  RAISE NOTICE '✅ 마이그레이션 완료';
  RAISE NOTICE '';
END $$;

-- ============================================
-- 3. 통합 프로필 조회
-- ============================================
DO $$
DECLARE
  v_profile RECORD;
  v_count INTEGER;
BEGIN
  RAISE NOTICE '----------------------------------------';
  RAISE NOTICE '3. 통합 프로필 조회 (user_complete_profile)';
  RAISE NOTICE '----------------------------------------';
  
  SELECT COUNT(*) INTO v_count
  FROM user_complete_profile
  WHERE user_id = auth.uid();
  
  IF v_count > 0 THEN
    FOR v_profile IN 
      SELECT * FROM user_complete_profile
      WHERE user_id = auth.uid()
    LOOP
      RAISE NOTICE '이메일: %', v_profile.email;
      RAISE NOTICE '이름: %', v_profile.name;
      RAISE NOTICE '표시 이름: %', v_profile.display_name;
      RAISE NOTICE '투자자 유형: %', COALESCE(v_profile.investor_type, 'N/A');
      RAISE NOTICE '위험 감수도: %', COALESCE(v_profile.risk_tolerance, 'N/A');
      RAISE NOTICE '활성 API 키 수: %', v_profile.active_api_keys_count;
      RAISE NOTICE '계정 상태: %', v_profile.account_status;
      RAISE NOTICE '가입일: %', v_profile.member_since;
    END LOOP;
  ELSE
    RAISE NOTICE '⚠️ 프로필이 없습니다';
  END IF;
  
  RAISE NOTICE '';
END $$;

-- ============================================
-- 4. 간단한 프로필 조회
-- ============================================
DO $$
DECLARE
  v_profile RECORD;
  v_count INTEGER;
BEGIN
  RAISE NOTICE '----------------------------------------';
  RAISE NOTICE '4. 간단한 프로필 조회 (get_user_profile)';
  RAISE NOTICE '----------------------------------------';
  
  SELECT COUNT(*) INTO v_count
  FROM get_user_profile(auth.uid());
  
  IF v_count > 0 THEN
    FOR v_profile IN 
      SELECT * FROM get_user_profile(auth.uid())
    LOOP
      RAISE NOTICE '이메일: %', v_profile.email;
      RAISE NOTICE '이름: %', v_profile.name;
      RAISE NOTICE '표시 이름: %', v_profile.display_name;
      RAISE NOTICE '전화번호: %', COALESCE(v_profile.phone_number, 'N/A');
      RAISE NOTICE '투자자 유형: %', COALESCE(v_profile.investor_type, 'N/A');
      RAISE NOTICE '위험 감수도: %', COALESCE(v_profile.risk_tolerance, 'N/A');
      RAISE NOTICE 'API 키 개수: %', v_profile.api_keys_count;
    END LOOP;
  ELSE
    RAISE NOTICE '⚠️ 프로필이 없습니다';
  END IF;
  
  RAISE NOTICE '';
END $$;

-- ============================================
-- 5. 전체 프로필 JSON 조회
-- ============================================
DO $$
DECLARE
  v_json JSON;
  v_basic JSON;
  v_extended JSON;
  v_api_keys JSON;
BEGIN
  RAISE NOTICE '----------------------------------------';
  RAISE NOTICE '5. 전체 프로필 JSON (get_user_full_profile)';
  RAISE NOTICE '----------------------------------------';
  
  -- JSON 데이터 가져오기
  SELECT get_user_full_profile(auth.uid()) INTO v_json;
  
  IF v_json IS NOT NULL THEN
    -- 기본 프로필
    v_basic := v_json->'basic_profile';
    IF v_basic IS NOT NULL THEN
      RAISE NOTICE '[기본 프로필]';
      RAISE NOTICE '  - ID: %', v_basic->>'id';
      RAISE NOTICE '  - 이름: %', v_basic->>'name';
      RAISE NOTICE '  - 키움계좌: %', COALESCE(v_basic->>'kiwoom_account', 'N/A');
    END IF;
    
    -- 확장 프로필
    v_extended := v_json->'extended_profile';
    IF v_extended IS NOT NULL THEN
      RAISE NOTICE '[확장 프로필]';
      RAISE NOTICE '  - 표시 이름: %', COALESCE(v_extended->>'display_name', 'N/A');
      RAISE NOTICE '  - 전화번호: %', COALESCE(v_extended->>'phone_number', 'N/A');
      RAISE NOTICE '  - 2FA 활성화: %', COALESCE(v_extended->>'two_factor_enabled', 'false');
    END IF;
    
    -- API 키
    v_api_keys := v_json->'api_keys';
    IF v_api_keys IS NOT NULL THEN
      RAISE NOTICE '[API 키]';
      RAISE NOTICE '  - 등록된 키: %', json_array_length(v_api_keys);
    END IF;
  ELSE
    RAISE NOTICE '⚠️ JSON 프로필이 없습니다';
  END IF;
  
  RAISE NOTICE '';
END $$;

-- ============================================
-- 6. API 키 테스트
-- ============================================
DO $$
DECLARE
  v_key_id UUID;
  v_test_value TEXT := 'TEST_KEY_' || substr(gen_random_uuid()::TEXT, 1, 8);
  v_retrieved TEXT;
BEGIN
  RAISE NOTICE '----------------------------------------';
  RAISE NOTICE '6. API 키 저장/조회 테스트';
  RAISE NOTICE '----------------------------------------';
  
  -- API 키 저장
  SELECT save_user_api_key(
    auth.uid(),
    'test_provider',
    'test_key',
    '테스트용',
    v_test_value,
    true
  ) INTO v_key_id;
  
  RAISE NOTICE '✅ API 키 저장 성공: %', v_key_id;
  
  -- API 키 조회
  SELECT get_user_api_key(
    auth.uid(),
    'test_provider',
    'test_key',
    '테스트용'
  ) INTO v_retrieved;
  
  IF v_retrieved = v_test_value THEN
    RAISE NOTICE '✅ API 키 조회 성공: 값이 일치합니다';
  ELSE
    RAISE NOTICE '❌ API 키 조회 실패: 값이 일치하지 않습니다';
    RAISE NOTICE '  - 저장된 값: %', v_test_value;
    RAISE NOTICE '  - 조회된 값: %', v_retrieved;
  END IF;
  
  -- 테스트 키 삭제
  PERFORM delete_user_api_key(auth.uid(), v_key_id);
  RAISE NOTICE '✅ 테스트 API 키 삭제 완료';
  
  RAISE NOTICE '';
END $$;

-- ============================================
-- 7. pgsodium 테스트 (활성화된 경우)
-- ============================================
DO $$
DECLARE
  v_result TEXT;
BEGIN
  RAISE NOTICE '----------------------------------------';
  RAISE NOTICE '7. pgsodium 암호화 테스트';
  RAISE NOTICE '----------------------------------------';
  
  -- pgsodium 테스트 함수가 있는지 확인
  IF EXISTS (
    SELECT 1 FROM pg_proc 
    WHERE proname = 'test_pgsodium'
  ) THEN
    SELECT test_pgsodium() INTO v_result;
    
    IF v_result = 'Hello pgsodium!' THEN
      RAISE NOTICE '✅ pgsodium 정상 작동: %', v_result;
    ELSE
      RAISE NOTICE '⚠️ pgsodium 테스트 실패: %', v_result;
    END IF;
  ELSE
    RAISE NOTICE '⚠️ pgsodium 테스트 함수가 없습니다';
  END IF;
  
  RAISE NOTICE '';
END $$;

-- ============================================
-- 8. 최종 요약
-- ============================================
DO $$
DECLARE
  v_profile_count INTEGER;
  v_extended_count INTEGER;
  v_api_key_count INTEGER;
BEGIN
  RAISE NOTICE '========================================';
  RAISE NOTICE '테스트 완료 - 최종 요약';
  RAISE NOTICE '========================================';
  
  -- 프로필 수
  SELECT COUNT(*) INTO v_profile_count
  FROM profiles
  WHERE id = auth.uid();
  
  -- 확장 프로필 수
  SELECT COUNT(*) INTO v_extended_count
  FROM user_profiles_extended
  WHERE user_id = auth.uid();
  
  -- API 키 수
  SELECT COUNT(*) INTO v_api_key_count
  FROM user_api_keys
  WHERE user_id = auth.uid();
  
  RAISE NOTICE '기본 프로필: % 개', v_profile_count;
  RAISE NOTICE '확장 프로필: % 개', v_extended_count;
  RAISE NOTICE 'API 키: % 개', v_api_key_count;
  
  IF v_profile_count > 0 AND v_extended_count > 0 THEN
    RAISE NOTICE '';
    RAISE NOTICE '✅ 모든 프로필 시스템이 정상 작동합니다!';
  ELSE
    RAISE NOTICE '';
    RAISE NOTICE '⚠️ 일부 프로필 데이터가 누락되었습니다';
    RAISE NOTICE '   migrate_existing_profiles() 실행을 고려하세요';
  END IF;
  
  RAISE NOTICE '========================================';
  RAISE NOTICE '';
END $$;

-- 실제 데이터 조회 (테이블 형태로 출력)
SELECT '=== 통합 프로필 뷰 ===' as section;
SELECT * FROM user_complete_profile WHERE user_id = auth.uid();

SELECT '=== API 키 상태 ===' as section;
SELECT * FROM user_api_status WHERE user_id = auth.uid();

SELECT '=== 프로필 요약 ===' as section;
SELECT * FROM user_profile_summary WHERE user_id = auth.uid();