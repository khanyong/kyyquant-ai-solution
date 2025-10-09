-- Add Sortino and Treynor ratios to backtest_results table
-- Migration: 2025-10-08 - Add risk-adjusted performance metrics
-- Simplified version without COMMENT (권한 문제 회피)

ALTER TABLE backtest_results
ADD COLUMN IF NOT EXISTS sortino_ratio DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS treynor_ratio DECIMAL(10, 4);
