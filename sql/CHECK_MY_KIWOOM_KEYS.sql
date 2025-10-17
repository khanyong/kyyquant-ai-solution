-- 현재 로그인된 사용자 확인
SELECT
  auth.uid() as my_user_id,
  CASE
    WHEN auth.uid() IS NULL THEN '❌ 로그인되지 않음'
    ELSE '✅ 로그인됨'
  END as status;

-- 내 키가 있는지 확인 (현재 로그인된 사용자 기준)
SELECT
  COUNT(*) as my_keys_count,
  CASE
    WHEN COUNT(*) >= 2 THEN '✅ App Key와 Secret Key가 모두 있음'
    WHEN COUNT(*) = 1 THEN '⚠️ 키가 1개만 있음'
    ELSE '❌ 키가 없음'
  END as status
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
  AND key_type IN ('app_key', 'app_secret')
  AND is_active = true;

-- 내 모든 키 상세 정보 확인
SELECT
  id,
  user_id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  created_at,
  -- 키 값의 일부만 표시 (보안)
  LEFT(encrypted_value, 20) || '...' as encrypted_value_preview
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type, created_at DESC;

-- user_id가 NULL인 키들 확인 (정리 필요)
SELECT
  COUNT(*) as null_user_keys_count,
  CASE
    WHEN COUNT(*) > 0 THEN '⚠️ user_id가 NULL인 키가 ' || COUNT(*) || '개 있음 (정리 필요)'
    ELSE '✅ 모든 키가 정상'
  END as status
FROM user_api_keys
WHERE user_id IS NULL
  AND provider = 'kiwoom';

-- profiles 테이블에 계좌번호 확인
SELECT
  id,
  email,
  kiwoom_account,
  CASE
    WHEN kiwoom_account IS NULL THEN '❌ 계좌번호 미설정'
    ELSE '✅ 계좌번호: ' || kiwoom_account
  END as account_status
FROM profiles
WHERE id = auth.uid();
