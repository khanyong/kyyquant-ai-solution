-- 현재 UI에 표시된 데이터의 출처 확인
-- 실행: Supabase SQL Editor

-- 1. kw_account_balance 테이블의 실제 데이터
SELECT
  '=== DB에 저장된 실제 데이터 ===' as section,
  user_id,
  account_number,
  total_cash,
  available_cash,
  order_cash,
  deposit,
  substitute_money,
  stock_value,
  total_asset,
  profit_loss,
  profit_loss_rate,
  updated_at,
  created_at,
  EXTRACT(EPOCH FROM (NOW() - updated_at)) / 60 as minutes_since_last_sync
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC;

-- 2. 이 데이터가 키움 API에서 온 것인지 확인
-- created_at과 updated_at 비교로 확인
SELECT
  '=== 데이터 동기화 이력 ===' as section,
  account_number,
  created_at as first_sync,
  updated_at as last_sync,
  CASE
    WHEN created_at = updated_at THEN '처음 동기화된 데이터 (1회만)'
    WHEN updated_at > created_at THEN '업데이트됨 (여러 번 동기화)'
    ELSE '알 수 없음'
  END as sync_status,
  CASE
    WHEN total_cash = 9782702 THEN '✅ 키움 API 응답과 일치 (prsm_dpst_aset_amt: 000000009782702)'
    ELSE '❌ 불일치'
  END as api_match
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 3. Edge Function 로그에서 확인한 키움 API 응답
-- 로그: "prsm_dpst_aset_amt":"000000009782702"
-- 이것이 total_cash로 저장되었는지 확인
SELECT
  '=== 키움 API → DB 매핑 확인 ===' as section,
  '키움 API 응답: prsm_dpst_aset_amt = 000000009782702' as kiwoom_api,
  'DB 저장: total_cash = ' || total_cash as db_stored,
  CASE
    WHEN total_cash = 9782702 THEN '✅ 정확히 매핑됨 (API에서 가져온 실제 데이터)'
    ELSE '❌ 매핑 오류'
  END as verification
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
