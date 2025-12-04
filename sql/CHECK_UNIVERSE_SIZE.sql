-- Check Universe Size for Active Strategies
SELECT 
    s.name as strategy_name,
    kif.name as filter_name,
    jsonb_array_length(kif.filtered_stocks) as universe_size,
    kif.filtered_stocks
FROM strategies s
JOIN strategy_universes su ON su.strategy_id = s.id
JOIN kw_investment_filters kif ON kif.id = su.investment_filter_id
WHERE s.is_active = true;
