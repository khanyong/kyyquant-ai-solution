-- auth.uid() 작동 확인

-- 1. auth.uid() 값 확인
SELECT auth.uid() as current_user_id;

-- 2. 하드코딩된 user_id로 조회 (이건 작동함)
SELECT
  'user_id 직접 지정' as test_type,
  key_type,
  is_active,
  is_test_mode
FROM user_api_keys
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 3. auth.uid()로 조회 (이게 안 되는 것)
SELECT
  'auth.uid() 사용' as test_type,
  key_type,
  is_active,
  is_test_mode
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 4. auth.uid()가 NULL인지 확인
SELECT
  CASE
    WHEN auth.uid() IS NULL THEN '❌ auth.uid()가 NULL입니다'
    ELSE '✅ auth.uid() 정상: ' || auth.uid()::text
  END as auth_status;
