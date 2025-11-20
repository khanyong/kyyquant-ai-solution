-- 키움 API 키 수정 및 등록

-- ========================================
-- 1. 현재 사용자 ID 확인
-- ========================================
SELECT auth.uid() as current_user_id;

-- ========================================
-- 2. 현재 사용자의 기존 키움 키 확인
-- ========================================
SELECT
  id,
  user_id,
  provider,
  key_type,
  is_active,
  created_at
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'  -- 본인 user_id
  AND provider = 'kiwoom'
ORDER BY key_type;

-- ========================================
-- 3. 기존 키움 키 삭제 (본인 것만)
-- ========================================
DELETE FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'  -- 본인 user_id
  AND provider = 'kiwoom';

-- ========================================
-- 4. 새 API 키 등록
-- ========================================
INSERT INTO user_api_keys (
  user_id,
  provider,
  key_type,
  encrypted_value,
  is_test_mode,
  is_active
) VALUES
  -- App Key
  (
    'f912da32-897f-4dbb-9242-3a438e9733a8',  -- 본인 user_id
    'kiwoom',
    'app_key',
    encode('S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'::bytea, 'base64'),
    true,  -- 모의투자
    true
  ),
  -- App Secret
  (
    'f912da32-897f-4dbb-9242-3a438e9733a8',  -- 본인 user_id
    'kiwoom',
    'app_secret',
    encode('tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'::bytea, 'base64'),
    true,  -- 모의투자
    true
  );

-- ========================================
-- 5. 등록 확인
-- ========================================
SELECT
  '✅ API 키 등록 완료' as status,
  id,
  user_id,
  provider,
  key_type,
  is_active,
  is_test_mode,
  LENGTH(encrypted_value) as key_length,
  created_at
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'  -- 본인 user_id
  AND provider = 'kiwoom'
ORDER BY key_type;

-- ========================================
-- 6. auth.uid()로도 조회 테스트
-- ========================================
SELECT
  '✅ auth.uid() 조회 테스트' as status,
  key_type,
  is_active,
  is_test_mode
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;
