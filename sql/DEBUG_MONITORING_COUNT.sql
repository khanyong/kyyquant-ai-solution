-- =============================================================================
-- Debug Script: Check Universe Size vs Monitored Count
-- =============================================================================

-- 1. Get Active Strategies and their Universe Size (from filtered_stocks)
SELECT 
    s.name as strategy_name,
    jsonb_array_length(kif.filtered_stocks) as universe_size,
    s.updated_at as strategy_updated_at
FROM strategies s
JOIN strategy_universes su ON su.strategy_id = s.id
JOIN kw_investment_filters kif ON kif.id = su.investment_filter_id
WHERE s.is_active = true;

-- 2. Count recently updated rows in strategy_monitoring (Last 1 hour)
SELECT 
    count(*) as monitored_count_last_1h,
    count(*) filter (where condition_match_score > 0) as score_gt_0,
    count(*) filter (where condition_match_score >= 80) as score_ge_80
FROM strategy_monitoring
WHERE updated_at > NOW() - INTERVAL '1 hour';

-- 3. List the recently updated stocks (Limit 10)
SELECT 
    stock_name, 
    condition_match_score, 
    updated_at 
FROM strategy_monitoring 
WHERE updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC
LIMIT 10;
