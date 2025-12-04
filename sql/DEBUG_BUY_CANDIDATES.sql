-- =============================================================================
-- Debug Script: Analyze why get_buy_candidates returns empty
-- =============================================================================

-- 1. Check raw candidates in strategy_monitoring
SELECT '1. Raw Candidates in strategy_monitoring' as check_step;
SELECT count(*) as total_candidates, 
       count(*) filter (where condition_match_score >= 100) as score_met,
       count(*) filter (where is_near_entry = true) as near_entry_met
FROM strategy_monitoring;

-- 2. Check Capital Status for these strategies
SELECT '2. Capital Status Check' as check_step;
SELECT 
    s.name as strategy_name,
    scs.allocated_amount,
    scs.remaining_budget,
    scs.available_for_next_order,
    scs.total_positions,
    scs.max_positions
FROM strategies s
JOIN strategy_capital_status scs ON scs.strategy_id = s.id
WHERE s.is_active = true;

-- 3. Check for Pending Orders (Blocking)
SELECT '3. Pending Orders Check' as check_step;
SELECT * FROM orders 
WHERE status IN ('PENDING', 'PARTIAL', 'FILLED')
AND created_at > NOW() - INTERVAL '1 day';

-- 4. Simulate the RPC Query (without filters) to see what fails
SELECT '4. Full Query Simulation' as check_step;
SELECT 
    sm.stock_name,
    sm.condition_match_score,
    sm.is_near_entry,
    scs.available_for_next_order,
    CASE 
        WHEN sm.condition_match_score < 100 THEN 'Low Score'
        WHEN sm.is_near_entry IS NOT TRUE THEN 'Not Near Entry'
        WHEN scs.available_for_next_order <= 0 THEN 'No Capital'
        ELSE 'OK'
    END as fail_reason
FROM strategy_monitoring sm
LEFT JOIN strategy_capital_status scs ON scs.strategy_id = sm.strategy_id
WHERE sm.updated_at > NOW() - INTERVAL '1 hour';
