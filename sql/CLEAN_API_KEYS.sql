-- user_api_keys 테이블의 불필요한 키 정리

-- 1. 현재 모든 키 확인 (삭제 전)
SELECT
  id,
  user_id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  created_at,
  CASE
    WHEN user_id IS NULL THEN '❌ user_id가 NULL'
    WHEN user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8' THEN '✅ 내 키'
    ELSE '⚠️ 다른 사용자 키'
  END as status
FROM user_api_keys
WHERE provider = 'kiwoom'
ORDER BY user_id NULLS FIRST, key_type;

-- 2. user_id가 NULL인 키 삭제
DELETE FROM user_api_keys
WHERE provider = 'kiwoom'
  AND user_id IS NULL;

-- 3. 다른 사용자의 키 삭제 (내 키만 남기기)
DELETE FROM user_api_keys
WHERE provider = 'kiwoom'
  AND user_id != 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 4. 내 키 중 중복된 키 정리 (최신 것만 남기고 삭제)
-- 먼저 중복 확인
SELECT
  user_id,
  provider,
  key_type,
  COUNT(*) as count,
  CASE
    WHEN COUNT(*) > 1 THEN '⚠️ 중복됨 - 정리 필요'
    ELSE '✅ 정상'
  END as status
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
GROUP BY user_id, provider, key_type;

-- 중복된 키 삭제 (최신 것만 남기기)
DELETE FROM user_api_keys
WHERE id IN (
  SELECT id
  FROM (
    SELECT
      id,
      ROW_NUMBER() OVER (
        PARTITION BY user_id, provider, key_type
        ORDER BY created_at DESC
      ) as rn
    FROM user_api_keys
    WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
      AND provider = 'kiwoom'
  ) sub
  WHERE rn > 1
);

-- 5. 정리 후 최종 상태 확인
SELECT
  id,
  user_id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  created_at,
  updated_at,
  -- 실제 값 확인 (일부만 표시)
  LEFT(convert_from(decode(encrypted_value, 'base64'), 'UTF8'), 20) || '...' as key_preview
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 6. 최종 카운트
SELECT
  '✅ 정리 완료' as status,
  COUNT(*) as total_keys,
  COUNT(CASE WHEN key_type = 'app_key' THEN 1 END) as app_keys,
  COUNT(CASE WHEN key_type = 'app_secret' THEN 1 END) as app_secrets,
  COUNT(CASE WHEN key_type = 'account_number' THEN 1 END) as account_numbers
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom';
