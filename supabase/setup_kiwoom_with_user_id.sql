-- 키움 계좌 및 API 키 설정 (사용자 ID 직접 지정)
-- 실행: Supabase SQL Editor

-- ========================================
-- 0. 현재 사용자 확인
-- ========================================
-- 먼저 이 쿼리를 실행하여 user_id를 확인하세요
SELECT
  id as user_id,
  email,
  created_at
FROM auth.users
ORDER BY created_at DESC
LIMIT 1;

-- ⚠️ 위 쿼리 결과의 user_id를 복사하여 아래 변수에 입력하세요!

-- ========================================
-- 1. 사용자 ID 설정 (변수)
-- ========================================
DO $$
DECLARE
  v_user_id UUID := (SELECT id FROM auth.users ORDER BY created_at DESC LIMIT 1);
BEGIN
  RAISE NOTICE '사용자 ID: %', v_user_id;

  -- ========================================
  -- 2. 계좌번호 설정
  -- ========================================
  UPDATE profiles
  SET kiwoom_account = '81126100'
  WHERE id = v_user_id;

  RAISE NOTICE '✅ 계좌번호 설정 완료: 81126100';

  -- ========================================
  -- 3. 기존 API 키 삭제
  -- ========================================
  DELETE FROM user_api_keys
  WHERE user_id = v_user_id
    AND provider = 'kiwoom';

  RAISE NOTICE '✅ 기존 API 키 삭제 완료';

  -- ========================================
  -- 4. APP_KEY 추가
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
  -- 5. APP_SECRET 추가
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
END $$;

-- ========================================
-- 6. 설정 확인
-- ========================================

-- 6-1. 프로필 확인
SELECT
  '=== 계좌번호 설정 ===' as section,
  id as user_id,
  kiwoom_account,
  created_at
FROM profiles
ORDER BY created_at DESC
LIMIT 1;

-- 6-2. API 키 확인
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
WHERE provider = 'kiwoom'
ORDER BY created_at DESC
LIMIT 2;

-- 6-3. 최종 진단
SELECT
  '=== 설정 완료 확인 ===' as section,
  CASE
    WHEN EXISTS (SELECT 1 FROM profiles WHERE kiwoom_account = '81126100')
      THEN '✅ 키움 계좌 설정됨'
    ELSE '❌ 키움 계좌 미설정'
  END as profile_status,
  CASE
    WHEN EXISTS (SELECT 1 FROM user_api_keys WHERE provider = 'kiwoom' AND is_active = true)
      THEN '✅ API 키 활성화 (' || (SELECT COUNT(*) FROM user_api_keys WHERE provider = 'kiwoom' AND is_active = true)::text || '개)'
    ELSE '❌ API 키 미설정'
  END as api_key_status;
