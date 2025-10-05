-- Fix "나의 전략 F" - Change 'stochastic' to 'stochastic_k' in conditions

UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions,0,left}',
    '"stochastic_k"'
  ),
  '{sellConditions,0,left}',
  '"stochastic_k"'
)
WHERE id = '152de7e7-493a-4ce7-bafa-53d1b4d43cac'
  AND name = '나의 전략 F';

-- Also fix buyStageStrategy and sellStageStrategy
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyStageStrategy,stages,0,conditions,0,left}',
    '"stochastic_k"'
  ),
  '{sellStageStrategy,stages,0,conditions,0,left}',
  '"stochastic_k"'
)
WHERE id = '152de7e7-493a-4ce7-bafa-53d1b4d43cac'
  AND name = '나의 전략 F';

-- Verify the fix
SELECT
  name,
  config->'buyConditions'->0->>'left' as buy_left,
  config->'sellConditions'->0->>'left' as sell_left,
  config->'buyStageStrategy'->'stages'->0->'conditions'->0->>'left' as stage_buy_left,
  config->'sellStageStrategy'->'stages'->0->'conditions'->0->>'left' as stage_sell_left
FROM strategies
WHERE id = '152de7e7-493a-4ce7-bafa-53d1b4d43cac';
