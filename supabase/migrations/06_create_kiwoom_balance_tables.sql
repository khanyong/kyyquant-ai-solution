-- 키움 API 연동을 위한 계좌 잔고 및 포트폴리오 테이블 생성
-- Edge Function: sync-kiwoom-balance가 사용하는 테이블

-- 1. 키움 계좌 잔고 테이블
CREATE TABLE IF NOT EXISTS kw_account_balance (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  account_number VARCHAR(20) NOT NULL,

  -- 현금 관련
  total_cash BIGINT DEFAULT 0,              -- 예수금 총액
  available_cash BIGINT DEFAULT 0,          -- 출금가능금액
  order_cash BIGINT DEFAULT 0,              -- 주문가능현금
  deposit BIGINT DEFAULT 0,                 -- 예수금
  substitute_money BIGINT DEFAULT 0,        -- 대용금

  -- 자산 관련
  total_asset BIGINT DEFAULT 0,             -- 총 자산 (현금 + 주식평가액)
  stock_value BIGINT DEFAULT 0,             -- 주식 평가액
  profit_loss BIGINT DEFAULT 0,             -- 평가손익
  profit_loss_rate DECIMAL(10, 4) DEFAULT 0,-- 평가손익률

  -- 메타데이터
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- 제약 조건: 사용자당 계좌번호는 유니크
  CONSTRAINT uq_kw_account_balance_user_account UNIQUE (user_id, account_number)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_kw_account_balance_user ON kw_account_balance(user_id);
CREATE INDEX IF NOT EXISTS idx_kw_account_balance_account ON kw_account_balance(account_number);

-- RLS 활성화
ALTER TABLE kw_account_balance ENABLE ROW LEVEL SECURITY;

-- RLS 정책
DROP POLICY IF EXISTS "Users can view own account balance" ON kw_account_balance;
CREATE POLICY "Users can view own account balance" ON kw_account_balance
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own account balance" ON kw_account_balance;
CREATE POLICY "Users can insert own account balance" ON kw_account_balance
  FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own account balance" ON kw_account_balance;
CREATE POLICY "Users can update own account balance" ON kw_account_balance
  FOR UPDATE USING (auth.uid() = user_id);

-- Service role은 모든 권한
DROP POLICY IF EXISTS "Service role full access on account balance" ON kw_account_balance;
CREATE POLICY "Service role full access on account balance" ON kw_account_balance
  FOR ALL USING (auth.role() = 'service_role');

-- 2. 키움 포트폴리오 테이블 (보유 종목)
CREATE TABLE IF NOT EXISTS kw_portfolio (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  account_number VARCHAR(20) NOT NULL,

  -- 종목 정보
  stock_code VARCHAR(20) NOT NULL,
  stock_name VARCHAR(100),

  -- 수량 정보
  quantity INTEGER NOT NULL DEFAULT 0,
  available_quantity INTEGER NOT NULL DEFAULT 0,

  -- 가격 정보
  avg_price DECIMAL(15, 2) NOT NULL DEFAULT 0,
  current_price DECIMAL(15, 2) NOT NULL DEFAULT 0,

  -- 평가 정보
  purchase_amount BIGINT DEFAULT 0,        -- 매입금액
  evaluated_amount BIGINT DEFAULT 0,       -- 평가금액
  profit_loss BIGINT DEFAULT 0,            -- 평가손익
  profit_loss_rate DECIMAL(10, 4) DEFAULT 0,-- 수익률

  -- 메타데이터
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- 제약 조건: 사용자당 계좌번호+종목코드는 유니크
  CONSTRAINT uq_kw_portfolio_user_account_stock UNIQUE (user_id, account_number, stock_code)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_kw_portfolio_user ON kw_portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_kw_portfolio_account ON kw_portfolio(account_number);
CREATE INDEX IF NOT EXISTS idx_kw_portfolio_stock ON kw_portfolio(stock_code);
CREATE INDEX IF NOT EXISTS idx_kw_portfolio_user_account ON kw_portfolio(user_id, account_number);

-- RLS 활성화
ALTER TABLE kw_portfolio ENABLE ROW LEVEL SECURITY;

-- RLS 정책
DROP POLICY IF EXISTS "Users can view own portfolio" ON kw_portfolio;
CREATE POLICY "Users can view own portfolio" ON kw_portfolio
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own portfolio" ON kw_portfolio;
CREATE POLICY "Users can insert own portfolio" ON kw_portfolio
  FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own portfolio" ON kw_portfolio;
CREATE POLICY "Users can update own portfolio" ON kw_portfolio
  FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own portfolio" ON kw_portfolio;
CREATE POLICY "Users can delete own portfolio" ON kw_portfolio
  FOR DELETE USING (auth.uid() = user_id);

-- Service role은 모든 권한
DROP POLICY IF EXISTS "Service role full access on portfolio" ON kw_portfolio;
CREATE POLICY "Service role full access on portfolio" ON kw_portfolio
  FOR ALL USING (auth.role() = 'service_role');

-- Realtime 구독 활성화
ALTER PUBLICATION supabase_realtime ADD TABLE kw_account_balance;
ALTER PUBLICATION supabase_realtime ADD TABLE kw_portfolio;

-- 주석
COMMENT ON TABLE kw_account_balance IS '키움 API로 동기화되는 계좌 잔고 정보';
COMMENT ON TABLE kw_portfolio IS '키움 API로 동기화되는 보유 종목 정보';
COMMENT ON COLUMN kw_account_balance.total_cash IS '예수금 총액 (dnca_tot_amt)';
COMMENT ON COLUMN kw_account_balance.available_cash IS '출금가능금액 (nxdy_excc_amt)';
COMMENT ON COLUMN kw_account_balance.order_cash IS '주문가능현금 (ord_psbl_cash)';
COMMENT ON COLUMN kw_portfolio.stock_code IS '종목코드 (pdno)';
COMMENT ON COLUMN kw_portfolio.quantity IS '보유수량 (hldg_qty)';
COMMENT ON COLUMN kw_portfolio.avg_price IS '매입평균가격 (pchs_avg_pric)';
