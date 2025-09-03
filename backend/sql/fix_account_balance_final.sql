-- account_balance 테이블에 남은 누락된 컬럼 추가
ALTER TABLE account_balance 
ADD COLUMN IF NOT EXISTS total_buy_amount DECIMAL(15,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS available_cash DECIMAL(15,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_profit_loss DECIMAL(15,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_profit_loss_rate DECIMAL(5,2) DEFAULT 0;