-- 키움 계좌 및 API 키 완전 설정
-- 실행: Supabase SQL Editor

-- ========================================
-- 1. 계좌번호 설정
-- ========================================
UPDATE profiles
SET kiwoom_account = '81126100'
WHERE id = auth.uid();

-- ========================================
-- 2. 기존 API 키 삭제 (있다면)
-- ========================================
DELETE FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom';

-- ========================================
-- 3. APP_KEY 추가
-- ========================================
INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_active, is_test_mode)
VALUES (
  auth.uid(),
  'kiwoom',
  'app_key',
  encode('S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'::bytea, 'base64'),
  true,
  true
);

-- ========================================
-- 4. APP_SECRET 추가
-- ========================================
INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_active, is_test_mode)
VALUES (
  auth.uid(),
  'kiwoom',
  'app_secret',
  encode('tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'::bytea, 'base64'),
  true,
  true
);

-- ========================================
-- 5. 설정 확인
-- ========================================

-- 5-1. 프로필 확인
SELECT
  '=== 계좌번호 설정 ===' as section,
  id as user_id,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = auth.uid();

-- 5-2. API 키 확인
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
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 5-3. 최종 진단
SELECT
  '=== 설정 완료 확인 ===' as section,
  CASE
    WHEN EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND kiwoom_account IS NOT NULL)
      THEN '✅ 키움 계좌 설정됨'
    ELSE '❌ 키움 계좌 미설정'
  END as profile_status,
  CASE
    WHEN EXISTS (SELECT 1 FROM user_api_keys WHERE user_id = auth.uid() AND provider = 'kiwoom' AND is_active = true)
      THEN '✅ API 키 활성화'
    ELSE '❌ API 키 미설정'
  END as api_key_status;
