-- Create backtest_results table
CREATE TABLE IF NOT EXISTS backtest_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    strategy_id UUID REFERENCES strategies(id) ON DELETE SET NULL,
    strategy_name TEXT NOT NULL,
    
    -- Date range
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Basic metrics
    initial_capital DECIMAL(15, 2) NOT NULL,
    total_return DECIMAL(15, 2) NOT NULL,
    total_return_rate DECIMAL(10, 4) NOT NULL,
    max_drawdown DECIMAL(10, 4) NOT NULL,
    sharpe_ratio DECIMAL(10, 4),
    
    -- Trade statistics
    win_rate DECIMAL(10, 4) NOT NULL,
    total_trades INTEGER NOT NULL,
    winning_trades INTEGER NOT NULL,
    losing_trades INTEGER NOT NULL,
    avg_profit DECIMAL(15, 2),
    avg_loss DECIMAL(15, 2),
    best_trade DECIMAL(15, 2),
    worst_trade DECIMAL(15, 2),
    avg_holding_days DECIMAL(10, 2),
    
    -- Additional metrics
    profit_factor DECIMAL(10, 4),
    recovery_factor DECIMAL(10, 4),
    volatility DECIMAL(10, 4),
    
    -- Detailed data (JSONB for flexibility)
    daily_returns JSONB,
    trades JSONB,
    equity_curve JSONB,
    investment_settings JSONB,
    strategy_conditions JSONB,
    filter_conditions JSONB,
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX idx_backtest_results_user_id ON backtest_results(user_id);
CREATE INDEX idx_backtest_results_strategy_id ON backtest_results(strategy_id);
CREATE INDEX idx_backtest_results_strategy_name ON backtest_results(strategy_name);
CREATE INDEX idx_backtest_results_created_at ON backtest_results(created_at DESC);
CREATE INDEX idx_backtest_results_total_return_rate ON backtest_results(total_return_rate DESC);
CREATE INDEX idx_backtest_results_sharpe_ratio ON backtest_results(sharpe_ratio DESC);
CREATE INDEX idx_backtest_results_win_rate ON backtest_results(win_rate DESC);
CREATE INDEX idx_backtest_results_date_range ON backtest_results(start_date, end_date);

-- Enable Row Level Security
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view own backtest results" ON backtest_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own backtest results" ON backtest_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own backtest results" ON backtest_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own backtest results" ON backtest_results
    FOR DELETE USING (auth.uid() = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_backtest_results_updated_at
    BEFORE UPDATE ON backtest_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE backtest_results IS 'Stores detailed backtest results for each strategy test';
COMMENT ON COLUMN backtest_results.user_id IS 'User who ran the backtest';
COMMENT ON COLUMN backtest_results.strategy_id IS 'Reference to the strategy if it was saved';
COMMENT ON COLUMN backtest_results.strategy_name IS 'Name of the strategy used';
COMMENT ON COLUMN backtest_results.total_return_rate IS 'Total return percentage';
COMMENT ON COLUMN backtest_results.max_drawdown IS 'Maximum drawdown percentage';
COMMENT ON COLUMN backtest_results.sharpe_ratio IS 'Risk-adjusted return metric';
COMMENT ON COLUMN backtest_results.win_rate IS 'Percentage of winning trades';
COMMENT ON COLUMN backtest_results.daily_returns IS 'Array of daily return data';
COMMENT ON COLUMN backtest_results.trades IS 'Array of all trade records';
COMMENT ON COLUMN backtest_results.equity_curve IS 'Array of equity curve data points';
COMMENT ON COLUMN backtest_results.investment_settings IS 'Investment parameters used';
COMMENT ON COLUMN backtest_results.strategy_conditions IS 'Strategy conditions applied';
COMMENT ON COLUMN backtest_results.filter_conditions IS 'Filter conditions applied';
COMMENT ON COLUMN backtest_results.metadata IS 'Additional metadata';