-- 1. Call the RPC function directly to see what it returns
SELECT * FROM get_active_strategies_with_universe();

-- 2. Check the specific strategy's allocated capital
SELECT id, name, allocated_capital, allocated_percent, auto_execute, is_active
FROM strategies
WHERE id = '57fe4599-9e3a-4be7-9a5c-97e9535cee79';
