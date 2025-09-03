-- ====================================================================
-- 키움 OpenAPI 완전한 거래 시스템 스키마
-- 실시간 데이터 수집, 전략 실행, 주문 관리를 위한 전체 테이블 구조
-- ====================================================================

-- 1. 실시간 시장 데이터 (키움 API에서 받는 모든 데이터)
-- ====================================================================
CREATE TABLE IF NOT EXISTS market_data (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_code varchar(10) NOT NULL,
    stock_name varchar(100),
    
    -- 가격 정보
    current_price numeric NOT NULL,
    open_price numeric,
    high_price numeric,
    low_price numeric,
    close_price numeric,
    prev_close numeric,
    
    -- 거래량 정보
    volume bigint,
    accumulated_volume bigint,
    trading_value numeric,
    
    -- 변동 정보
    change_amount numeric,
    change_rate numeric(5,2),
    
    -- 호가 정보
    bid_price numeric,
    ask_price numeric,
    bid_volume bigint,
    ask_volume bigint,
    
    -- 시간 정보
    trading_date date,
    trading_time time,
    timestamp timestamp with time zone DEFAULT now()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_market_data_stock_time ON market_data(stock_code, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp DESC);

-- 2. 기술적 지표 데이터 (전략 실행에 필요)
-- ====================================================================
CREATE TABLE IF NOT EXISTS technical_indicators (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_code varchar(10) NOT NULL,
    timeframe varchar(10) NOT NULL, -- '1m', '5m', '15m', '1h', '1d'
    
    -- 이동평균
    ma5 numeric,
    ma10 numeric,
    ma20 numeric,
    ma60 numeric,
    ma120 numeric,
    
    -- 볼린저밴드
    bb_upper numeric,
    bb_middle numeric,
    bb_lower numeric,
    
    -- RSI
    rsi numeric(5,2),
    rsi_signal varchar(10), -- 'oversold', 'neutral', 'overbought'
    
    -- MACD
    macd numeric,
    macd_signal numeric,
    macd_histogram numeric,
    
    -- 스토캐스틱
    stochastic_k numeric(5,2),
    stochastic_d numeric(5,2),
    
    -- 거래량 지표
    obv numeric, -- On Balance Volume
    vwap numeric, -- Volume Weighted Average Price
    
    -- 기타 지표
    cci numeric, -- Commodity Channel Index
    atr numeric, -- Average True Range
    
    calculated_at timestamp with time zone DEFAULT now(),
    
    UNIQUE(stock_code, timeframe, calculated_at)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_indicators_stock_time ON technical_indicators(stock_code, timeframe, calculated_at DESC);

-- 3. 거래 신호 (개선된 버전)
-- ====================================================================
ALTER TABLE trading_signals 
ADD COLUMN IF NOT EXISTS signal_strength varchar(10), -- 'weak', 'medium', 'strong'
ADD COLUMN IF NOT EXISTS confidence_score numeric(3,2), -- 0.00 ~ 1.00
ADD COLUMN IF NOT EXISTS entry_price numeric,
ADD COLUMN IF NOT EXISTS target_price numeric,
ADD COLUMN IF NOT EXISTS stop_loss_price numeric,
ADD COLUMN IF NOT EXISTS position_size integer,
ADD COLUMN IF NOT EXISTS risk_reward_ratio numeric(4,2),
ADD COLUMN IF NOT EXISTS indicators_snapshot jsonb, -- 신호 생성 시점의 지표들
ADD COLUMN IF NOT EXISTS market_conditions jsonb, -- 시장 상황
ADD COLUMN IF NOT EXISTS executed boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS execution_time timestamp with time zone,
ADD COLUMN IF NOT EXISTS expiry_time timestamp with time zone;

-- 4. 주문 관리 (키움 API 주문 정보)
-- ====================================================================
CREATE TABLE IF NOT EXISTS kiwoom_orders (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id uuid REFERENCES strategies(id),
    signal_id uuid REFERENCES trading_signals(id),
    
    -- 키움 주문 정보
    kiwoom_order_no varchar(20) UNIQUE,
    original_order_no varchar(20),
    account_no varchar(20) NOT NULL,
    
    -- 주문 상세
    stock_code varchar(10) NOT NULL,
    stock_name varchar(100),
    order_type varchar(10) NOT NULL, -- 'BUY', 'SELL'
    order_method varchar(20), -- '시장가', '지정가', '조건부지정가'
    
    -- 수량 및 가격
    order_quantity integer NOT NULL,
    order_price numeric NOT NULL,
    executed_quantity integer DEFAULT 0,
    executed_price numeric,
    remaining_quantity integer,
    
    -- 상태 관리
    order_status varchar(20), -- 'PENDING', 'PARTIAL', 'FILLED', 'CANCELLED', 'REJECTED'
    status_message text,
    
    -- 시간 정보
    order_time timestamp with time zone DEFAULT now(),
    executed_time timestamp with time zone,
    cancelled_time timestamp with time zone,
    
    -- 수수료 및 세금
    commission numeric DEFAULT 0,
    tax numeric DEFAULT 0,
    
    -- 메타 정보
    order_reason text,
    metadata jsonb
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_orders_status ON kiwoom_orders(order_status, order_time DESC);
CREATE INDEX IF NOT EXISTS idx_orders_stock ON kiwoom_orders(stock_code, order_time DESC);
CREATE INDEX IF NOT EXISTS idx_orders_account ON kiwoom_orders(account_no, order_time DESC);

-- 5. 포지션 관리 (현재 보유 종목)
-- ====================================================================
CREATE TABLE IF NOT EXISTS positions (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    strategy_id uuid REFERENCES strategies(id),
    account_no varchar(20) NOT NULL,
    
    -- 종목 정보
    stock_code varchar(10) NOT NULL,
    stock_name varchar(100),
    
    -- 수량 및 가격
    quantity integer NOT NULL,
    available_quantity integer, -- 매도 가능 수량
    avg_buy_price numeric NOT NULL,
    current_price numeric,
    
    -- 손익 계산
    total_buy_amount numeric,
    current_value numeric,
    profit_loss numeric,
    profit_loss_rate numeric(6,2),
    realized_profit_loss numeric DEFAULT 0,
    
    -- 리스크 관리
    stop_loss_price numeric,
    take_profit_price numeric,
    trailing_stop_percent numeric(5,2),
    
    -- 상태 관리
    position_status varchar(20) DEFAULT 'OPEN', -- 'OPEN', 'CLOSING', 'CLOSED'
    entry_signal_id uuid REFERENCES trading_signals(id),
    exit_signal_id uuid REFERENCES trading_signals(id),
    
    -- 시간 정보
    opened_at timestamp with time zone DEFAULT now(),
    closed_at timestamp with time zone,
    last_updated timestamp with time zone DEFAULT now(),
    
    UNIQUE(account_no, stock_code, strategy_id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_positions_account ON positions(account_no, position_status);
CREATE INDEX IF NOT EXISTS idx_positions_stock ON positions(stock_code, position_status);

-- 6. 계좌 정보 (키움 계좌 잔고)
-- ====================================================================
CREATE TABLE IF NOT EXISTS account_balance (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    account_no varchar(20) NOT NULL,
    
    -- 잔고 정보
    total_evaluation numeric, -- 총평가금액
    total_buy_amount numeric, -- 총매입금액
    available_cash numeric, -- 주문가능금액
    total_profit_loss numeric, -- 총평가손익
    total_profit_loss_rate numeric(6,2), -- 총수익률
    
    -- 자산 구성
    stock_value numeric, -- 주식평가금액
    cash_balance numeric, -- 예수금
    receivable_amount numeric, -- 미수금
    
    -- 투자 정보
    invested_amount numeric, -- 투자원금
    withdrawn_amount numeric, -- 출금액
    
    -- 업데이트 정보
    updated_at timestamp with time zone DEFAULT now(),
    
    UNIQUE(account_no, updated_at)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_balance_account_time ON account_balance(account_no, updated_at DESC);

-- 7. 전략 실행 로그
-- ====================================================================
CREATE TABLE IF NOT EXISTS strategy_execution_logs (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id uuid REFERENCES strategies(id),
    
    -- 실행 정보
    execution_type varchar(20), -- 'SIGNAL_CHECK', 'ORDER_PLACED', 'POSITION_CLOSED', 'ERROR'
    execution_status varchar(20), -- 'SUCCESS', 'FAILED', 'SKIPPED'
    
    -- 상세 정보
    stock_code varchar(10),
    action_taken text,
    reason text,
    
    -- 시장 상황
    market_snapshot jsonb,
    indicators_snapshot jsonb,
    
    -- 결과
    result jsonb,
    error_message text,
    
    -- 실행 시간
    executed_at timestamp with time zone DEFAULT now(),
    execution_time_ms integer -- 실행 소요 시간
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_execution_logs_strategy ON strategy_execution_logs(strategy_id, executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_execution_logs_type ON strategy_execution_logs(execution_type, executed_at DESC);

-- 8. 백테스트 결과 (전략 성능 분석)
-- ====================================================================
ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS total_trades integer,
ADD COLUMN IF NOT EXISTS winning_trades integer,
ADD COLUMN IF NOT EXISTS losing_trades integer,
ADD COLUMN IF NOT EXISTS win_rate numeric(5,2),
ADD COLUMN IF NOT EXISTS avg_profit numeric,
ADD COLUMN IF NOT EXISTS avg_loss numeric,
ADD COLUMN IF NOT EXISTS max_drawdown numeric(5,2),
ADD COLUMN IF NOT EXISTS sharpe_ratio numeric(5,2),
ADD COLUMN IF NOT EXISTS profit_factor numeric(5,2),
ADD COLUMN IF NOT EXISTS recovery_factor numeric(5,2),
ADD COLUMN IF NOT EXISTS trade_details jsonb,
ADD COLUMN IF NOT EXISTS daily_returns jsonb,
ADD COLUMN IF NOT EXISTS test_period_start date,
ADD COLUMN IF NOT EXISTS test_period_end date;

-- 9. 실시간 알림
-- ====================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    
    -- 알림 정보
    alert_type varchar(20), -- 'SIGNAL', 'ORDER', 'POSITION', 'RISK', 'SYSTEM'
    alert_level varchar(10), -- 'INFO', 'WARNING', 'CRITICAL'
    
    -- 내용
    title varchar(200),
    message text,
    stock_code varchar(10),
    
    -- 관련 정보
    related_id uuid, -- signal_id, order_id, position_id 등
    related_table varchar(50),
    
    -- 상태
    is_read boolean DEFAULT false,
    is_sent boolean DEFAULT false,
    sent_channels jsonb, -- ['email', 'push', 'telegram']
    
    -- 시간
    created_at timestamp with time zone DEFAULT now(),
    read_at timestamp with time zone
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id, is_read, created_at DESC);

-- 10. 시스템 설정
-- ====================================================================
CREATE TABLE IF NOT EXISTS system_settings (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    
    -- 거래 설정
    auto_trading_enabled boolean DEFAULT false,
    max_positions integer DEFAULT 10,
    max_position_size numeric(5,2) DEFAULT 10.00, -- 최대 10%
    
    -- 리스크 관리
    daily_loss_limit numeric,
    total_loss_limit numeric,
    use_stop_loss boolean DEFAULT true,
    default_stop_loss_percent numeric(5,2) DEFAULT 3.00,
    use_trailing_stop boolean DEFAULT false,
    
    -- 알림 설정
    alert_on_signal boolean DEFAULT true,
    alert_on_execution boolean DEFAULT true,
    alert_on_risk boolean DEFAULT true,
    alert_channels jsonb DEFAULT '["email"]'::jsonb,
    
    -- API 설정
    kiwoom_account_no varchar(20),
    kiwoom_api_key varchar(100),
    kiwoom_api_secret varchar(100),
    is_demo_mode boolean DEFAULT true,
    
    updated_at timestamp with time zone DEFAULT now()
);

-- ====================================================================
-- 인덱스 및 성능 최적화
-- ====================================================================

-- 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_market_data_analysis 
ON market_data(stock_code, timestamp DESC, current_price);

CREATE INDEX IF NOT EXISTS idx_signals_execution 
ON trading_signals(strategy_id, executed, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_positions_performance 
ON positions(account_no, position_status, profit_loss_rate);

-- ====================================================================
-- RLS (Row Level Security) 정책
-- ====================================================================

-- 모든 테이블에 RLS 활성화
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE technical_indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE kiwoom_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategy_execution_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_balance ENABLE ROW LEVEL SECURITY;

-- 시장 데이터는 모든 사용자가 읽을 수 있음
CREATE POLICY "market_data_read_all" ON market_data
    FOR SELECT USING (true);

-- 기술적 지표는 모든 사용자가 읽을 수 있음
CREATE POLICY "indicators_read_all" ON technical_indicators
    FOR SELECT USING (true);

-- 사용자별 데이터 접근 제한
CREATE POLICY "orders_user_own" ON kiwoom_orders
    FOR ALL USING (
        strategy_id IN (
            SELECT id FROM strategies WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "alerts_user_own" ON alerts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "settings_user_own" ON system_settings
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "balance_user_own" ON account_balance
    FOR ALL USING (auth.uid() = user_id);