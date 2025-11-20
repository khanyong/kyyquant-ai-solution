-- 키움 API 설정 확인 및 직접 테스트

-- 1. 현재 설정 확인
SELECT
  '프로필 정보' as check_type,
  id as user_id,
  email,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = auth.uid();

-- 2. API 키 확인
SELECT
  'API 키' as check_type,
  key_type,
  is_active,
  is_test_mode,
  LENGTH(encrypted_value) as key_length,
  created_at
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 3. 계좌번호 형식 확인
SELECT
  '계좌번호 분석' as check_type,
  kiwoom_account as full_account,
  SPLIT_PART(kiwoom_account, '-', 1) as account_prefix,
  SPLIT_PART(kiwoom_account, '-', 2) as account_suffix,
  LENGTH(SPLIT_PART(kiwoom_account, '-', 1)) as prefix_length,
  LENGTH(SPLIT_PART(kiwoom_account, '-', 2)) as suffix_length
FROM profiles
WHERE id = auth.uid();

-- 예상 결과:
-- account_prefix = '8112' (4자리)
-- account_suffix = '5100' (4자리)
-- 만약 다르면 계좌번호 형식 문제
