-- Supabase에서는 auth.users를 사용하므로 별도 users 테이블 대신 profiles 테이블 생성
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    kiwoom_account VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Stocks table (종목 마스터)
CREATE TABLE IF NOT EXISTS stocks (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    market VARCHAR(20) CHECK (market IN ('KOSPI', 'KOSDAQ', 'KONEX')),
    sector VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Price data table (일별 가격 데이터)
CREATE TABLE IF NOT EXISTS price_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_code VARCHAR(20) REFERENCES stocks(code),
    date DATE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    trading_value BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, date)
);

-- Realtime prices table (실시간 가격)
CREATE TABLE IF NOT EXISTS realtime_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_code VARCHAR(20) REFERENCES stocks(code),
    current_price DECIMAL(10, 2) NOT NULL,
    change_rate DECIMAL(5, 2) NOT NULL,
    volume BIGINT NOT NULL,
    bid_price DECIMAL(10, 2),
    ask_price DECIMAL(10, 2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code)
);

-- Orders table (주문)
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) REFERENCES stocks(code),
    order_type VARCHAR(10) CHECK (order_type IN ('BUY', 'SELL')),
    order_status VARCHAR(20) CHECK (order_status IN ('PENDING', 'EXECUTED', 'CANCELLED', 'PARTIAL')),
    order_price DECIMAL(10, 2) NOT NULL,
    order_quantity INTEGER NOT NULL,
    executed_price DECIMAL(10, 2),
    executed_quantity INTEGER,
    kiwoom_order_no VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio table (포트폴리오)
CREATE TABLE IF NOT EXISTS portfolio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) REFERENCES stocks(code),
    quantity INTEGER NOT NULL,
    avg_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2),
    profit_loss DECIMAL(12, 2),
    profit_loss_rate DECIMAL(5, 2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, stock_code)
);

-- Strategies table (전략)
CREATE TABLE IF NOT EXISTS strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(20) CHECK (type IN ('TECHNICAL', 'FUNDAMENTAL', 'HYBRID')),
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Backtest results table (백테스트 결과)
CREATE TABLE IF NOT EXISTS backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15, 2) NOT NULL,
    final_capital DECIMAL(15, 2) NOT NULL,
    total_return DECIMAL(10, 4) NOT NULL,
    max_drawdown DECIMAL(10, 4) NOT NULL,
    sharpe_ratio DECIMAL(10, 4),
    win_rate DECIMAL(5, 2),
    total_trades INTEGER NOT NULL,
    profitable_trades INTEGER NOT NULL,
    results_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trading signals table (거래 신호)
CREATE TABLE IF NOT EXISTS trading_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
    stock_code VARCHAR(20) REFERENCES stocks(code),
    signal_type VARCHAR(10) CHECK (signal_type IN ('BUY', 'SELL', 'HOLD')),
    signal_strength DECIMAL(5, 2) CHECK (signal_strength >= 0 AND signal_strength <= 100),
    price DECIMAL(10, 2) NOT NULL,
    indicators JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Account balance table (계좌 잔고)
CREATE TABLE IF NOT EXISTS account_balance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    total_assets DECIMAL(15, 2) NOT NULL,
    available_cash DECIMAL(15, 2) NOT NULL,
    total_evaluation DECIMAL(15, 2) NOT NULL,
    total_profit_loss DECIMAL(15, 2),
    total_profit_loss_rate DECIMAL(5, 2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Market index table (시장 지수)
CREATE TABLE IF NOT EXISTS market_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    index_code VARCHAR(20) NOT NULL,
    index_name VARCHAR(100) NOT NULL,
    current_value DECIMAL(10, 2) NOT NULL,
    change_value DECIMAL(10, 2),
    change_rate DECIMAL(5, 2),
    trading_volume BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_code)
);

-- News alerts table (뉴스/공시)
CREATE TABLE IF NOT EXISTS news_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_code VARCHAR(20) REFERENCES stocks(code),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    source VARCHAR(100),
    url TEXT,
    sentiment VARCHAR(20) CHECK (sentiment IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')),
    importance VARCHAR(10) CHECK (importance IN ('HIGH', 'MEDIUM', 'LOW')),
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_price_data_stock_date ON price_data(stock_code, date DESC);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_active ON strategies(is_active);
CREATE INDEX IF NOT EXISTS idx_backtest_results_strategy ON backtest_results(strategy_id);
CREATE INDEX IF NOT EXISTS idx_trading_signals_strategy ON trading_signals(strategy_id);
CREATE INDEX IF NOT EXISTS idx_trading_signals_timestamp ON trading_signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_news_alerts_stock ON news_alerts(stock_code);
CREATE INDEX IF NOT EXISTS idx_news_alerts_published ON news_alerts(published_at DESC);

-- Row Level Security (RLS) policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_balance ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Orders policies
CREATE POLICY "Users can view own orders" ON orders
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own orders" ON orders
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own orders" ON orders
    FOR UPDATE USING (auth.uid() = user_id);

-- Portfolio policies
CREATE POLICY "Users can view own portfolio" ON portfolio
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own portfolio" ON portfolio
    FOR ALL USING (auth.uid() = user_id);

-- Strategies policies
CREATE POLICY "Users can manage own strategies" ON strategies
    FOR ALL USING (auth.uid() = user_id);

-- Backtest results policies
CREATE POLICY "Users can view own backtest results" ON backtest_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own backtest results" ON backtest_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Account balance policies
CREATE POLICY "Users can view own balance" ON account_balance
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own balance" ON account_balance
    FOR ALL USING (auth.uid() = user_id);

-- Public read access for market data (no RLS needed)
-- stocks, price_data, realtime_prices, market_index, news_alerts are public

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stocks_updated_at BEFORE UPDATE ON stocks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolio_updated_at BEFORE UPDATE ON portfolio
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_account_balance_updated_at BEFORE UPDATE ON account_balance
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, name)
  VALUES (new.id, new.email, new.raw_user_meta_data->>'name');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on auth.users insert
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();