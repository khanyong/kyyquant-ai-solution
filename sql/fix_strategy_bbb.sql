-- Fix "나의 전략 BBB" (ID: b83f3dcf-4ef9-499f-8f1f-01c45b69ceec)
-- Problem: golden_cross operator with number value instead of another SMA

-- Option 1: Change to simple comparison (sma > 30)
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions,2,operator}',
    '">"'::jsonb
  ),
  '{buyStageStrategy,stages,2,conditions,0,operator}',
  '">"'::jsonb
)
WHERE id = 'b83f3dcf-4ef9-499f-8f1f-01c45b69ceec';

-- Option 2: Change to crossover (price crosses above SMA)
-- Uncomment if you want crossover instead
/*
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{buyConditions,2,left}',
      '"close"'::jsonb
    ),
    '{buyConditions,2,operator}',
    '"crossover"'::jsonb
  ),
  '{buyConditions,2,right}',
  '"sma"'::jsonb
)
WHERE id = 'b83f3dcf-4ef9-499f-8f1f-01c45b69ceec';

-- Also update stage strategy
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{buyStageStrategy,stages,2,conditions,0,left}',
      '"close"'::jsonb
    ),
    '{buyStageStrategy,stages,2,conditions,0,operator}',
    '"crossover"'::jsonb
  ),
  '{buyStageStrategy,stages,2,conditions,0,right}',
  '"sma"'::jsonb
)
WHERE id = 'b83f3dcf-4ef9-499f-8f1f-01c45b69ceec';
*/

-- Verify the fix
SELECT
  name,
  config->'buyConditions'->2->>'left' as buy_cond_2_left,
  config->'buyConditions'->2->>'operator' as buy_cond_2_operator,
  config->'buyConditions'->2->>'right' as buy_cond_2_right,
  config->'buyStageStrategy'->'stages'->2->'conditions'->0->>'operator' as stage_operator
FROM strategies
WHERE id = 'b83f3dcf-4ef9-499f-8f1f-01c45b69ceec';
