-- Fix "나의 전략 C" (ID: 4a719524-494f-4187-a956-a3f3d3dd7e92)
-- Replace all 'stochastic' with 'stochastic_k' in conditions

-- Use text replacement to fix all occurrences at once
UPDATE strategies
SET config = replace(
  replace(config::text, '"left":"stochastic"', '"left":"stochastic_k"'),
  '"left": "stochastic"',
  '"left": "stochastic_k"'
)::jsonb
WHERE id = '4a719524-494f-4187-a956-a3f3d3dd7e92';

-- Verify the fix - check all conditions
SELECT
  name,
  -- Check buyConditions
  config->'buyConditions'->0->>'left' as buy_cond_0,
  config->'buyConditions'->1->>'left' as buy_cond_1,
  -- Check buyStageStrategy stages
  config->'buyStageStrategy'->'stages'->0->'conditions'->0->>'left' as buy_stage_0,
  config->'buyStageStrategy'->'stages'->1->'conditions'->0->>'left' as buy_stage_1,
  -- Full config check
  CASE
    WHEN config::text LIKE '%"left":"stochastic"%'
      OR config::text LIKE '%"left": "stochastic"%'
    THEN '❌ Still has stochastic'
    ELSE '✅ All fixed'
  END as status
FROM strategies
WHERE id = '4a719524-494f-4187-a956-a3f3d3dd7e92';
