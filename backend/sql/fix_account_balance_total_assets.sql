-- account_balance 테이블의 total_assets 컬럼 설정
-- NOT NULL 제약 조건 제거 또는 기본값 설정
ALTER TABLE account_balance 
ALTER COLUMN total_assets SET DEFAULT 0;

-- 또는 컬럼이 없다면 추가
ALTER TABLE account_balance 
ADD COLUMN IF NOT EXISTS total_assets DECIMAL(15,2) DEFAULT 0;