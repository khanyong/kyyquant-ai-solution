-- API 키 값 확인 (디코딩)
SELECT
  id,
  user_id,
  provider,
  key_type,
  key_name,
  is_test_mode,
  is_active,
  -- Base64 디코딩해서 실제 값 확인
  convert_from(decode(encrypted_value, 'base64'), 'UTF8') as decrypted_value,
  created_at
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
  AND key_type IN ('app_key', 'app_secret')
ORDER BY key_type;

-- 예상 값과 비교
SELECT
  'Expected App Key' as type,
  'S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU' as expected_value;

SELECT
  'Expected Secret Key' as type,
  'tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA' as expected_value;
