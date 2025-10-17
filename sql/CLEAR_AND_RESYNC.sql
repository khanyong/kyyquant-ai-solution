-- 샘플 데이터 삭제 후 재동기화 준비

-- 1. 기존 데이터 모두 삭제
DELETE FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

DELETE FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';

-- 2. 삭제 확인
SELECT
  'kw_account_balance' as table_name,
  COUNT(*) as remaining_count
FROM kw_account_balance
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8'
UNION ALL
SELECT
  'kw_portfolio' as table_name,
  COUNT(*) as remaining_count
FROM kw_portfolio
WHERE user_id = 'f912da32-897f-4dbb-9242-3a438e9733a8';
