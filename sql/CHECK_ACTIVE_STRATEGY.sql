-- Check why "[분할] RSI 3단계 매수매도" strategy is active

-- 1. Check the strategy itself
SELECT
  id,
  name,
  auto_execute,
  is_active,
  created_at
FROM strategies
WHERE name LIKE '%RSI%3단계%'
ORDER BY created_at DESC;

-- 2. Check strategy_universes connections
SELECT
  su.id,
  su.strategy_id,
  s.name as strategy_name,
  su.investment_filter_id,
  kif.name as filter_name,
  su.is_active as connection_active,
  su.created_at
FROM strategy_universes su
INNER JOIN strategies s ON s.id = su.strategy_id
INNER JOIN kw_investment_filters kif ON kif.id = su.investment_filter_id
WHERE s.name LIKE '%RSI%3단계%'
ORDER BY su.created_at DESC;

-- 3. Check complete active status (same as the RPC function)
SELECT
  s.id as strategy_id,
  s.name as strategy_name,
  s.auto_execute,
  s.is_active as strategy_active,
  su.is_active as connection_active,
  kif.name as filter_name,
  kif.is_active as filter_active,
  kif.filtered_stocks_count as stock_count
FROM strategies s
INNER JOIN strategy_universes su ON s.id = su.strategy_id
INNER JOIN kw_investment_filters kif ON su.investment_filter_id = kif.id
WHERE s.name LIKE '%RSI%3단계%';

-- 4. Call the actual RPC function
SELECT * FROM get_active_strategies_with_universe()
WHERE strategy_name LIKE '%RSI%3단계%';
