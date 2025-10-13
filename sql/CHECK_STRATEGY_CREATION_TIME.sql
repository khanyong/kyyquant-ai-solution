-- Check when the strategy was created and activated

-- 1. Strategy creation and activation time
SELECT
  id,
  name,
  auto_execute,
  is_active,
  created_at as strategy_created,
  updated_at as strategy_updated
FROM strategies
WHERE id = 'de2718d0-f3fb-45ad-9610-50d46ca1bff0';

-- 2. When was it connected to the investment universe?
SELECT
  id,
  strategy_id,
  investment_filter_id,
  is_active,
  created_at as connection_created,
  updated_at as connection_updated
FROM strategy_universes
WHERE strategy_id = 'de2718d0-f3fb-45ad-9610-50d46ca1bff0';

-- 3. Investment filter details
SELECT
  id,
  name,
  filtered_stocks_count,
  is_active,
  created_at as filter_created,
  updated_at as filter_updated
FROM kw_investment_filters
WHERE id = '5ead6e97-dd5a-4f00-b180-cc421ac0acde';
