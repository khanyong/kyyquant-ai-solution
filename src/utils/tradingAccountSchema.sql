-- 사용자 거래 계좌 테이블
CREATE TABLE IF NOT EXISTS user_trading_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  account_type VARCHAR(20) CHECK (account_type IN ('mock', 'real')),
  account_number VARCHAR(20) NOT NULL,
  account_name VARCHAR(100),
  broker VARCHAR(20) DEFAULT 'kiwoom',
  
  -- OAuth 인증 정보
  access_token TEXT,
  refresh_token TEXT,
  token_expires_at TIMESTAMP WITH TIME ZONE,
  
  -- 계좌 상태
  is_active BOOLEAN DEFAULT false,
  is_connected BOOLEAN DEFAULT false,
  is_default BOOLEAN DEFAULT false,
  last_sync_at TIMESTAMP WITH TIME ZONE,
  
  -- 계좌 정보
  initial_balance DECIMAL(15, 2),
  current_balance DECIMAL(15, 2),
  available_balance DECIMAL(15, 2),
  total_profit DECIMAL(15, 2) DEFAULT 0,
  total_profit_rate DECIMAL(10, 2) DEFAULT 0,
  
  -- 거래 설정
  max_trade_amount DECIMAL(15, 2),
  max_position_size INTEGER DEFAULT 10,
  allow_auto_trading BOOLEAN DEFAULT false,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, account_number, broker)
);

-- 거래 세션 테이블
CREATE TABLE IF NOT EXISTS trading_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES user_trading_accounts(id) ON DELETE CASCADE,
  session_type VARCHAR(20) CHECK (session_type IN ('manual', 'auto')),
  strategy_id UUID REFERENCES strategies(id),
  
  -- 세션 상태
  status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'stopped', 'completed')),
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ended_at TIMESTAMP WITH TIME ZONE,
  
  -- 세션 통계
  total_trades INTEGER DEFAULT 0,
  profitable_trades INTEGER DEFAULT 0,
  total_profit DECIMAL(15, 2) DEFAULT 0,
  max_drawdown DECIMAL(10, 2) DEFAULT 0,
  win_rate DECIMAL(5, 2) DEFAULT 0,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 실시간 주문 테이블
CREATE TABLE IF NOT EXISTS trading_orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES user_trading_accounts(id) ON DELETE CASCADE,
  session_id UUID REFERENCES trading_sessions(id),
  
  -- 주문 정보
  order_id VARCHAR(50) UNIQUE, -- 키움 주문번호
  symbol VARCHAR(20) NOT NULL,
  symbol_name VARCHAR(100),
  order_type VARCHAR(20) CHECK (order_type IN ('market', 'limit')),
  side VARCHAR(10) CHECK (side IN ('buy', 'sell')),
  
  -- 수량 및 가격
  quantity INTEGER NOT NULL,
  price DECIMAL(15, 2),
  executed_quantity INTEGER DEFAULT 0,
  executed_price DECIMAL(15, 2),
  
  -- 주문 상태
  status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN ('pending', 'submitted', 'partial', 'filled', 'cancelled', 'rejected')
  ),
  
  -- 시간 정보
  submitted_at TIMESTAMP WITH TIME ZONE,
  executed_at TIMESTAMP WITH TIME ZONE,
  cancelled_at TIMESTAMP WITH TIME ZONE,
  
  -- 메타 정보
  reason TEXT,
  error_message TEXT,
  metadata JSONB,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 실시간 포지션 테이블
CREATE TABLE IF NOT EXISTS trading_positions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES user_trading_accounts(id) ON DELETE CASCADE,
  session_id UUID REFERENCES trading_sessions(id),
  
  -- 종목 정보
  symbol VARCHAR(20) NOT NULL,
  symbol_name VARCHAR(100),
  
  -- 포지션 정보
  quantity INTEGER NOT NULL,
  avg_price DECIMAL(15, 2) NOT NULL,
  current_price DECIMAL(15, 2),
  
  -- 손익 정보
  unrealized_pnl DECIMAL(15, 2),
  unrealized_pnl_rate DECIMAL(10, 2),
  realized_pnl DECIMAL(15, 2),
  
  -- 상태
  status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closing', 'closed')),
  
  opened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  closed_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(account_id, symbol, status)
);

-- 계좌 활동 로그
CREATE TABLE IF NOT EXISTS account_activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES user_trading_accounts(id) ON DELETE CASCADE,
  activity_type VARCHAR(50) NOT NULL,
  description TEXT,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS 정책 설정
ALTER TABLE user_trading_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_activity_logs ENABLE ROW LEVEL SECURITY;

-- 사용자는 자신의 계좌만 볼 수 있음
CREATE POLICY "Users can view own accounts" 
  ON user_trading_accounts FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own accounts" 
  ON user_trading_accounts FOR ALL 
  USING (auth.uid() = user_id);

-- 세션 정책
CREATE POLICY "Users can view own sessions" 
  ON trading_sessions FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM user_trading_accounts 
      WHERE id = trading_sessions.account_id 
      AND user_id = auth.uid()
    )
  );

-- 주문 정책
CREATE POLICY "Users can view own orders" 
  ON trading_orders FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM user_trading_accounts 
      WHERE id = trading_orders.account_id 
      AND user_id = auth.uid()
    )
  );

-- 포지션 정책
CREATE POLICY "Users can view own positions" 
  ON trading_positions FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM user_trading_accounts 
      WHERE id = trading_positions.account_id 
      AND user_id = auth.uid()
    )
  );

-- 활동 로그 정책
CREATE POLICY "Users can view own activity logs" 
  ON account_activity_logs FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM user_trading_accounts 
      WHERE id = account_activity_logs.account_id 
      AND user_id = auth.uid()
    )
  );

-- 인덱스 생성
CREATE INDEX idx_trading_accounts_user_id ON user_trading_accounts(user_id);
CREATE INDEX idx_trading_accounts_account_type ON user_trading_accounts(account_type);
CREATE INDEX idx_trading_sessions_account_id ON trading_sessions(account_id);
CREATE INDEX idx_trading_sessions_status ON trading_sessions(status);
CREATE INDEX idx_trading_orders_account_id ON trading_orders(account_id);
CREATE INDEX idx_trading_orders_status ON trading_orders(status);
CREATE INDEX idx_trading_orders_symbol ON trading_orders(symbol);
CREATE INDEX idx_trading_positions_account_id ON trading_positions(account_id);
CREATE INDEX idx_trading_positions_symbol ON trading_positions(symbol);
CREATE INDEX idx_trading_positions_status ON trading_positions(status);

-- 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_trading_accounts_updated_at
  BEFORE UPDATE ON user_trading_accounts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_trading_orders_updated_at
  BEFORE UPDATE ON trading_orders
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_trading_positions_updated_at
  BEFORE UPDATE ON trading_positions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();