-- 키움 API 키 설정 상태 확인

-- ========================================
-- 1. 현재 사용자의 API 키 확인
-- ========================================
SELECT
  'API 키 상태' as check_type,
  key_type,
  is_active,
  is_test_mode,
  LENGTH(encrypted_value) as key_length,
  created_at,
  updated_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- ========================================
-- 2. 프로필 계좌번호 확인
-- ========================================
SELECT
  '프로필 정보' as check_type,
  id,
  email,
  name,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = auth.uid();

-- ========================================
-- 3. API 키 복호화 테스트 (Base64)
-- ========================================
SELECT
  'API 키 복호화' as check_type,
  key_type,
  LEFT(convert_from(decode(encrypted_value, 'base64'), 'UTF8'), 10) || '...' as decrypted_preview,
  LENGTH(convert_from(decode(encrypted_value, 'base64'), 'UTF8')) as decrypted_length
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
  AND is_active = true
ORDER BY key_type;

-- ========================================
-- 예상 결과
-- ========================================

/*
✅ 정상인 경우:
1. API 키: app_key, app_secret 2개 존재
2. is_active = true, is_test_mode = true (모의투자)
3. key_length > 0 (암호화된 키 길이)
4. kiwoom_account = '8112-5100' 등

❌ 문제가 있는 경우:
1. API 키가 없음 (레코드 0개)
2. is_active = false
3. key_length = 0 또는 NULL
4. kiwoom_account = NULL
5. 복호화된 키가 이상함 (예: 매우 짧거나 이상한 문자)
*/
