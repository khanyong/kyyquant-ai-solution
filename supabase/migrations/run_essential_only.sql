-- ====================================================================
-- 필수 마이그레이션만 실행 (01, 03번)
-- positions 관련 오류를 피하고 핵심 테이블만 생성
-- ====================================================================

-- ====================================================================
-- PART 1: 새 테이블 생성 (01_create_new_tables.sql 내용)
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

-- ====================================================================
-- PART 2: 기존 테이블 업데이트 (03_update_existing_tables.sql 내용)
-- ====================================================================

-- trading_signals 테이블 업데이트
ALTER TABLE trading_signals 
ADD COLUMN IF NOT EXISTS signal_strength varchar(10),
ADD COLUMN IF NOT EXISTS confidence_score numeric(3,2),
ADD COLUMN IF NOT EXISTS entry_price numeric,
ADD COLUMN IF NOT EXISTS target_price numeric,
ADD COLUMN IF NOT EXISTS stop_loss_price numeric,
ADD COLUMN IF NOT EXISTS position_size integer,
ADD COLUMN IF NOT EXISTS risk_reward_ratio numeric(4,2),
ADD COLUMN IF NOT EXISTS indicators_snapshot jsonb,
ADD COLUMN IF NOT EXISTS market_conditions jsonb,
ADD COLUMN IF NOT EXISTS executed boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS execution_time timestamp with time zone,
ADD COLUMN IF NOT EXISTS expiry_time timestamp with time zone;

-- strategies 테이블에 누락된 컬럼 추가
ALTER TABLE strategies
ADD COLUMN IF NOT EXISTS conditions jsonb,
ADD COLUMN IF NOT EXISTS target_stocks text[],
ADD COLUMN IF NOT EXISTS position_size numeric DEFAULT 10,
ADD COLUMN IF NOT EXISTS auto_execute boolean DEFAULT false;

-- ====================================================================
-- PART 3: 간단한 인덱스만 생성 (오류 없는 것만)
-- ====================================================================

-- market_data 인덱스
CREATE INDEX IF NOT EXISTS idx_market_data_stock_time 
ON market_data(stock_code, timestamp DESC);

-- technical_indicators 인덱스
CREATE INDEX IF NOT EXISTS idx_indicators_stock_time 
ON technical_indicators(stock_code, timeframe, calculated_at DESC);

-- kiwoom_orders 인덱스
CREATE INDEX IF NOT EXISTS idx_orders_status 
ON kiwoom_orders(order_status, order_time DESC);

CREATE INDEX IF NOT EXISTS idx_orders_stock 
ON kiwoom_orders(stock_code, order_time DESC);

-- account_balance 인덱스
CREATE INDEX IF NOT EXISTS idx_balance_account_time 
ON account_balance(account_no, updated_at DESC);

-- strategy_execution_logs 인덱스
CREATE INDEX IF NOT EXISTS idx_execution_logs_strategy 
ON strategy_execution_logs(strategy_id, executed_at DESC);

-- ====================================================================
-- 완료 메시지
-- ====================================================================
SELECT '필수 테이블과 인덱스 생성 완료' as status;