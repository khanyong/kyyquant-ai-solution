-- ============================================================================
-- 키움 API 동기화 디버깅
-- ============================================================================

-- 1. 현재 등록된 API 키 확인
SELECT
  '=== 등록된 키움 API 키 ===' as section;

SELECT
  user_id,
  provider,
  key_type,
  is_test_mode,
  is_active,
  created_at
FROM user_api_keys
WHERE provider = 'kiwoom'
  AND is_active = true
ORDER BY created_at DESC;

-- 2. 최근 계좌 동기화 시도 로그 확인 (Edge Function 호출 여부)
-- Edge Function이 호출되었는지 확인하려면 Supabase Dashboard > Edge Functions > Logs 확인 필요

-- 3. 현재 계좌 정보
SELECT
  '=== 현재 계좌 정보 ===' as section;

SELECT
  account_number,
  total_cash,
  stock_value,
  total_asset,
  profit_loss,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_update
FROM kw_account_balance
ORDER BY updated_at DESC;

-- 4. API 키가 정상적으로 복호화되는지 테스트
-- (실제로는 Edge Function 내부에서 복호화됨)
SELECT
  '=== API 키 존재 여부 확인 ===' as section,
  COUNT(*) as total_keys,
  COUNT(CASE WHEN key_type = 'app_key' THEN 1 END) as app_key_count,
  COUNT(CASE WHEN key_type = 'app_secret' THEN 1 END) as app_secret_count
FROM user_api_keys
WHERE provider = 'kiwoom'
  AND is_active = true;
