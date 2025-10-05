-- Fix "나의 전략 AAA" (ID: b3e6d551-b961-423e-b248-746fa1af62ea)
-- Ichimoku columns: ichimoku_tenkan, ichimoku_kijun (with prefix!)

-- Step 1: Fix stochastic → stochastic_k
UPDATE strategies
SET config = replace(
  replace(config::text, '"left":"stochastic"', '"left":"stochastic_k"'),
  '"left": "stochastic"',
  '"left": "stochastic_k"'
)::jsonb
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Step 2: Fix ichimoku buy conditions
-- tenkan_above_kijun → ichimoku_tenkan > ichimoku_kijun
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{buyConditions,2,left}',
      '"ichimoku_tenkan"'::jsonb
    ),
    '{buyConditions,2,operator}',
    '">"'::jsonb
  ),
  '{buyConditions,2,right}',
  '"ichimoku_kijun"'::jsonb
)
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Step 3: Fix ichimoku buy stage 3
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{buyStageStrategy,stages,2,conditions,0,left}',
      '"ichimoku_tenkan"'::jsonb
    ),
    '{buyStageStrategy,stages,2,conditions,0,operator}',
    '">"'::jsonb
  ),
  '{buyStageStrategy,stages,2,conditions,0,right}',
  '"ichimoku_kijun"'::jsonb
)
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Step 4: Fix ichimoku sell conditions
-- tenkan_below_kijun → ichimoku_tenkan < ichimoku_kijun
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{sellConditions,2,left}',
      '"ichimoku_tenkan"'::jsonb
    ),
    '{sellConditions,2,operator}',
    '"<"'::jsonb
  ),
  '{sellConditions,2,right}',
  '"ichimoku_kijun"'::jsonb
)
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Step 5: Fix ichimoku sell stage 3
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{sellStageStrategy,stages,2,conditions,0,left}',
      '"ichimoku_tenkan"'::jsonb
    ),
    '{sellStageStrategy,stages,2,conditions,0,operator}',
    '"<"'::jsonb
  ),
  '{sellStageStrategy,stages,2,conditions,0,right}',
  '"ichimoku_kijun"'::jsonb
)
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Step 6: Verify the fixes
SELECT
  name,
  config->'buyConditions'->2->>'left' as buy_2_left,
  config->'buyConditions'->2->>'operator' as buy_2_op,
  config->'buyConditions'->2->>'right' as buy_2_right,
  config->'sellConditions'->2->>'left' as sell_2_left,
  config->'sellConditions'->2->>'operator' as sell_2_op,
  config->'sellConditions'->2->>'right' as sell_2_right,
  CASE
    WHEN config::text LIKE '%"left":"stochastic"%'
    THEN '❌ stochastic not fixed'
    WHEN config::text LIKE '%"left":"tenkan"%'
      OR config::text LIKE '%"right":"kijun"%'
    THEN '❌ missing ichimoku_ prefix'
    ELSE '✅ Fixed'
  END as status
FROM strategies
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';
