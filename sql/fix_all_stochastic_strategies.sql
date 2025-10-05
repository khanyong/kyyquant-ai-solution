-- Fix ALL strategies using 'stochastic' - Change to 'stochastic_k' in all conditions
-- This will update buyConditions, sellConditions, buyStageStrategy, and sellStageStrategy

-- Step 1: Find all strategies with stochastic conditions
SELECT
  id,
  name,
  config->'buyConditions'->0->>'left' as buy_left,
  config->'sellConditions'->0->>'left' as sell_left
FROM strategies
WHERE config::text LIKE '%"left":"stochastic"%'
  OR config::text LIKE '%"left": "stochastic"%';

-- Step 2: Update buyConditions and sellConditions
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions,0,left}',
    '"stochastic_k"'::jsonb,
    true
  ),
  '{sellConditions,0,left}',
  '"stochastic_k"'::jsonb,
  true
)
WHERE (
  config->'buyConditions'->0->>'left' = 'stochastic'
  OR config->'sellConditions'->0->>'left' = 'stochastic'
)
AND is_active = true;

-- Step 3: Update buyStageStrategy conditions
UPDATE strategies
SET config = jsonb_set(
  config,
  '{buyStageStrategy,stages,0,conditions,0,left}',
  '"stochastic_k"'::jsonb,
  true
)
WHERE config->'buyStageStrategy'->'stages'->0->'conditions'->0->>'left' = 'stochastic'
  AND is_active = true;

-- Step 4: Update sellStageStrategy conditions
UPDATE strategies
SET config = jsonb_set(
  config,
  '{sellStageStrategy,stages,0,conditions,0,left}',
  '"stochastic_k"'::jsonb,
  true
)
WHERE config->'sellStageStrategy'->'stages'->0->'conditions'->0->>'left' = 'stochastic'
  AND is_active = true;

-- Step 5: Verify all fixes
SELECT
  id,
  name,
  config->'buyConditions'->0->>'left' as buy_left,
  config->'sellConditions'->0->>'left' as sell_left,
  config->'buyStageStrategy'->'stages'->0->'conditions'->0->>'left' as stage_buy_left,
  config->'sellStageStrategy'->'stages'->0->'conditions'->0->>'left' as stage_sell_left
FROM strategies
WHERE config::text LIKE '%stochastic%'
  AND is_active = true
ORDER BY name;
