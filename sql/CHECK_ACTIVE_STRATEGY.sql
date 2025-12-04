-- Check Strategies
SELECT id, name, auto_execute, is_active, allocated_capital 
FROM strategies;

-- Check Investment Filters
SELECT id, name, is_active 
FROM kw_investment_filters;

-- Check Strategy Universes (Connections)
SELECT strategy_id, investment_filter_id, is_active 
FROM strategy_universes;

-- Try the RPC query logic directly
SELECT
    s.id as strategy_id,
    s.name as strategy_name,
    kif.name as filter_name
FROM strategies s
INNER JOIN strategy_universes su ON s.id = su.strategy_id
INNER JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
WHERE
    s.auto_execute = true
    AND s.is_active = true
    AND su.is_active = true
    AND kif.is_active = true;
