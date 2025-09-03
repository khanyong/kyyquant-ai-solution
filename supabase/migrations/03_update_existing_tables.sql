-- ====================================================================
-- STEP 3: 기존 테이블 업데이트 (컬럼 추가)
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

-- backtest_results 테이블 업데이트
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

-- strategies 테이블에 누락된 컬럼 추가 (있을 경우)
ALTER TABLE strategies
ADD COLUMN IF NOT EXISTS conditions jsonb,
ADD COLUMN IF NOT EXISTS target_stocks text[],
ADD COLUMN IF NOT EXISTS position_size numeric DEFAULT 10,
ADD COLUMN IF NOT EXISTS auto_execute boolean DEFAULT false;