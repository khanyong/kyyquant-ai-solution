-- 특정 사용자 ID로 키 확인
-- User ID: f912da32-897f-4dbb-9242-3a438e9733a8

-- 1. 이 user_id로 저장된 Kiwoom 키 개수
SELECT
  COUNT(*) as key_count,
  CASE
    WHEN COUNT(*) >= 2 THEN '✅ 키가 ' || COUNT(*) || '개 있음'
    WHEN COUNT(*) = 1 THEN '⚠️ 키가 1개만 있음'
    ELSE '❌ 키가 없음 - 새로 추가 필요'
  END as status
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
  AND is_active = true;

-- 2. 상세 키 정보 확인
SELECT
  id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  created_at,
  updated_at,
  -- 암호화된 값 디코드해서 확인 (처음 30자만)
  LEFT(convert_from(decode(encrypted_value, 'base64'), 'UTF8'), 30) || '...' as decrypted_preview
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
ORDER BY key_type, created_at DESC;

-- 3. profiles 테이블에서 계좌번호 확인
SELECT
  id,
  email,
  kiwoom_account,
  CASE
    WHEN kiwoom_account IS NULL OR kiwoom_account = '' THEN '❌ 계좌번호 미설정'
    ELSE '✅ 계좌번호: ' || kiwoom_account
  END as account_status
FROM profiles
WHERE id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 4. user_id가 NULL이거나 다른 사용자의 Kiwoom 키들 (참고용)
SELECT
  user_id,
  provider,
  key_type,
  COUNT(*) as count
FROM user_api_keys
WHERE provider = 'kiwoom'
GROUP BY user_id, provider, key_type
ORDER BY user_id NULLS FIRST, key_type;
