-- Fix ALL strategies with 'sma' or 'ema' in conditions
-- These need to be converted to dynamic column names (sma_20, ema_12, etc.)

-- Step 1: Find all strategies with sma/ema in conditions
SELECT
  id,
  name,
  config->'indicators' as indicators,
  config->'buyConditions' as buy_conditions,
  config->'sellConditions' as sell_conditions
FROM strategies
WHERE (
  config::text LIKE '%"left":"sma"%'
  OR config::text LIKE '%"right":"sma"%'
  OR config::text LIKE '%"left":"ema"%'
  OR config::text LIKE '%"right":"ema"%'
  OR config::text LIKE '%"left": "sma"%'
  OR config::text LIKE '%"right": "sma"%'
  OR config::text LIKE '%"left": "ema"%'
  OR config::text LIKE '%"right": "ema"%'
)
AND is_active = true;

-- Step 2: Common pattern - SMA with period 20
-- Replace "sma" with "sma_20" where SMA indicator has period 20
UPDATE strategies
SET config = replace(
  replace(
    replace(
      replace(config::text, '"left":"sma"', '"left":"sma_20"'),
      '"right":"sma"',
      '"right":"sma_20"'
    ),
    '"left": "sma"',
    '"left": "sma_20"'
  ),
  '"right": "sma"',
  '"right": "sma_20"'
)::jsonb
WHERE config::text LIKE '%"name":"sma"%'
  AND config::text LIKE '%"period":20%'
  AND (
    config::text LIKE '%"left":"sma"%'
    OR config::text LIKE '%"right":"sma"%'
    OR config::text LIKE '%"left": "sma"%'
    OR config::text LIKE '%"right": "sma"%'
  )
  AND is_active = true;

-- Step 3: EMA with period 12
UPDATE strategies
SET config = replace(
  replace(
    replace(
      replace(config::text, '"left":"ema"', '"left":"ema_12"'),
      '"right":"ema"',
      '"right":"ema_12"'
    ),
    '"left": "ema"',
    '"left": "ema_12"'
  ),
  '"right": "ema"',
  '"right": "ema_12"'
)::jsonb
WHERE config::text LIKE '%"name":"ema"%'
  AND config::text LIKE '%"period":12%'
  AND (
    config::text LIKE '%"left":"ema"%'
    OR config::text LIKE '%"right":"ema"%'
    OR config::text LIKE '%"left": "ema"%'
    OR config::text LIKE '%"right": "ema"%'
  )
  AND is_active = true;

-- Step 4: Verify the fixes
SELECT
  id,
  name,
  config->'buyConditions'->0->>'left' as buy_cond_0_left,
  config->'buyConditions'->0->>'right' as buy_cond_0_right,
  config->'buyConditions'->1->>'left' as buy_cond_1_left,
  config->'buyConditions'->1->>'right' as buy_cond_1_right,
  config->'buyConditions'->2->>'left' as buy_cond_2_left,
  config->'buyConditions'->2->>'right' as buy_cond_2_right,
  CASE
    WHEN config::text LIKE '%"left":"sma"%'
      OR config::text LIKE '%"right":"sma"%'
      OR config::text LIKE '%"left":"ema"%'
      OR config::text LIKE '%"right":"ema"%'
      OR config::text LIKE '%"left": "sma"%'
      OR config::text LIKE '%"right": "sma"%'
      OR config::text LIKE '%"left": "ema"%'
      OR config::text LIKE '%"right": "ema"%'
    THEN '❌ Still has bare sma/ema'
    ELSE '✅ Fixed'
  END as status
FROM strategies
WHERE config::text LIKE '%sma%' OR config::text LIKE '%ema%'
  AND is_active = true
ORDER BY name;
