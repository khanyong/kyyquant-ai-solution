-- account_balance 테이블에 누락된 컬럼 추가
ALTER TABLE account_balance 
ADD COLUMN IF NOT EXISTS cash_balance DECIMAL(15,2),
ADD COLUMN IF NOT EXISTS receivable_amount DECIMAL(15,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS invested_amount DECIMAL(15,2) DEFAULT 0;