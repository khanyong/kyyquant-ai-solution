-- account_balance 테이블 구조 확인
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'account_balance'
ORDER BY ordinal_position;