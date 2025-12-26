-- [FIX VISIBILITY]
-- The RPC function 'get_active_strategies_with_universe' requires:
-- 1. strategy.auto_execute = true
-- 2. Link to strategy_universes table
-- 3. Link to kw_investment_filters table

-- 1. Enable Auto Execute (Required for visibility in current frontend logic)
UPDATE strategies 
SET auto_execute = true 
WHERE name IN ('TEST_STRATEGY_A_MACD', 'TEST_STRATEGY_B_BB');

-- 2. Link to Filters (Create if not exists)
-- Ensure we have default filters
INSERT INTO kw_investment_filters (name, description, is_active)
SELECT 'KOSPI Default', 'Default KOSPI Filter', true
WHERE NOT EXISTS (SELECT 1 FROM kw_investment_filters WHERE name = 'KOSPI Default');

INSERT INTO kw_investment_filters (name, description, is_active)
SELECT 'KOSDAQ Default', 'Default KOSDAQ Filter', true
WHERE NOT EXISTS (SELECT 1 FROM kw_investment_filters WHERE name = 'KOSDAQ Default');

-- 3. Insert into strategy_universes
INSERT INTO strategy_universes (strategy_id, investment_filter_id, is_active)
SELECT 
    s.id,
    f.id,
    true
FROM strategies s
CROSS JOIN kw_investment_filters f
WHERE s.name = 'TEST_STRATEGY_A_MACD' AND f.name = 'KOSPI Default'
AND NOT EXISTS (
    SELECT 1 FROM strategy_universes su 
    WHERE su.strategy_id = s.id AND su.investment_filter_id = f.id
);

INSERT INTO strategy_universes (strategy_id, investment_filter_id, is_active)
SELECT 
    s.id,
    f.id,
    true
FROM strategies s
CROSS JOIN kw_investment_filters f
WHERE s.name = 'TEST_STRATEGY_B_BB' AND f.name = 'KOSDAQ Default'
AND NOT EXISTS (
    SELECT 1 FROM strategy_universes su 
    WHERE su.strategy_id = s.id AND su.investment_filter_id = f.id
);
