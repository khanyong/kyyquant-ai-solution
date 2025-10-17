-- 계좌 잔고 및 보유 자산 테이블 생성

-- 1. 계좌 잔고 테이블 (현금 잔고)
CREATE TABLE IF NOT EXISTS kw_account_balance (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  account_number varchar(50) NOT NULL,

  -- 잔고 정보
  total_cash bigint DEFAULT 0,              -- 총 현금
  available_cash bigint DEFAULT 0,          -- 출금 가능 금액
  order_cash bigint DEFAULT 0,              -- 주문 가능 금액
  deposit bigint DEFAULT 0,                 -- 예수금
  substitute_money bigint DEFAULT 0,        -- 대용금

  -- 평가 정보
  total_asset bigint DEFAULT 0,             -- 총 자산 (현금 + 주식평가액)
  stock_value bigint DEFAULT 0,             -- 보유 주식 평가액
  profit_loss bigint DEFAULT 0,             -- 평가손익
  profit_loss_rate decimal(10, 4) DEFAULT 0, -- 수익률

  -- 메타 정보
  updated_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),

  -- 계좌당 최신 레코드만 유지 (사용자당 하나의 계좌만 가정)
  UNIQUE(user_id, account_number)
);

-- 2. 보유 주식 테이블
CREATE TABLE IF NOT EXISTS kw_portfolio (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  account_number varchar(50) NOT NULL,

  -- 종목 정보
  stock_code varchar(20) NOT NULL,
  stock_name varchar(100),

  -- 보유 정보
  quantity integer NOT NULL,                -- 보유 수량
  available_quantity integer DEFAULT 0,     -- 매도 가능 수량
  avg_price decimal(15, 2) NOT NULL,        -- 평균 매입가
  purchase_amount bigint NOT NULL,          -- 매입 금액

  -- 평가 정보
  current_price decimal(15, 2),             -- 현재가
  evaluated_amount bigint,                  -- 평가 금액
  profit_loss bigint,                       -- 평가손익
  profit_loss_rate decimal(10, 4),          -- 수익률

  -- 메타 정보
  updated_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),

  -- 계좌당 종목 하나만 (중복 방지)
  UNIQUE(user_id, account_number, stock_code),

  -- 제약 조건
  CONSTRAINT kw_portfolio_quantity_positive CHECK (quantity > 0),
  CONSTRAINT kw_portfolio_stock_code_check CHECK (char_length(stock_code) > 0)
);

-- 3. 거래 내역 테이블
CREATE TABLE IF NOT EXISTS kw_transaction_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  account_number varchar(50) NOT NULL,

  -- 거래 정보
  stock_code varchar(20) NOT NULL,
  stock_name varchar(100),
  transaction_type varchar(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),

  -- 거래 상세
  quantity integer NOT NULL,
  price decimal(15, 2) NOT NULL,
  total_amount bigint NOT NULL,
  fee bigint DEFAULT 0,
  tax bigint DEFAULT 0,

  -- 주문 정보
  order_id varchar(50),
  order_status varchar(20) DEFAULT 'COMPLETED',

  -- 메타 정보
  executed_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),

  -- 인덱스
  CONSTRAINT kw_transaction_quantity_positive CHECK (quantity > 0)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_account_balance_user ON kw_account_balance(user_id);
CREATE INDEX IF NOT EXISTS idx_account_balance_account ON kw_account_balance(account_number);
CREATE INDEX IF NOT EXISTS idx_account_balance_updated ON kw_account_balance(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_portfolio_user ON kw_portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_account ON kw_portfolio(account_number);
CREATE INDEX IF NOT EXISTS idx_portfolio_stock ON kw_portfolio(stock_code);
CREATE INDEX IF NOT EXISTS idx_portfolio_updated ON kw_portfolio(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_transaction_user ON kw_transaction_history(user_id);
CREATE INDEX IF NOT EXISTS idx_transaction_account ON kw_transaction_history(account_number);
CREATE INDEX IF NOT EXISTS idx_transaction_executed ON kw_transaction_history(executed_at DESC);

-- RLS (Row Level Security) 활성화
ALTER TABLE kw_account_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE kw_portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE kw_transaction_history ENABLE ROW LEVEL SECURITY;

-- RLS 정책: 사용자는 자신의 데이터만 조회/수정 가능
DROP POLICY IF EXISTS "Users can view their own balance" ON kw_account_balance;
CREATE POLICY "Users can view their own balance"
  ON kw_account_balance FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own balance" ON kw_account_balance;
CREATE POLICY "Users can update their own balance"
  ON kw_account_balance FOR ALL
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view their own portfolio" ON kw_portfolio;
CREATE POLICY "Users can view their own portfolio"
  ON kw_portfolio FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update their own portfolio" ON kw_portfolio;
CREATE POLICY "Users can update their own portfolio"
  ON kw_portfolio FOR ALL
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view their own transactions" ON kw_transaction_history;
CREATE POLICY "Users can view their own transactions"
  ON kw_transaction_history FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own transactions" ON kw_transaction_history;
CREATE POLICY "Users can insert their own transactions"
  ON kw_transaction_history FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON kw_account_balance TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON kw_portfolio TO authenticated;
GRANT SELECT, INSERT ON kw_transaction_history TO authenticated;

-- 샘플 데이터 삽입 함수
CREATE OR REPLACE FUNCTION insert_sample_account_data(p_user_id uuid, p_account_number varchar)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- 계좌 잔고 샘플 데이터
  INSERT INTO kw_account_balance (
    user_id, account_number, total_cash, available_cash, order_cash,
    total_asset, stock_value, profit_loss, profit_loss_rate
  ) VALUES (
    p_user_id, p_account_number,
    50000000,  -- 5천만원 현금
    45000000,  -- 4천5백만원 출금가능
    45000000,  -- 4천5백만원 주문가능
    80000000,  -- 8천만원 총자산
    30000000,  -- 3천만원 주식평가액
    5000000,   -- 5백만원 평가손익
    6.67       -- 6.67% 수익률
  )
  ON CONFLICT (user_id, account_number)
  DO UPDATE SET
    total_cash = EXCLUDED.total_cash,
    available_cash = EXCLUDED.available_cash,
    order_cash = EXCLUDED.order_cash,
    total_asset = EXCLUDED.total_asset,
    stock_value = EXCLUDED.stock_value,
    profit_loss = EXCLUDED.profit_loss,
    profit_loss_rate = EXCLUDED.profit_loss_rate,
    updated_at = now();

  -- 보유 주식 샘플 데이터
  INSERT INTO kw_portfolio (
    user_id, account_number, stock_code, stock_name,
    quantity, available_quantity, avg_price, purchase_amount,
    current_price, evaluated_amount, profit_loss, profit_loss_rate
  ) VALUES
  (
    p_user_id, p_account_number, '005930', '삼성전자',
    100, 100, 70000, 7000000,
    75000, 7500000, 500000, 7.14
  ),
  (
    p_user_id, p_account_number, '000660', 'SK하이닉스',
    50, 50, 130000, 6500000,
    140000, 7000000, 500000, 7.69
  ),
  (
    p_user_id, p_account_number, '035720', '카카오',
    80, 80, 50000, 4000000,
    48000, 3840000, -160000, -4.00
  )
  ON CONFLICT (user_id, account_number, stock_code)
  DO UPDATE SET
    quantity = EXCLUDED.quantity,
    available_quantity = EXCLUDED.available_quantity,
    current_price = EXCLUDED.current_price,
    evaluated_amount = EXCLUDED.evaluated_amount,
    profit_loss = EXCLUDED.profit_loss,
    profit_loss_rate = EXCLUDED.profit_loss_rate,
    updated_at = now();
END;
$$;

-- 사용 방법:
-- SELECT insert_sample_account_data(auth.uid(), '본인계좌번호');
