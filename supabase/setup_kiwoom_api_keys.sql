-- 키움 API 키 설정
-- 실행: Supabase SQL Editor

-- ⚠️ 아래 값들을 실제 키움 API 키로 변경하세요
-- Base64 인코딩이 필요합니다: btoa('실제_앱키') 형식

-- 1. 기존 키움 API 키 삭제 (있다면)
DELETE FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom';

-- 2. APP_KEY 추가
INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_active, is_test_mode)
VALUES (
  auth.uid(),
  'kiwoom',
  'app_key',
  encode('귀하의_APP_KEY'::bytea, 'base64'),  -- 실제 APP_KEY로 변경
  true,
  true  -- 모의투자는 true
);

-- 3. APP_SECRET 추가
INSERT INTO user_api_keys (user_id, provider, key_type, encrypted_value, is_active, is_test_mode)
VALUES (
  auth.uid(),
  'kiwoom',
  'app_secret',
  encode('귀하의_APP_SECRET'::bytea, 'base64'),  -- 실제 APP_SECRET로 변경
  true,
  true  -- 모의투자는 true
);

-- 4. 설정 확인
SELECT
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
