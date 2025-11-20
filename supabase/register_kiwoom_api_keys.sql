-- 키움 API 키 등록

-- ========================================
-- 1. 기존 키 확인 및 삭제 (있다면)
-- ========================================
SELECT * FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';

-- 기존 키 삭제 (재등록하는 경우)
DELETE FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';

-- ========================================
-- 2. 새 API 키 등록
-- ========================================
-- ⚠️ 아래 YOUR_APP_KEY와 YOUR_APP_SECRET을
--    실제 키움 OpenAPI에서 발급받은 키로 교체하세요!

INSERT INTO user_api_keys (
  user_id,
  provider,
  key_type,
  encrypted_value,
  is_test_mode,
  is_active,
  created_at,
  updated_at
) VALUES
  -- App Key
  (
    auth.uid(),
    'kiwoom',
    'app_key',
    encode('YOUR_APP_KEY'::bytea, 'base64'),  -- 🔑 여기에 실제 App Key 입력
    true,  -- 모의투자: true, 실전투자: false
    true,
    NOW(),
    NOW()
  ),
  -- App Secret
  (
    auth.uid(),
    'kiwoom',
    'app_secret',
    encode('YOUR_APP_SECRET'::bytea, 'base64'),  -- 🔑 여기에 실제 App Secret 입력
    true,  -- 모의투자: true, 실전투자: false
    true,
    NOW(),
    NOW()
  );

-- ========================================
-- 3. 등록 확인
-- ========================================
SELECT
  'API 키 등록 확인' as status,
  key_type,
  is_active,
  is_test_mode,
  LENGTH(encrypted_value) as key_length,
  created_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- ========================================
-- 예상 결과
-- ========================================
/*
status          | key_type    | is_active | is_test_mode | key_length | created_at
----------------|-------------|-----------|--------------|------------|------------
API 키 등록 확인 | app_key     | true      | true         | 60         | 2025-11-17...
API 키 등록 확인 | app_secret  | true      | true         | 60         | 2025-11-17...
*/
