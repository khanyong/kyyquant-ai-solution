-- 계좌 동기화 문제 진단
-- 실행: Supabase SQL Editor

-- 1. 현재 로그인한 사용자 ID 확인
SELECT
  '=== 현재 사용자 정보 ===' as section,
  auth.uid() as user_id,
  email
FROM auth.users
WHERE id = auth.uid();

-- 2. kw_account_balance 테이블 확인
SELECT
  '=== 계좌 잔고 데이터 ===' as section,
  user_id,
  account_number,
  total_cash,
  available_cash,
  stock_value,
  total_asset,
  profit_loss,
  profit_loss_rate,
  updated_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_update
FROM kw_account_balance
ORDER BY updated_at DESC
LIMIT 5;

-- 3. kw_portfolio 테이블 확인
SELECT
  '=== 보유 종목 데이터 ===' as section,
  user_id,
  account_number,
  stock_code,
  quantity,
  avg_price,
  current_price,
  updated_at
FROM kw_portfolio
ORDER BY updated_at DESC
LIMIT 5;

-- 4. profiles 테이블에서 키움 계좌 정보 확인
SELECT
  '=== 프로필 계좌 정보 ===' as section,
  id as user_id,
  kiwoom_account,
  created_at
FROM profiles
WHERE id = auth.uid();

-- 5. user_api_keys 테이블에서 API 키 확인
SELECT
  '=== API 키 설정 ===' as section,
  user_id,
  provider,
  key_type,
  is_active,
  is_test_mode,
  LENGTH(encrypted_value) as key_length
FROM user_api_keys
WHERE user_id = auth.uid()
  AND provider = 'kiwoom'
ORDER BY key_type;

-- 6. 최근 Edge Function 로그 확인 (있다면)
-- Edge Function 로그는 Supabase Dashboard > Edge Functions > Logs에서 확인

-- 진단 요약
SELECT
  '=== 진단 요약 ===' as section,
  CASE
    WHEN EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND kiwoom_account IS NOT NULL)
      THEN '✅ 키움 계좌 설정됨'
    ELSE '❌ 키움 계좌 미설정'
  END as profile_status,
  CASE
    WHEN EXISTS (SELECT 1 FROM user_api_keys WHERE user_id = auth.uid() AND provider = 'kiwoom' AND is_active = true)
      THEN '✅ API 키 활성화'
    ELSE '❌ API 키 미설정'
  END as api_key_status,
  CASE
    WHEN EXISTS (SELECT 1 FROM kw_account_balance WHERE user_id = auth.uid())
      THEN '✅ 계좌 잔고 데이터 존재'
    ELSE '❌ 계좌 잔고 데이터 없음'
  END as balance_status;
