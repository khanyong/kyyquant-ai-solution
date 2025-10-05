-- Check if backtest_results table exists and has RLS enabled
SELECT
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
AND tablename = 'backtest_results';

-- Check existing RLS policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'backtest_results';

-- Check if auth.uid() is working (run this as authenticated user)
SELECT
    auth.uid() as current_user_id,
    CASE
        WHEN auth.uid() IS NULL THEN '❌ No authenticated user'
        ELSE '✅ User authenticated'
    END as auth_status;

-- Test INSERT permission (run this as authenticated user)
-- This will show if the user can insert
EXPLAIN (FORMAT TEXT)
INSERT INTO backtest_results (
    user_id,
    strategy_name,
    start_date,
    end_date,
    initial_capital,
    total_return,
    total_return_rate,
    max_drawdown,
    win_rate,
    total_trades,
    winning_trades,
    losing_trades
) VALUES (
    auth.uid(),
    'Test Strategy',
    '2024-01-01',
    '2024-12-31',
    10000000,
    1000000,
    10.0,
    5.0,
    60.0,
    100,
    60,
    40
);

-- Rollback the test insert
ROLLBACK;
