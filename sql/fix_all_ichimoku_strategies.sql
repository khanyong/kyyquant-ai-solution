-- Fix ALL strategies with ichimoku custom operators
-- Convert tenkan_above_kijun → ichimoku_tenkan > ichimoku_kijun
-- Convert tenkan_below_kijun → ichimoku_tenkan < ichimoku_kijun
-- IMPORTANT: Ichimoku columns have ichimoku_ prefix!

-- Step 1: Find all strategies with ichimoku custom operators
SELECT
  id,
  name,
  config->'buyConditions' as buy_conditions,
  config->'sellConditions' as sell_conditions
FROM strategies
WHERE (
  config::text LIKE '%tenkan_above_kijun%'
  OR config::text LIKE '%tenkan_below_kijun%'
  OR config::text LIKE '%tenkan_cross_kijun%'
)
AND is_active = true;

-- Step 2: Replace tenkan_above_kijun with proper comparison
UPDATE strategies
SET config = replace(
  config::text,
  '"operator":"tenkan_above_kijun"',
  '"operator":">"'
)::jsonb
WHERE config::text LIKE '%"operator":"tenkan_above_kijun"%'
  AND is_active = true;

UPDATE strategies
SET config = replace(
  config::text,
  '"operator": "tenkan_above_kijun"',
  '"operator": ">"'
)::jsonb
WHERE config::text LIKE '%"operator": "tenkan_above_kijun"%'
  AND is_active = true;

-- Step 3: Replace tenkan_below_kijun with proper comparison
UPDATE strategies
SET config = replace(
  config::text,
  '"operator":"tenkan_below_kijun"',
  '"operator":"<"'
)::jsonb
WHERE config::text LIKE '%"operator":"tenkan_below_kijun"%'
  AND is_active = true;

UPDATE strategies
SET config = replace(
  config::text,
  '"operator": "tenkan_below_kijun"',
  '"operator": "<"'
)::jsonb
WHERE config::text LIKE '%"operator": "tenkan_below_kijun"%'
  AND is_active = true;

-- Step 4: Fix left: ichimoku → ichimoku_tenkan (for conditions using above operators)
UPDATE strategies
SET config = replace(
  config::text,
  '"left":"ichimoku"',
  '"left":"ichimoku_tenkan"'
)::jsonb
WHERE config::text LIKE '%"left":"ichimoku"%'
  AND (
    config::text LIKE '%tenkan%kijun%'
    OR config::text LIKE '%"operator":">"%'
    OR config::text LIKE '%"operator":"<"%'
  )
  AND is_active = true;

UPDATE strategies
SET config = replace(
  config::text,
  '"left": "ichimoku"',
  '"left": "ichimoku_tenkan"'
)::jsonb
WHERE config::text LIKE '%"left": "ichimoku"%'
  AND (
    config::text LIKE '%tenkan%kijun%'
    OR config::text LIKE '%"operator": ">"%'
    OR config::text LIKE '%"operator": "<"%'
  )
  AND is_active = true;

-- Step 4b: Fix any bare tenkan → ichimoku_tenkan
UPDATE strategies
SET config = replace(
  config::text,
  '"left":"tenkan"',
  '"left":"ichimoku_tenkan"'
)::jsonb
WHERE config::text LIKE '%"left":"tenkan"%'
  AND is_active = true;

UPDATE strategies
SET config = replace(
  config::text,
  '"left": "tenkan"',
  '"left": "ichimoku_tenkan"'
)::jsonb
WHERE config::text LIKE '%"left": "tenkan"%'
  AND is_active = true;

-- Step 5: Fix right: number → ichimoku_kijun (for tenkan/kijun comparisons)
-- WARNING: This will replace ALL numeric right values in ichimoku conditions
-- Only run if you're sure all ichimoku comparisons should use kijun

-- For safer approach, use the individual strategy fix SQL files instead
-- Example: fix_strategy_aaa_correct.sql

-- Step 5b: Fix any bare kijun → ichimoku_kijun
UPDATE strategies
SET config = replace(
  config::text,
  '"right":"kijun"',
  '"right":"ichimoku_kijun"'
)::jsonb
WHERE config::text LIKE '%"right":"kijun"%'
  AND is_active = true;

UPDATE strategies
SET config = replace(
  config::text,
  '"right": "kijun"',
  '"right": "ichimoku_kijun"'
)::jsonb
WHERE config::text LIKE '%"right": "kijun"%'
  AND is_active = true;

-- Step 6: Verify the fixes
SELECT
  id,
  name,
  config->'buyConditions' as buy_conditions,
  config->'sellConditions' as sell_conditions,
  CASE
    WHEN config::text LIKE '%tenkan_above_kijun%'
      OR config::text LIKE '%tenkan_below_kijun%'
    THEN '❌ Still has custom operators'
    WHEN config::text LIKE '%"left":"ichimoku"%'
      OR config::text LIKE '%"left": "ichimoku"%'
    THEN '❌ Still has bare ichimoku left'
    WHEN config::text LIKE '%"left":"tenkan"%'
      OR config::text LIKE '%"left": "tenkan"%'
      OR config::text LIKE '%"right":"kijun"%'
      OR config::text LIKE '%"right": "kijun"%'
    THEN '❌ Missing ichimoku_ prefix'
    WHEN config::text LIKE '%"left":"ichimoku_tenkan"%'
      AND config::text LIKE '%"right":"ichimoku_kijun"%'
    THEN '✅ Fixed with prefix'
    ELSE '⚠️ Check manually'
  END as status
FROM strategies
WHERE config::text LIKE '%ichimoku%'
  AND is_active = true
ORDER BY name;
