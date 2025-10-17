-- 새로운 키움 API 키로 업데이트
-- 새 App Key: vW9vzXKmGROepjFal0vVryDSWdYaLJ3bialKM1sRvu4
-- 새 Secret Key: Q0iO6ARyIdiX_0-g585uD-7MhE55sZE9ugY1Bpt9EvE

-- 1. 기존 키 삭제
DELETE FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
  AND key_type IN ('app_key', 'app_secret');

-- 2. 새 키 삽입
INSERT INTO user_api_keys (
  user_id,
  provider,
  key_type,
  key_name,
  encrypted_value,
  is_test_mode,
  is_active,
  created_at,
  updated_at
) VALUES
-- App Key
(
  'f912da32-897f-4dbb-9242-3a438e9733a8',
  'kiwoom',
  'app_key',
  'Kiwoom App Key (NEW)',
  encode('vW9vzXKmGROepjFal0vVryDSWdYaLJ3bialKM1sRvu4'::bytea, 'base64'),
  true,
  true,
  NOW(),
  NOW()
),
-- Secret Key
(
  'f912da32-897f-4dbb-9242-3a438e9733a8',
  'kiwoom',
  'app_secret',
  'Kiwoom App Secret (NEW)',
  encode('Q0iO6ARyIdiX_0-g585uD-7MhE55sZE9ugY1Bpt9EvE'::bytea, 'base64'),
  true,
  true,
  NOW(),
  NOW()
);

-- 3. 삽입 확인
SELECT
  key_type,
  key_name,
  is_test_mode,
  is_active,
  convert_from(decode(encrypted_value, 'base64'), 'UTF8') as actual_key_value,
  created_at
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
  AND key_type IN ('app_key', 'app_secret')
ORDER BY key_type;

-- 4. 최종 확인
SELECT
  '✅ 새 키 업데이트 완료' as status,
  COUNT(*) as key_count,
  '이제 브라우저에서 키움 계좌 동기화 버튼을 클릭하세요' as next_step
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
  AND key_type IN ('app_key', 'app_secret')
  AND is_active = true;
