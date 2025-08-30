-- Step 2: 의존성이 있는 테이블 생성

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
    user_id UUID NOT NULL,
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
    user_id UUID NOT NULL,
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
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(20) CHECK (type IN ('TECHNICAL', 'FUNDAMENTAL', 'HYBRID')),
    config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Backtest results table (백테스트 결과)
CREATE TABLE IF NOT EXISTS backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
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
    user_id UUID NOT NULL,
    total_assets DECIMAL(15, 2) NOT NULL,
    available_cash DECIMAL(15, 2) NOT NULL,
    total_evaluation DECIMAL(15, 2) NOT NULL,
    total_profit_loss DECIMAL(15, 2),
    total_profit_loss_rate DECIMAL(5, 2),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
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