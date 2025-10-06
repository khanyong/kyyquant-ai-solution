-- Migration: Rename total_return to total_return_rate in backtest_results table
-- Purpose: Clarify that this field stores percentage return rate, not absolute return value
-- Created: 2025-10-06

BEGIN;

-- 1. Rename column from total_return to total_return_rate
ALTER TABLE backtest_results
RENAME COLUMN total_return TO total_return_rate;

-- 2. Update column comment for clarity
COMMENT ON COLUMN backtest_results.total_return_rate IS '총 수익률 (%, percentage return rate)';

-- 3. Verify the change
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'backtest_results'
        AND column_name = 'total_return_rate'
    ) THEN
        RAISE NOTICE 'Migration successful: total_return renamed to total_return_rate';
    ELSE
        RAISE EXCEPTION 'Migration failed: total_return_rate column not found';
    END IF;
END $$;

COMMIT;
