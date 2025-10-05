-- Fix ALL 'stochastic' references in strategies (deep search)
-- This handles multiple conditions in arrays, not just index 0

-- Helper function to recursively replace 'stochastic' with 'stochastic_k' in JSONB
CREATE OR REPLACE FUNCTION replace_stochastic_in_jsonb(data jsonb)
RETURNS jsonb AS $$
DECLARE
  result jsonb;
BEGIN
  -- If it's an object with 'left' = 'stochastic', replace it
  IF jsonb_typeof(data) = 'object' AND data->>'left' = 'stochastic' THEN
    result := jsonb_set(data, '{left}', '"stochastic_k"'::jsonb);
  -- If it's an array, recursively process each element
  ELSIF jsonb_typeof(data) = 'array' THEN
    result := '[]'::jsonb;
    FOR i IN 0..jsonb_array_length(data)-1 LOOP
      result := result || jsonb_build_array(replace_stochastic_in_jsonb(data->i));
    END LOOP;
  -- If it's an object, recursively process each value
  ELSIF jsonb_typeof(data) = 'object' THEN
    result := '{}'::jsonb;
    FOR key IN SELECT * FROM jsonb_object_keys(data) LOOP
      result := jsonb_set(result, ARRAY[key], replace_stochastic_in_jsonb(data->key));
    END LOOP;
  ELSE
    result := data;
  END IF;

  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Update all strategies
UPDATE strategies
SET config = replace_stochastic_in_jsonb(config)
WHERE config::text LIKE '%"left"%:%"stochastic"%'
  AND is_active = true;

-- Verify the results
SELECT
  id,
  name,
  config
FROM strategies
WHERE config::text LIKE '%stochastic%'
  AND is_active = true
ORDER BY name;

-- Clean up function
DROP FUNCTION replace_stochastic_in_jsonb(jsonb);
