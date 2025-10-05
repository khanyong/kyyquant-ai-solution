-- Fix "나의 전략 AAA" (ID: b3e6d551-b961-423e-b248-746fa1af62ea)
-- Problems:
-- 1. stochastic → stochastic_k
-- 2. ichimoku with tenkan_above_kijun operator needs proper conversion
-- 3. Remove unnecessary bollingerLine from ichimoku condition

-- Step 1: Fix stochastic → stochastic_k in all conditions
UPDATE strategies
SET config = replace(
  replace(config::text, '"left":"stochastic"', '"left":"stochastic_k"'),
  '"left": "stochastic"',
  '"left": "stochastic_k"'
)::jsonb
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Step 2: Fix ichimoku conditions
-- tenkan_above_kijun → convert to proper comparison
-- Buy conditions: tenkan > kijun (remove right: 30)
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{buyConditions,2,left}',
      '"tenkan"'::jsonb
    ),
    '{buyConditions,2,operator}',
    '">"'::jsonb
  ),
  '{buyConditions,2,right}',
  '"kijun"'::jsonb
)
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Buy stage 3: tenkan > kijun
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{buyStageStrategy,stages,2,conditions,0,left}',
      '"tenkan"'::jsonb
    ),
    '{buyStageStrategy,stages,2,conditions,0,operator}',
    '">"'::jsonb
  ),
  '{buyStageStrategy,stages,2,conditions,0,right}',
  '"kijun"'::jsonb
)
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Sell conditions: tenkan < kijun (tenkan_below_kijun)
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{sellConditions,2,left}',
      '"tenkan"'::jsonb
    ),
    '{sellConditions,2,operator}',
    '"<"'::jsonb
  ),
  '{sellConditions,2,right}',
  '"kijun"'::jsonb
)
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Sell stage 3: tenkan < kijun
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{sellStageStrategy,stages,2,conditions,0,left}',
      '"tenkan"'::jsonb
    ),
    '{sellStageStrategy,stages,2,conditions,0,operator}',
    '"<"'::jsonb
  ),
  '{sellStageStrategy,stages,2,conditions,0,right}',
  '"kijun"'::jsonb
)
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';

-- Step 3: Verify the fixes
SELECT
  name,
  -- Buy conditions
  config->'buyConditions'->0->>'left' as buy_0,
  config->'buyConditions'->1->>'left' as buy_1,
  config->'buyConditions'->2->>'left' as buy_2_left,
  config->'buyConditions'->2->>'operator' as buy_2_op,
  config->'buyConditions'->2->>'right' as buy_2_right,
  -- Sell conditions
  config->'sellConditions'->2->>'left' as sell_2_left,
  config->'sellConditions'->2->>'operator' as sell_2_op,
  config->'sellConditions'->2->>'right' as sell_2_right,
  -- Status
  CASE
    WHEN config::text LIKE '%"left":"stochastic"%'
      OR config::text LIKE '%"left": "stochastic"%'
    THEN '❌ Still has stochastic'
    WHEN config::text LIKE '%"tenkan_above_kijun"%'
      OR config::text LIKE '%"tenkan_below_kijun"%'
    THEN '❌ Still has ichimoku operators'
    ELSE '✅ Fixed'
  END as status
FROM strategies
WHERE id = 'b3e6d551-b961-423e-b248-746fa1af62ea';
