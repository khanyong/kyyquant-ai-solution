-- Test the RPC function to see what it actually returns
SELECT * FROM get_active_strategies_with_universe();

-- Also check if there are any active strategies
SELECT
    s.id,
    s.name,
    s.auto_execute,
    s.is_active,
    s.allocated_capital,
    s.allocated_percent,
    s.entry_conditions,
    s.exit_conditions
FROM strategies s
WHERE s.auto_execute = true AND s.is_active = true;

-- Check if strategy_universes exist
SELECT
    su.id,
    su.strategy_id,
    su.investment_filter_id,
    su.is_active
FROM strategy_universes su
WHERE su.is_active = true;

-- Check if filters exist
SELECT
    kif.id,
    kif.name,
    kif.filtered_stocks,
    kif.is_active
FROM kw_investment_filters kif
WHERE kif.is_active = true;
