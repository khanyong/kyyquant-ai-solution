-- 키움 계좌 및 API 키 최종 설정
-- 사용자 ID: f912da32-897f-4dbb-9242-3a438e9733a8
-- 실행: Supabase SQL Editor

DO $$
DECLARE
  v_user_id UUID := 'f912da32-897f-4dbb-9242-3a438e9733a8';
BEGIN
  RAISE NOTICE '========================================';
  RAISE NOTICE '사용자 ID: %', v_user_id;
  RAISE NOTICE '========================================';

  -- ========================================
  -- 1. 계좌번호 설정
  -- ========================================
  UPDATE profiles
  SET kiwoom_account = '81126100'
  WHERE id = v_user_id;

  RAISE NOTICE '✅ 계좌번호 설정 완료: 81126100';

  -- ========================================
  -- 2. 기존 API 키 삭제
  -- ========================================
  DELETE FROM user_api_keys
  WHERE user_id = v_user_id
    AND provider = 'kiwoom';

  RAISE NOTICE '✅ 기존 API 키 삭제 완료';

  -- ========================================
  -- 3. APP_KEY 추가
  -- ========================================
  INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_active, is_test_mode)
  VALUES (
    v_user_id,
    'kiwoom',
    'app_key',
    encode('S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'::bytea, 'base64'),
    true,
    true
  );

  RAISE NOTICE '✅ APP_KEY 설정 완료';

  -- ========================================
  -- 4. APP_SECRET 추가
  -- ========================================
  INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_active, is_test_mode)
  VALUES (
    v_user_id,
    'kiwoom',
    'app_secret',
    encode('tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'::bytea, 'base64'),
    true,
    true
  );

  RAISE NOTICE '✅ APP_SECRET 설정 완료';
  RAISE NOTICE '';
  RAISE NOTICE '🎉 모든 설정 완료!';
  RAISE NOTICE '========================================';
END $$;

-- ========================================
-- 설정 확인
-- ========================================

-- 1. 프로필 확인
SELECT
  '=== 계좌번호 설정 ===' as section,
  id as user_id,
  email,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 2. API 키 확인
SELECT
  '=== API 키 설정 ===' as section,
  user_id,
  provider,
  key_type,
  is_active,
  is_test_mode,
  LENGTH(encrypted_value) as key_length,
  created_at
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 3. 최종 진단
SELECT
  '=== 설정 완료 확인 ===' as section,
  CASE
    WHEN EXISTS (SELECT 1 FROM profiles WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND kiwoom_account = '81126100')
      THEN '✅ 키움 계좌 설정됨 (81126100)'
    ELSE '❌ 키움 계좌 미설정'
  END as profile_status,
  CASE
    WHEN (SELECT COUNT(*) FROM user_api_keys WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' AND provider = 'kiwoom' AND is_active = true) = 2
      THEN '✅ API 키 활성화 (2개)'
    ELSE '❌ API 키 미설정'
  END as api_key_status;
