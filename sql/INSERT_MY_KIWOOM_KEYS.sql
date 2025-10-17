-- 본인의 키움 모의투자 API 키 저장
-- 실행 전 로그인 필수!

-- 1. 현재 사용자 ID 확인
SELECT auth.uid() as current_user_id;

-- 2. 기존 키움 키 삭제 (선택사항)
DELETE FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom';

-- 3. App Key 저장
INSERT INTO user_api_keys (
  user_id,
  provider,
  key_type,
  key_name,
  encrypted_value,
  is_test_mode,
  is_active
) VALUES (
  auth.uid(),
  'kiwoom',
  'app_key',
  'Kiwoom App Key',
  encode('S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'::bytea, 'base64'),
  true,  -- 모의투자
  true
)
ON CONFLICT (user_id, provider, key_type, key_name)
DO UPDATE SET
  encrypted_value = encode('S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU'::bytea, 'base64'),
  is_test_mode = true,
  is_active = true,
  updated_at = NOW();

-- 4. Secret Key 저장
INSERT INTO user_api_keys (
  user_id,
  provider,
  key_type,
  key_name,
  encrypted_value,
  is_test_mode,
  is_active
) VALUES (
  auth.uid(),
  'kiwoom',
  'app_secret',
  'Kiwoom App Secret',
  encode('tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'::bytea, 'base64'),
  true,  -- 모의투자
  true
)
ON CONFLICT (user_id, provider, key_type, key_name)
DO UPDATE SET
  encrypted_value = encode('tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA'::bytea, 'base64'),
  is_test_mode = true,
  is_active = true,
  updated_at = NOW();

-- 5. 키 저장 확인
SELECT
  id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  created_at,
  updated_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 6. 계좌번호 확인 (아직 설정 안했다면 아래 실행)
SELECT kiwoom_account FROM profiles WHERE id = auth.uid();

-- 7. 계좌번호 설정 (본인 계좌번호로 수정 후 실행)
-- 형식: '계좌번호8자리-계좌상품코드2자리' 예: '81126100-01'
/*
UPDATE profiles
SET kiwoom_account = '본인계좌번호-01'  -- 본인 계좌번호로 수정!
WHERE id = auth.uid();
*/

-- 8. 최종 확인
SELECT
  'API Keys' as type,
  COUNT(*) as count
FROM user_api_keys
WHERE user_id = auth.uid() AND provider = 'kiwoom' AND is_active = true
UNION ALL
SELECT
  'Account Number' as type,
  CASE WHEN kiwoom_account IS NOT NULL THEN 1 ELSE 0 END as count
FROM profiles
WHERE id = auth.uid();
