-- 중복된 계좌 잔고 레코드 정리
-- 실행: Supabase SQL Editor

-- 1. 현재 상태 확인
SELECT
  '=== 삭제 전 ===' as section,
  user_id,
  account_number,
  total_cash,
  updated_at,
  id
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC;

-- 2. 오래된 레코드 삭제 (최신 것만 남기기)
DELETE FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
  AND account_number != '81126100';

-- 3. 삭제 후 확인
SELECT
  '=== 삭제 후 ===' as section,
  user_id,
  account_number,
  total_cash,
  updated_at,
  id
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
ORDER BY updated_at DESC;

-- 4. 최종 카운트
SELECT
  '=== 최종 확인 ===' as section,
  COUNT(*) as total_records,
  CASE
    WHEN COUNT(*) = 1 THEN '✅ .single() 사용 가능'
    ELSE '❌ 여전히 중복 존재'
  END as status
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
