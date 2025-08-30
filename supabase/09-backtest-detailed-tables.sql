-- 백테스트 상세 테이블 생성
-- 기존 backtest_results 테이블에 더 많은 컬럼 추가 및 관련 테이블 생성

-- 1. 백테스트 결과 테이블 확장
ALTER TABLE backtest_results 
ADD COLUMN IF NOT EXISTS strategy_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS annual_return DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS volatility DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS sortino_ratio DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS calmar_ratio DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS beta DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS alpha DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS max_drawdown_duration INTEGER,
ADD COLUMN IF NOT EXISTS avg_win DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS avg_loss DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS profit_factor DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS avg_holding_days DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS max_consecutive_wins INTEGER,
ADD COLUMN IF NOT EXISTS max_consecutive_losses INTEGER,
ADD COLUMN IF NOT EXISTS max_positions INTEGER,
ADD COLUMN IF NOT EXISTS avg_positions DECIMAL(10, 2),
ADD COLUMN IF NOT EXISTS turnover DECIMAL(10, 4);

-- 2. 백테스트 거래 내역 테이블
CREATE TABLE IF NOT EXISTS backtest_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    trade_date DATE NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    action VARCHAR(10) CHECK (action IN ('BUY', 'SELL')),
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    commission DECIMAL(10, 2),
    returns DECIMAL(10, 4),
    holding_days INTEGER,
    profit_loss DECIMAL(15, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_backtest_trades_backtest_id (backtest_id),
    INDEX idx_backtest_trades_date (trade_date)
);

-- 3. 백테스트 일별 수익률 테이블
CREATE TABLE IF NOT EXISTS backtest_daily_returns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    portfolio_value DECIMAL(15, 2) NOT NULL,
    daily_return DECIMAL(10, 6),
    cumulative_return DECIMAL(10, 6),
    drawdown DECIMAL(10, 6),
    positions_count INTEGER,
    cash_balance DECIMAL(15, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backtest_id, date),
    INDEX idx_daily_returns_backtest_id (backtest_id),
    INDEX idx_daily_returns_date (date)
);

-- 4. 백테스트 월별 수익률 테이블
CREATE TABLE IF NOT EXISTS backtest_monthly_returns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    monthly_return DECIMAL(10, 4),
    trades_count INTEGER,
    win_rate DECIMAL(5, 2),
    avg_gain DECIMAL(10, 4),
    avg_loss DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backtest_id, year, month),
    INDEX idx_monthly_returns_backtest_id (backtest_id)
);

-- 5. 백테스트 섹터별 성과 테이블
CREATE TABLE IF NOT EXISTS backtest_sector_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    sector VARCHAR(100) NOT NULL,
    trades_count INTEGER NOT NULL,
    total_return DECIMAL(10, 4),
    win_rate DECIMAL(5, 2),
    avg_return DECIMAL(10, 4),
    total_profit DECIMAL(15, 2),
    total_loss DECIMAL(15, 2),
    best_trade DECIMAL(10, 4),
    worst_trade DECIMAL(10, 4),
    avg_holding_days DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backtest_id, sector),
    INDEX idx_sector_performance_backtest_id (backtest_id)
);

-- 6. 백테스트 리스크 지표 테이블
CREATE TABLE IF NOT EXISTS backtest_risk_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 6),
    metric_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backtest_id, metric_name),
    INDEX idx_risk_metrics_backtest_id (backtest_id)
);

-- 7. 백테스트 포지션 히스토리 테이블
CREATE TABLE IF NOT EXISTS backtest_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    quantity INTEGER NOT NULL,
    avg_price DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    market_value DECIMAL(15, 2),
    unrealized_pnl DECIMAL(15, 2),
    weight DECIMAL(5, 2), -- 포트폴리오 내 비중
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_positions_backtest_id (backtest_id),
    INDEX idx_positions_date (date)
);

-- 8. 백테스트 비교 분석을 위한 벤치마크 테이블
CREATE TABLE IF NOT EXISTS backtest_benchmark (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    benchmark_name VARCHAR(100) NOT NULL, -- KOSPI, KOSDAQ 등
    total_return DECIMAL(10, 4),
    annual_return DECIMAL(10, 4),
    volatility DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    correlation DECIMAL(10, 4), -- 전략과의 상관관계
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backtest_id, benchmark_name),
    INDEX idx_benchmark_backtest_id (backtest_id)
);

-- 9. 백테스트 요약 통계 테이블 (빠른 조회용)
CREATE TABLE IF NOT EXISTS backtest_summary_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    stat_category VARCHAR(50) NOT NULL, -- 'returns', 'risk', 'trades', 'drawdown' 등
    stat_name VARCHAR(100) NOT NULL,
    stat_value DECIMAL(15, 6),
    stat_unit VARCHAR(20), -- '%', 'days', 'count' 등
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backtest_id, stat_category, stat_name),
    INDEX idx_summary_stats_backtest_id (backtest_id),
    INDEX idx_summary_stats_category (stat_category)
);

-- 10. 백테스트 실행 로그 테이블
CREATE TABLE IF NOT EXISTS backtest_execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    log_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    log_level VARCHAR(20) CHECK (log_level IN ('INFO', 'WARNING', 'ERROR')),
    log_message TEXT,
    log_data JSONB,
    INDEX idx_execution_logs_backtest_id (backtest_id),
    INDEX idx_execution_logs_timestamp (log_timestamp)
);

-- RLS 정책 추가
ALTER TABLE backtest_trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_daily_returns ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_monthly_returns ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_sector_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_risk_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_benchmark ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_summary_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_execution_logs ENABLE ROW LEVEL SECURITY;

-- 각 테이블에 대한 RLS 정책 생성
-- 사용자는 자신의 백테스트 결과만 볼 수 있음
CREATE POLICY "Users can view own backtest trades"
    ON backtest_trades FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own daily returns"
    ON backtest_daily_returns FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own monthly returns"
    ON backtest_monthly_returns FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own sector performance"
    ON backtest_sector_performance FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own risk metrics"
    ON backtest_risk_metrics FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own positions"
    ON backtest_positions FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own benchmark"
    ON backtest_benchmark FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own summary stats"
    ON backtest_summary_stats FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own execution logs"
    ON backtest_execution_logs FOR SELECT
    USING (backtest_id IN (
        SELECT id FROM backtest_results WHERE user_id = auth.uid()
    ));