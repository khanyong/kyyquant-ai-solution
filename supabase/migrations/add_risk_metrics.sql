-- Add Sortino and Treynor ratios to backtest_results table
-- Migration: 2025-10-08 - Add risk-adjusted performance metrics

ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS sortino_ratio DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS treynor_ratio DECIMAL(10, 4);

-- Add comments for documentation
COMMENT ON COLUMN backtest_results.sharpe_ratio IS '샤프 비율: (평균 수익률 - 무위험 이자율) / 전체 변동성';
COMMENT ON COLUMN backtest_results.sortino_ratio IS '소르티노 비율: (평균 수익률 - 무위험 이자율) / 하방 변동성 (손실만 고려)';
COMMENT ON COLUMN backtest_results.treynor_ratio IS '트레이너 비율: (평균 수익률 - 무위험 이자율) / 베타 (시장 대비 변동성)';
