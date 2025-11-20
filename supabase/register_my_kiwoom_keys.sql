-- 키움 API 키 등록 (2025-10-05 ~ 2026-01-05)

-- 1. 기존 키 삭제 (있다면)
DELETE FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom';

-- 2. 새 API 키 등록
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
    encode('S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'::bytea, 'base64'),
    true,  -- 모의투자
    true,
    NOW(),
    NOW()
  ),
  -- App Secret
  (
    auth.uid(),
    'kiwoom',
    'app_secret',
    encode('tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'::bytea, 'base64'),
    true,  -- 모의투자
    true,
    NOW(),
    NOW()
  );

-- 3. 등록 확인
SELECT
  '✅ API 키 등록 완료' as status,
  key_type,
  is_active,
  is_test_mode,
  LENGTH(encrypted_value) as key_length,
  created_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 4. 프로필 확인 (계좌번호도 함께 확인)
SELECT
  '✅ 프로필 확인' as status,
  email,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = auth.uid();
