-- Fix "나의 전략 C" - Replace all 'stochastic' with 'stochastic_k'
-- This uses PostgreSQL's string replacement on JSONB

-- Option 1: Simple text replacement (works for most cases)
UPDATE strategies
SET config = (config::text)::jsonb
WHERE name = '나의 전략 C'
  AND is_active = true;

-- Better option: Use JSONB replace function
UPDATE strategies
SET config = replace(config::text, '"left":"stochastic"', '"left":"stochastic_k"')::jsonb
WHERE name = '나의 전략 C'
  AND is_active = true;

-- Also handle with spaces
UPDATE strategies
SET config = replace(
  replace(config::text, '"left":"stochastic"', '"left":"stochastic_k"'),
  '"left": "stochastic"',
  '"left": "stochastic_k"'
)::jsonb
WHERE name = '나의 전략 C'
  AND is_active = true;

-- Verify the fix
SELECT
  name,
  jsonb_pretty(config) as config
FROM strategies
WHERE name = '나의 전략 C'
  AND is_active = true;
