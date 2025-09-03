-- ====================================================================
-- STEP 1: 새로운 테이블 생성 (기존 테이블과 충돌 없음)
-- ====================================================================

-- UUID 확장 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 실시간 시장 데이터
CREATE TABLE IF NOT EXISTS market_data (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_code varchar(10) NOT NULL,
    stock_name varchar(100),
    current_price numeric NOT NULL,
    open_price numeric,
    high_price numeric,
    low_price numeric,
    close_price numeric,
    prev_close numeric,
    volume bigint,
    accumulated_volume bigint,
    trading_value numeric,
    change_amount numeric,
    change_rate numeric(5,2),
    bid_price numeric,
    ask_price numeric,
    bid_volume bigint,
    ask_volume bigint,
    trading_date date,
    trading_time time,
    timestamp timestamp with time zone DEFAULT now()
);

-- 2. 기술적 지표 데이터
CREATE TABLE IF NOT EXISTS technical_indicators (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_code varchar(10) NOT NULL,
    timeframe varchar(10) NOT NULL,
    ma5 numeric,
    ma10 numeric,
    ma20 numeric,
    ma60 numeric,
    ma120 numeric,
    bb_upper numeric,
    bb_middle numeric,
    bb_lower numeric,
    rsi numeric(5,2),
    rsi_signal varchar(10),
    macd numeric,
    macd_signal numeric,
    macd_histogram numeric,
    stochastic_k numeric(5,2),
    stochastic_d numeric(5,2),
    obv numeric,
    vwap numeric,
    cci numeric,
    atr numeric,
    calculated_at timestamp with time zone DEFAULT now(),
    UNIQUE(stock_code, timeframe, calculated_at)
);

-- 3. 키움 주문 관리
CREATE TABLE IF NOT EXISTS kiwoom_orders (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id uuid REFERENCES strategies(id),
    signal_id uuid REFERENCES trading_signals(id),
    kiwoom_order_no varchar(20) UNIQUE,
    original_order_no varchar(20),
    account_no varchar(20) NOT NULL,
    stock_code varchar(10) NOT NULL,
    stock_name varchar(100),
    order_type varchar(10) NOT NULL,
    order_method varchar(20),
    order_quantity integer NOT NULL,
    order_price numeric NOT NULL,
    executed_quantity integer DEFAULT 0,
    executed_price numeric,
    remaining_quantity integer,
    order_status varchar(20),
    status_message text,
    order_time timestamp with time zone DEFAULT now(),
    executed_time timestamp with time zone,
    cancelled_time timestamp with time zone,
    commission numeric DEFAULT 0,
    tax numeric DEFAULT 0,
    order_reason text,
    metadata jsonb
);

-- 4. 계좌 정보
CREATE TABLE IF NOT EXISTS account_balance (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    account_no varchar(20) NOT NULL,
    total_evaluation numeric,
    total_buy_amount numeric,
    available_cash numeric,
    total_profit_loss numeric,
    total_profit_loss_rate numeric(6,2),
    stock_value numeric,
    cash_balance numeric,
    receivable_amount numeric,
    invested_amount numeric,
    withdrawn_amount numeric,
    updated_at timestamp with time zone DEFAULT now(),
    UNIQUE(account_no, updated_at)
);

-- 5. 전략 실행 로그
CREATE TABLE IF NOT EXISTS strategy_execution_logs (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id uuid REFERENCES strategies(id),
    execution_type varchar(20),
    execution_status varchar(20),
    stock_code varchar(10),
    action_taken text,
    reason text,
    market_snapshot jsonb,
    indicators_snapshot jsonb,
    result jsonb,
    error_message text,
    executed_at timestamp with time zone DEFAULT now(),
    execution_time_ms integer
);

-- 6. 실시간 알림
CREATE TABLE IF NOT EXISTS alerts (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    alert_type varchar(20),
    alert_level varchar(10),
    title varchar(200),
    message text,
    stock_code varchar(10),
    related_id uuid,
    related_table varchar(50),
    is_read boolean DEFAULT false,
    is_sent boolean DEFAULT false,
    sent_channels jsonb,
    created_at timestamp with time zone DEFAULT now(),
    read_at timestamp with time zone
);

-- 7. 시스템 설정
CREATE TABLE IF NOT EXISTS system_settings (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id uuid REFERENCES auth.users(id),
    auto_trading_enabled boolean DEFAULT false,
    max_positions integer DEFAULT 10,
    max_position_size numeric(5,2) DEFAULT 10.00,
    daily_loss_limit numeric,
    total_loss_limit numeric,
    use_stop_loss boolean DEFAULT true,
    default_stop_loss_percent numeric(5,2) DEFAULT 3.00,
    use_trailing_stop boolean DEFAULT false,
    alert_on_signal boolean DEFAULT true,
    alert_on_execution boolean DEFAULT true,
    alert_on_risk boolean DEFAULT true,
    alert_channels jsonb DEFAULT '["email"]'::jsonb,
    kiwoom_account_no varchar(20),
    kiwoom_api_key varchar(100),
    kiwoom_api_secret varchar(100),
    is_demo_mode boolean DEFAULT true,
    updated_at timestamp with time zone DEFAULT now()
);