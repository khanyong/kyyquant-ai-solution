-- 최종 저장된 키 값 확인

SELECT
  key_type,
  key_name,
  is_test_mode,
  -- 전체 키 값 디코딩
  convert_from(decode(encrypted_value, 'base64'), 'UTF8') as actual_key_value,
  created_at
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
  AND key_type IN ('app_key', 'app_secret')
ORDER BY key_type;

-- 예상 값과 비교
SELECT 'Expected' as source, 'app_key' as key_type, 'S0FEQ8I3UYwgcEPepJrfO6NteTCziz4540NljbYIASU' as expected_value
UNION ALL
SELECT 'Expected' as source, 'app_secret' as key_type, 'tBh2TG4i0nwvKMC5s_DCVSlnWec3pgvLEmxIqL2RDsA' as expected_value;
