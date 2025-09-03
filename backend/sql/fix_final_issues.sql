-- 1. 테스트 user 생성 (profiles 테이블에)
-- profiles 테이블에 추가 (정확한 컬럼명 사용)
INSERT INTO profiles (id, email, name, kiwoom_account, is_approved, created_at)
VALUES ('2ca318c1-34d6-4e6b-b16c-3be494cd0048', 'demo@example.com', 'Demo User', 'DEMO001', true, now())
ON CONFLICT (id) DO NOTHING;

-- 2. account_balance 테이블에 누락된 컬럼 추가
ALTER TABLE account_balance 
ADD COLUMN IF NOT EXISTS stock_value DECIMAL(15,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS cash_balance DECIMAL(15,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS receivable_amount DECIMAL(15,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS invested_amount DECIMAL(15,2) DEFAULT 0;