-- kw_account_balance 테이블 구조 확인
SELECT
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name = 'kw_account_balance'
ORDER BY ordinal_position;

-- kw_portfolio 테이블 구조 확인
SELECT
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns
WHERE table_name = 'kw_portfolio'
ORDER BY ordinal_position;

-- 실제 데이터 확인
SELECT * FROM kw_account_balance LIMIT 5;
SELECT * FROM kw_portfolio LIMIT 5;
